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
    # Auth
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(auth_url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    token = r.json().get('access_token')
    
    # ... (The rest of your STK push logic stays exactly the same)
    if not token:
        return {"ResponseCode": "1", "errorMessage": "Auth failed."}