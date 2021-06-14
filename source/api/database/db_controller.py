from fastapi import Header
from fastapi import HTTPException
from schemas import AddDatabase

from . import RestBaseDatabaseRouter
from localbase import LocalBaseWorker
from token_worker import TokenWorker
from utils import make_response
from utils import validate_admin_access


@RestBaseDatabaseRouter.put("/Database/Add")
async def add_database(body: AddDatabase, token: str = Header(None)):
    try:
        local_base_worker = LocalBaseWorker()
        if not validate_admin_access(token, local_base_worker):
            raise HTTPException(
                status_code=403,
                detail={"status": "Error", "message": "Permission denied"},
            )
        db_local_name = local_base_worker.add_database(
            body.type,
            body.description,
            local_name=body.local_name,
            host=body.host,
            port=body.port,
            username=body.username,
            password=body.password,
        )
        return make_response(0, {"local_db_name": db_local_name})
    except Exception as e:
        if not isinstance(e, HTTPException):
            raise HTTPException(
                status_code=502, detail={"status": "Error", "message": str(e)}
            )
        raise