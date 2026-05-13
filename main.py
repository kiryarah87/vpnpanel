from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import router
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.init_db import create_admin_if_not_exists


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await create_admin_if_not_exists(session)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    app.include_router(router)

    @app.get("/health", tags=["system"])
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
