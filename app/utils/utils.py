import os
import cognitojwt
from dotenv import load_dotenv
load_dotenv()

from fastapi import HTTPException

# User ID from Cognito is currently not utilized
class CognitoResponse(object):
    def __init__(self, access_token, refresh_token, cognito_user_id=None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.cognito_user_id = cognito_user_id

    
def authenticate_token(access_token: str):
    REGION = os.environ.get('COGNITO_REGION_NAME')
    USERPOOL_ID = os.environ.get('USER_POOL_ID')
    APP_CLIENT_ID = os.environ.get('COGNITO_USER_CLIENT_ID')
    # Attempt to decode the access token
    try:
        # Can get user properties from these claims
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
