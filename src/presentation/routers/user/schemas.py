from pydantic import BaseModel, EmailStr

from domain.entities.verification_code import VerificationCodePurpose


class ActivateUserRequest(BaseModel):
    email: EmailStr
    verification_code: str


class SendVerificationCodeRequest(BaseModel):
    purpose: VerificationCodePurpose


class ChangeEmailRequest(BaseModel):
    new_email: EmailStr


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class ChangeUsernameRequest(BaseModel):
    new_username: str


class ChangeNicknameRequest(BaseModel):
    new_nickname: str
