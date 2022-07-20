import os
from dotenv import load_dotenv
load_dotenv()

from alpaca.broker import BrokerClient
from alpaca.broker.models import ListAccountsRequest
from alpaca.broker.enums import AccountEntities

from datetime import datetime

BROKER_API_KEY = os.environ.get("APCA_BROKER_API_KEY")
BROKER_SECRET_KEY = os.environ.get("APCA_BROKER_API_SECRET")

client = BrokerClient(
                api_key=BROKER_API_KEY,
                secret_key=BROKER_SECRET_KEY,
                sandbox=True,
                )

filter_date = "2022-01-30T00:00:00.000Z"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
filter_datetime = datetime.strptime(filter_date, DATE_FORMAT)

print(filter_datetime)

filter = ListAccountsRequest(
                    created_after=filter_datetime, 
                    entities=[AccountEntities.CONTACT, AccountEntities.IDENTITY]
                    )

accounts = client.list_accounts(search_parameters=filter)
print(accounts)