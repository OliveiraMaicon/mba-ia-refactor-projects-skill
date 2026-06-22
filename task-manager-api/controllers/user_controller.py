from flask import request
from database import db
from models.user import User
from models.task import Task
import re

VALID_ROLES = ['user', 'admin', 'manager']
MIN_PASSWORD_LENGTH = 4


class UserController:

    def get_users(self):
        users = User.query.all()
        result = []
        for u in users:
            result.append({
                'id': u.id, 'name': u.name, 'email': u.email,
                'role': u.role, 'active': u.active,
                'created_at': str(u.created_at), 'task_count': len(u.tasks)
            })
        return result, 200

    def get_user(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        data = user.to_dict()
        data['tasks'] = [t.to_dict() for t in user.tasks]
        return data, 200

    def create_user(self):
        data = request.get_json()
        if not data:
            return {'error': 'Invalid data'}, 400

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        if not name:
            return {'error': 'Name is required'}, 400
        if not email:
            return {'error': 'Email is required'}, 400
        if not password:
            return {'error': 'Password is required'}, 400

        if not re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email):
            return {'error': 'Invalid email'}, 400

        if len(password) < MIN_PASSWORD_LENGTH:
            return {'error': f'Password must have at least {MIN_PASSWORD_LENGTH} characters'}, 400

        if User.query.filter_by(email=email).first():
            return {'error': 'Email already registered'}, 409

        if role not in VALID_ROLES:
            return {'error': 'Invalid role'}, 400

        user = User()
        user.name = name
        user.email = email
        user.set_password(password)
        user.role = role

        db.session.add(user)
        db.session.commit()
        return user.to_dict(), 201

    def update_user(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        data = request.get_json()
        if not data:
            return {'error': 'Invalid data'}, 400

        if 'name' in data:
            user.name = data['name']

        if 'email' in data:
            if not re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', data['email']):
                return {'error': 'Invalid email'}, 400
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                return {'error': 'Email already registered'}, 409
            user.email = data['email']

        if 'password' in data:
            if len(data['password']) < MIN_PASSWORD_LENGTH:
                return {'error': 'Password too short'}, 400
            user.set_password(data['password'])

        if 'role' in data:
            if data['role'] not in VALID_ROLES:
                return {'error': 'Invalid role'}, 400
            user.role = data['role']

        if 'active' in data:
            user.active = data['active']

        db.session.commit()
        return user.to_dict(), 200

    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        for t in user.tasks:
            db.session.delete(t)

        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}, 200

    def get_user_tasks(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        result = []
        for t in user.tasks:
            data = {
                'id': t.id, 'title': t.title, 'description': t.description,
                'status': t.status, 'priority': t.priority,
                'created_at': str(t.created_at),
                'due_date': str(t.due_date) if t.due_date else None,
                'overdue': t.is_overdue()
            }
            result.append(data)
        return result, 200

    def login(self):
        data = request.get_json()
        if not data:
            return {'error': 'Invalid data'}, 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'error': 'Email and password are required'}, 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return {'error': 'Invalid credentials'}, 401
        if not user.check_password(password):
            return {'error': 'Invalid credentials'}, 401
        if not user.active:
            return {'error': 'Inactive user'}, 403

        return {
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': 'fake-jwt-token-' + str(user.id)
        }, 200
