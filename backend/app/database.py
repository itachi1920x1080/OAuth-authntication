from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONNECTION = os.getenv("DB_CONNECTION")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if DB_CONNECTION == "mysql":
    SQLALCHEMY_DATABASE_URL = (
        f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@"
        f"{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    )
    echo = False
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
    echo = False


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, echo=echo
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
