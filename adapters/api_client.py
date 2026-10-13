# adapters/api_client.py

from typing import List, Dict, Any
import httpx

API_BASE_URL = "http://localhost:8000"


# --- Usuários ---

def listar_usuarios_sistema(token: str = "") -> List[Dict[str, Any]]:
    """Consome a listagem de usuarios atraves da API FastAPI."""
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(f"{API_BASE_URL}/usuarios", headers=headers, timeout=10.0)
    return response.json() if response.status_code == 200 else []

