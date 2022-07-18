import os
from dotenv import load_dotenv
load_dotenv()

import boto3
import cognitojwt

from fastapi import APIRouter, HTTPException, Request

from schemas.models import User

router = APIRouter() # Do I need prefix, tags, or responses?

@router.post("/signup")
async def register_user(user: User):
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
        ClientId=os.environ.get('COGNITO_USER_CLIENT_ID'),
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password
        }
    )
    access_token = auth_response['AuthenticationResult']['AccessToken']
    refresh_token = auth_response['AuthenticationResult']['RefreshToken']

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@router.post("/login")
async def login_user(user: User):
    username = user.email_address
    password = user.password

    client = boto3.client('cognito-idp', region_name=os.environ.get('COGNITO_REGION_NAME'))
    # Authenticate the user and return the tokens
    auth_response = client.initiate_auth(
        ClientId=os.environ.get('COGNITO_USER_CLIENT_ID'),
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password
        }
    )
    access_token = auth_response['AuthenticationResult']['AccessToken']
    refresh_token = auth_response['AuthenticationResult']['RefreshToken']

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@router.get("/protected")
async def root(request: Request):
    access_token = request.headers.get('access-token')
    REGION = os.environ.get('COGNITO_REGION_NAME')
    USERPOOL_ID = os.environ.get('USER_POOL_ID')
    APP_CLIENT_ID = os.environ.get('COGNITO_USER_CLIENT_ID')
    # Attempt to decode the access token
    try:
        verified_claims: dict = cognitojwt.decode(
            access_token,
            REGION,
            USERPOOL_ID,
            app_client_id=APP_CLIENT_ID 
        )
    except:
        raise HTTPException(
            status_code=401,
            detail="User is not authorized to get this resource"
        )
    username = verified_claims["username"]
    return {"message": f"Good job {username}, you're authorized"}