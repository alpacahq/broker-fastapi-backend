from typing import List
from fastapi import FastAPI, HTTPException
from uuid import UUID

import os
import boto3
import cognitojwt
from dotenv import load_dotenv
load_dotenv()

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

# @app.post("/api/v1/users")
# async def register_user(user: User):
#     db.append(user)
#     return {"id": user.id}

@app.post("/api/v1/users")
async def register_user(user: User):
    # Sign user up. In the future should put this in utils folder
    username = user.email_address
    password = user.password

    client = boto3.client('cognito-idp', region_name=os.environ.get('COGNITO_REGION_NAME'))
    signup_response = client.sign_up(
        ClientId=os.environ.get('COGNITO_USER_CLIENT_ID'),
        Username=username,
        Password=password
    )
    user_sub = signup_response['UserSub']

    # This will confirm user registration as an admin without a confirmation code
    client.admin_confirm_sign_up(
        UserPoolId=os.environ.get('USER_POOL_ID'),
        Username=username,
    )

    # Now authenticate the user and return the tokens
    auth_response = client.initiate_auth(
        ClientId=os.getenv('COGNITO_USER_CLIENT_ID'),
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password
        }
    )
    access_token = auth_response['AuthenticationResult']['AccessToken']
    refresh_token = auth_response['AuthenticationResult']['RefreshToken']

    return {
        "id": user_sub,
        "access_token": access_token,
        "refresh_token": refresh_token
    }

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
