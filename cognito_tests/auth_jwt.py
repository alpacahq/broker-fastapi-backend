import os

import cognitojwt
from dotenv import load_dotenv
load_dotenv()

id_token = 'eyJraWQiOiJcL0Fia01US1h1UitIVmtsb0N2SE1PdVJ0NXJZZStvY1VxRThFNEJMeVNBdz0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI1ZmM5MGYzYy00ZGMwLTQ3MmUtYmNlNy1jYTI2MGMzZGY3MjIiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9aaEhESllMNWMiLCJjbGllbnRfaWQiOiIybmx2NGdvMWpjMWE3ajV1ZXFiNWsxcnYxaSIsIm9yaWdpbl9qdGkiOiI5ZDNkNTgxZi0xYTA1LTRlZTgtYmJiMS1iN2MzZTRkZTQ3ZmQiLCJldmVudF9pZCI6IjJmYjhhYTFjLTU3ZTktNDYzMS1iZDJjLTYzMGNkMTlmNGJiZiIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE2NTgxNDkzNTAsImV4cCI6MTY1ODE1Mjk1MCwiaWF0IjoxNjU4MTQ5MzUwLCJqdGkiOiJkZGY3MzRmNS05M2E5LTQ2NWYtODRlMS04Yzk3YzZjMDYwZDgiLCJ1c2VybmFtZSI6IjVmYzkwZjNjLTRkYzAtNDcyZS1iY2U3LWNhMjYwYzNkZjcyMiJ9.PKH1drhz_AJ_pm3qaz5jBaHWp2oUqKTG3k8l6aeRkmZ_Hl_BUzpcH5kQxqKMXy2z2QknH0-A4OQYxVK7hI_Iul36drOyUxrFjLt4pmwAwgsxpu-eOuGavnacP_WTZU8XSZnwMkXH-iFx-zScpLR4BAdyBBuWFiYNBWXqUHfzZIKr5FGsDxn_BLck_9jfGgnFQGQV0n5D-RDBhC2iizUUOnmZ6rKytlUudRHdomz7SeZ0tux3VakXbYi0dTu6-zBOZW8sNFLDyU0Z7RjKSRCbw9Pt-_ZhBSIGiiqbLnn9t-AoZjlnHvqtIzoOB6QzQljzUYAIl6dB5zxsplmOgCO6aQ'
REGION = os.environ.get('COGNITO_REGION_NAME')
USERPOOL_ID = os.environ.get('USER_POOL_ID')
APP_CLIENT_ID = os.environ.get('COGNITO_USER_CLIENT_ID')


verified_claims: dict = cognitojwt.decode(
    id_token,
    REGION,
    USERPOOL_ID,
    app_client_id=APP_CLIENT_ID  # Optional
    # testmode=False  # Disable token expiration check for testing purposes
)

"""
Accessible properties are:
- sub
- iss
- client_id
- origin_jti
- event_id
- token_use
- scope
- auth_time
- exp
- iat
- jti
- username
"""

print(verified_claims)