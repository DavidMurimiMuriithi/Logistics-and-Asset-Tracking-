# modules/mpesa.py

import requests
import base64
from datetime import datetime

# Configuration / Credentials - Replace with your actual values
CONSUMER_KEY = "wUPlANtGBDqUPfJGQgILaGpIkpVGS0Lb1rm4BAxFJ5DdmLKs"
CONSUMER_SECRET = "T8jWHm8rwHrlsBJmik3BtRC5M1tVSeaaggiRJfi6TjloEDm8VodttC5i5Fe5IXyl"
BUSINESS_SHORT_CODE = "174379"  # e.g., "174379"
LIPA_NA_MPESA_ONLINE_PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"       # e.g., "YourPassKeyHere"

# API Endpoints (using sandbox URLs; change for production)
TOKEN_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
STK_PUSH_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

def get_mpesa_access_token():
    """
    Generates and returns an access token using Daraja credentials.
    """
    credentials = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    headers = {"Authorization": f"Basic {encoded_credentials}"}
    response = requests.get(TOKEN_URL, headers=headers)
    token_data = response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise Exception("Failed to obtain MPESA access token.")
    return access_token

def lipa_na_mpesa_stk_push(phone_number, amount, account_reference, transaction_desc):
    """
    Initiates an MPESA STK Push request.
    
    :param phone_number: Customer's phone number (international format, e.g., 2547XXXXXXXX)
    :param amount: Payment amount (as integer/float)
    :param account_reference: A reference for the transaction (e.g., invoice number)
    :param transaction_desc: Description for the transaction
    :return: The JSON response from the MPESA API.
    """
    # Generate timestamp in format YYYYMMDDHHMMSS
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Generate password: Base64(BusinessShortCode + Passkey + Timestamp)
    data_to_encode = f"{BUSINESS_SHORT_CODE}{LIPA_NA_MPESA_ONLINE_PASSKEY}{timestamp}"
    password = base64.b64encode(data_to_encode.encode("utf-8")).decode("utf-8")
    
    access_token = get_mpesa_access_token()
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "BusinessShortCode": BUSINESS_SHORT_CODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,              # Customer's phone number
        "PartyB": BUSINESS_SHORT_CODE,         # Typically your business shortcode
        "PhoneNumber": phone_number,
        "CallBackURL": "https://yourdomain.com/mpesa_callback",  # Update with your actual callback URL
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }
    
    response = requests.post(STK_PUSH_URL, headers=headers, json=payload)
    return response.json()
