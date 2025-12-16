import mysql.connector
from db import get_db_connection

def check():
    print("--- DIAGNÓSTICO DE CONEXIÓN ---")
    
    # 1. Test Connection
    print("1. Intentando conectar...")
    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            print("   [OK] Conexión exitosa a MySQL.")
            print(f"   Host: localhost, User: root, DB: veterinaria")
        else:
            print("   [ERROR] No se pudo conectar via get_db_connection().")
            return
    except Exception as e:
        print(f"   [FATAL] Excepción al conectar: {e}")
        return

    # 2. Check Tables
    print("\n2. Verificando tablas existentes...")
    expected_tables = ['Perro', 'Vacuna', 'Dueno', 'Vendedor', 'Venta', 'Comprobante']
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    existing_tables = [table[0] for table in cursor.fetchall()]
    
    missing = []
    for table in expected_tables:
        if table.lower() in [t.lower() for t in existing_tables]:
             print(f"   [OK] Tabla encontrada: {table}")
        else:
             print(f"   [FALTA] Tabla NO encontrada: {table}")
             missing.append(table)
    
    if missing:
        print(f"\n[ATENCIÓN] Faltan {len(missing)} tablas. Ejecuta init_db.py nuevamente.")
    else:
        print("\n[OK] Todas las tablas requeridas existen.")

    conn.close()

if __name__ == '__main__':
    check()
