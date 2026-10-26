# frontend/views/admin.py
import streamlit as st
import utils.auth_utils as auth

@auth.role_required(allowed_roles="dev", login_page="views/login.py")
def render_home_page() -> None:

    st.subheader("`DEV` role page!")

render_home_page()
