from typing import List

from pydantic import BaseModel


class BaseHeader(BaseModel):
    token: str


class GenerateAdminToken(BaseModel):
    token_name: str
    description: str = None


class GenerateUserToken(GenerateAdminToken):
    token: str = None
    access_tables: List[str] = ()


class DeleteUserToken(BaseModel):
    token_name: str
