### 📂 Estrutura de Diretórios (base: C:\Users\gtnas\Downloads\boilerplate_streamlit_sql_fastapi)

```text
boilerplate_streamlit_sql_fastapi/
├── LICENSE
├── adapters
│   ├── api_client.py
│   └── db_local.py
├── core
│   ├── config.py
│   └── database.py
├── database
│   ├── models.py
│   └── repository.py
├── frontend
│   ├── app.py
│   ├── utils
│   │   └── auth_utils.py
│   └── views
│       ├── home.py
│       ├── lista_usuarios.py
│       └── login.py
├── mydatabase.db
├── services
│   └── data_service.py
```

### 📄 LICENSE:

```text
MIT License

Copyright (c) 2026 gtnasser

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```

### 📄 adapters\api_client.py:

```text
# adapters/api_client.py

from typing import List, Dict, Any
import httpx

API_BASE_URL = "http://localhost:8000"


# --- Usuários ---

def listar_usuarios_sistema(token: str = "") -> List[Dict[str, Any]]:
    """Consome a listagem de usuarios atraves da API FastAPI."""
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(f"{API_BASE_URL}/usuarios", headers=headers, timeout=10.0)
    return response.json() if response.status_code == 200 else []


```

### 📄 adapters\db_local.py:

```text
# adapters/db_local.py

from typing import List, Dict, Any
from core.database import get_database_session
from database.repository import listar_usuarios

# --- Usuários ---

def listar_usuarios_sistema(token: str = "") -> List[Dict[str, Any]]:
    """Retorna todos os usuários cadastrados."""
    db = next(get_database_session())
    try:
        usuarios = listar_usuarios(db)
        # Converte os modelos SQLAlchemy em dicionarios para padronizar com a API
        return [
            {
                "id": u.id,
                "username": u.username,
                "name": u.name,
                "role": u.role,
                "is_active": u.is_active
            }
            for u in usuarios
        ]
    finally:
        db.close()
```

### 📄 core\config.py:

```text
# core/config.py

import os
from dotenv import load_dotenv

load_dotenv()

# Define se o sistema roda em modo "local" ou "api"
APP_MODE = os.getenv("APP_MODE", "local")  # Opções: "local" ou "api"
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

```

### 📄 core\database.py:

```text
# core/database.py

import hashlib
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from typing import Generator, Tuple

DATABASE_URL = "sqlite:///./mydatabase.db"
INITIAL_USERNAME = "admin"
INITIAL_PASSWORD = "admin123"
ITERATIONS = 100_000

#---  Configurações do banco SQLITE ---

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)
Base = declarative_base()

# --- Inicialização de banco e sessão

def init_database() -> None:
    """Cria todas as tabelas do banco de dados SQLite, tabelas existentes não são recriadas."""
    Base.metadata.create_all(bind=engine)
    _seed_initial_admin()


def get_database_session() -> Generator[Session, None, None]:
    """Provê uma sessão ativa do banco SQLite para operações locais ou via API."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _seed_initial_admin() -> None:
    """Insere um usuario administrador padrao utilizando a funcao create_user."""
    from database.models import UsuarioModel
    
    with SessionLocal() as session:
        admin_existente = session.query(UsuarioModel).filter(UsuarioModel.username == "admin").first()
        if not admin_existente:
            create_user(
                username="admin",
                password="admin123",
                name="Administrador do Sistema",
                role="admin"
            )


# --- Autenticação ---

def _hash_password(password: str, salt: bytes | None = None) -> Tuple[str, str]:
    """Gera o salt e o hash de uma senha utilizando PBKDF2 com SHA-256."""
    if salt is None:
        salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return salt.hex(), digest.hex()


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verifica se a senha informada confere com o hash armazenado."""
    try:
        salt_hex, hash_hex = stored_password.split("$")
        salt = bytes.fromhex(salt_hex)
        _, provided_digest_hex = _hash_password(provided_password, salt)
        return provided_digest_hex == hash_hex
    except Exception:
        return False


# --- Usuário ---

def create_user(username: str, password: str, name: str, role: str = "agent") -> bool:
    """Cria um novo usuario no banco de dados com senha hasheada. Retorna True se sucesso ou False se o username ja existir."""
    from database.models import UsuarioModel
    
    salt_hex, hash_hex = _hash_password(password)
    stored_password = f"{salt_hex}${hash_hex}"
    
    user = UsuarioModel(
        username=username,
        name=name,
        hashed_password=stored_password,
        role=role,
        is_active=True
    )
    
    try:
        with SessionLocal() as session:
            session.add(user)
            session.commit()
        return True
    except IntegrityError:
        return False
    
```

### 📄 database\models.py:

```text
# database/models.py

from sqlalchemy import String, Text, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime
from core.database import Base

#class User(Base):
#    __tablename__ = "users"
#    id: Mapped[int] = mapped_column(primary_key=True)
#    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
#    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

class UsuarioModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="agent") # Ex: "admin", "agent", "client"
    is_active = Column(Boolean, default=True)



```

### 📄 database\repository.py:

```text
# database/repository.py
from sqlalchemy.orm import Session
from database.models import UsuarioModel
from typing import List, Optional

def listar_usuarios(db: Session) -> List[UsuarioModel]:
    """Retorna todos os usuarios cadastrados no banco local."""
    return db.query(UsuarioModel).order_by(UsuarioModel.username.asc()).all()

def buscar_usuario_por_username(db: Session, username: str) -> Optional[UsuarioModel]:
    """Busca um usuario cadastrado pelo seu nome de usuario."""
    return db.query(UsuarioModel).filter(UsuarioModel.username == username).first()

```

### 📄 frontend\app.py:

```text
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
```

### 📄 frontend\utils\auth_utils.py:

```text
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
    Pode receber uma string única (ex: 'admin') ou uma lista (ex: ['gerente', 'coordenador']).
    """
    _ensure_session_initialized()
    if not is_authenticated():
        return False
    user_roles = get_current_user_roles()
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    return any(role in user_roles for role in required_roles)
```

### 📄 frontend\views\home.py:

```text
# frontend/views/home.py
import streamlit as st
import utils.auth_utils as auth

def render_home_page() -> None:
    """Renderiza a pagina inicial protegida."""
    user_data = auth.get_current_user_data()
    user_name = user_data.get("name", "Unknown")

    st.subheader(f"Bem-vindo, {user_name}!")

    st.write("Esta á a página inicial do MyProject.")
    st.info("Utilize o menu lateral para navegar entre as opções do sistema disponíveis para você.")

render_home_page()

```

### 📄 frontend\views\lista_usuarios.py:

```text
# frontend/views/home.py

import streamlit as st
import utils.auth_utils as auth
from services.data_service import listar_usuarios_sistema


def render_home_page() -> None:
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
                "role": "Perfil (Role)",
                "is_active": "Ativo"
            }
        )
    except Exception as erro:
        st.error(f"Erro ao carregar a listagem de usuários: {erro}")

render_home_page()
```

### 📄 frontend\views\login.py:

```text
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


```

### 📄 services\data_service.py:

```text
# services/data_service.py

import os
from typing import List, Dict, Any


# Carrega o adaptador correto conforme o valor da variável de ambiente (padrão: local)
APP_MODE = os.getenv("APP_MODE", "local")

if APP_MODE == "local":
    from adapters import db_local as data_provider
    # inicializa banco de dados
    from core.database import init_database
    init_database()
else:
    from adapters import api_client as data_provider

# Interface unificada com todos os adapters

# --- Usuários ---

def listar_usuarios_sistema(token: str = "") -> List[Dict[str, Any]]:
    """Retorna todos os usuários cadastrados."""
    return data_provider.listar_usuarios_sistema(token)

```

