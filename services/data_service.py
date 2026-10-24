# services/data_service.py

import os
from typing import List, Dict, Any


# Carrega o adaptador correto conforme o valor da variável de ambiente (padrão: local)
APP_MODE = os.getenv("APP_MODE", "local")
print("APP_MODE:", APP_MODE)

if APP_MODE == "local":
    from adapters import db_local as data_provider
    # inicializa banco de dados
    from core.database import init_database
    init_database()
else:
    from adapters import api_client as data_provider

# Interface unificada com todos os adapters

# --- Usuários ---

def criar_usuario_sistema(username: str, password: str, name: str, roles: List[str] = [], token: str = "") -> bool:
    """Interface unificada para a criação de um novo usuário no sistema."""
    return data_provider.criar_usuario_sistema(username, password, name, roles, token)

def autenticar_usuario_sistema(username: str, password: str) -> Dict[str, Any]:
    """Interface unificada para autenticação de usuários."""
    return data_provider.autenticar_usuario_sistema(username, password)

def listar_usuarios_sistema(token: str = "") -> List[Dict[str, Any]]:
    """Retorna todos os usuários cadastrados."""
    return data_provider.listar_usuarios_sistema(token)
