from fastapi import APIRouter

from app.api.v1 import auth, client, domain, inbound, subscription

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(client.router)
router.include_router(domain.router)
router.include_router(inbound.router)
router.include_router(subscription.router)
router.include_router(subscription.public_router)
