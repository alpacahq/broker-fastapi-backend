import os
from dotenv import load_dotenv
load_dotenv()

from alpaca.broker.client import BrokerClient
from alpaca.broker.models import (
                        Contact,
                        Identity,
                        Disclosures,
                        Agreement
                    )
from alpaca.broker.models.requests import AccountCreationRequest
from alpaca.broker.enums import TaxIdType, FundingSource, AgreementType

BROKER_API_KEY = os.environ.get("APCA_BROKER_API_KEY")
BROKER_SECRET_KEY = os.environ.get("APCA_BROKER_API_SECRET")

broker_client = BrokerClient(
                api_key=BROKER_API_KEY,
                secret_key=BROKER_SECRET_KEY,
                sandbox=True,
                )

# Contact
contact_data = Contact(
            email_address="cool_alpaca5@example.com",
            phone_number="555-666-7788",
            street_address=["20 N San Mateo Dr"],
            city="San Mateo",
            state="CA",
            postal_code="94401",
            country="USA"
            )
# Identity
identity_data = Identity(
        given_name="John2",
        middle_name="Smith",
        family_name="Doe",
        date_of_birth="1990-01-01",
        tax_id="666-55-4321",
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
user_id = account.id
created_at = account.created_at

print(type(user_id), user_id)
print(type(created_at), created_at)