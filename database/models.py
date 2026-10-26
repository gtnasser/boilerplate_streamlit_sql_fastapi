# database/models.py

from datetime import datetime
from sqlalchemy import String, Text, Column, Integer, DateTime, Boolean, JSON, func, text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from core.database import Base

# ---------- Mixins ----------

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

ver = """
class SoftDeleteMixin:
    " ""Exclusão lógica: registros nunca são apagados fisicamente."" "
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, default=None, index=True
    )
"""

# lista fixa de roles
_ROLES_VALIDAS = ["login", "admin", "dev"]

class UsuarioModel(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name:Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    roles: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("1"), nullable=False)


