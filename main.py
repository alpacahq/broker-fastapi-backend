from fastapi import FastAPI

from dotenv import load_dotenv
load_dotenv()

from routers import routes

app = FastAPI()

app.include_router(routes.router)


@app.get("/")
async def root():
    return {"message": "Default route working"}
