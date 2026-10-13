# frontend/app.py

import sys
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path do Python para evitar erros na carga dos módulos.
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
    
import streamlit as st
import utils.auth_utils as auth

# Configuracao da pagina (sempre o primeiro comando Streamlit)
st.set_page_config(
    page_title="MyProject",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)


def setup_navigation() -> any:
    """Configura o sistema de navegação."""

    # Chama a tela de login se sessao nao estiver autenticada
    if not auth.is_authenticated():
        return st.navigation([
            st.Page("views/login.py", title="Login", icon="🔑")
        ])

    
    # Monta o menu baseado nas permissoes do usuario
    pages = [
            st.Page("views/home.py", title="Home", icon="🏠"),
            st.Page("views/lista_usuarios.py", title="Listagem de Usuários", icon="👤"),
        ]
    return st.navigation(pages)


def render_sidebar():
    """Customiza o sidebar com informacoes do usuario, status e botao de logout."""
    if auth.is_authenticated():
        with st.sidebar:
            st.title("🎫 MyProject")
            user_data = auth.get_current_user_data()
            user_name = user_data.get("name", "Unknown")
            st.markdown(f"👤 {user_name}")

            if st.button("🚪 Sair / Logout", width='stretch', type="secondary"):
                auth.clear_user_session()
                st.rerun()

            st.info("Sessão ativa (JWT - Expira em 4h)")

            if user_data:
                st.json(user_data)

def main():
    """Inicia a aplicacao Streamlit."""
    nav = setup_navigation()
    render_sidebar()
    nav.run()


if __name__ == "__main__":
    main()