from db import get_db_connection
from reportlab.pdfgen import canvas
import os
import time

# Config
PDF_FOLDER = 'static/comprobantes'
os.makedirs(PDF_FOLDER, exist_ok=True)

def regenerate():
    print("--- REGENERANDO TODOS LOS PDFs CON NUEVO DISEÑO ---")
    conn = get_db_connection()
    if not conn: return
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT v.id_venta, v.id_perro, v.fecha, v.total, p.nombre, p.raza, p.pelaje, d.nombre as dueno 
        FROM Venta v
        JOIN Perro p ON v.id_perro = p.id_perro
        JOIN Dueno d ON v.id_dueno = d.id_dueno
    """)
    ventas = cursor.fetchall()
    
    for venta in ventas:
        id_venta = venta['id_venta']
        filename = f"factura_{id_venta}.pdf"
        filepath = os.path.join(PDF_FOLDER, filename)
        
        try:
            # Generar PDF Real usando ReportLab (Lógica duplicada para el script)
            c = canvas.Canvas(filepath)
            
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, 800, "VETERINARIA WAU WAU PET SHOP")
            c.setFont("Helvetica", 10)
            c.drawString(50, 785, "Especialistas en Caninos de Alta Gama")
            c.drawString(50, 770, "----------------------------------------------------------------")

            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, 740, f"COMPROBANTE DE VENTA #{id_venta}")
            
            c.setFont("Helvetica", 12)
            c.drawString(50, 710, f"Fecha: {venta['fecha']}")
            c.drawString(50, 690, f"Cliente: {venta['dueno']}")
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, 650, "DETALLES DEL EJEMPLAR:") # Corregido typo
            
            c.setFont("Helvetica", 12)
            c.drawString(50, 630, f"Nombre: {venta['nombre']}")
            c.drawString(50, 610, f"Raza Oficial: {venta['raza']}")
            c.drawString(50, 590, f"Pelaje: {venta['pelaje']}")
            c.drawString(50, 570, f"Precio: ${venta['total']}")

            # 4. FOTO DEL PERRO (Logica mejorada)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Intentar buscar foto específica por ID
            img_path = os.path.join(base_dir, "static", "dogs", f"{venta['id_perro']}.jpg")
            
            # Si no existe, usar placeholder
            if not os.path.exists(img_path):
                img_path = os.path.join(base_dir, "static", "dogs", "placeholder.jpg")

            if os.path.exists(img_path):
                try:
                    c.drawImage(img_path, 300, 550, width=200, height=150)
                    c.setFont("Helvetica-Oblique", 8)
                    c.drawString(300, 540, "(Imagen referencial de la raza)")
                except Exception as e:
                    print(f"   [WARN] No se pudo cargar imagen: {e}")
            
            c.setFont("Helvetica", 10)
            c.drawString(50, 450, "Gracias por su preferencia.")
            c.drawString(50, 430, "Atentamente, El Tio Chato")
            
            c.save()
            print(f"   [OK] PDF Regenerado: {filename}")
            
        except Exception as e:
            print(f"   [ERROR] Venta #{id_venta}: {e}")

    conn.close()

if __name__ == '__main__':
    regenerate()
