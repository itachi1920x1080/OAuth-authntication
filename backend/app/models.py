from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255), nullable=True)
    auth_provider = Column(String(50), default="local")
    name = Column(String(255), nullable=True)
    avatar = Column(String(1024), nullable=True)
    oauth_id = Column(String(255), unique=True, index=True, nullable=True)
