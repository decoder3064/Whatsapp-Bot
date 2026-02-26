from dotenv import load_dotenv
import os

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')

# Redis (for Celery)
REDIS_URL = os.getenv('REDIS_URL')

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')

# JWT
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'change-this-in-production')

# OpenAI (for AI chatbot)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
