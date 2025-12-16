from db import get_db_connection
import random
from datetime import datetime, timedelta

def seed():
    print("--- POBLANDO BASE DE DATOS CON DATOS DE PRUEBA ---")
    conn = get_db_connection()
    if not conn:
        print("Error de conexion")
        return
    
    cursor = conn.cursor()

    # 1. Insert Perros
    perros = [
        ('Max', 'Golden Retriever', 2, 'Dorado', 'Vacuna A', 500.00),
        ('Bella', 'Bulldog Frances', 1, 'Negro', 'Vacuna B', 1200.00),
        ('Rocky', 'Pastor Aleman', 3, 'Cafe', 'Ninguno', 800.00),
        ('Luna', 'Husky', 2, 'Gris/Blanco', 'Completo', 950.00),
        ('Coco', 'Poodle', 1, 'Blanco', 'Vacuna A', 450.00)
    ]
    
    print(f"Insertando {len(perros)} perros...")
    for p in perros:
        cursor.execute(
            "INSERT INTO Perro (nombre, raza, edad, pelaje, tratamiento, precio, estado) VALUES (%s, %s, %s, %s, %s, %s, 'DISPONIBLE')",
            p
        )

    # 2. Insert Duenos
    duenos = [
        ('Juan Perez', '12345678', '555-0101', 'Av. Principal 123'),
        ('Maria Gomez', '87654321', '555-0102', 'Calle Secundaria 456')
    ]
    
    print(f"Insertando {len(duenos)} dueños...")
    for d in duenos:
        cursor.execute(
            "INSERT INTO Dueno (nombre, dni, telefono, direccion) VALUES (%s, %s, %s, %s)",
            d
        )
    
    conn.commit()

    # 3. Simulate a past sale
    print("Simulando una venta pasada...")
    cursor.execute("SELECT id_perro FROM Perro WHERE nombre = 'Coco'")
    id_perro_vendido = cursor.fetchone()[0]
    
    cursor.execute("SELECT id_dueno FROM Dueno LIMIT 1")
    id_dueno = cursor.fetchone()[0]
    
    cursor.execute("SELECT id_vendedor FROM Vendedor LIMIT 1")
    id_vendedor = cursor.fetchone()[0]

    precio = 450.00
    fecha = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute(
        "INSERT INTO Venta (fecha, id_perro, id_dueno, id_vendedor, total) VALUES (%s, %s, %s, %s, %s)",
        (fecha, id_perro_vendido, id_dueno, id_vendedor, precio)
    )
    
    cursor.execute("UPDATE Perro SET estado = 'VENDIDO' WHERE id_perro = %s", (id_perro_vendido,))
    
    conn.commit()
    conn.close()
    print("--- DB LISTA. VISTAS ACTUALIZADAS ---")

if __name__ == '__main__':
    seed()
