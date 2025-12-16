import init_db
from app import app, create_admin_user

def main():
    print("--- INICIANDO SISTEMA VETERINARIA ---")
    
    # 1. Initialize Database
    print("[1/3] Verificando base de datos...")
    if init_db.create_database():
        init_db.create_tables()
        print("      Base de datos OK.")
    else:
        print("      Error al inicializar base de datos. Verifique conexión.")
        return

    # 2. Check/Create Admin User
    print("[2/3] Verificando usuario administrador...")
    create_admin_user()
    
    # 3. Start Server
    print("[3/3] Iniciando servidor web...")
    print("      Acceda a: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)

if __name__ == '__main__':
    main()
