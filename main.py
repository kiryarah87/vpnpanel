from fastapi import FastAPI

from app.api.v1 import router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
    )

    app.include_router(router)

    @app.get("/health", tags=["system"])
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
