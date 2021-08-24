import uvicorn
from fastapi import FastAPI
from routes.v1 import v1_router

app = FastAPI()


app.include_router(v1_router)

if __name__ == "__main__":
    uvicorn.run(app, port=8000)
