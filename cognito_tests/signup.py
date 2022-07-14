import os
import boto3
from dotenv import load_dotenv
load_dotenv()

username = 'admin2@test.com'
password = 'asdfasdf'

client = boto3.client('cognito-idp', region_name=os.environ.get('COGNITO_REGION_NAME'))
response = client.sign_up(
    ClientId=os.environ.get('COGNITO_USER_CLIENT_ID'),
    Username=username,
    Password=password
)

# This will confirm user registration as an admin without a confirmation code
response = client.admin_confirm_sign_up(
    UserPoolId=os.environ.get('USER_POOL_ID'),
    Username=username,
)

print(response)