from flask import Flask
from db import get_db_connection
from reportlab.pdfgen import canvas
import os
import time

# Config
PDF_FOLDER = 'static/comprobantes'
os.makedirs(PDF_FOLDER, exist_ok=True)

def seed_pdfs():
    print("--- GENERANDO PDFs PARA VENTAS EXISTENTES ---")
    conn = get_db_connection()
    if not conn:
        print("Error de conexión")
        return

    cursor = conn.cursor(dictionary=True)
    
    # Buscar ventas sin comprobante
    cursor.execute("""
        SELECT v.id_venta, v.id_dueno, v.total, v.fecha 
        FROM Venta v
        LEFT JOIN Comprobante c ON v.id_venta = c.id_venta
        WHERE c.id_comprobante IS NULL
    """)
    ventas_sin_pdf = cursor.fetchall()
    
    if not ventas_sin_pdf:
        print("Todas las ventas ya tienen PDF.")
        conn.close()
        return

    print(f"Encontradas {len(ventas_sin_pdf)} ventas sin PDF. Generando...")

    cursor_insert = conn.cursor()
    
    for venta in ventas_sin_pdf:
        id_venta = venta['id_venta']
        filename = f"factura_{id_venta}.pdf"
        filepath = os.path.join(PDF_FOLDER, filename)
        
        try:
            # Generar PDF
            c = canvas.Canvas(filepath)
            c.drawString(100, 800, f"COMPROBANTE RETROACTIVO DE VENTA #{id_venta}")
            c.drawString(100, 780, "--------------------------------")
            c.drawString(100, 760, "Veterinaria Wau Wau Pet Shop")
            c.drawString(100, 740, f"Fecha original: {venta['fecha']}")
            c.drawString(100, 720, f"Total: ${venta['total']}")
            c.drawString(100, 700, "Gracias por su compra.")
            c.save()
            
            # Insertar en BD
            cursor_insert.execute(
                "INSERT INTO Comprobante (id_venta, archivo_pdf, estado) VALUES (%s, %s, %s)",
                (id_venta, filename, "COMPLETADO")
            )
            print(f"   [OK] PDF generado para Venta #{id_venta}")
            
        except Exception as e:
            print(f"   [ERROR] Venta #{id_venta}: {e}")

    conn.commit()
    conn.close()
    print("--- PROCESO TERMINADO ---")

if __name__ == '__main__':
    seed_pdfs()
