from bson import ObjectId
from backend.database import obter_colecao_livros


# Obtém a coleção de livros
livros = obter_colecao_livros()


# READ: listar todos os livros
def listar_livros():

    resultado = []

    for livro in livros.find().sort("titulo", 1):

        livro["_id"] = str(livro["_id"])

        resultado.append(livro)

    return resultado


# CREATE: cadastrar um livro
def cadastrar_livro(dados):

    resultado = livros.insert_one(dados)

    return str(resultado.inserted_id)


# UPDATE: atualizar um livro
def atualizar_livro(id, dados):

    resultado = livros.update_one(
        {"_id": ObjectId(id)},
        {"$set": dados}
    )

    return resultado.matched_count > 0


# DELETE: excluir um livro
def excluir_livro(id):

    resultado = livros.delete_one(
        {"_id": ObjectId(id)}
    )

    return resultado.deleted_count > 0