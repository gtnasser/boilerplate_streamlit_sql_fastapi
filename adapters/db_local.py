# adapters/db_local.py

from typing import List, Dict, Any
from core.database import get_database_session, _hash_password, verify_password
from database.repository import criar_usuario, listar_usuarios, buscar_usuario_por_username


# --- Usuários ---

def criar_usuario_sistema(username: str, password: str, name: str, role: str = "agent", token: str = "") -> bool:
    """Cria um novo utilizador gerando o hash localmente e persistindo via repositório."""
    salt_hex, hash_hex = _hash_password(password)
    stored_password = f"{salt_hex}${hash_hex}"
    
    db = next(get_database_session())
    try:
        return criar_usuario(
            db=db,
            username=username,
            password_hash=stored_password,
            name=name,
            role=role
        )
    finally:
        db.close()


def autenticar_usuario_sistema(username: str, password: str) -> Dict[str, Any]:
    """Valida as credenciais do usuário diretamente no banco SQLite local."""
    db = next(get_database_session())
    try:
        user = buscar_usuario_por_username(db, username)
        if user and user.is_active and verify_password(user.hashed_password, password):
            # Retorna os dados do usuário logado (simulando um payload de autenticação)
            return {
                "authenticated": True,
                "user": {
                    "username": user.username,
                    "name": user.name,
                    "role": user.role
                },
                "token": f"local-token-{user.username}" # Token simulado para o modo local
            }
        return {"authenticated": False}
    finally:
        db.close()

def listar_usuarios_sistema(token: str = "") -> List[Dict[str, Any]]:
    """Retorna todos os usuários cadastrados."""
    db = next(get_database_session())
    try:
        usuarios = listar_usuarios(db)
        # Converte os modelos SQLAlchemy em dicionarios para padronizar com a API
        return [
            {
                "id": u.id,
                "username": u.username,
                "name": u.name,
                "role": u.role,
                "is_active": u.is_active
            }
            for u in usuarios
        ]
    finally:
        db.close()