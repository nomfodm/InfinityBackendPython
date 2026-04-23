import enum


class VerificationCodePurpose(str, enum.Enum):
    ACTIVATION = "activation"
    PASSWORD_RESET = "password_reset"
