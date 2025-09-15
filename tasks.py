from utils.twilio_client import send_sms
from celery import Celery
import os
from dotenv import load_dotenv


load_dotenv()

celery = Celery('tasks', broker=os.getenv('REDIS_URL'), backend=os.getenv('REDIS_URL'))


@celery.task
def send_reminder(to , message):
    """
    Send a reminder message using Twilio.
    """
    return send_sms(to, message)

