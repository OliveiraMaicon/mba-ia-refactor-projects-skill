from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"erro": str(error.description)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"erro": "Recurso não encontrado"}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"erro": "Método não permitido"}), 405

    @app.errorhandler(500)
    def internal_error(error):
        logger.exception("Internal server error")
        return jsonify({"erro": "Erro interno do servidor"}), 500
