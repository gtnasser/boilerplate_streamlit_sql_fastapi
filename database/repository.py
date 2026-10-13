# database/repository.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.models import UsuarioModel
from typing import List, Optional


# --- Usuários ---

def criar_usuario(db: Session, username: str, password_hash: str, name: str, role: str = "agent") -> bool:
    """Insere um novo utilizador na base de dados."""
    novo_usuario = UsuarioModel(
        username=username,
        name=name,
        hashed_password=password_hash,
        role=role,
        is_active=True
    )
    try:
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        return True
    except IntegrityError:
        db.rollback()
        return False

def buscar_usuario_por_username(db: Session, username: str) -> Optional[UsuarioModel]:
    """Busca um utilizador cadastrado pelo seu nome de utilizador."""
    return db.query(UsuarioModel).filter(UsuarioModel.username == username).first()

def listar_usuarios(db: Session) -> List[UsuarioModel]:
    """Retorna todos os utilizadores cadastrados no banco local."""
    return db.query(UsuarioModel).order_by(UsuarioModel.username.asc()).all()
