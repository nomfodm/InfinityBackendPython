import enum


class VerificationCodePurpose(enum.StrEnum):
    ACTIVATION = "activation"
    PASSWORD_RESET = "password_reset"
