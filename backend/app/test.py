import mysql.connector
from dotenv import load_dotenv
import os 


load_dotenv()

con = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port = os.getenv("DB_PORT"),
    user = os.getenv("DB_USERNAME"),
    password = os.getenv("DB_PASSWORD"),
    database = os.getenv("DB_DATABASE"),
)
if con.is_connected():
    print("connected to database")
else:
    print("not connected to database")
