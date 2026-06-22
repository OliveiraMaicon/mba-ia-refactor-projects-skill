from flask import Blueprint, jsonify
from controllers.report_controller import ReportController

report_bp = Blueprint('reports', __name__)
controller = ReportController()

@report_bp.route('/relatorios/vendas', methods=['GET'])
def sales_report():
    result, status = controller.sales_report()
    return jsonify(result), status

@report_bp.route('/health', methods=['GET'])
def health_check():
    result, status = controller.health_check()
    return jsonify(result), status
