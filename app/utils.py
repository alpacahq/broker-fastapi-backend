import os
import boto3
from dotenv import load_dotenv
load_dotenv()

# Maybe should change this to Cognito Response?
class SignupResult(object):
    def __init__(self, user_id, access_token, refresh_token):
        self.user_id = user_id
        self.access_token = access_token
        self.refresh_token =refresh_token


# Getting quite messy, this will be temporary
class ServiceResult(object):
    def __init__(self, result, access_token, refresh_token):
        self.result = result
        self.access_token = access_token
        self.refresh_token =refresh_token


def cognito_signup(username: str, password: str):
    # In order to get the ID and authenticate, use AWS Cognito
    client = boto3.client('cognito-idp', region_name=os.environ.get('COGNITO_REGION_NAME'))
    response = client.sign_up(
        ClientId=os.environ.get('COGNITO_USER_CLIENT_ID'),
        Username=username,
        Password=password
    )
    user_sub = response['UserSub']

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

    signup_result = SignupResult(
        user_id=user_sub,
        access_token=access_token,
        refresh_token=refresh_token
    )
    return signup_result