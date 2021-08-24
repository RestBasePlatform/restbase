from controller.v1.module import install_from_release
from controller.v1.module import install_module_from_github
from controller.v1.module import list_installed_modules
from controller.v1.module import list_modules
from controller.v1.module import remove_module
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from models.utils import get_db_session

from ..schemas import DeleteModule
from ..schemas import InstallModule


installation_router = APIRouter(prefix="/modules", tags=["Installation"])


@installation_router.get("/list_all/")
def _list_modules():
    try:
        return list_modules()
    except BaseException as e:
        raise HTTPException(status_code=500, detail=str(e))


@installation_router.get("/list_installed/")
def _list_installed_modules(pg_session=Depends(get_db_session)):
    try:
        return list_installed_modules(pg_session)
    except BaseException as e:
        raise HTTPException(status_code=500, detail=str(e))


@installation_router.post("/install/")
def _install_module(data: InstallModule, pg_session=Depends(get_db_session)):
    # try:
    if data.source.lower() == "githuburl":
        return install_module_from_github(data.github_url, pg_session)
    if data.source.lower() == "release":
        return install_from_release(data.module_name, data.version, pg_session)
        # raise ValueError(f"Install from {data.source} is not supported yet")
    # except BaseException as e:
    #     raise HTTPException(status_code=500, detail=str(e))


@installation_router.delete("/delete/")
def _delete_module(data: DeleteModule, pg_session=Depends(get_db_session)):
    try:
        return remove_module(
            data.module_name, data.version, pg_session, data.all_versions
        )
    except BaseException as e:
        raise HTTPException(status_code=500, detail=str(e))


@installation_router.delete("/delete/all/")
def delete_all_modules(pg_session=Depends(get_db_session)):
    try:
        for module_data in list_installed_modules(pg_session):
            remove_module(
                module_data["module_name"], module_data["version"], pg_session
            )
        return "All modules successfully removed"
    except BaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
