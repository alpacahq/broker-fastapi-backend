import os
import boto3
from dotenv import load_dotenv
load_dotenv()

access_token = 'eyJraWQiOiJcL0Fia01US1h1UitIVmtsb0N2SE1PdVJ0NXJZZStvY1VxRThFNEJMeVNBdz0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI2MjNiMjRiMC1iOTk0LTRlZDctYjA0ZS02ZTgzNjU3NmY0NzYiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9aaEhESllMNWMiLCJjbGllbnRfaWQiOiIybmx2NGdvMWpjMWE3ajV1ZXFiNWsxcnYxaSIsIm9yaWdpbl9qdGkiOiJjOGQ3NDQ5NC1mNzcxLTQxZDEtYjFiNS0zMmNlMTE3MzIzNzciLCJldmVudF9pZCI6ImQ1NDBlZmM1LTU3NGItNGU5MC04Y2ExLWVlNDUzNzY0ZjA4OCIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE2NTc3MzQwNzAsImV4cCI6MTY1NzczNzY3MCwiaWF0IjoxNjU3NzM0MDcwLCJqdGkiOiJmNDA5OTg1Ny03M2Q5LTRlY2EtYmJhMS0yM2NhMTNhNGIyNmMiLCJ1c2VybmFtZSI6IjYyM2IyNGIwLWI5OTQtNGVkNy1iMDRlLTZlODM2NTc2ZjQ3NiJ9.OuDmpiJuhY-0jvVzxfun1hSFYhSKWtYG37lEjaZqHbya-FuoHXYehfg3cge8Iac9jxLnc5yZTjsFRJbJG5elx65abX45R9TmIL3wUXOyYrRq7TpK5ivVk85l4sRPED_8sKHMekurMFSc7UQcvXsW2-Kn7XLJa9aGOk6nNSACDGLfsjOgPzKzoIay8QTBYshu3Zsks2jdMR2-NjIPZX8N5JC_ji96nfbp1KHq99qoKyYAz8MC_Z0Dk5yHXoDX6Lp_5PUsTYTx2a5HoNSVp0VKpt8-mu-Vq0gKHtE4CB7bI-XKUjG2QA-ebbIuLAaQlHIVg_ztc9FZvh9Fg6xKrLNgUQ'

client = boto3.client('cognito-idp', region_name=os.getenv('COGNITO_REGION_NAME'))
response = client.get_user(
    AccessToken=access_token
)

print(response)

# user_attributes = response['UserAttributes']
# user_sub = None
# for attribute in user_attributes:
#     if attribute['Name'] == 'sub':
#         user_sub = attribute['Value']
#         break

# if user_sub:
#     print(f'User is: {user_sub}')
# else:
#     print('User not found')