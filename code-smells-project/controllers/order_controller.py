from flask import request
import models.order_model as order_model

VALID_ORDER_STATUSES = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


class OrderController:

    def create_order(self):
        data = request.get_json()
        if not data:
            return {"erro": "Dados inválidos"}, 400

        usuario_id = data.get("usuario_id")
        itens = data.get("itens", [])

        if not usuario_id:
            return {"erro": "Usuario ID é obrigatório"}, 400
        if not itens or len(itens) == 0:
            return {"erro": "Pedido deve ter pelo menos 1 item"}, 400

        result = order_model.create_order(usuario_id, itens)
        if "erro" in result:
            return {"erro": result["erro"], "sucesso": False}, 400

        return {
            "dados": result,
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso"
        }, 201

    def list_user_orders(self, usuario_id):
        orders = order_model.get_orders_by_user(usuario_id)
        return {"dados": orders, "sucesso": True}, 200

    def list_all_orders(self):
        orders = order_model.get_all_orders()
        return {"dados": orders, "sucesso": True}, 200

    def update_order_status(self, pedido_id):
        data = request.get_json()
        novo_status = data.get("status", "")

        if novo_status not in VALID_ORDER_STATUSES:
            return {"erro": "Status inválido"}, 400

        order_model.update_order_status(pedido_id, novo_status)
        return {"sucesso": True, "mensagem": "Status atualizado"}, 200
