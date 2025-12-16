from db import get_db_connection
from reportlab.pdfgen import canvas
import os
import time

def debug_pending():
    print("--- DEBUGGING PENDING PDFS ---")
    conn = get_db_connection()
    if not conn: return
    
    cursor = conn.cursor(dictionary=True)
    # Fetch sales where PDF status is NOT 'COMPLETADO' or doesn't exist
    cursor.execute("""
        SELECT v.id_venta, v.id_perro, v.fecha, v.total, p.nombre, p.raza, p.pelaje, d.nombre as dueno 
        FROM Venta v
        JOIN Perro p ON v.id_perro = p.id_perro
        JOIN Dueno d ON v.id_dueno = d.id_dueno
        LEFT JOIN Comprobante c ON v.id_venta = c.id_venta
        WHERE c.estado IS NULL OR c.estado != 'COMPLETADO'
    """)
    pending_sales = cursor.fetchall()
    
    print(f"Found {len(pending_sales)} pending sales.")
    
    for venta in pending_sales:
        id_venta = venta['id_venta']
        print(f"\nProcessing Sale #{id_venta} (Dog ID: {venta['id_perro']})...")
        
        try:
            filename = f"factura_{id_venta}.pdf"
            base_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(base_dir, "static", "comprobantes", filename)
            
            print(f"Target path: {filepath}")
            
            c = canvas.Canvas(filepath)

            # 1. Cabecera (Profesional)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, 800, "VETERINARIA WAU WAU PET SHOP")
            c.setFont("Helvetica", 10)
            c.drawString(50, 785, "Especialistas en Caninos de Alta Gama")
            c.drawString(50, 770, "----------------------------------------------------------------")

            # 2. Datos de la Venta
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, 740, f"COMPROBANTE DE VENTA #{id_venta}")
            
            c.setFont("Helvetica", 12)
            c.drawString(50, 710, f"Fecha: {venta['fecha']}")
            c.drawString(50, 690, f"Cliente: {venta['dueno']}")
            
            # 3. Datos del Perro
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, 650, "DETALLES DEL EJEMPLAR:")
            
            c.setFont("Helvetica", 12)
            c.drawString(50, 630, f"Nombre: {venta['nombre']}")
            c.drawString(50, 610, f"Raza Oficial: {venta['raza']}")
            c.drawString(50, 590, f"Pelaje: {venta['pelaje']}")
            c.drawString(50, 570, f"Precio: ${venta['total']}")

            # 4. FOTO DEL PERRO
            img_filename = f"{venta['id_perro']}.jpg"
            img_path = os.path.join(base_dir, "static", "dogs", img_filename)
            
            if os.path.exists(img_path):
                c.drawImage(img_path, 300, 550, width=200, height=150)
                c.setFont("Helvetica-Oblique", 8)
                c.drawString(300, 540, "(Imagen referencial de la raza)")
            else:
                placeholder = os.path.join(base_dir, "static", "dogs", "placeholder.jpg")
                if os.path.exists(placeholder):
                    c.drawImage(placeholder, 300, 550, width=200, height=150)
            
            # 5. Pie de página
            c.setFont("Helvetica", 10)
            c.drawString(50, 450, "Gracias por su preferencia.")
            c.drawString(50, 430, "Atentamente, El Tio Chato")
            
            c.save()
            print("PDF Saved Successfully.")
            
            # Update DB
            cursor2 = conn.cursor()
            cursor2.execute("INSERT INTO Comprobante (id_venta, archivo_pdf, estado) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE estado='COMPLETADO'", (id_venta, filename, "COMPLETADO"))
            conn.commit()
            print("Database updated.")
            
        except Exception as e:
            print(f"!!! CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()

    conn.close()

if __name__ == '__main__':
    debug_pending()
