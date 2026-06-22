from flask import request
import models.user_model as user_model


class UserController:

    def list_users(self):
        users = user_model.get_all_users()
        return {"dados": users, "sucesso": True}, 200

    def get_user(self, user_id):
        user = user_model.get_user_by_id(user_id)
        if user:
            return {"dados": user, "sucesso": True}, 200
        return {"erro": "Usuário não encontrado"}, 404

    def create_user(self):
        data = request.get_json()
        if not data:
            return {"erro": "Dados inválidos"}, 400

        nome = data.get("nome", "")
        email = data.get("email", "")
        senha = data.get("senha", "")

        if not nome or not email or not senha:
            return {"erro": "Nome, email e senha são obrigatórios"}, 400

        user_id = user_model.create_user(nome, email, senha)
        return {"dados": {"id": user_id}, "sucesso": True}, 201

    def login(self):
        data = request.get_json()
        email = data.get("email", "")
        senha = data.get("senha", "")

        if not email or not senha:
            return {"erro": "Email e senha são obrigatórios"}, 400

        user = user_model.login_user(email, senha)
        if user:
            return {"dados": user, "sucesso": True, "mensagem": "Login OK"}, 200
        return {"erro": "Email ou senha inválidos", "sucesso": False}, 401
