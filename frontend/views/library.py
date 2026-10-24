# views/library.py
import streamlit as st
import utils.auth_utils as auth
import pandas as pd

@auth.role_required(allowed_roles="dev", login_page="views/login.py")
def render():
    st.markdown("#### 📚 Bibliotecas e funções publicadas")

    st.write("`utils/auth_utils.py`")
    data = [
        ["set_user_session(token: str, user_data: Dict[str, Any]) -> None" , "Seta os dados do usuario e o token na sessao apos um login bem-sucedido."],
        ["clear_user_session() -> None", "Limpa todas as credenciais e dados da sessao (Logout)."],
        ["is_authenticated() -> bool", "Retorna True se houver um usuario autenticado com token valido na sessao."],
        ["get_current_token() -> str", "Retorna o token JWT atual armazenado na sessao."],
        ["get_current_user_data() -> Dict[str, Any]" , "Retorna o dicionario com os dados do usuario logado."],
        ["get_current_user_roles() -> List[str]", "Retorna a lista de permissoes (roles) atribuidas ao usuario logado."],
        ["check_user_has_role(required_roles: Union[str, List[str]]) -> bool", "Verifica se o usuario logado possui pelo menos uma das roles especificadas."],
        ["@role_required(allowed_roles: list[str], login_page: str)", "Decorador para proteger páginas do Streamlit; valida autenticação e roles."],
    ]
    df = pd.DataFrame(data, columns=["Função", "Descrição"])
    st.dataframe(df, hide_index=True,  width='stretch')

    st.write("`services/data_service.py`")
    data = [
        ["criar_usuario_sistema(username: str, password: str, name: str, roles: List[str] = [], token: str = '') -> bool",
        "Interface unificada para a criação de um novo usuário no sistema."],
        ["autenticar_usuario_sistema(username: str, password: str) -> Dict[str, Any]",
        "Interface unificada para autenticação de usuários."],
        ["listar_usuarios_sistema(token: str = '') -> List[Dict[str, Any]]",
        "Retorna todos os usuários cadastrados."]
    ]
    df = pd.DataFrame(data, columns=["Função", "Descrição"])
    st.dataframe(df, hide_index=True,  width='stretch')

if __name__ == "__main__":
    render()