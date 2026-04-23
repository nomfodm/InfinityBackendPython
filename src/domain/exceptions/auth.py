from domain.exceptions.base import DomainError


class AccessDeniedError(DomainError):
    pass


class UserBannedError(DomainError):
    pass


class UserNeedsActivationError(DomainError):
    pass


class InvalidCredentialError(DomainError):
    pass


class EmailTakenError(DomainError):
    pass


class UsernameTakenError(DomainError):
    pass


class UnauthenticatedError(DomainError):
    pass
