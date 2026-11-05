def validar_livro(dados, cadastro=False):

    if not isinstance(dados, dict):
        return None, "Envie um objeto JSON válido."

    # Campos obrigatórios no cadastro
    obrigatorios = ["titulo", "autor", "ano", "genero"]

    if cadastro:
        for campo in obrigatorios:
            if campo not in dados:
                return None, f"O campo '{campo}' é obrigatório."

    resultado = {}

    # Validação dos textos
    for campo in ["titulo", "autor", "genero"]:

        if campo in dados:

            valor = dados[campo]

            if not isinstance(valor, str) or not valor.strip():
                return None, f"O campo '{campo}' deve ser um texto válido."

            resultado[campo] = valor.strip()

    # Validação do ano
    if "ano" in dados:

        ano = dados["ano"]

        if type(ano) is not int or not 0 <= ano <= 2100:
            return None, "O ano deve ser um número inteiro entre 0 e 2100."

        resultado["ano"] = ano

    # Validação da disponibilidade
    if "disponivel" in dados:

        disponivel = dados["disponivel"]

        if type(disponivel) is not bool:
            return None, "O campo 'disponivel' deve ser verdadeiro ou falso."

        resultado["disponivel"] = disponivel

    if not resultado:
        return None, "Nenhum campo válido foi enviado."

    return resultado, None