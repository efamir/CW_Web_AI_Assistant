from pydantic import BaseModel
import datetime

class UserAuthorize(BaseModel):
    username: str
    password: str

class RegisterAnswer(BaseModel):
    token: str
    success: bool

class LoginAnswer(BaseModel):
    token: str
    success: bool
    error: str | None

class TokenCheckResponse(BaseModel):
    exist: bool
    is_admin: bool

class Token(BaseModel):
    token: str

class AdminError(BaseModel):
    token_dont_exist: bool | None
    is_not_admin: bool | None

class UserInfo(BaseModel):
    username: str
    token: str
    role: str

class DeleteUser(BaseModel):
    admin_token: str
    user_token: str

class ProcessTextPrompt(BaseModel):
    token: str
    prompt: str

class ProcessPromptResponse(BaseModel):
    response_text: str
    audio_file_path: str
    timer_timestamp: int | None

class CreateNote(BaseModel):
    token: str
    text: str

class Note(BaseModel):
    id: int
    text: str
    created_at: datetime.datetime

class DeleteNote(BaseModel):
    note_id: int
    token: str

class UpdateNote(BaseModel):
    note_id: int
    token: str
    new_text: str
