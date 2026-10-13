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
    """Insere um usuario administrador padrao utilizando uma função do modulo repositorio."""
    from database.models import UsuarioModel
    from database.repository import buscar_usuario_por_username, criar_usuario
    
    with SessionLocal() as session:
        admin_existente = buscar_usuario_por_username(session, "admin")
        if not admin_existente:
            salt_hex, hash_hex = _hash_password("admin123")
            stored_password = f"{salt_hex}${hash_hex}"
            criar_usuario(
                db=session,
                username="admin",
                password_hash=stored_password,
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
