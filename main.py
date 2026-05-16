from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router
from app.api.v1.subscription import public_router
from app.config_gen.manager import ConfigManager
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.utils.init_db import create_admin_if_not_exists, create_default_configs


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_default_configs()
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await create_admin_if_not_exists(session)
            manager = ConfigManager(session)
            await manager.regenerate_all()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    app.include_router(router)
    app.include_router(public_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost", "http://localhost:8080"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["system"])
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
