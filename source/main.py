import os

import uvicorn
from controller.v1.utils import generate_secret_token
from fastapi import FastAPI
from loguru import logger
from routes.v1 import v1_router


app = FastAPI()


app.include_router(v1_router)

if __name__ == "__main__":
    if not os.getenv("SECRET_TOKEN"):
        logger.warning("Token not found.")
        token = generate_secret_token()
        os.environ["SECRET_TOKEN"] = token
        logger.info(f"Your token: '{token}'")

    uvicorn.run(app, port=8000)
