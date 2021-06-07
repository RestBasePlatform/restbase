from pydantic import BaseModel
from typing import List
from typing import Optional


class BaseHeader(BaseModel):
    token: str


class GenerateAdminToken(BaseModel):
    token_name: str
    description: str = None


class GenerateUserToken(GenerateAdminToken):
    token: str = None
    access_tables: List[str] = ()
