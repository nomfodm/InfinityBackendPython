from application.dtos.wardrobe import TextureCatalogItemResponse
from domain.interfaces.unit_of_work import UnitOfWork


class GetTextureCatalogUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    async def execute(self) -> list[TextureCatalogItemResponse]:
        async with self._uow:
            items = await self._uow.texture_catalog.get_all()
            return [TextureCatalogItemResponse.from_domain(item) for item in items]
