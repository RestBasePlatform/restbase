from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel


class BaseHeader(BaseModel):
    token: str


class GenerateAdminToken(BaseModel):
    token_name: str
    description: str = None


class GenerateUserToken(GenerateAdminToken):
    token: str = None
    access_tables: Optional[List[str]] = ()


class DeleteUserToken(BaseModel):
    token_name: str


class AddDatabase(BaseModel):
    type: str
    host: str
    port: Optional[Union[str, int]]
    database: str
    username: str
    password: str
    connect_args: Optional[dict] = dict()
    local_name: Optional[str] = None
    description: Optional[str] = None
