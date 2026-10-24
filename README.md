# 🎫 Boilerplate Streamlit, SQL & FastAPI

Um boilerplate profissional e desacoplado para aplicações em Python que combinam **Streamlit** (Frontend) com **FastAPI** (Backend) e **SQLAlchemy** (Banco de Dados relacional), estruturado sob os princípios da **Arquitetura de Portas e Adaptadores (Hexagonal)**, permitindo flexibilidade total na arquitetura de implantação.

---

## 🏗️ Arquitetura e Flexibilidade

Este projeto adota uma abordagem baseada em **Ports & Adapters (Arquitetura Hexagonal / Clean Architecture)**. O grande diferencial dessa estrutura é que a interface e as regras de negócio são completamente desacopladas da camada de persistência e comunicação, permitindo alternar facilmente entre dois modos de execução através da variável de ambiente `APP_MODE`:

1. **Modo Monolítico (`APP_MODE=local`)**: O Streamlit interage diretamente com a base de dados através de adaptadores (`adapters/db_local.py`). Ideal para MVPs rápidos ou aplicações internas.
2. **Modo Desacoplado / Microsserviço (`APP_MODE=api`)**: O Streamlit atua estritamente como um cliente HTTP (`httpx`), consumindo uma API REST independente (`adapters/api_client.py`). Ideal para arquiteturas escaláveis.

Vantagens:
- O acesso aos dados é feito somente pela camada de serviços (`services/data_service.py`), sendo completamente transparente para as telas do Streamlit.
- A separação rígida de responsabilidades promove alta **manutenibilidade** e **testabilidade**. É possível, por exemplo, criar cenários adicionais totalmente isolados (como um `mock_repository.py` para testes automatizados) ajustando apenas o mapeamento no `data_service.py`.

---

## 📂 Estrutura do Projeto

```text
boilerplate_streamlit_sql_fastapi/
├── LICENSE
├── adapters/
│   ├── api_client.py        # Adaptador para consumo da API FastAPI (Modo API)
│   └── db_local.py          # Adaptador para acesso direto ao SQLite (Modo Local)
├── core/
│   ├── config.py            # Configurações globais e leitura de variáveis de ambiente
│   └── database.py          # Configuração do SQLAlchemy, Sessão e Hashing de senhas
├── database/
│   ├── models.py            # Modelos/Tabelas do banco de dados (SQLAlchemy)
│   └── repository.py        # Consultas e operações de CRUD no banco
├── frontend/
│   ├── app.py               # Ponto de entrada principal do Streamlit
│   ├── utils/
│   │   └── auth_utils.py    # Gerenciamento de sessão, token e permissões
│   └── views/               # Páginas/Telas do sistema que consomem exclusivamente o data_service
├── services/
│   └── data_service.py      # Camada unificada (Facade) que chaveia os adaptadores
├── create_user.py           # Script CLI para criação de usuários administrativos/iniciais
└── requirements.txt         # Dependências do projeto
```


## 🎯 Funções e Responsabilidade dos Módulos Principais

1. Configuração do Ambiente (`core/config.py`)

Responsável por carregar as variáveis de configuração que determinam o comportamento do sistema.

`core/config.py`
``` python
import os
from dotenv import load_dotenv

load_dotenv()

# Define se o sistema roda em modo "local" ou "api"
APP_MODE = os.getenv("APP_MODE", "local")  # Opções: "local" ou "api"
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
```

2. Configuração do Banco de Dados (`core/database.py`)

Gerencia unicamente a conexão com o banco de dados (exemplo utilizando **SQLite**) e provê as sessões ativas.

`core/database.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator

DATABASE_URL = "sqlite:///./mydatabase.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_database() -> None:
    """Cria todas as tabelas do banco de dados SQLite caso não existam."""
    Base.metadata.create_all(bind=engine)

def get_database_session() -> Generator[Session, None, None]:
    """Provê uma sessão ativa do banco SQLite para operações locais ou via API."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

3. Interface Central de Dados (`services/data_service.py`)

Atua como o ponto de chaveamento do sistema, isolando completamente as camadas visual e dados. O frontend interage exclusivamente com este serviço, que injeta o adaptador correspondente com base na variável `APP_MODE`.

`services/data_service.py`:
```python
import os
from typing import List, Dict, Any

# Define o modo com base na variável de ambiente (padrão: local)
APP_MODE = os.getenv("APP_MODE", "local")

if APP_MODE == "local":
    from adapters import db_local as data_provider
else:
    from adapters import api_client as data_provider

def listar_ocorrencias_sistema(token: str = "") -> List[Dict[str, Any]]:
    """Interface unificada para listar ocorrências."""
    return data_provider.listar_ocorrencias_sistema(token)

def criar_ocorrencia_sistema(dados: Dict[str, Any], token: str = "") -> Dict[str, Any]:
    """Interface unificada para criar ocorrência."""
    return data_provider.criar_ocorrencia_sistema(dados, token)
```

4. Adaptador Local (adapters/db_local.py)

Gerencia a abertura de sessões locais e aciona diretamente os repositórios do banco de dados.

`adapters/db_local.py`:
```python
from typing import List, Dict, Any
from core.database import get_database_session
from database.repository import listar_ocorrencias, criar_ocorrencia

def listar_ocorrencias_sistema(token: str = "") -> List[Dict[str, Any]]:
    """Acessa direto o banco de dados local."""
    db = next(get_database_session())
    try:
        return listar_ocorrencias(db)
    finally:
        db.close()

def criar_ocorrencia_sistema(dados: Dict[str, Any], token: str = "") -> Dict[str, Any]:
    """Salva direto no banco de dados local."""
    db = next(get_database_session())
    try:
        return criar_ocorrencia(db, dados)
    finally:
        db.close()
```

5. Adaptador Remoto (adapters/api_client.py)

Responsável por disparar as requisições HTTP utilizando httpx para interagir com o backend FastAPI.

`adapters/api_client.py`:
```python
from typing import List, Dict, Any
import httpx

API_BASE_URL = "http://localhost:8000"

def listar_ocorrencias_sistema(token: str = "") -> List[Dict[str, Any]]:
    """Consome os dados através da API FastAPI."""
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(f"{API_BASE_URL}/ocorrencias", headers=headers, timeout=10.0)
    return response.json() if response.status_code == 200 else []

def criar_ocorrencia_sistema(dados: Dict[str, Any], token: str = "") -> Dict[str, Any]:
    """Envia os dados para a API FastAPI."""
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.post(f"{API_BASE_URL}/ocorrencias", json=dados, headers=headers, timeout=10.0)
    return response.json() if response.status_code == 201 else {}
```

-----


## 🎯 Navegação básica

Fluxo básico do Frontend: Menu de navegação, controle de sessão e login.

### 📂 Estrutura de Diretórios

```text
└── frontend/
    ├── app.py                # Aplicação principal, menu lateral, roteamento e login
    ├── utils/
    |   └── auth_utils.py     # Gerencia o estado da sessão e permissões
    └── views/                # Telas do Streamlit que consomem exclusivamente o data_service
        ├── home.py           # Tela de entrada do sistema
        └── lista_usuario.py  # Tela com listagem de usuários, como exemplo para menu, dados, etc.
```

O módulo `auth_utils.py` disponibiliza o decorador `role_required` para que se possa controlar o acesso a cada página, e a função `check_user_has_role` para que se possa controlar o acesso a componentes ou funcionalidades, Validando a autenticação e a exixstência das roles necessárias para o acesso.

`anypage.py`:
```
import streamlit as st
import utils.auth_utils as auth

@auth.role_required(allowed_roles=["admin"], login_page="views/login.py")
def render():
    st.title("Restricted Page")

    # restricted content, allowed just for admin

    if auth.check_user_has_role(["dev"]):
        st.write("restricted content, allowed just for role.")

if __name__ == "__main__":
    render()
```

### ️📄 Funções e Responsabilidade dos Módulos Principais

1. Aplicação Principal (`app.py`)

É a aplicação principal do sistema, atua como o roteador central, verifica o estado de autenticação do usuário (`st.session_state`), decide se exibe a tela de login ou o painel protegido com o menu lateral de navegação.

2. Rotinas de Autenticação (`auth_utils.py`)

Conjunto de rotinas para manipulação dos dados de autenticação da sessão e das variáveis de memória da sessão.

2. Tela de Autenticação (`login.py`)

Tela de autenticação do usuário, chamada sempre que a sessão não estiver devidamente autenticada.

-----


## 🎯 Módulos de Banco de Dados

Para manter o projeto limpo e coeso, vamos redefinir a fronteira exata entre estes dois módulos.

### 📂 Estrutura de Diretórios

```text
myproject/
├── core/
│   └── database.py           # Configuração, infraestrutura e segurança
├── database/
│   ├── repository.py         # Camada de persistência
```

A Separação Ideal: `core/database.py` vs `database/repository.py1`.

1. `core/database.py` (Infraestrutura Pura)

- O que deve conter: Apenas a infraestrutura técnica de ligação à base de dados e funções utilitárias agnósticas de segurança.
  - Configuração da `engine` e do `SessionLocal()`.
  - Declaração da Base do ORM.
  - Função de criação da base de dados (`init_database()`).
  - Funções puras de encriptação e verificação de passwords (`_hash_password`, `verify_password)`.   
- O que NÃO deve conter: 
  - Consultas ou manipulações diretas de tabelas de negócio (como utilizadores ou ocorrências). 
  - Ela não deve conhecer os modelos específicos da aplicação.
  
2. `database/repository.py` (Camada de Persistência / Queries / ORM)

- O que deve conter: Toda a lógica de interação com o ORM (consultas, inserções, atualizações e eliminações) usando os modelos definidos em `database/models.py`.
  - Funções que recebem uma sessão ativa (db: `Session`) e executam operações nas tabelas.
  - Exemplo: `listar_usuarios(db)`, `buscar_usuario_por_username(db, username)` e a função de escrita `criar_usuario(db, ...)`. 


---


## 🎯 Resumo:

O projeto possui uma arquitetura limpa e excelente, destacando-se por:
1. **Padrão Adapter / Strategy (`services/data_service.py`):** Ele chaveia de forma totalmente transparente entre **modo local** (acesso direto ao SQLite via SQLAlchemy) e **modo API** (consumindo um backend FastAPI via `httpx`) apenas usando a variável de ambiente `APP_MODE`.
2. **Separação de Camadas:** Modelos, repositórios, serviços, adaptadores e views do Streamlit bem isolados.
4. **Segurança Inicial:** Hashing robusto de senhas com **PBKDF2-HMAC-SHA256**, gerando seeds automáticas para o usuário administrador (`admin` / `admin123`) na primeira execução.

### ️📄 Como fazer para começar a implementar as funcionalidades?

Primeiro é necessário definir o cenário **Monolítico** (base relacional local) ou **Desacoplado** (acesso a dados através de API).

Em seguida, siga um dos guias correspondente ao cenário escolhido, eles cobrem todo o passo a passo com trechos funcionais de código para criar novas funcionalidades do banco à interface no modo monolítico local e como conectar os endpoints FastAPI e chamadas HTTP httpx no modo desacoplado.

- [Monolítico](MONOLITHIC_GUIDE.md)
- [Desacoplado](DECOUPLED_GUIDE.md)

