# frontend/views/lista_usuarios.py

import streamlit as st
import utils.auth_utils as auth
from services.data_service import listar_usuarios_sistema

user_data = auth.get_current_user_data()

import streamlit as st
import utils.auth_utils as auth

@auth.role_required(allowed_roles="admin", login_page="views/login.py")
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

    if not auth.check_user_has_role(["dev"]):
        st.error("⚠️ Acesso negado: você tem que ser **dev** para visualizar essas informações.")
        st.stop() 

if __name__ == "__main__":
    render_lista_usuarios_page()