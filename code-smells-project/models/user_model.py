from database import get_db


def get_all_users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"],
            "criado_em": row["criado_em"]
        })
    return result


def get_user_by_id(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"],
            "criado_em": row["criado_em"]
        }
    return None


def login_user(email, senha):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM usuarios WHERE email = ? AND senha = ?",
        (email, senha)
    )
    row = cursor.fetchone()
    if row:
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"]
        }
    return None


def create_user(nome, email, senha, tipo="cliente"):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha, tipo)
    )
    db.commit()
    return cursor.lastrowid
