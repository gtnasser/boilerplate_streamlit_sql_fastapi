# database/repository.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.models import UsuarioModel, _ROLES_VALIDAS
from typing import List, Optional


# --- Usuários ---

def _obter_roles_invalidas(roles: List[str]) -> List[str]:
    """Retorna uma lista com todas as roles que são inválidas."""
    return [r for r in roles if r not in _ROLES_VALIDAS]

def criar_usuario(db: Session, username: str, password_hash: str, name: str, roles: List[str] = ["login"]) -> bool:
    """Insere um novo utilizador na base de dados após validar as roles."""

    roles_invalidas = _obter_roles_invalidas(roles)
    if roles_invalidas:
        print(f"❌ Erro: Roles inválidas: {roles}")
        return False
        
    novo_usuario = UsuarioModel(
        username=username,
        name=name,
        hashed_password=password_hash,
        roles=roles,
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
