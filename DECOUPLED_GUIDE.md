# 🌐 Guia de Implementação: Arquitetura Desacoplada (`APP_MODE=api`)

Este guia instrui como implementar novas funcionalidades mantendo a separação completa entre o **Frontend (Streamlit)** e o **Backend (FastAPI)** rodando de modo desacoplado (`APP_MODE=api`).

---

## 🏗️ Fluxo de Arquitetura Desacoplada

Na arquitetura cliente-servidor/API, a comunicação ocorre através do protocolo HTTP utilizando JSON:

```
[ Frontend: Streamlit View ]
              ↓
[ Frontend: services/data_service.py ]
              ↓ (APP_MODE=api)
[ Frontend: adapters/api_client.py ] (httpx)
              ↓  (HTTP REST Request / JSON)
[ Backend: FastAPI Endpoints / Routes ]
              ↓
[ Backend: Pydantic Schemas & Security ]
              ↓
[ Backend: Repository & SQLAlchemy ] -> [ SQLite / PostgreSQL ]
```

---

## 🛠️ Passo a Passo Prático (Exemplo: API e Frontend de Produtos)

### 1. Criar os Schemas Pydantic no Backend (`backend/schemas.py`)

Crie a validação de entrada e saída de dados com Pydantic para os endpoints do FastAPI.

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProdutoBase(BaseModel):
    nome: str
    preco: float
    em_estoque: Optional[bool] = True

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoResponse(ProdutoBase):
    id: int
    criado_em: datetime

    class Config:
        from_attributes = True
```

---

### 2. Implementar as Rotas / Endpoints no FastAPI (`backend/routes/produtos.py`)

Crie os endpoints no FastAPI conectando com o repositório.

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_database_session
from database.repository import criar_produto, listar_produtos
from schemas import ProdutoCreate, ProdutoResponse

router = APIRouter(prefix="/produtos", tags=["Produtos"])

@router.post("/", response_model=bool, status_code=status.HTTP_201_CREATED)
def api_criar_produto(
    payload: ProdutoCreate, 
    db: Session = Depends(get_database_session)
):
    sucesso = criar_produto(
        db=db, 
        nome=payload.nome, 
        preco=payload.preco, 
        em_estoque=payload.em_estoque
    )
    if not sucesso:
        raise HTTPException(status_code=400, detail="Erro ao criar produto.")
    return True

@router.get("/", response_model=List[ProdutoResponse])
def api_listar_produtos(
    db: Session = Depends(get_database_session)
):
    produtos = listar_produtos(db)
    return produtos
```

*(Lembre-se de registrar o `router` no arquivo principal da sua aplicação FastAPI, ex: `app.include_router(produtos.router)`)*.

---

### 3. Implementar a Chamada HTTP no Adaptador Client (`adapters/api_client.py`)

Configure o cliente HTTP (`httpx`) para consumir o FastAPI no `api_client.py`.

```python
# adapters/api_client.py
from typing import List, Dict, Any
import httpx

API_BASE_URL = "http://localhost:8000"

# --- Produtos ---

def criar_produto_sistema(nome: str, preco: float, em_estoque: bool = True, token: str = "") -> bool:
    """Envia requisição POST para a API FastAPI para cadastrar produto."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "nome": nome,
        "preco": preco,
        "em_estoque": em_estoque
    }
    try:
        response = httpx.post(f"{API_BASE_URL}/produtos", json=payload, headers=headers, timeout=10.0)
        return response.status_code in (200, 201)
    except Exception:
        return False

def listar_produtos_sistema(token: str = "") -> List[Dict[str, Any]]:
    """Envia requisição GET para a API FastAPI para obter a lista de produtos."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = httpx.get(f"{API_BASE_URL}/produtos", headers=headers, timeout=10.0)
        return response.json() if response.status_code == 200 else []
    except Exception:
        return []
```

---

### 4. Garantir Paridade na Interface Unificada (`services/data_service.py`)

Como o `data_service.py` importa dinamicamente o `api_client` quando `APP_MODE=api`, basta que as assinaturas das funções no `api_client.py` e no `db_local.py` sejam **exatamente idênticas**.

```python
# services/data_service.py

def criar_produto_sistema(nome: str, preco: float, em_estoque: bool = True, token: str = "") -> bool:
    """Consome o data_provider ativo (api_client se APP_MODE=api)."""
    return data_provider.criar_produto_sistema(nome, preco, em_estoque, token)

def listar_produtos_sistema(token: str = "") -> List[Dict[str, Any]]:
    """Consome o data_provider ativo (api_client se APP_MODE=api)."""
    return data_provider.listar_produtos_sistema(token)
```

---

### 5. Consumo no Streamlit (`frontend/views/produtos.py`)

O código da view do Streamlit permanece **100% inalterado**, pois ele consome apenas a camada `services/data_service.py`.

```python
# frontend/views/produtos.py
from services.data_service import listar_produtos_sistema, criar_produto_sistema

# A view invoca o service sem se preocupar se é local ou remoto via HTTP
produtos = listar_produtos_sistema(token=token)
```

---

## ⚡ Testando no Modo Desacoplado (API)

1. Altere o arquivo `.env`:
```env
APP_MODE=api
API_BASE_URL=http://localhost:8000
```

2. Em um terminal, inicie o servidor FastAPI:
```bash
uvicorn main:app --reload --port 8000
```

3. Em outro terminal, inicie o cliente Streamlit:
```bash
streamlit run frontend/app.py
```

4. A aplicação Streamlit enviará todas as requisições via `httpx` para o FastAPI, mantendo as duas aplicações completamente desacopladas!