# Myproject

Base para o desenvolvimento de sistemas modulares com autenticação, controle de sessão via **JWT** e acesso a bancos de dados relacionais. 
O projeto foi desenhado para servir como ponto de partida (*boilerplate*) para novos softwares, permitindo flexibilidade total na arquitetura de implantação.

## 🏛️ Arquitetura e Padrões de Projeto

O projeto adota uma abordagem baseada em **Ports & Adapters (Arquitetura Hexagonal / Clean Architecture)**. 
O grande diferencial dessa estrutura é que a interface e as regras de negócio são completamente desacopladas da camada de persistência e comunicação. 

O sistema pode rodar em dois cenários distintos, controlados de forma simples por meio de uma variável de ambiente (`APP_MODE`):

- **Cenário 1 (Monolítico / Local):** O frontend consome diretamente o repositório local via **SQLAlchemy**, executando operações de banco de dados no mesmo servidor.
- **Cenário 2 (Desacoplado / API):** O frontend realiza requisições HTTP (`httpx`) para um backend em **FastAPI**, que por sua vez gerencia o acesso ao banco de dados.

Essa separação rígida de responsabilidades promove alta **manutenibilidade** e **testabilidade**. 
É possível, por exemplo, criar cenários adicionais totalmente isolados (como um `mock_repository.py` para testes automatizados) ajustando apenas o mapeamento no `data_service.py`.

---

## 📂 Estrutura de Diretórios

```text
myproject/
├── core/
│   ├── config.py             # Lê as variáveis de ambiente e define o modo (local vs api)
│   └── database.py           # Configura a engine do SQLite e provê as sessões (SessionLocal)
├── services/
│   └── data_service.py       # Interface central de negócio (orquestrador que define o adaptador ativo)
├── adapters/
│   ├── db_local.py           # Acesso direto ao banco local (Usado no Cenário 1)
│   └── api_client.py         # Acesso via HTTP/FastAPI (Usado no Cenário 2)
└── frontend/
    └── views/                # Telas do Streamlit que consomem exclusivamente o data_service
```


⚙️ Configuração e Módulos Principais

1. Configuração do Ambiente (core/config.py)

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

2. Configuração do Banco de Dados (core/database.py)

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

3. Interface Central de Dados (services/data_service.py)

Atua como o ponto de chaveamento do sistema. O frontend interage exclusivamente com este serviço, que injeta o adaptador correspondente com base na variável `APP_MODE`.

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
