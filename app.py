from fastapi import FastAPI, UploadFile, File, Form, status
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from typing import Union, List, Annotated
import uuid
import shutil

from request_parameters import *
import db
from prompt_handler.llm import UserPromptHandler, DeepSeekConversationExtractor

USER_ROLE: db.Role | None = None
ADMIN_ROLE: db.Role | None = None
llm_model_name = "deepseek-r1:8b"
tts_model_name = "tts_models/en/ljspeech/fast_pitch"
conv_extractor = DeepSeekConversationExtractor()
handler = UserPromptHandler(llm_model_name, tts_model_name, conversation_extractor=conv_extractor)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global USER_ROLE, ADMIN_ROLE
    try:
        user_role = db.session.query(db.Role).filter_by(name="user").first()
        if not user_role:
            user_role = db.Role(name="user")
            db.session.add(user_role)

        admin_role = db.session.query(db.Role).filter_by(name="admin").first()
        if not admin_role:
            admin_role = db.Role(name="admin")
            db.session.add(admin_role)

        admin_user = db.session.query(db.User).filter_by(username="admin").first()
        if not admin_user:
            admin_user = db.User("admin", "admin", admin_role)
            db.session.add(admin_user)

        db.session.commit()

        USER_ROLE = user_role
        ADMIN_ROLE = admin_role
    except Exception as e:
        db.session.rollback()
        print(f"Error during startup role initialization: {e}")
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/register", response_model=RegisterAnswer)
async def register(register_params: UserAuthorize):
    existing_user = db.session.query(db.User).filter(db.User.username == register_params.username).first()
    if existing_user:
        return RegisterAnswer(token="", success=False)
    new_user = db.User(
        username=register_params.username,
        password_string=register_params.password,
        role=USER_ROLE
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        db.session.refresh(new_user)
        return RegisterAnswer(token=new_user.token, success=True)
    except Exception as e:
        db.session.rollback()
        print(f"Error during registration: {e}")
        raise HTTPException(status_code=500, detail="Could not register user")


@app.post("/login", response_model=LoginAnswer)
async def login(login_params: UserAuthorize):
    existing_user: db.User | None = db.session.query(db.User).filter(db.User.username == login_params.username).first()
    if not existing_user:
        return LoginAnswer(token="", success=False, error="username")
    if not existing_user.check_password(login_params.password):
        return LoginAnswer(token="", success=False, error="password")
    return LoginAnswer(token=existing_user.token, success=True, error=None)


def check_token(token: Token) -> TokenCheckResponse:
    existing_user: db.User | None = db.session.query(db.User).filter(db.User.token == token.token).first()
    if not existing_user:
        return TokenCheckResponse(exist=False, is_admin=False)
    if existing_user.role == ADMIN_ROLE:
        return TokenCheckResponse(exist=True, is_admin=True)
    return TokenCheckResponse(exist=True, is_admin=False)


@app.post("/verify_token", response_model=TokenCheckResponse)
async def verify_token(token: Token):
    return check_token(token)


def check_admin(token: Token) -> AdminError | None:
    token_check_res = check_token(token)
    if not token_check_res.exist:
        return AdminError(token_dont_exist=True, is_not_admin=None)
    if not token_check_res.is_admin:
        return AdminError(token_dont_exist=False, is_not_admin=True)


@app.post("/admin/users", response_model=Union[AdminError, List[UserInfo]])
async def get_users(token: Token):
    check_admin_res = check_admin(token)
    if check_admin_res:
        return check_admin_res
    users = db.session.query(db.User).all()
    return [
        UserInfo(
            username=user.username,
            token=user.token,
            role=user.role.name if user.role else "N/A"
        ) for user in users
    ]


@app.delete("/admin/users/delete", response_model=Union[AdminError, TokenCheckResponse, dict])
async def del_user(delete_user: DeleteUser):
    check_admin_res = check_admin(Token(token=delete_user.admin_token))
    if check_admin_res:
        return check_admin_res
    user_to_delete: db.User | None = db.session.query(db.User).filter(db.User.token == delete_user.user_token).first()
    if not user_to_delete:
        return TokenCheckResponse(exist=False, is_admin=False)

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return {"message": f"User '{user_to_delete.username}' deleted successfully"}
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail="Could not delete user")


@app.post("/create_note", response_model=Union[TokenCheckResponse, Note])
async def create_note(note: CreateNote):
    user: db.User | None = db.session.query(db.User).filter(db.User.token == note.token).first()
    if not user:
        return TokenCheckResponse(exist=False, is_admin=False)
    new_note = db.Note(text=note.text, user_id=user.id)
    try:
        db.session.add(new_note)
        db.session.commit()
        db.session.refresh(new_note)
        return Note(id=new_note.id, text=new_note.text, created_at=new_note.created_at)
    except Exception as e:
        db.session.rollback()
        print(f"Error during creating note: {e}")
        raise HTTPException(status_code=500, detail="Could not create note")


@app.post("/update_note", response_model=Union[TokenCheckResponse, dict])
async def update_note(note: UpdateNote):
    user: db.User | None = db.session.query(db.User).filter(db.User.token == note.token).first()
    if not user:
        return TokenCheckResponse(exist=False, is_admin=False)

    note_to_update: db.Note | None = db.session.query(db.Note).filter(db.Note.id == note.note_id).first()
    if not note_to_update:
        return {"error": f"There is no note with such id"}

    try:
        note_to_update.text = note.new_text
        db.session.commit()
        db.session.refresh(note_to_update)
        return {"message": f"Note '{note_to_update}' updated successfully"}
    except Exception as e:
        db.session.rollback()
        print(f"Error updating note: {e}")
        raise HTTPException(status_code=500, detail="Could not update note")


@app.post("/notes", response_model=Union[TokenCheckResponse, List[Note]])
async def notes(token: Token):
    user: db.User | None = db.session.query(db.User).filter(db.User.token == token.token).first()
    if not user:
        return TokenCheckResponse(exist=False, is_admin=False)
    user_notes: list[db.Note] = user.notes
    return [
        Note(
            id=note.id,
            text=note.text,
            created_at=note.created_at,
        ) for note in user_notes
    ]


@app.delete("/note", response_model=Union[TokenCheckResponse, dict])
async def del_note(delete_note: DeleteNote):
    user: db.User | None = db.session.query(db.User).filter(db.User.token == delete_note.token).first()
    if not user:
        return TokenCheckResponse(exist=False, is_admin=False)

    note_to_delete: db.Note | None = db.session.query(db.Note).filter(db.Note.user_id == user.id).first()
    if not note_to_delete:
        return {"error": f"There is no note with such id"}

    try:
        db.session.delete(note_to_delete)
        db.session.commit()
        return {"message": f"User '{note_to_delete}' deleted successfully"}
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting note: {e}")
        raise HTTPException(status_code=500, detail="Could not delete note")


def delete_last_output_file(user: db.User, new_output_file):
    if user.last_output_file_path:
        try:
            os.remove(os.path.join("static", user.last_output_file_path))
        except Exception as e:
            print(f"Error while deleting file: {e}")
    user.last_output_file_path = new_output_file


@app.post("/process_text", response_model=Union[TokenCheckResponse, ProcessPromptResponse])
async def process_text(process_text_prompt: ProcessTextPrompt):
    user: db.User | None = db.session.query(db.User).filter(db.User.token == process_text_prompt.token).first()
    if not user:
        return TokenCheckResponse(exist=False, is_admin=False)
    res = handler.process_prompt(user.id, process_text_prompt.prompt)
    delete_last_output_file(user, res["audio_file_path"].split("/")[-1])

    return ProcessPromptResponse(
        response_text=res["response_text"], audio_file_path=res["audio_file_path"],
        timer_timestamp=res["timer_timestamp"]
    )


@app.post("/process_audio")
async def process_audio(
        file: Annotated[UploadFile, File()],
        token: Annotated[str, Form()]
):
    user: db.User | None = db.session.query(db.User).filter(db.User.token == token).first()
    if not user:
        return TokenCheckResponse(exist=False, is_admin=False)

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No audio file provided."
        )

    allowed_mime_types = ["audio/webm", "audio/mpeg", "video/webm"]

    if file.content_type not in allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported content type: {file.content_type}. Only webm and mp3 audio are allowed."
        )

    res = handler.process_prompt_by_audio_file(user.id, file.file)
    delete_last_output_file(user, res["audio_file_path"].split("/")[-1])

    return ProcessPromptResponse(
        response_text=res["response_text"], audio_file_path=res["audio_file_path"],
        timer_timestamp=res["timer_timestamp"]
    )
