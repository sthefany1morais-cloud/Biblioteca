from flask import Blueprint, request, jsonify
from pymongo.errors import PyMongoError
from bson import ObjectId

from backend.database import verificar_conexao

from backend.validators.livro_validator import validar_livro

from backend.services.livro_service import (
    listar_livros,
    cadastrar_livro,
    atualizar_livro,
    excluir_livro
)


# Criação do Blueprint
livros_bp = Blueprint("livros", __name__)


# READ: listar livros
@livros_bp.get("/livros")
def rota_listar_livros():

    try:
        verificar_conexao()

        resultado = listar_livros()

        return jsonify(resultado), 200

    except PyMongoError:
        return jsonify({
            "erro": "Não foi possível consultar os livros."
        }), 503


# CREATE: cadastrar livro
@livros_bp.post("/livros")
def rota_cadastrar_livro():

    dados = request.get_json(silent=True)

    novo_livro, erro = validar_livro(dados, cadastro=True)

    if erro:
        return jsonify({"erro": erro}), 400

    novo_livro.setdefault("disponivel", True)

    try:
        verificar_conexao()

        id_livro = cadastrar_livro(novo_livro)

        return jsonify({
            "mensagem": "Livro cadastrado com sucesso.",
            "id": id_livro
        }), 201

    except PyMongoError:
        return jsonify({
            "erro": "Não foi possível cadastrar o livro."
        }), 503


# UPDATE: atualizar livro
@livros_bp.put("/livros/<id>")
def rota_atualizar_livro(id):

    if not ObjectId.is_valid(id):
        return jsonify({"erro": "ID inválido."}), 400

    dados = request.get_json(silent=True)

    atualizacao, erro = validar_livro(dados)

    if erro:
        return jsonify({"erro": erro}), 400

    try:
        verificar_conexao()

        resultado = atualizar_livro(id, atualizacao)

        if not resultado:
            return jsonify({
                "erro": "Livro não encontrado."
            }), 404

        return jsonify({
            "mensagem": "Livro atualizado com sucesso."
        }), 200

    except PyMongoError:
        return jsonify({
            "erro": "Não foi possível atualizar o livro."
        }), 503


# DELETE: excluir livro
@livros_bp.delete("/livros/<id>")
def rota_excluir_livro(id):

    if not ObjectId.is_valid(id):
        return jsonify({"erro": "ID inválido."}), 400

    try:
        verificar_conexao()

        resultado = excluir_livro(id)

        if not resultado:
            return jsonify({
                "erro": "Livro não encontrado."
            }), 404

        return jsonify({
            "mensagem": "Livro excluído com sucesso."
        }), 200

    except PyMongoError:
        return jsonify({
            "erro": "Não foi possível excluir o livro."
        }), 503