# frontend/views/home.py
import streamlit as st
import utils.auth_utils as auth

@auth.role_required(allowed_roles="login", login_page="views/login.py")
def render_home_page() -> None:
    """Renderiza a pagina inicial protegida."""
    user_data = auth.get_current_user_data()
    user_name = user_data.get("name", "Unknown")

    st.subheader(f"Bem-vindo, {user_name}!")

    st.write("Esta á a página inicial do MyProject.")
    st.info("Utilize o menu lateral para navegar entre as opções do sistema disponíveis para você.")

render_home_page()
