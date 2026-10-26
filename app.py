from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId

app = Flask(__name__)

# Conexão com o MongoDB
cliente = MongoClient(
    "mongodb://localhost:27017/",
    serverSelectionTimeoutMS=5000
)

banco = cliente["biblioteca"]
livros = banco["livros"]


# Verifica se o MongoDB está acessível
def verificar_conexao():
    cliente.admin.command("ping")


# Converte ObjectId para string antes de retornar JSON
def converter_id(livro):
    livro["_id"] = str(livro["_id"])
    return livro


# Valida os campos recebidos
def validar_livro(dados, cadastro=False):
    if not isinstance(dados, dict):
        return None, "Envie um objeto JSON válido."

    permitidos = ["titulo", "autor", "ano", "genero", "disponivel"]

    # No cadastro, os quatro primeiros campos são obrigatórios.
    obrigatorios = ["titulo", "autor", "ano", "genero"]

    if cadastro:
        for campo in obrigatorios:
            if campo not in dados:
                return None, f"O campo '{campo}' é obrigatório."

    resultado = {}

    for campo in ["titulo", "autor", "genero"]:
        if campo in dados:
            valor = dados[campo]

            if not isinstance(valor, str) or not valor.strip():
                return None, f"O campo '{campo}' deve ser um texto válido."

            resultado[campo] = valor.strip()

    if "ano" in dados:
        ano = dados["ano"]

        # bool é uma subclasse de int em Python, por isso usamos type().
        if type(ano) is not int or not 0 <= ano <= 2100:
            return None, "O ano deve ser um número inteiro entre 0 e 2100."

        resultado["ano"] = ano

    if "disponivel" in dados:
        disponivel = dados["disponivel"]

        if type(disponivel) is not bool:
            return None, "O campo 'disponivel' deve ser verdadeiro ou falso."

        resultado["disponivel"] = disponivel

    # Verifica se há pelo menos um campo permitido para atualizar.
    if not resultado:
        return None, "Nenhum campo válido foi enviado."

    return resultado, None


# Página inicial: interface gráfica
@app.get("/")
def pagina_inicial():
    return render_template("index.html")


# READ: listar todos os livros
@app.get("/livros")
def listar_livros():
    try:
        verificar_conexao()

        resultado = [
            converter_id(livro)
            for livro in livros.find().sort("titulo", 1)
        ]

        return jsonify(resultado), 200

    except PyMongoError:
        app.logger.exception("Erro ao consultar os livros.")
        return jsonify({
            "erro": "Não foi possível consultar os livros no banco de dados."
        }), 503


# CREATE: cadastrar um livro
@app.post("/livros")
def cadastrar_livro():
    dados = request.get_json(silent=True)

    novo_livro, erro = validar_livro(dados, cadastro=True)

    if erro:
        return jsonify({"erro": erro}), 400

    # Se a disponibilidade não foi enviada, o livro começa disponível.
    novo_livro.setdefault("disponivel", True)

    try:
        verificar_conexao()

        resultado = livros.insert_one(novo_livro)

        return jsonify({
            "mensagem": "Livro cadastrado com sucesso.",
            "id": str(resultado.inserted_id)
        }), 201

    except PyMongoError:
        app.logger.exception("Erro ao cadastrar livro.")
        return jsonify({
            "erro": "Não foi possível cadastrar o livro."
        }), 503


# UPDATE: atualizar um livro
@app.put("/livros/<id>")
def atualizar_livro(id):
    if not ObjectId.is_valid(id):
        return jsonify({"erro": "ID inválido."}), 400

    dados = request.get_json(silent=True)

    atualizacao, erro = validar_livro(dados)

    if erro:
        return jsonify({"erro": erro}), 400

    try:
        verificar_conexao()

        resultado = livros.update_one(
            {"_id": ObjectId(id)},
            {"$set": atualizacao}
        )

        if resultado.matched_count == 0:
            return jsonify({"erro": "Livro não encontrado."}), 404

        return jsonify({
            "mensagem": "Livro atualizado com sucesso."
        }), 200

    except PyMongoError:
        app.logger.exception("Erro ao atualizar livro.")
        return jsonify({
            "erro": "Não foi possível atualizar o livro."
        }), 503


# DELETE: excluir um livro
@app.delete("/livros/<id>")
def excluir_livro(id):
    if not ObjectId.is_valid(id):
        return jsonify({"erro": "ID inválido."}), 400

    try:
        verificar_conexao()

        resultado = livros.delete_one(
            {"_id": ObjectId(id)}
        )

        if resultado.deleted_count == 0:
            return jsonify({"erro": "Livro não encontrado."}), 404

        return jsonify({
            "mensagem": "Livro excluído com sucesso."
        }), 200

    except PyMongoError:
        app.logger.exception("Erro ao excluir livro.")
        return jsonify({
            "erro": "Não foi possível excluir o livro."
        }), 503


# Inicialização da aplicação
if __name__ == "__main__":
    app.run(debug=True)