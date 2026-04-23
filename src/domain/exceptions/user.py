from domain.exceptions.base import DomainError


class InvalidVerificationCode(DomainError):
    pass


class NicknameTakenError(DomainError):
    pass
