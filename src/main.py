from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.infrastructure.database.session import create_db_and_tables

from presentation.routers.auth.router import auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    

app = FastAPI(lifespan=lifespan)


app.include_router(auth_router, prefix="/auth")


