# frontend/views/lista_usuarios.py

import streamlit as st
import utils.auth_utils as auth
from services.data_service import listar_usuarios_sistema


def render_lista_usuarios_page() -> None:
    """Renderiza a pagina Listagem de usuários."""

    st.subheader("👤 Listagem de Usuários Cadastrados")

    # Obtém o token JWT atual armazenado na sessão para autenticação nas requisições
    token = auth.get_current_token()

    try:
        # Chama a interface unificada do data_service
        usuarios = listar_usuarios_sistema(token=token)

        if not usuarios:
            st.info("Nenhum usuario encontrado no sistema.")
            return

        # Exibe os dados em uma tabela estruturada do Streamlit
        st.dataframe(
            usuarios,
            width="stretch",
            column_config={
                "id": "ID",
                "username": "Nome de Usuário",
                "name": "Nome Completo",
                "roles": "Perfil (Roles)",
                "is_active": "Ativo"
            }
        )
    except Exception as erro:
        st.error(f"Erro ao carregar a listagem de usuários: {erro}")

render_lista_usuarios_page()