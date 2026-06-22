from flask import Blueprint, jsonify
from controllers.product_controller import ProductController

product_bp = Blueprint('products', __name__)
controller = ProductController()

@product_bp.route('/produtos', methods=['GET'])
def list_products():
    result, status = controller.list_products()
    return jsonify(result), status

@product_bp.route('/produtos/busca', methods=['GET'])
def search_products():
    result, status = controller.search_products()
    return jsonify(result), status

@product_bp.route('/produtos/<int:product_id>', methods=['GET'])
def get_product(product_id):
    result, status = controller.get_product(product_id)
    return jsonify(result), status

@product_bp.route('/produtos', methods=['POST'])
def create_product():
    result, status = controller.create_product()
    return jsonify(result), status

@product_bp.route('/produtos/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    result, status = controller.update_product(product_id)
    return jsonify(result), status

@product_bp.route('/produtos/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    result, status = controller.delete_product(product_id)
    return jsonify(result), status
