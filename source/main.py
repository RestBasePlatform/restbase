import os

import fastapi as fa
from api import RestBaseTokensRouter
from localbase import LocalBaseWorker

from utils import run_migrations

app = fa.FastAPI()


run_migrations()


if os.getenv('TEST'):
    LocalBaseWorker.add_test_token()

app.include_router(RestBaseTokensRouter)
