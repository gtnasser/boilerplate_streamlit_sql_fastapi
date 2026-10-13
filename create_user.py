# create_user.py
import sys
from services.data_service import criar_usuario_sistema

def main() -> None:
    """Script de linha de comando para criar um novo utilizador no sistema através do data_service."""
    if len(sys.argv) < 3:
        print("❌ Uso incorreto!")
        print("Exemplo de uso: python create_user.py <username> <password> [nome_completo] [role]")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else username.capitalize()
    role = sys.argv[4] if len(sys.argv) > 4 else "agent"

    print(f"👤 A criar o utilizador '{username}' com a role '{role}' via data_service...")
    
    sucesso = criar_usuario_sistema(username=username, password=password, name=name, role=role)

    if sucesso:
        print(f"✅ Utilizador '{username}' criado com sucesso!")
    else:
        print(f"❌ Erro: O nome de utilizador '{username}' já existe ou ocorreu um erro na operação.")
        sys.exit(1)

if __name__ == "__main__":
    main()