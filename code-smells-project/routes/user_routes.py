from flask import Blueprint, jsonify
from controllers.user_controller import UserController

user_bp = Blueprint('users', __name__)
controller = UserController()

@user_bp.route('/usuarios', methods=['GET'])
def list_users():
    result, status = controller.list_users()
    return jsonify(result), status

@user_bp.route('/usuarios/<int:user_id>', methods=['GET'])
def get_user(user_id):
    result, status = controller.get_user(user_id)
    return jsonify(result), status

@user_bp.route('/usuarios', methods=['POST'])
def create_user():
    result, status = controller.create_user()
    return jsonify(result), status

@user_bp.route('/login', methods=['POST'])
def login():
    result, status = controller.login()
    return jsonify(result), status
