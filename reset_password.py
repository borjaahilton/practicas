from db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

def fix_admin():
    conn = get_db_connection()
    if not conn:
        print("Error: No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()
    
    try:
        # 1. Check table structure for password column length
        cursor.execute("DESCRIBE Vendedor")
        columns = cursor.fetchall()
        pass_col_type = next((col[1] for col in columns if col[0] == 'password'), '')
        
        print(f"Tipo de columna 'password' actual: {pass_col_type}")
        
        # If varchar is small (e.g. 100), alter it to 255 just in case
        if 'varchar(100)' in pass_col_type.lower():
            print("Ampliando columna password a VARCHAR(255)...")
            cursor.execute("ALTER TABLE Vendedor MODIFY COLUMN password VARCHAR(255)")
            conn.commit()

        # 2. Reset Admin User
        print("Reseteando usuario 'admin'...")
        cursor.execute("DELETE FROM Vendedor WHERE usuario = 'admin'")
        conn.commit()

        new_pass_hash = generate_password_hash('admin123')
        
        cursor.execute(
            'INSERT INTO Vendedor (nombre, usuario, password) VALUES (%s, %s, %s)',
            ('Administrador', 'admin', new_pass_hash)
        )
        conn.commit()
        
        print("\n=== ÉXITO ===")
        print("Usuario: admin")
        print("Password: admin123")
        print("Intenta ingresar nuevamente.")
        
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_admin()
