import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def test_database_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("Database connection successful")
    except Exception as e:
        print(f"Database connection failed due to: {e}")

if __name__ == "__main__":
    test_database_connection()


    