from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": str(error.description)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(error):
        logger.exception("Internal server error")
        return jsonify({"error": "Internal server error"}), 500
