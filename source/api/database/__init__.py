from fastapi import APIRouter

RestBaseDatabaseRouter = APIRouter(tags=["Databases"])

from .db_controller import *  # noqa: E402, F403, F401
