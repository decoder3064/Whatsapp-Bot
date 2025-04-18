import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()
acc_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_number = os.getenv('TWILIO_WHATSAPP_NUMBER')


client = Client(acc_sid, auth_token)

def send_sms(to, message):
    try:
        message = client.messages.create(
            body=message,
            from_=twilio_number,
            to=to
        )
        return message.sid
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None