# frontend/views/home.py
import streamlit as st
import utils.auth_utils as auth

def render_login_page() -> None:
    """Renderiza a pagina de autenticação do usuário."""

    cols = st.columns([1,1,1])            
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
#                else:
                    with st.spinner("Autenticando..."):
                        if 1==1:
#                        if api_client.login(email, senha):

                            # provisorio
                            auth.set_user_session("hasdgfhdasgflhagd", {"name": "absurdo", "roles": ["developer", "admin"]})

                            st.success("Login realizado com sucesso!")
                            st.rerun()
                        else:
                            st.error("Credenciais inválidas ou erro no servidor.")

            return False

render_login_page()

