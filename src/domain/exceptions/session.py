from domain.exceptions.base import DomainError


class InvalidTokenError(DomainError):
    pass


class SessionNotFoundError(DomainError):
    pass


class SessionRevokedError(DomainError):
    pass


class SessionExpiredError(DomainError):
    pass


class TokenAuthenticityError(DomainError):
    pass


class CannotRevokeSessionError(DomainError):
    pass
