# adapters/db_local.py

from typing import List, Dict, Any
from core.database import get_database_session
from database.repository import listar_usuarios

# --- Usuários ---

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