from fastapi import APIRouter

RestBaseTokensRouter = APIRouter()

from .admin_token import *  # noqa: E402, F403, F401
from .user_token import *  # noqa: E402, F403, F401
