import boto3
from datetime import datetime
from faker import Faker
from sqlalchemy.orm import Session
from fastapi import HTTPException, Request
from uuid import UUID

from alpaca.broker.client import BrokerClient
from alpaca.broker.models import (
                        Contact,
                        Identity,
                        Disclosures,
                        Agreement
                    )
from alpaca.broker.requests import CreateAccountRequest, CreatePlaidRelationshipRequest, CreateACHTransferRequest, CreateJournalRequest, CreateBatchJournalRequest, MarketOrderRequest, LimitOrderRequest
from alpaca.broker.enums import TaxIdType, FundingSource, AgreementType, TransferDirection, TransferTiming

from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.processor_token_create_request import ProcessorTokenCreateRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.api import plaid_api

from ..schemas import schemas
from ..models import models
from ..utils import utils, constants

import os
from webbrowser import get
from dotenv import load_dotenv
load_dotenv()


def cognito_signup(username: str, password: str):
    # In order to get the ID and authenticate, use AWS Cognito
    client = boto3.client('cognito-idp', region_name=os.environ.get('COGNITO_REGION_NAME'))
    try:
        response = client.sign_up(
            ClientId=os.environ.get('COGNITO_USER_CLIENT_ID'),
            Username=username,
            Password=password
        )
    except Exception as e: # Generally, will trigger upon non-unique email
        raise HTTPException(status_code=400, detail=f"{e}")
    
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

    signup_result = utils.CognitoResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        cognito_user_id=user_sub
    )
    return signup_result


def cognito_login(username: str, password: str):
    client = boto3.client('cognito-idp', region_name=os.environ.get('COGNITO_REGION_NAME'))
    # Authenticate the user and return the tokens
    try:
        auth_response = client.initiate_auth(
            ClientId=os.environ.get('COGNITO_USER_CLIENT_ID'),
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
    except Exception as e: # Generally, will trigger upon wrong email/password
        raise HTTPException(status_code=400, detail=f"{e}")

    access_token = auth_response['AuthenticationResult']['AccessToken']
    refresh_token = auth_response['AuthenticationResult']['RefreshToken']
    login_result = utils.CognitoResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )
    return login_result


def create_broker_account(email: str, first_name: str):
    fake = Faker()

    broker_client = get_broker_client()

    contact_data = Contact(
            email_address=email,
            phone_number=fake.phone_number(),
            street_address=[fake.street_address()],
            city=fake.city(),
            state=fake.state_abbr(),
            postal_code=fake.postcode(),
            country=fake.country()
            )
    # Identity
    identity_data = Identity(
            given_name=first_name,
            middle_name=fake.first_name(),
            family_name=fake.last_name(),
            date_of_birth=str(fake.date_of_birth(minimum_age=21, maximum_age=81)),
            tax_id=fake.ssn(),
            tax_id_type=TaxIdType.USA_SSN,
            country_of_citizenship="USA",
            country_of_birth="USA",
            country_of_tax_residence="USA",
            funding_source=[FundingSource.EMPLOYMENT_INCOME]
            )

    # Disclosures
    disclosure_data = Disclosures(
            is_control_person=False,
            is_affiliated_exchange_or_finra=False,
            is_politically_exposed=False,
            immediate_family_exposed=False,
            )

    # Agreements
    agreement_data = [
        Agreement(
        agreement=AgreementType.MARGIN,
        signed_at="2020-09-11T18:09:33Z",
        ip_address="185.13.21.99",
        ),
        Agreement(
        agreement=AgreementType.ACCOUNT,
        signed_at="2020-09-11T18:13:44Z",
        ip_address="185.13.21.99",
        ),
        Agreement(
        agreement=AgreementType.CUSTOMER,
        signed_at="2020-09-11T18:13:44Z",
        ip_address="185.13.21.99",
        ),
        Agreement(
        agreement=AgreementType.CRYPTO,
        signed_at="2020-09-11T18:13:44Z",
        ip_address="185.13.21.99",
        )
    ]

    # ## CreateAccountRequest ## #
    account_data = CreateAccountRequest(
                            contact=contact_data,
                            identity=identity_data,
                            disclosures=disclosure_data,
                            agreements=agreement_data
                            )

    # Make a request to create a new brokerage account
    account = broker_client.create_account(account_data)
    return account


def create_account(db: Session, account: schemas.AccountCreate, request: Request):
    # Check if email already exists in the DB
    db_user = get_account_by_email(db, email=account.email, request=request)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    name = account.name
    email = account.email
    password = account.password
    hashed_password = password + "notreallyhashed"

    # Use Alpaca-py to create broker account
    broker_account = create_broker_account(email=email, first_name=name)
    id = broker_account.id # Is type UUID
    created_at = broker_account.created_at
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    created_at = datetime.strptime(created_at, DATE_FORMAT)

    # After getting ID and authenticating, create model and store it in DB
    db_user = models.Account(
        id=id,
        name=name,
        email=email,
        created_at=created_at,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_account(db: Session, identifier: str, request: Request):
    # Authenticate token before querying DB
    access_token = request.headers.get('access-token')
    utils.authenticate_token(access_token)

    try:
        identifier = UUID(identifier)
        db_user = db.query(models.Account).filter(models.Account.id == identifier).first()
    except:
        db_user = db.query(models.Account).filter(models.Account.email == identifier).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


def get_account_by_email(db: Session, email: str, request: Request):
    # Authenticate token before querying DB
    access_token = request.headers.get('access-token')
    utils.authenticate_token(access_token)

    account = db.query(models.Account).filter(models.Account.email == email).first()
    return account

def get_broker_client():
    BROKER_API_KEY = os.environ.get("APCA_BROKER_API_KEY")
    BROKER_SECRET_KEY = os.environ.get("APCA_BROKER_API_SECRET")

    broker_client = BrokerClient(
                    api_key=BROKER_API_KEY,
                    secret_key=BROKER_SECRET_KEY,
                    sandbox=True,
                    )
    return broker_client

def get_link_token(plaid_client: plaid_api.PlaidApi, request: Request):
    access_token = request.headers.get('access-token')
    utils.authenticate_token(access_token)
    # Create a link_token for the given user
    request = LinkTokenCreateRequest(
            products=[Products("auth")],
            client_name="Plaid Test App",
            country_codes=[CountryCode('US')],
            language='en',
            webhook='https://webhook.example.com',
            user=LinkTokenCreateRequestUser(
                client_user_id=os.environ.get("PLAID_CLIENT_ID")
            )
        )
    response = plaid_client.link_token_create(request)
    # Send the data to the client
    return response.to_dict()

def get_processor_token(plaid_response: schemas.PlaidExchangeInfo, 
                        plaid_client: plaid_api.PlaidApi,
                        request: Request):
    access_token = request.headers.get('access-token')
    utils.authenticate_token(access_token)

    # Exchange the public token from Plaid Link for an access token.
    public_token = plaid_response.public_token
    account_id = plaid_response.account_id
    exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
    exchange_token_response = plaid_client.item_public_token_exchange(exchange_request)
    access_token = exchange_token_response['access_token']

    # Create a processor token for a specific account id.
    create_request = ProcessorTokenCreateRequest(
        access_token=access_token,
        account_id=account_id,
        processor="alpaca"
    )
    create_response = plaid_client.processor_token_create(create_request)
    processor_token = create_response['processor_token']
    print(f"Processor token is: {processor_token}")
    return {"processor_token": processor_token}

def create_ach_relationship(processor_token: schemas.ProcessorToken, identifier: str, db: Session, request: Request):
    # Obtain Alpaca ID from identifier
    account = get_account(db, identifier, request)
    alpaca_id = str(account.id)

    broker_client = get_broker_client()
    ach_data = CreatePlaidRelationshipRequest(processor_token=processor_token.processor_token)
    ach_relationship = broker_client.create_ach_relationship_for_account(
                    account_id=alpaca_id,
                    ach_data=ach_data
                )
    
    return {"ach_relationship": ach_relationship}
    

def create_funds_transfer(request_params: schemas.FundsTransferRequest, identifier: str, db: Session, request: Request):
    account = get_account(db, identifier, request)
    alpaca_id = str(account.id)

    relationship_id = request_params.relationship_id
    transfer_amount = request_params.transfer_amount

    broker_client = get_broker_client()
    transfer_data = CreateACHTransferRequest(
                    amount=transfer_amount,
                    direction=TransferDirection.INCOMING,
                    timing=TransferTiming.IMMEDIATE,
                    relationship_id=relationship_id.relationship_id
                )
    transfer = broker_client.create_transfer_for_account(
                account_id=alpaca_id,
                transfer_data=transfer_data
            )
    return {"transfer_data": transfer}


def create_journal(request_params: schemas.JournalParams, request: Request):
    access_token = request.headers.get('access-token')
    utils.authenticate_token(access_token)
    utils.validate_journal_request(request_params)

    entry_type = constants.journal_entry_types[request_params.entry_type]
    if request_params.entry_type == "JNLC":
        journal_data = CreateJournalRequest(
                        from_account=request_params.from_account,
                        entry_type=entry_type,
                        to_account=request_params.to_account,
                        amount=request_params.amount
                    )
    else: # Is security journal
        journal_data = CreateJournalRequest(
                        from_account=request_params.from_account,
                        entry_type=entry_type,
                        to_account=request_params.to_account,
                        symbol=request_params.symbol,
                        qty=request_params.qty
            )
    return journal_data


def create_batch_journal(request_params: schemas.BatchJournalParams, request: Request):
    access_token = request.headers.get('access-token')
    utils.authenticate_token(access_token)
    utils.validate_journal_request(request_params)

    entry_type = constants.journal_entry_types[request_params.entry_type]
    batch_entries = []
    for entry in request_params.entries:
        batch_journal_request = utils.create_batch_entry(request_params.entry_type, entry)
        batch_entries.append(batch_journal_request)

    batch_journal_data = CreateBatchJournalRequest(
                    entry_type=entry_type,
                    from_account=request_params.from_account, 
                    entries=batch_entries
                )
    broker_client = get_broker_client()
    batch_journal = broker_client.create_batch_journal(batch_data=batch_journal_data)
    return batch_journal


# Creates only market and limit orders for now
def create_order(identifier: str, request_params: schemas.OrderParams, db: Session, request: Request):
    account = get_account(db, identifier, request)
    account_id = str(account.id)
    utils.validate_order_request(request_params)

    if request_params.type == "market":
        if request_params.notional:
            order_request = MarketOrderRequest(
                symbol=request_params.symbol,
                notional=request_params.notional,
                side=constants.order_sides[request_params.side],
                type = constants.order_types[request_params.type],
                time_in_force=constants.time_in_forces[request_params.time_in_force],
                commission=request_params.commission
            )
        else:
            order_request = MarketOrderRequest(
                symbol=request_params.symbol,
                qty=request_params.qty,
                side=constants.order_sides[request_params.side],
                type = constants.order_types[request_params.type],
                time_in_force=constants.time_in_forces[request_params.time_in_force],
                commission=request_params.commission
            )
    elif request_params.type == "limit":
        order_request = LimitOrderRequest(
            symbol=request_params.symbol,
            qty=request_params.qty,
            side=constants.order_sides[request_params.side],
            type = constants.order_types[request_params.type],
            time_in_force=constants.time_in_forces[request_params.time_in_force],
            commission=request_params.commission,
            limit_price=request_params.limit_price
        )
    else:
        raise HTTPException(status_code=400, detail="Only market and limit orders are currently implemented")

    broker_client = get_broker_client()
    order = broker_client.submit_order_for_account(account_id, order_request)
    return {"order": order}


def get_orders(identifier: str, db: Session, request: Request):
    account = get_account(db, identifier, request)
    account_id = str(account.id)

    broker_client = get_broker_client()
    orders = broker_client.get_orders_for_account(account_id)
    return {"orders": orders}


def get_open_positions(identifier: str, db: Session, request: Request):
    account = get_account(db, identifier, request)
    account_id = str(account.id)

    broker_client = get_broker_client()
    positions = broker_client.get_all_positions_for_account(account_id=account_id)

    return {"positions": positions}


def get_all_positions(request: Request):
    access_token = request.headers.get('access-token')
    utils.authenticate_token(access_token)

    broker_client = get_broker_client()
    all_positions = broker_client.foo()  # Bulk fetch is not implemented yet

    return {"positions": all_positions}
