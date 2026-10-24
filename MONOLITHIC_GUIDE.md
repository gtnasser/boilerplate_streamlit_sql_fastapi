# 📖 Guia de Implementação: Arquitetura Monolítica (`APP_MODE=local`)

Este guia detalha o fluxo completo para implementar novas funcionalidades quando a aplicação roda em modo **monolítico local** (`APP_MODE=local`). Nessa arquitetura, o Streamlit executa as regras de negócio e consulta o banco SQLite diretamente via SQLAlchemy através do adaptador local.

---

## 🏗️ Fluxo de Desenvolvimento em Camadas

Para adicionar qualquer nova entidade (exemplo: **Produtos**), você deve seguir rigorosamente o fluxo em camadas:

```
[ frontend/views/produtos.py ] 
              ↓
[ frontend/app.py ] (Registra a nova rota no menu)
              ↓
[ services/data_service.py ] 
              ↓
[ adapters/db_local.py ] 
              ↓
[ database/repository.py ] 
              ↓
[ database/models.py ] (Tabela SQLite via SQLAlchemy)
```

---

## 🚀 Passo a Passo Prático (Exemplo: Módulo de Produtos)

### 1. Criar o Modelo no Banco (`database/models.py`)

Defina a tabela `ProdutoModel` e seus campos.

```python
# database/models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from core.database import Base

class ProdutoModel(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    preco = Column(Float, nullable=False)
    em_estoque = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
```

---

### 2. Criar as Operações de Banco no Repositório (`database/repository.py`)

Adicione as funções de busca, criação e listagem utilizando sessões SQLAlchemy.

```python
# database/repository.py
from sqlalchemy.orm import Session
from database.models import ProdutoModel
from typing import List, Optional

# --- Produtos ---

def criar_produto(db: Session, nome: str, preco: float, em_estoque: bool = True) -> bool:
    """Cadastra um novo produto no banco de dados SQLite."""
    novo_produto = ProdutoModel(nome=nome, preco=preco, em_estoque=em_estoque)
    try:
        db.add(novo_produto)
        db.commit()
        db.refresh(novo_produto)
        return True
    except Exception:
        db.rollback()
        return False

def listar_produtos(db: Session) -> List[ProdutoModel]:
    """Retorna todos os produtos cadastrados."""
    return db.query(ProdutoModel).order_by(ProdutoModel.nome.asc()).all()
```

---

### 3. Implementar a Lógica no Adaptador Local (`adapters/db_local.py`)

Conecte as funções do repositório gerenciando a sessão do banco com `get_database_session()`.

```python
# adapters/db_local.py
from typing import List, Dict, Any
from core.database import get_database_session
from database.repository import criar_produto, listar_produtos

# --- Produtos ---

def criar_produto_sistema(nome: str, preco: float, em_estoque: bool = True, token: str = "") -> bool:
    """Gere a sessão e chama a persistência local do produto."""
    db = next(get_database_session())
    try:
        return criar_produto(db=db, nome=nome, preco=preco, em_estoque=em_estoque)
    finally:
        db.close()

def listar_produtos_sistema(token: str = "") -> List[Dict[str, Any]]:
    """Busca produtos locais e os formata em dicionário."""
    db = next(get_database_session())
    try:
        produtos = listar_produtos(db)
        return [
            {
                "id": p.id,
                "nome": p.nome,
                "preco": p.preco,
                "em_estoque": p.em_estoque,
                "criado_em": p.criado_em.strftime("%Y-%m-%d %H:%M:%S") if p.criado_em else ""
            }
            for p in produtos
        ]
    finally:
        db.close()
```

---

### 4. Expor as Funções na Interface Unificada (`services/data_service.py`)

Estenda a interface do `data_service.py`. O redirecionamento para o `data_provider` já garante o envio para o adaptador local ativado.

```python
# services/data_service.py

# --- Produtos ---

def criar_produto_sistema(nome: str, preco: float, em_estoque: bool = True, token: str = "") -> bool:
    """Interface unificada para criação de produtos."""
    return data_provider.criar_produto_sistema(nome, preco, em_estoque, token)

def listar_produtos_sistema(token: str = "") -> List[Dict[str, Any]]:
    """Interface unificada para listagem de produtos."""
    return data_provider.listar_produtos_sistema(token)
```

---

### 5. Criar a Tela no Streamlit (`frontend/views/produtos.py`)

Crie uma nova view para listar e cadastrar produtos.

```python
# frontend/views/produtos.py
import streamlit as st
import utils.auth_utils as auth
from services.data_service import listar_produtos_sistema, criar_produto_sistema

def render_produtos_page() -> None:
    st.subheader("📦 Gerenciamento de Produtos")

    token = auth.get_current_token()

    # Formulario para adicionar novo produto
    with st.expander("➕ Cadastrar Novo Produto"):
        with st.form("form_novo_produto", clear_on_submit=True):
            nome = st.text_input("Nome do Produto")
            preco = st.number_input("Preço (R$)", min_value=0.0, step=0.50, format="%.2f")
            em_estoque = st.checkbox("Disponível em Estoque", value=True)
            
            if st.form_submit_button("Salvar Produto"):
                if not nome:
                    st.warning("O nome do produto é obrigatório.")
                else:
                    sucesso = criar_produto_sistema(nome=nome, preco=preco, em_estoque=em_estoque, token=token)
                    if sucesso:
                        st.success("Produto cadastrado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao cadastrar produto.")

    # Tabela com listagem
    st.markdown("### Lista de Produtos Cadastrados")
    produtos = listar_produtos_sistema(token=token)

    if not produtos:
        st.info("Nenhum produto cadastrado.")
    else:
        st.dataframe(
            produtos,
            use_container_width=True,
            column_config={
                "id": "ID",
                "nome": "Nome do Produto",
                "preco": st.column_config.NumberColumn("Preço", format="R$ %.2f"),
                "em_estoque": "Estoque Ativo",
                "criado_em": "Data Cadastro"
            }
        )

render_produtos_page()
```

---

### 6. Registrar a Nova View na Navegação (`frontend/app.py`)

Adicione a nova página dentro do objeto de navegação no `app.py`:

```python
# frontend/app.py

def setup_navigation() -> any:
    if not auth.is_authenticated():
        return st.navigation([
            st.Page("views/login.py", title="Login", icon="🔑")
        ])

    pages = [
        st.Page("views/home.py", title="Home", icon="🏠"),
        st.Page("views/lista_usuarios.py", title="Listagem de Usuários", icon="👤"),
        st.Page("views/produtos.py", title="Produtos", icon="📦"),
    ]
    return st.navigation(pages)
```

---

## ⚡ Testando no Modo Monolítico
1. Garanta que o `.env` esteja configurado com: `APP_MODE=local`
2. Execute o Streamlit localmente:
```bash
streamlit run frontend/app.py
```
3. O banco SQLite `mydatabase.db` criará automaticamente a tabela `produtos` na inicialização e tudo funcionará localmente sem necessidade de servidor backend externo.