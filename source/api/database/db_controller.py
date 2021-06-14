from fastapi import Header
from fastapi import HTTPException
from schemas import AddDatabase

from . import RestBaseDatabaseRouter
from localbase import LocalBaseWorker
from utils import get_worker
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
            database=body.database,
            host=body.host,
            port=body.port,
            username=body.username,
            password=body.password,
            con_args=body.connect_args,
        )

        worker = get_worker(body.type)(db_local_name, local_base_worker)
        tables = worker.download_table_list()
        for local_table_name in tables:
            for token in local_base_worker.get_admin_tokens_objects_list(
                with_main_admin=True
            ):
                local_base_worker.add_table_for_token(
                    token.token, local_table_name=local_table_name
                )
        return make_response(0, {"local_db_name": db_local_name})
    except Exception as e:
        if not isinstance(e, HTTPException):
            raise HTTPException(
                status_code=502, detail={"status": "Error", "message": str(e)}
            )
        raise


@RestBaseDatabaseRouter.get("/Database/List")
async def add_database(token: str = Header(None)):
    try:
        local_base_worker = LocalBaseWorker()
        if not validate_admin_access(token, local_base_worker):
            raise HTTPException(
                status_code=403,
                detail={"status": "Error", "message": "Permission denied"},
            )
        db_list = local_base_worker.get_db_name_list()
        return make_response(0, {"Databases": db_list})
    except Exception as e:
        if not isinstance(e, HTTPException):
            raise HTTPException(
                status_code=502, detail={"status": "Error", "message": str(e)}
            )
        raise


@RestBaseDatabaseRouter.get("/Database/{local_database_name}")
async def add_database(local_database_name: str, token: str = Header(None)):
    try:
        local_base_worker = LocalBaseWorker()
        if not validate_admin_access(token, local_base_worker):
            raise HTTPException(
                status_code=403,
                detail={"status": "Error", "message": "Permission denied"},
            )
        database_data = local_base_worker.get_database_data(local_database_name)
        return make_response(0, {f"Database {local_database_name} data": database_data})
    except Exception as e:
        if not isinstance(e, HTTPException):
            raise HTTPException(
                status_code=502, detail={"status": "Error", "message": str(e)}
            )
        raise
