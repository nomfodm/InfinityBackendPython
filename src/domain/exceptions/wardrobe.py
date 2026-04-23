from domain.exceptions.base import DomainError


class WardrobeItemNotFoundError(DomainError):
    pass


class CannotPublishAddedTextureError(DomainError):
    pass


class TextureCatalogItemNotFoundError(DomainError):
    pass
