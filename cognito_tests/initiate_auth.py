import os
import boto3
from dotenv import load_dotenv
load_dotenv()

username = 'admin2@test.com'
password = 'asdfasdf'

client = boto3.client('cognito-idp', region_name=os.getenv('COGNITO_REGION_NAME'))
response = client.initiate_auth(
    ClientId=os.getenv('COGNITO_USER_CLIENT_ID'),
    AuthFlow='USER_PASSWORD_AUTH',
    AuthParameters={
        'USERNAME': username,
        'PASSWORD': password
    }
)

access_token = response['AuthenticationResult']['AccessToken']
refresh_token = response['AuthenticationResult']['RefreshToken']

print(f'Response: {response}\n')
print(f'Access token: {access_token}\n')
print(f'Refresh token: {refresh_token}\n')

