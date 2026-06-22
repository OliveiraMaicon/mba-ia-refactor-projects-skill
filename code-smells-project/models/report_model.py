from database import get_db


def get_sales_report():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM pedidos")
    total_pedidos = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM pedidos")
    faturamento = cursor.fetchone()[0]
    if faturamento is None:
        faturamento = 0

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'")
    pendentes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'")
    aprovados = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'")
    cancelados = cursor.fetchone()[0]

    HIGH_REVENUE_THRESHOLD = 10000
    MID_REVENUE_THRESHOLD = 5000
    LOW_REVENUE_THRESHOLD = 1000

    desconto = 0
    if faturamento > HIGH_REVENUE_THRESHOLD:
        desconto = faturamento * 0.1
    elif faturamento > MID_REVENUE_THRESHOLD:
        desconto = faturamento * 0.05
    elif faturamento > LOW_REVENUE_THRESHOLD:
        desconto = faturamento * 0.02

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0
    }
