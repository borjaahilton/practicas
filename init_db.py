import mysql.connector
from mysql.connector import Error

def create_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='' 
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS veterinaria")
            print("Database 'veterinaria' created or already exists.")
            return True
    except Error as e:
        print(f"Error creating database: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def create_tables():
    commands = [
        """
        CREATE TABLE IF NOT EXISTS Perro (
            id_perro INT PRIMARY KEY AUTO_INCREMENT,
            nombre VARCHAR(50),
            raza VARCHAR(50) NOT NULL,
            edad INT,
            pelaje VARCHAR(50),
            tratamiento TEXT,
            precio DECIMAL(10,2) NOT NULL,
            estado VARCHAR(20) DEFAULT 'DISPONIBLE'
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Vacuna (
            id_vacuna INT PRIMARY KEY AUTO_INCREMENT,
            nombre VARCHAR(50),
            fecha DATE,
            id_perro INT,
            FOREIGN KEY (id_perro) REFERENCES Perro(id_perro)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Dueno (
            id_dueno INT PRIMARY KEY AUTO_INCREMENT,
            nombre VARCHAR(100),
            dni VARCHAR(15),
            telefono VARCHAR(20),
            direccion VARCHAR(150)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Vendedor (
            id_vendedor INT PRIMARY KEY AUTO_INCREMENT,
            nombre VARCHAR(100),
            usuario VARCHAR(50),
            password VARCHAR(255)  -- Increased length for hashed passwords
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Venta (
            id_venta INT PRIMARY KEY AUTO_INCREMENT,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            id_perro INT,
            id_dueno INT,
            id_vendedor INT,
            total DECIMAL(10,2),
            FOREIGN KEY (id_perro) REFERENCES Perro(id_perro),
            FOREIGN KEY (id_dueno) REFERENCES Dueno(id_dueno),
            FOREIGN KEY (id_vendedor) REFERENCES Vendedor(id_vendedor)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Comprobante (
            id_comprobante INT PRIMARY KEY AUTO_INCREMENT,
            id_venta INT,
            archivo_pdf VARCHAR(200),
            estado VARCHAR(20) DEFAULT 'GENERANDO',
            FOREIGN KEY (id_venta) REFERENCES Venta(id_venta)
        );
        """
    ]

    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='veterinaria',
            user='root',
            password=''
        )
        if connection.is_connected():
            cursor = connection.cursor()
            for command in commands:
                cursor.execute(command)
            
            # Create a default admin user if not exists
            # We will handle password hashing in the app, but inserting a raw one for initial setup test if needed,
            # BUT better to rely on the app to create it or insert a known hashed one.
            # For simplicity let's just create tables.
            
            print("Tables created successfully.")
    except Error as e:
        print(f"Error creating tables: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    if create_database():
        create_tables()
