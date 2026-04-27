from contextlib import asynccontextmanager

from fastapi import FastAPI

from infrastructure.database.metadata import create_db_and_tables
from presentation.exception_handlers import register_exception_handlers
from presentation.routers.admin.router import admin_router
from presentation.routers.auth.router import auth_router
from presentation.routers.launcher.router import launcher_router
from presentation.routers.user.router import user_router
from presentation.routers.wardrobe.router import wardrobe_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.include_router(auth_router, prefix="/v1")
app.include_router(user_router, prefix="/v1")
app.include_router(wardrobe_router, prefix="/v1")
app.include_router(launcher_router, prefix="/v1")
app.include_router(admin_router, prefix="/v1")
