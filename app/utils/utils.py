import os
import boto3
import cognitojwt
from dotenv import load_dotenv
load_dotenv()

from faker import Faker

from fastapi import HTTPException

from alpaca.broker.client import BrokerClient
from alpaca.broker.models import (
                        Contact,
                        Identity,
                        Disclosures,
                        Agreement
                    )
from alpaca.broker.models.requests import AccountCreationRequest
from alpaca.broker.enums import TaxIdType, FundingSource, AgreementType


# User ID from Cognito is currently not utilized
class CognitoResponse(object):
    def __init__(self, access_token, refresh_token, user_id=None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.user_id = user_id


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

    signup_result = CognitoResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user_sub
    )
    return signup_result

def cognito_login(username: str, password: str):
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
    login_result = CognitoResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )
    return login_result

def create_broker_account(email: str, first_name: str):
    fake = Faker()

    BROKER_API_KEY = os.environ.get("APCA_BROKER_API_KEY")
    BROKER_SECRET_KEY = os.environ.get("APCA_BROKER_API_SECRET")

    broker_client = BrokerClient(
                    api_key=BROKER_API_KEY,
                    secret_key=BROKER_SECRET_KEY,
                    sandbox=True,
                    )

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
    account_data = AccountCreationRequest(
                            contact=contact_data,
                            identity=identity_data,
                            disclosures=disclosure_data,
                            agreements=agreement_data
                            )

    # Make a request to create a new brokerage account
    account = broker_client.create_account(account_data)
    return account

def get_broker_account(id: str):
    BROKER_API_KEY = os.environ.get("APCA_BROKER_API_KEY")
    BROKER_SECRET_KEY = os.environ.get("APCA_BROKER_API_SECRET")

    broker_client = BrokerClient(
                    api_key=BROKER_API_KEY,
                    secret_key=BROKER_SECRET_KEY,
                    sandbox=True,
                    )

    account = broker_client.get_account_by_id(account_id=id)
    return account
    
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
