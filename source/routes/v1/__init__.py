from fastapi import APIRouter


v1_router = APIRouter(prefix="/v1")


from .installation import installation_router

v1_router.include_router(installation_router)
