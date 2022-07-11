from typing import List
from fastapi import FastAPI, HTTPException
from uuid import UUID

from models import User

app = FastAPI()

db: List[User] = [
    User(
        id=UUID("8a3c42d8-2d1c-4f3c-924d-6e403cb49d15"),
        email_address="andrew@alpaca.markets",
        password="cheekypassword"
    ),
    User(
        id=UUID("7630704f-8ac8-4487-a5bd-3281b23aa1d4"),
        email_address="rahul@alpaca.markets",
        password="haxdds"
    ),
]

@app.get("/")
async def root():
    return {"Hello": "wooder"}

@app.get("/api/v1/users")
async def fetch_users():
    return db

@app.post("/api/v1/users")
async def register_user(user: User):
    db.append(user)
    return {"id": user.id}

@app.delete("/api/v1/users/{user_id}")
async def delete_user(user_id: UUID):
    for user in db:
        if user.id == user_id:
            db.remove(user)
            return
    raise HTTPException(
        status_code=404,
        detail=f"User with id: {user_id} could not be found"
    )
