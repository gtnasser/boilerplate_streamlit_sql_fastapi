# frontend/utils/auth_utils.py
import streamlit as st
from typing import List, Dict, Any, Union
from functools import wraps
import time

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
    print(f"🔑 set_user_session(): {user_data.get('username')}", user_data)


def clear_user_session() -> None:
    """Limpa todas as credenciais e dados da sessao (Logout)."""
    _ensure_session_initialized()
    print(f"🔑 clear_user_session(): {st.session_state["user_data"].get('username')}")
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


def role_required(allowed_roles: list[str], login_page: str):
    """
    Decorador para proteger páginas do Streamlit, executa a pagina se usuário tiver a role necessária;
    Mavega para login se não autenticado; Mostra mensagem regressiva se não tiver acesso; 
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            if not is_authenticated():
                # TODO: criar um componente (largura, cores, tempo, mensagens, callback), #ID/key para unicidade
                # custom progress bar downtime
                st.markdown(
                    """
                    <style>
                        /* container da barra de progresso*/
                        .stProgress { 
                            --width: 500px; 
                            background-color: rgba(255, 43, 43, 0.1);
                            padding: 10px;
                            margin: 0px;
                            border-radius: 0.5rem;
                        }
                        /* barra de progresso */
                        [data-testid="stProgressBarTrack"] > div {
                            background-color: red;
                        }
                        .react-aria-ProgressBar {
                        }
                        /* mensagem da barra de progresso */
                        .stProgress [data-testid="stMarkdownContainer"] {
                            font-weight: 400;
                            font-size: 16px;
                            margin: 0px;
                            border-radius: 0.5rem;
                            padding: 0.5rem;
                            line-height: 1.5;
                            --background-color: rgba(255, 43, 43, 0.1);
                            color: rgb(189, 64, 67);
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                timer = 5
                msg = st.empty()
                bar = st.progress(100, text=f"⚠️ Sessão expirada ou não autenticada. Voce será redirecionado em {timer} seg.")
                for last in range(timer, 0, -1):
                    bar.progress(int(last/timer*100), text=f"⚠️ Sessão expirada ou não autenticada. Voce será redirecionado em {last} seg.")
                    time.sleep(1)
                bar.empty()
                if login_page:
                    st.switch_page(st.Page(login_page))
                else:
                    st.error("⛔ Acesso negado: Sessão expirada ou não autenticada.")
                    st.stop() 

            if not check_user_has_role(allowed_roles):
                st.error("⛔ Acesso negado: você não possui permissão para visualizar esta página.")
                st.stop() 

            # Se autorizado, executa o conteúdo da página
            return func(*args, **kwargs)
        return wrapper
    return decorator
