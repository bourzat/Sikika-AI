import requests
import base64
import os
from datetime import datetime
from dotenv import load_dotenv

# Load the hidden variables from the .env file
load_dotenv()

# Pull the keys securely
CONSUMER_KEY = os.getenv("DARAJA_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("DARAJA_CONSUMER_SECRET")

# Sandbox Defaults (Safe to leave in the code)
SHORTCODE = "174379"
PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"

def trigger_stk(phone_number, amount):
    # 1. Auth
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(auth_url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    token = r.json().get('access_token')
    
    if not token:
        return {"ResponseCode": "1", "errorMessage": "Auth failed. Check API keys in .env"}

    # 2. Formatting phone to 254XXXXXXXXX
    if phone_number.startswith("07") or phone_number.startswith("01"):
        phone_number = "254" + phone_number[1:]
    elif phone_number.startswith("+254"):
        phone_number = phone_number[1:]

    # 3. STK Payload Generation
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((SHORTCODE + PASSKEY + timestamp).encode()).decode('utf-8')
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://mydomain.com/path", 
        "AccountReference": "Sikika AI",
        "TransactionDesc": "API Access"
    }

    push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    # 4. Send the Request and RETURN the actual JSON
    try:
        response = requests.post(push_url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"ResponseCode": "1", "errorMessage": str(e)}