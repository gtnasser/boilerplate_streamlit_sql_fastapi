# database/models.py

from sqlalchemy import String, Text, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime
from core.database import Base

#class User(Base):
#    __tablename__ = "users"
#    id: Mapped[int] = mapped_column(primary_key=True)
#    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
#    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

class UsuarioModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="agent") # Ex: "admin", "agent", "client"
    is_active = Column(Boolean, default=True)


