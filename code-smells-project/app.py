from flask import Flask, jsonify, request
from flask_cors import CORS
from config.settings import SECRET_KEY, DEBUG, HOST, PORT
from database import get_db
from routes.product_routes import product_bp
from routes.user_routes import user_bp
from routes.order_routes import order_bp
from routes.report_routes import report_bp
from middlewares.error_handler import register_error_handlers

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["DEBUG"] = DEBUG
CORS(app)

register_error_handlers(app)

app.register_blueprint(product_bp)
app.register_blueprint(user_bp)
app.register_blueprint(order_bp)
app.register_blueprint(report_bp)


@app.route("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health"
        }
    })


@app.route("/admin/reset-db", methods=["POST"])
def reset_database():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM itens_pedido")
    cursor.execute("DELETE FROM pedidos")
    cursor.execute("DELETE FROM produtos")
    cursor.execute("DELETE FROM usuarios")
    db.commit()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200


if __name__ == "__main__":
    get_db()
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://{HOST}:{PORT}")
    print("=" * 50)
    app.run(host=HOST, port=PORT, debug=DEBUG)
