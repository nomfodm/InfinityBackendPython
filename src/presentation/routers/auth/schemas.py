from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str


class LauncherLoginResponse(BaseModel):
    access_token: str
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str


class LogoutFromOthersRequest(BaseModel):
    password: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    verification_code: str
    new_password: str
