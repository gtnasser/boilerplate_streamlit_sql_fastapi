# frontend/utils/auth_utils.py
import streamlit as st
from typing import List, Dict, Any, Union

def _ensure_session_initialized() -> None:
    """Garante internamente que as chaves de sessao existem antes de qualquer operacao."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "token" not in st.session_state:
        st.session_state["token"] = ""
    if "user_data" not in st.session_state:
        st.session_state["user_data"] = {}


def set_user_session(token: str, user_data: Dict[str, Any]) -> None:
    """Seta os dados do usuario e o token na sessao apos um login bem-sucedido."""
    _ensure_session_initialized()
    st.session_state["authenticated"] = True
    st.session_state["token"] = token
    st.session_state["user_data"] = user_data


def clear_user_session() -> None:
    """Limpa todas as credenciais e dados da sessao (Logout)."""
    _ensure_session_initialized()
    st.session_state["authenticated"] = False
    st.session_state["token"] = ""
    st.session_state["user_data"] = {}


def is_authenticated() -> bool:
    """Retorna True se houver um usuario autenticado com token valido na sessao."""
    _ensure_session_initialized()
    return bool(st.session_state.get("authenticated", False) and st.session_state.get("token"))


def get_current_token() -> str:
    """Retorna o token JWT atual armazenado na sessao."""
    _ensure_session_initialized()
    return st.session_state.get("token", "")


def get_current_user_data() -> Dict[str, Any]:
    """Retorna o dicionario com os dados do usuario logado."""
    _ensure_session_initialized()
    return st.session_state.get("user_data", {})


def get_current_user_roles() -> List[str]:
    """Retorna a lista de permissoes (roles) atribuidas ao usuario logado."""
    _ensure_session_initialized()
    user_data = get_current_user_data()
    return user_data.get("roles", [])


def check_user_has_role(required_roles: Union[str, List[str]]) -> bool:
    """
    Verifica se o usuario logado possui pelo menos uma das roles especificadas.
    Pode receber uma string única (ex: 'admin') ou uma lista (ex: ['admin', 'director']).
    """
    _ensure_session_initialized()
    if not is_authenticated():
        return False
    user_roles = get_current_user_roles()
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    return any(roles in user_roles for roles in required_roles)