# database/models.py

from datetime import datetime
from sqlalchemy import String, Text, Column, Integer, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from core.database import Base

#class User(Base):
#    __tablename__ = "users"
#    id: Mapped[int] = mapped_column(primary_key=True)
#    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
#    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

# lista fixa de roles
_ROLES_VALIDAS = ["login", "admin", "dev"]

class UsuarioModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    roles = Column(JSON, default=[], nullable=False)
    is_active = Column(Boolean, default=True)


