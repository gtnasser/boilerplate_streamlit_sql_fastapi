# frontend/views/login.py

import streamlit as st
import utils.auth_utils as auth
from services.data_service import autenticar_usuario_sistema


def render_login_page() -> None:
    """Renderiza a página de autenticação do usuário."""

    cols = st.columns([1, 1, 1])            
    with cols[1]:
        with st.form("login", clear_on_submit=False):
            st.subheader("🔑 MyProject Login")
            st.caption(":blue-background[Entre com seu usuário e senha]")
            username = st.text_input('Usuário', placeholder='Digite o seu usuário')
            password = st.text_input('Senha', type="password", placeholder='Digite a sua senha')

            submit = st.form_submit_button("Entrar", width="stretch")
            if submit:
                if not username or not password:
                    st.warning("É necessário preencher todos os campos.")
                else:
                    with st.spinner("Autenticando..."):
                        resultado = autenticar_usuario_sistema(username, password)
                        
                        if resultado.get("authenticated"):
                            user_info = resultado.get("user", {})
                            token = resultado.get("token", "")
                            
                            # Salva a sessão com os dados reais do usuário
                            auth.set_user_session(token, {
                                "name": user_info.get("name"),
                                "username": user_info.get("username"),
                                "roles": [user_info.get("role", "agent")]
                            })

                            st.success("Login realizado com sucesso!")
                            st.rerun()
                        else:
                            st.error("Credenciais inválidas ou usuário inativo.")

            # provisorio
            submit2 = st.form_submit_button("Desenvolvimento", width="stretch")
            if submit2:
                auth.set_user_session("hasdgfhdasgflhagd", {"name": "desenvolvedor", "roles": ["developer", "admin"]})
                st.rerun()

render_login_page()

