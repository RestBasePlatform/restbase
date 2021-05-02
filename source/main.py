import fastapi as fa

from api import RestBaseTokensRouter
from utils import run_migrations


app = fa.FastAPI()


# run_migrations()

app.include_router(RestBaseTokensRouter)
