from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from contextlib import asynccontextmanager

from request_parameters import *
import db
from llm import UserPromptHandler, DeepSeekConversationExtractor

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


@app.post("/register")
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


@app.post("/login")
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


@app.post("/verify_token")
async def verify_token(token: Token):
    return check_token(token)


def check_admin(token: Token) -> AdminError | None:
    token_check_res = check_token(token)
    if not token_check_res.exist:
        return AdminError(token_dont_exist=True, is_not_admin=None)
    if not token_check_res.is_admin:
        return AdminError(token_dont_exist=False, is_not_admin=True)


@app.post("/admin/users")
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


@app.delete("/admin/users/delete")
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


@app.post("/process_text")
async def process_text(process_text_prompt: ProcessTextPrompt):
    user: db.User | None = db.session.query(db.User).filter(db.User.token == process_text_prompt.token).first()
    if not user:
        return TokenCheckResponse(exist=False, is_admin=False)
    res = handler.process_prompt(user.id, process_text_prompt.prompt)
    return ProcessPromptResponse(
        response_text=res["response_text"], audio_file_path=res["audio_file_path"], timer_timestamp=res["timer_timestamp"]
    )


@app.post("/process_audio")
async def process_audio():
    return {"message": "Hello World"}
