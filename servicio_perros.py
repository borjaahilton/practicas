from flask import Flask, jsonify, request
from db import get_db_connection

app = Flask(__name__)

# --- MICROSERVICIO A: Módulo Perro ---
# Responsabilidad: Data técnica del perro

@app.route('/api/perro/<int:id_perro>', methods=['GET'])
def get_perro(id_perro):
    print(f"[Microservicio Perros] Recibida solicitud para ID: {id_perro}")
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Perro WHERE id_perro = %s", (id_perro,))
        perro = cursor.fetchone()
        conn.close()
        
        if perro:
            # Simular "foto"
            perro['foto_url'] = f"/static/dogs/{id_perro}.jpg"
            return jsonify(perro)
        else:
            return jsonify({'error': 'Perro no encontrado'}), 404
    return jsonify({'error': 'Error de BD'}), 500

@app.route('/api/perro', methods=['POST'])
def create_perro():
    data = request.json
    print(f"[Microservicio Perros] Creando nuevo perro: {data.get('nombre')}")
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "INSERT INTO Perro (nombre, raza, edad, pelaje, tratamiento, precio, estado) VALUES (%s, %s, %s, %s, %s, %s, 'DISPONIBLE')"
        values = (data['nombre'], data['raza'], data['edad'], data['pelaje'], data['tratamiento'], data['precio'])
        
        try:
            cursor.execute(query, values)
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return jsonify({'id_perro': new_id, 'message': 'Perro creado exitosamente'}), 201
        except Exception as e:
            conn.close()
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Error de conexión'}), 500

if __name__ == '__main__':
    print("Iniciando Servicio de Perros en puerto 5001...")
    app.run(port=5001, debug=True)
