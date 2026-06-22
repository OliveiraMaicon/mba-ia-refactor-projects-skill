from flask import Blueprint, jsonify
from controllers.task_controller import TaskController

task_bp = Blueprint('tasks', __name__)
controller = TaskController()


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    result, status = controller.get_tasks()
    return jsonify(result), status


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    result, status = controller.search_tasks()
    return jsonify(result), status


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    result, status = controller.task_stats()
    return jsonify(result), status


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    result, status = controller.get_task(task_id)
    return jsonify(result), status


@task_bp.route('/tasks', methods=['POST'])
def create_task():
    result, status = controller.create_task()
    return jsonify(result), status


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    result, status = controller.update_task(task_id)
    return jsonify(result), status


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    result, status = controller.delete_task(task_id)
    return jsonify(result), status
