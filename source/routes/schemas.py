from pydantic import BaseModel
from pydantic import Field


class InstallModule(BaseModel):
    module_name: str = Field(title="Название модуля", default=None)
    version: str = Field(title="Версия модуля", default="latest")
    source: str = Field(title="Источник", default="GithubURL")
    github_url: str = Field(title="Ссылка на гит", default=None)


class DeleteModule(BaseModel):
    module_name: str = Field(title="Название модуля")
    version: str = Field(title="Версия модуля")
    all_versions: bool = Field(title="Флаг удаления всех версий", default=False)
