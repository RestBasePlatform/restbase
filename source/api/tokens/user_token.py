import json

from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from pydantic import ValidationError
from schemas import BaseHeader
from schemas import GenerateAdminToken

from . import RestBaseTokensRouter
from localbase import LocalBaseWorker
from token_worker import TokenWorker


@RestBaseTokensRouter.get("/UserToken/Generate/")
async def generate_user_token(request: Request):
    pass