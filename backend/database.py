from pymongo import MongoClient


# Conexão com o MongoDB
cliente = MongoClient(
    "mongodb://localhost:27017/",
    serverSelectionTimeoutMS=5000
)

# Seleção do banco de dados
banco = cliente["biblioteca"]

# Seleção da coleção
livros = banco["livros"]


def verificar_conexao():
    """Verifica se o MongoDB está acessível."""
    cliente.admin.command("ping")


def obter_colecao_livros():
    """Retorna a coleção de livros."""
    return livros