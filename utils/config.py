from dotenv import load_dotenv
import os


load_dotenv()

class Config:
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")


    DB_PARAMS = {
        "host": POSTGRES_HOST,
        "user": POSTGRES_USER,
        "password": POSTGRES_PASSWORD,
        "port": POSTGRES_PORT
    }
