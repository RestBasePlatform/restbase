from typing import Optional

from pydantic import BaseModel


class BaseHeader(BaseModel):
    token: str


class GenerateAdminToken(BaseModel):
    token_name: str
    description: str = None
