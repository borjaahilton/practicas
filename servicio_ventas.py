from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
import requests
import threading
import time
import os
from reportlab.pdfgen import canvas
from db import get_db_connection
# Import logic from original app just for dependencies, but we are rewriting the routes here.
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_key_microservice'

# URL del otro microservicio
SERVICIO_PERROS_URL = "http://127.0.0.1:5001/api/perro"

# Crear carpeta para PDFs si no existe
PDF_FOLDER = 'static/comprobantes'
os.makedirs(PDF_FOLDER, exist_ok=True)

# --- TAREA ASÍNCRONA (Req 3) ---
def generar_comprobante_pdf_async(id_venta):
    print(f"   [Async] Iniciando generación PDF Venta {id_venta}...")
    
    # Retry mechanism: Intentar obtener datos hasta 3 veces
    venta_data = None
    for attempt in range(3):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT v.id_venta, v.fecha, v.total, p.id_perro, p.nombre, p.raza, p.pelaje, d.nombre as dueno 
                FROM Venta v
                JOIN Perro p ON v.id_perro = p.id_perro
                JOIN Dueno d ON v.id_dueno = d.id_dueno
                WHERE v.id_venta = %s
            """, (id_venta,))
            venta_data = cursor.fetchone()
            conn.close()
            
            if venta_data:
                break # Datos encontrados
        
        time.sleep(1) # Esperar 1s antes de reintentar

    if not venta_data:
        print(f"   [Async] Error: Imposible obtener datos para venta {id_venta} tras reintentos.")
        return

    try:
        # Generar PDF Real usando ReportLab
        filename = f"factura_{id_venta}.pdf"
        filepath = os.path.join(PDF_FOLDER, filename)
        
        c = canvas.Canvas(filepath)
        
        # 1. Cabecera
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 800, "VETERINARIA WAU WAU PET SHOP")
        c.setFont("Helvetica", 10)
        c.drawString(50, 785, "Especialistas en Caninos de Alta Gama")
        c.drawString(50, 770, "----------------------------------------------------------------")

        # 2. Datos de la Venta
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 740, f"COMPROBANTE DE VENTA #{id_venta}")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, 710, f"Fecha: {venta_data['fecha']}")
        c.drawString(50, 690, f"Cliente: {venta_data['dueno']}")
        
        # 3. Datos del Perro (El "Producto")
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 650, "DETALLES DEL EJEMPLAR:")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, 630, f"Nombre: {venta_data['nombre']}")
        c.drawString(50, 610, f"Raza Oficial: {venta_data['raza']}")
        c.drawString(50, 590, f"Pelaje: {venta_data['pelaje']}")
        c.drawString(50, 570, f"Precio: ${venta_data['total']}")

        # 4. FOTO DEL PERRO
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Intentar buscar foto específica por ID
        img_path = os.path.join(base_dir, "static", "dogs", f"{venta_data['id_perro']}.jpg")
        
        # Si no existe, usar placeholder
        if not os.path.exists(img_path):
            img_path = os.path.join(base_dir, "static", "dogs", "placeholder.jpg")
        
        # FIX: Usar ruta absoluta para evitar errores de "file not found" en reportlab
        
        if os.path.exists(img_path):
            try:
                c.drawImage(img_path, 300, 550, width=200, height=150)
                c.setFont("Helvetica-Oblique", 8)
                c.drawString(300, 540, "(Imagen referencial de la raza)")
            except Exception as img_err:
                 print(f"   [Async] Warning: No se pudo cargar la imagen: {img_err}")
        
        # 5. Pie de página
        c.setFont("Helvetica", 10)
        c.drawString(50, 450, "Gracias por su preferencia.")
        c.drawString(50, 430, "Atentamente, El Tio Chato")
        
        c.save()
        
        # Actualizar estado en BD
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            # Crear registro de comprobante si no estuviere, o actualizar
            cursor.execute("INSERT INTO Comprobante (id_venta, archivo_pdf, estado) VALUES (%s, %s, %s)", 
                           (id_venta, filename, "COMPLETADO"))
            conn.commit()
            conn.close()
            print(f"   [Async] PDF Generado exitosamente en: {filepath}")
    except Exception as e:
        print(f"   [Async] Error generando PDF: {e}")

# --- RUTAS ---
@app.route('/descargar_pdf/<filename>')
def descargar_pdf(filename):
    return send_from_directory(PDF_FOLDER, filename, as_attachment=True)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        
        conn = get_db_connection()
        user = None
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM Vendedor WHERE usuario = %s', (usuario,))
            user = cursor.fetchone()
            conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id_vendedor']
            session['user_name'] = user['nombre']
            return redirect(url_for('dashboard'))
        flash('Credenciales inválidas')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    # Reutilizamos la lógica del dashboard original
    stats = {'dogs': 0, 'sales': 0, 'clients': 0, 'vaccines': 0}
    recent_sales = []
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM Perro WHERE estado = 'DISPONIBLE'")
        stats['dogs'] = cursor.fetchone()['count']
        cursor.execute("SELECT COALESCE(SUM(total), 0) as total FROM Venta")
        stats['sales'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as count FROM Dueno")
        stats['clients'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Vacuna")
        stats['vaccines'] = cursor.fetchone()['count']

        # Fetch Available Dogs for Quick Sale
        cursor.execute("SELECT * FROM Perro WHERE estado = 'DISPONIBLE' LIMIT 5")
        available_dogs = cursor.fetchall()

        # Fetch Recent Sales with PDF Status
        cursor.execute("""
            SELECT v.id_venta, d.nombre as dueno, v.fecha, v.total, c.archivo_pdf, c.estado as estado_pdf
            FROM Venta v 
            JOIN Dueno d ON v.id_dueno = d.id_dueno 
            LEFT JOIN Comprobante c ON v.id_venta = c.id_venta
            ORDER BY v.fecha DESC LIMIT 5
        """)
        recent_sales = cursor.fetchall()
        conn.close()

    return render_template('dashboard.html', user_name=session['user_name'], stats=stats, sales=recent_sales, dogs=available_dogs)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/database')
def database_view():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    data = {}
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Fetch all tables
        tables = ['Perro', 'Dueno', 'Venta', 'Vacuna', 'Vendedor']
        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            data[table] = cursor.fetchall()
            
        conn.close()
    
    return render_template('database_view.html', tables=data)

    return render_template('database_view.html', tables=data)

@app.route('/agregar_perro', methods=['GET', 'POST'])
def agregar_perro():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        # Recolectar datos del form
        nuevo_perro = {
            'nombre': request.form['nombre'],
            'raza': request.form['raza'],
            'edad': request.form['edad'],
            'pelaje': request.form['pelaje'],
            'tratamiento': request.form['tratamiento'] or 'Ninguno',
            'precio': request.form['precio']
        }
        
        # Enviar al MICROSERVICIO PERROS (POST)
        try:
            response = requests.post(f"{SERVICIO_PERROS_URL}", json=nuevo_perro)
            if response.status_code == 201:
                data_resp = response.json()
                new_id = data_resp.get('id_perro')
                
                # Guardar Imagen si se subió
                file = request.files.get('imagen')
                if file and new_id:
                    filename = f"{new_id}.jpg"
                    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "dogs", filename)
                    file.save(filepath)
                
                # CHEQUEAR SI SE SALECCIONO UN CLIENTE (VENTA INMEDIATA)
                id_cliente_venta = request.form.get('id_cliente_venta')
                if id_cliente_venta and id_cliente_venta != "":
                    print(f"   [Venta Inmediata] Procesando venta para Cliente {id_cliente_venta}...")
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        # Registrar Venta
                        cursor.execute("INSERT INTO Venta (id_perro, id_dueno, id_vendedor, total) VALUES (%s, %s, %s, %s)", 
                                       (new_id, id_cliente_venta, session['user_id'], nuevo_perro['precio']))
                        id_venta = cursor.lastrowid
                        
                        # Actualizar estado perro a VENDIDO
                        cursor.execute("UPDATE Perro SET estado = 'VENDIDO' WHERE id_perro = %s", (new_id,))
                        conn.commit()
                        conn.close()
                        
                        # Lanzar PDF Async
                        if id_venta:
                            hilo_pdf = threading.Thread(target=generar_comprobante_pdf_async, args=(id_venta,))
                            hilo_pdf.start()
                            flash('Perro registrado y VENDIDO exitosamente! Generando factura...')
                            return redirect(url_for('dashboard'))

                flash('Perro registrado exitosamente en inventario.')
                return redirect(url_for('dashboard'))
            else:
                flash('Error al registrar perro en el microservicio.')
        except requests.exceptions.ConnectionError:
            flash('Error: El servicio de Perros no está respondiendo.')
            
    # GET: Obtener clientes para el dropdown
    clients = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_dueno, nombre FROM Dueno")
        clients = cursor.fetchall()
        conn.close()

    return render_template('add_dog.html', clients=clients)

@app.route('/agregar_cliente', methods=['GET', 'POST'])
def agregar_cliente():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        nombre = request.form['nombre']
        dni = request.form['dni']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            id_dueno_nuevo = None
            try:
                cursor.execute("INSERT INTO Dueno (nombre, dni, telefono, direccion) VALUES (%s, %s, %s, %s)", 
                               (nombre, dni, telefono, direccion))
                conn.commit()
                id_dueno_nuevo = cursor.lastrowid
                flash(f'Cliente {nombre} registrado exitosamente!')
            except Exception as e:
                flash(f'Error al registrar cliente: {e}')
            conn.close()
            
            # Si se creó, retornar a la vista de base de datos
            return redirect(url_for('database_view'))

    return render_template('add_client.html')

# --- VENTA (Req 2: Consumir API Perros) ---
@app.route('/procesar_venta_demo/<int:id_perro>')
def procesar_venta_demo(id_perro):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    print(f"[Microservicio Ventas] Iniciando venta para Perro {id_perro}")
    
    # 1. LLAMADA API A MICROSERVICIO A
    try:
        response = requests.get(f"{SERVICIO_PERROS_URL}/{id_perro}")
        if response.status_code != 200:
            flash('Error: No se pudo consultar el servicio de perros.')
            return redirect(url_for('dashboard'))
        
        data_perro = response.json()
        print(f"[Microservicio Ventas] Datos del perro recibidos: {data_perro['nombre']} ({data_perro['raza']})")
        
        # Validar disponibilidad
        if data_perro['estado'] != 'DISPONIBLE':
             flash('Error: El perro ya no está disponible.')
             return redirect(url_for('dashboard'))

    except Exception as e:
        flash(f'Error: Servicio de Perros no disponible ({e})')
        return redirect(url_for('dashboard'))

    # 2. Registrar Venta en BD Local
    id_venta = None
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        # Insertar venta dummy (usando ID dueño 1 y vendedor actual)
        cursor.execute("INSERT INTO Venta (id_perro, id_dueno, id_vendedor, total) VALUES (%s, 1, %s, %s)", 
                       (id_perro, session['user_id'], data_perro['precio']))
        id_venta = cursor.lastrowid
        
        # Actualizar estado perro
        cursor.execute("UPDATE Perro SET estado = 'VENDIDO' WHERE id_perro = %s", (id_perro,))
        conn.commit()
        conn.close()

    if id_venta:
        # 3. LANZAR TAREA ASÍNCRONA (Req 3)
        # No esperamos a que termine, respondemos al usuario YA.
        hilo_pdf = threading.Thread(target=generar_comprobante_pdf_async, args=(id_venta,))
        hilo_pdf.start()
        
        flash(f"Venta registrada exitosamente para {data_perro['nombre']}. El comprobante se está generando.")
        return redirect(url_for('dashboard'))
    
    flash('Error crítico al guardar la venta.')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    print("Iniciando Servicio de Ventas en puerto 5002...")
    app.run(port=5002, debug=True)
