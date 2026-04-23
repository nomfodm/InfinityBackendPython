from domain.exceptions.base import DomainError


class MinecraftSessionNotFoundError(DomainError):
    pass


class MinecraftProfileNotFoundError(DomainError):
    pass


class InvalidMCAccessToken(DomainError):
    pass


class InvalidMCServerID(DomainError):
    pass
