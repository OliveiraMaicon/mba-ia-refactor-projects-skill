from flask import Blueprint, jsonify
from controllers.report_controller import ReportController

report_bp = Blueprint('reports', __name__)
controller = ReportController()


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    result, status = controller.summary_report()
    return jsonify(result), status


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    result, status = controller.user_report(user_id)
    return jsonify(result), status


@report_bp.route('/categories', methods=['GET'])
def get_categories():
    result, status = controller.get_categories()
    return jsonify(result), status


@report_bp.route('/categories', methods=['POST'])
def create_category():
    result, status = controller.create_category()
    return jsonify(result), status


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    result, status = controller.update_category(cat_id)
    return jsonify(result), status


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    result, status = controller.delete_category(cat_id)
    return jsonify(result), status
