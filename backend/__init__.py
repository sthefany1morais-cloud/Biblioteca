from flask import Flask, render_template


def criar_app():

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    # Página inicial
    @app.get("/")
    def pagina_inicial():
        return render_template("index.html")

    # Importação das rotas
    from backend.routes.livro_routes import livros_bp

    # Registro do Blueprint
    app.register_blueprint(livros_bp)

    return app