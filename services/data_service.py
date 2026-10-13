# services/data_service.py

import os
from typing import List, Dict, Any


# Carrega o adaptador correto conforme o valor da variável de ambiente (padrão: local)
APP_MODE = os.getenv("APP_MODE", "local")

if APP_MODE == "local":
    from adapters import db_local as data_provider
    # inicializa banco de dados
    from core.database import init_database
    init_database()
else:
    from adapters import api_client as data_provider

# Interface unificada com todos os adapters

# --- Usuários ---

def listar_usuarios_sistema(token: str = "") -> List[Dict[str, Any]]:
    """Retorna todos os usuários cadastrados."""
    return data_provider.listar_usuarios_sistema(token)
