from plaid.api import plaid_api
import plaid
import os
from dotenv import load_dotenv
load_dotenv()

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')

host = plaid.Environment.Sandbox
configuration = plaid.Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
        'plaidVersion': '2020-09-14'
    }
)

def get_plaid_client():
    client = plaid.ApiClient(configuration)
    api = plaid_api.PlaidApi(client)
    return api