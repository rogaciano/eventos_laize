import requests
import json

# API credentials
API_URL = "https://webpicne.digisac.co/api/v1/messages"  # Notice the endpoint is "messages" now
USER_ID = "60bcdfb2-52c0-46cf-b55f-8c2520cddb43"
TOKEN = "2930f5542e1e25861e9362672f9aa9528a4a3cea"

# Recipient phone number
phone_number = "5581999216560"

# Message content
message = "Olá, esta é uma mensagem de teste!"

# Headers
headers = {
    "Content-Type": "application/json",
    "user_id": USER_ID,
    "token": TOKEN
}

# Payload - adjust based on the API documentation
payload = {
    "number": phone_number,
    "text": message
}

# Send the request
try:
    response = requests.post(API_URL, headers=headers, json=payload)
    
    # Check if request was successful
    if response.status_code == 200:
        print("Message sent successfully!")
        print(response.json())
    else:
        print(f"Failed to send message. Status code: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"An error occurred: {str(e)}")
    