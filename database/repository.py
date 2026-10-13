# database/repository.py
from sqlalchemy.orm import Session
from database.models import UsuarioModel
from typing import List, Optional


# --- Usuários ---

def buscar_usuario_por_username(db: Session, username: str) -> Optional[UsuarioModel]:
    """Busca um usuário cadastrado pelo seu nome de usuário."""
    return db.query(UsuarioModel).filter(UsuarioModel.username == username).first()

def listar_usuarios(db: Session) -> List[UsuarioModel]:
    """Retorna todos os usuarios cadastrados no banco local."""
    return db.query(UsuarioModel).order_by(UsuarioModel.username.asc()).all()

def buscar_usuario_por_username(db: Session, username: str) -> Optional[UsuarioModel]:
    """Busca um usuario cadastrado pelo seu nome de usuario."""
    return db.query(UsuarioModel).filter(UsuarioModel.username == username).first()
