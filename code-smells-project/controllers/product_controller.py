from flask import request
import models.product_model as product_model

VALID_CATEGORIES = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 200


class ProductController:

    def list_products(self):
        products = product_model.get_all_products()
        return {"dados": products, "sucesso": True}, 200

    def get_product(self, product_id):
        product = product_model.get_product_by_id(product_id)
        if product:
            return {"dados": product, "sucesso": True}, 200
        return {"erro": "Produto não encontrado", "sucesso": False}, 404

    def create_product(self):
        data = request.get_json()
        errors = self._validate_product_data(data)
        if errors:
            return {"erro": errors[0]}, 400

        product_id = product_model.create_product(
            data["nome"], data.get("descricao", ""), data["preco"],
            data["estoque"], data.get("categoria", "geral")
        )
        return {"dados": {"id": product_id}, "sucesso": True, "mensagem": "Produto criado"}, 201

    def update_product(self, product_id):
        existing = product_model.get_product_by_id(product_id)
        if not existing:
            return {"erro": "Produto não encontrado"}, 404

        data = request.get_json()
        errors = self._validate_product_data(data)
        if errors:
            return {"erro": errors[0]}, 400

        product_model.update_product(
            product_id, data["nome"], data.get("descricao", ""),
            data["preco"], data["estoque"], data.get("categoria", "geral")
        )
        return {"sucesso": True, "mensagem": "Produto atualizado"}, 200

    def delete_product(self, product_id):
        product = product_model.get_product_by_id(product_id)
        if not product:
            return {"erro": "Produto não encontrado"}, 404

        product_model.delete_product(product_id)
        return {"sucesso": True, "mensagem": "Produto deletado"}, 200

    def search_products(self):
        termo = request.args.get("q", "")
        categoria = request.args.get("categoria", None)
        preco_min = request.args.get("preco_min", None)
        preco_max = request.args.get("preco_max", None)

        if preco_min:
            preco_min = float(preco_min)
        if preco_max:
            preco_max = float(preco_max)

        results = product_model.search_products(termo, categoria, preco_min, preco_max)
        return {"dados": results, "total": len(results), "sucesso": True}, 200

    def _validate_product_data(self, data):
        errors = []
        if not data:
            errors.append("Dados inválidos")
            return errors
        if "nome" not in data:
            errors.append("Nome é obrigatório")
        if "preco" not in data:
            errors.append("Preço é obrigatório")
        if "estoque" not in data:
            errors.append("Estoque é obrigatório")
        if errors:
            return errors

        nome = data["nome"]
        preco = data["preco"]
        estoque = data["estoque"]
        categoria = data.get("categoria", "geral")

        if preco < 0:
            errors.append("Preço não pode ser negativo")
        if estoque < 0:
            errors.append("Estoque não pode ser negativo")
        if len(nome) < MIN_NAME_LENGTH:
            errors.append("Nome muito curto")
        if len(nome) > MAX_NAME_LENGTH:
            errors.append("Nome muito longo")
        if categoria not in VALID_CATEGORIES:
            errors.append(f"Categoria inválida. Válidas: {VALID_CATEGORIES}")

        return errors
