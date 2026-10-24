# adapters/api_client.py

from typing import List, Dict, Any
import httpx

API_BASE_URL = "http://localhost:8000"


# --- Usuários ---

def criar_usuario_sistema(username: str, password: str, name: str, roles: str = ["login"], token: str = "") -> bool:
    """Consome a API FastAPI para criar um novo usuário."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "username": username,
        "password": password,
        "name": name,
        "roles": roles
    }
    try:
        response = httpx.post(f"{API_BASE_URL}/usuarios", json=payload, headers=headers, timeout=10.0)
        return response.status_code in (200, 201)
    except Exception:
        return False
    
def autenticar_usuario_sistema(username: str, password: str) -> Dict[str, Any]:
    """Envia as credenciais para autenticação na API FastAPI."""
    try:
        response = httpx.post(
            f"{API_BASE_URL}/auth/login", 
            json={"username": username, "password": password}, 
            timeout=10.0
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {"authenticated": False}

def listar_usuarios_sistema(token: str = "") -> List[Dict[str, Any]]:
    """Consome a listagem de usuarios atraves da API FastAPI."""
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(f"{API_BASE_URL}/usuarios", headers=headers, timeout=10.0)
    return response.json() if response.status_code == 200 else []

