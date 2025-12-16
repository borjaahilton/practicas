from db import get_db_connection

def check_status():
    print("--- CHECKING LAST 5 SALES ---")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT v.id_venta, v.fecha, c.archivo_pdf, c.estado
        FROM Venta v
        LEFT JOIN Comprobante c ON v.id_venta = c.id_venta
        ORDER BY v.id_venta DESC
        LIMIT 5
    """)
    sales = cursor.fetchall()
    
    for s in sales:
        print(f"#{s['id_venta']} | {s['estado']}")

    conn.close()

if __name__ == "__main__":
    check_status()
