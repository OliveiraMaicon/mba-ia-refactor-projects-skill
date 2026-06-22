from flask import jsonify, request
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload

VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200


class TaskController:

    def get_tasks(self):
        tasks = Task.query.options(
            joinedload(Task.user),
            joinedload(Task.category)
        ).all()
        result = []
        for t in tasks:
            data = t.to_dict()
            data['user_name'] = t.user.name if t.user else None
            data['category_name'] = t.category.name if t.category else None
            data['overdue'] = t.is_overdue()
            result.append(data)
        return result, 200

    def get_task(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            return {'error': 'Task not found'}, 404
        data = task.to_dict()
        data['overdue'] = task.is_overdue()
        return data, 200

    def create_task(self):
        data = request.get_json()
        if not data:
            return {'error': 'Invalid data'}, 400

        title = data.get('title')
        if not title:
            return {'error': 'Title is required'}, 400
        if len(title) < MIN_TITLE_LENGTH:
            return {'error': 'Title too short'}, 400
        if len(title) > MAX_TITLE_LENGTH:
            return {'error': 'Title too long'}, 400

        status = data.get('status', 'pending')
        priority = data.get('priority', 3)

        if status not in VALID_STATUSES:
            return {'error': 'Invalid status'}, 400
        if not (1 <= priority <= 5):
            return {'error': 'Priority must be between 1 and 5'}, 400

        user_id = data.get('user_id')
        category_id = data.get('category_id')

        if user_id:
            if not User.query.get(user_id):
                return {'error': 'User not found'}, 404
        if category_id:
            if not Category.query.get(category_id):
                return {'error': 'Category not found'}, 404

        task = Task()
        task.title = title
        task.description = data.get('description', '')
        task.status = status
        task.priority = priority
        task.user_id = user_id
        task.category_id = category_id

        due_date = data.get('due_date')
        if due_date:
            try:
                task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                return {'error': 'Invalid date format. Use YYYY-MM-DD'}, 400

        tags = data.get('tags')
        if tags:
            task.tags = ','.join(tags) if isinstance(tags, list) else tags

        db.session.add(task)
        db.session.commit()
        return task.to_dict(), 201

    def update_task(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            return {'error': 'Task not found'}, 404

        data = request.get_json()
        if not data:
            return {'error': 'Invalid data'}, 400

        if 'title' in data:
            if len(data['title']) < MIN_TITLE_LENGTH:
                return {'error': 'Title too short'}, 400
            if len(data['title']) > MAX_TITLE_LENGTH:
                return {'error': 'Title too long'}, 400
            task.title = data['title']

        if 'description' in data:
            task.description = data['description']

        if 'status' in data:
            if data['status'] not in VALID_STATUSES:
                return {'error': 'Invalid status'}, 400
            task.status = data['status']

        if 'priority' in data:
            if not (1 <= data['priority'] <= 5):
                return {'error': 'Priority must be between 1 and 5'}, 400
            task.priority = data['priority']

        if 'user_id' in data:
            if data['user_id'] and not User.query.get(data['user_id']):
                return {'error': 'User not found'}, 404
            task.user_id = data['user_id']

        if 'category_id' in data:
            if data['category_id'] and not Category.query.get(data['category_id']):
                return {'error': 'Category not found'}, 404
            task.category_id = data['category_id']

        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
                except ValueError:
                    return {'error': 'Invalid date format'}, 400
            else:
                task.due_date = None

        if 'tags' in data:
            tags = data['tags']
            task.tags = ','.join(tags) if isinstance(tags, list) else tags

        task.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return task.to_dict(), 200

    def delete_task(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            return {'error': 'Task not found'}, 404
        db.session.delete(task)
        db.session.commit()
        return {'message': 'Task deleted successfully'}, 200

    def search_tasks(self):
        query = request.args.get('q', '')
        status = request.args.get('status', '')
        priority = request.args.get('priority', '')
        user_id = request.args.get('user_id', '')

        tasks_query = Task.query

        if query:
            tasks_query = tasks_query.filter(
                db.or_(
                    Task.title.like(f'%{query}%'),
                    Task.description.like(f'%{query}%')
                )
            )
        if status:
            tasks_query = tasks_query.filter(Task.status == status)
        if priority:
            tasks_query = tasks_query.filter(Task.priority == int(priority))
        if user_id:
            tasks_query = tasks_query.filter(Task.user_id == int(user_id))

        results = tasks_query.all()
        return [t.to_dict() for t in results], 200

    def task_stats(self):
        total = Task.query.count()
        pending = Task.query.filter_by(status='pending').count()
        in_progress = Task.query.filter_by(status='in_progress').count()
        done = Task.query.filter_by(status='done').count()
        cancelled = Task.query.filter_by(status='cancelled').count()

        overdue_count = 0
        for t in Task.query.all():
            if t.is_overdue():
                overdue_count += 1

        return {
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
            'overdue': overdue_count,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
        }, 200
