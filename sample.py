import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Initiate the call via VideoSDK SIP Gateway

response = requests.post(
    "https://api.videosdk.live/v2/sip/call",
    headers={
        "Authorization": os.getenv("VIDEOSDK_AUTH_TOKEN"),
        "Content-Type": "application/json"
    },
    json={
        "gatewayId": os.getenv("VIDEOSDK_GATEWAY_ID"),
        "sipCallTo": os.getenv("PHONE_NUMBER_TO_CALL"),
    }
)
print("Status:", response.status_code)
print("Response:", response.text)
