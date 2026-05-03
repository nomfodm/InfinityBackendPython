from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],       # List of origins allowed to make requests
    allow_credentials=True,      # Allow cookies/auth headers in cross-origin requests
    allow_methods=["*"],         # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],         # Allow all headers
)

register_exception_handlers(app)

app.mount("/uploads", StaticFiles(directory=Path(__file__).parent.parent / "uploads"), name="uploads")

@app.get("/health")
async def health():
    return {"status": "operational"}

app.include_router(auth_router, prefix="/v1")
app.include_router(user_router, prefix="/v1")
app.include_router(wardrobe_router, prefix="/v1")
app.include_router(launcher_router, prefix="/v1")
app.include_router(admin_router, prefix="/v1")
