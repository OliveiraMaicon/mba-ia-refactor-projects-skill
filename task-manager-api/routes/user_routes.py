from flask import Blueprint, jsonify
from controllers.user_controller import UserController

user_bp = Blueprint('users', __name__)
controller = UserController()


@user_bp.route('/users', methods=['GET'])
def get_users():
    result, status = controller.get_users()
    return jsonify(result), status


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    result, status = controller.get_user(user_id)
    return jsonify(result), status


@user_bp.route('/users', methods=['POST'])
def create_user():
    result, status = controller.create_user()
    return jsonify(result), status


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    result, status = controller.update_user(user_id)
    return jsonify(result), status


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    result, status = controller.delete_user(user_id)
    return jsonify(result), status


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    result, status = controller.get_user_tasks(user_id)
    return jsonify(result), status


@user_bp.route('/login', methods=['POST'])
def login():
    result, status = controller.login()
    return jsonify(result), status
