from . import RestBaseTokensRouter
from localbase import LocalBaseWorker
from token_worker import TokenWorker


@RestBaseTokensRouter.get("/AdminToken/GenerateFirstToken/", tags=['admin_token'])
async def generate_admin_token():
    local_base_worker = LocalBaseWorker()
    token_worker = TokenWorker(local_base_worker)
    admin_token = token_worker.add_admin_token()
    return admin_token
