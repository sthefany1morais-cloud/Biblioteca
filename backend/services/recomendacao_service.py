from bson import ObjectId
from backend.database import obter_colecao_livros

livros = obter_colecao_livros()


def recomendar_livros(id_livro):
    livro_base = livros.find_one({"_id": ObjectId(id_livro)})

    if livro_base is None:
        return None

    outros_livros = livros.find({
        "_id": {"$ne": ObjectId(id_livro)}
    })

    recomendacoes = []

    for livro in outros_livros:
        pontuacao = 0
        motivos = []

        if livro.get("genero") == livro_base.get("genero"):
            pontuacao += 5
            motivos.append("Mesmo gênero")

        if livro.get("autor") == livro_base.get("autor"):
            pontuacao += 3
            motivos.append("Mesmo autor")

        ano_livro = livro.get("ano")
        ano_base = livro_base.get("ano")

        if ano_livro is not None and ano_base is not None:
            if abs(ano_livro - ano_base) <= 10:
                pontuacao += 1
                motivos.append("Período de publicação semelhante")

        if pontuacao > 0:
            livro["_id"] = str(livro["_id"])
            livro["pontuacao_recomendacao"] = pontuacao
            livro["motivos_recomendacao"] = motivos

            recomendacoes.append(livro)

    recomendacoes.sort(
        key=lambda livro: livro["pontuacao_recomendacao"],
        reverse=True
    )

    return recomendacoes
