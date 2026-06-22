from flask import Blueprint, jsonify
from controllers.order_controller import OrderController

order_bp = Blueprint('orders', __name__)
controller = OrderController()

@order_bp.route('/pedidos', methods=['POST'])
def create_order():
    result, status = controller.create_order()
    return jsonify(result), status

@order_bp.route('/pedidos', methods=['GET'])
def list_all_orders():
    result, status = controller.list_all_orders()
    return jsonify(result), status

@order_bp.route('/pedidos/usuario/<int:usuario_id>', methods=['GET'])
def list_user_orders(usuario_id):
    result, status = controller.list_user_orders(usuario_id)
    return jsonify(result), status

@order_bp.route('/pedidos/<int:pedido_id>/status', methods=['PUT'])
def update_order_status(pedido_id):
    result, status = controller.update_order_status(pedido_id)
    return jsonify(result), status
