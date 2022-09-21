import os
import cognitojwt
from dotenv import load_dotenv
load_dotenv()

from typing import Union
from ..schemas import schemas
from .constants import *

from alpaca.broker.requests import BatchJournalRequestEntry

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
            detail="User is not authorized to access this resource. Check access token."
        )

def validate_journal_request(request_params: Union[schemas.JournalParams, schemas.JournalEntry]):
    if request_params.entry_type not in journal_entry_types:
        raise HTTPException(status_code=422, detail="Journal entry type must be JNLC or JNLS")

    if isinstance(request_params, schemas.JournalParams):
        if request_params.entry_type == "JNLC" and request_params.amount is None:
            raise HTTPException(status_code=400, detail="Cash journals require amount in the request")
        elif request_params.entry_type == "JNLS" and (request_params.symbol is None or request_params.qty is None):
            raise HTTPException(status_code=400, detail="Security journals require symbol and qty")


def create_batch_entry(entry_type: str, entry: schemas.JournalEntry):
    if entry_type == "JNLC":
        to_account, amount = entry.to_account, entry.amount
        batch_journal_request = BatchJournalRequestEntry(to_account=to_account, amount=amount)
    else:  # entry_type == "JNLS"
        to_account, symbol, qty = entry.to_account, entry.symbol, entry.qty
        batch_journal_request = BatchJournalRequestEntry(to_account=to_account, symbol=symbol, qty=qty)
    return batch_journal_request


def validate_order_request(request_params: schemas.OrderParams):
    # Validate order side
    if request_params.side not in order_sides:
        raise HTTPException(status_code=422, detail="Order side must be buy or sell")

    # Validate time in force
    if request_params.time_in_force not in time_in_forces:
        raise HTTPException(status_code=422, detail="Time in force must be day, gtc, opg, cls, ioc, or fok")

    # Validate order type
    if request_params.type not in order_types:
        raise HTTPException(status_code=422, detail="Order type must be market, limit, stop, stop_limit, or trailing_stop")
    elif request_params.type == "market" and not ((request_params.notional is None) ^ (request_params.qty is None)):
        raise HTTPException(status_code=400, detail="Market orders must have only one of notional OR qty")
    elif request_params.type == "limit" and request_params.limit_price is None:
        raise HTTPException(status_code=400, detail="Limit orders must be used with limit_price")
