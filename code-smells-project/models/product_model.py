from database import get_db


def get_all_products():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "nome": row["nome"],
            "descricao": row["descricao"],
            "preco": row["preco"],
            "estoque": row["estoque"],
            "categoria": row["categoria"],
            "ativo": row["ativo"],
            "criado_em": row["criado_em"]
        })
    return result


def get_product_by_id(product_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    if row:
        return {
            "id": row["id"],
            "nome": row["nome"],
            "descricao": row["descricao"],
            "preco": row["preco"],
            "estoque": row["estoque"],
            "categoria": row["categoria"],
            "ativo": row["ativo"],
            "criado_em": row["criado_em"]
        }
    return None


def create_product(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria)
    )
    db.commit()
    return cursor.lastrowid


def update_product(product_id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, product_id)
    )
    db.commit()
    return True


def delete_product(product_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
    db.commit()
    return True


def search_products(termo, categoria=None, preco_min=None, preco_max=None):
    db = get_db()
    cursor = db.cursor()

    conditions = []
    params = []

    if termo:
        conditions.append("(nome LIKE ? OR descricao LIKE ?)")
        params.extend([f"%{termo}%", f"%{termo}%"])
    if categoria:
        conditions.append("categoria = ?")
        params.append(categoria)
    if preco_min is not None:
        conditions.append("preco >= ?")
        params.append(preco_min)
    if preco_max is not None:
        conditions.append("preco <= ?")
        params.append(preco_max)

    query = "SELECT * FROM produtos"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "nome": row["nome"],
            "descricao": row["descricao"],
            "preco": row["preco"],
            "estoque": row["estoque"],
            "categoria": row["categoria"],
            "ativo": row["ativo"],
            "criado_em": row["criado_em"]
        })
    return result
