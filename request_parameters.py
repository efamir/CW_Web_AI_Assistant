from pydantic import BaseModel

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
