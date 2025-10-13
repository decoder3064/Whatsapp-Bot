from dotenv import load_dotenv
import os


# Put own configuration in .env file

load_dotenv()  # Load variables from .env file into environment

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')

# Redis (for Celery)
REDIS_URL = os.getenv('REDIS_URL')

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')

