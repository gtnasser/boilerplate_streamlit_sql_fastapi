# create_user.py
import sys
from services.data_service import criar_usuario_sistema

def main() -> None:
    """Script de linha de comando para criar um novo usuário com acesso a login no sistema."""
    if len(sys.argv) < 3:
        print("❌ Uso incorreto!")
        print("Usage: python create_user.py <username> <password> [nome_completo] [role ...]")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else username.capitalize()
    roles = sys.argv[4:] if len(sys.argv) > 4 else []
    # evita duplicidades e insere role "login" por padrão 
    roles = list(set(roles))
    #roles.append("login") if "login" not in roles else None

    print(f"👤 Criando o utilizador '{username}' com as roles '{roles}' via data_service...")
    
    sucesso = criar_usuario_sistema(username=username, password=password, name=name, roles=roles)

    if sucesso:
        print(f"✅ Utilizador '{username}' criado com sucesso!")
    else:
        print(f"❌ Erro: O nome de utilizador '{username}' já existe ou ocorreu um erro na operação.")
        sys.exit(1)

if __name__ == "__main__":
    main()