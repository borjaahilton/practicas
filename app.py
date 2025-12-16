from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection
import functools

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key for production

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM Vendedor WHERE usuario = %s', (usuario,))
            user = cursor.fetchone()
            conn.close()

            if user and check_password_hash(user['password'], password):
                session.clear()
                session['user_id'] = user['id_vendedor']
                session['user_name'] = user['nombre']
                return redirect(url_for('dashboard'))
            
            flash('Usuario o contraseña incorrectos.')
        else:
            flash('Error de conexión a la base de datos.')

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'dogs': 0,
        'sales': 0,
        'clients': 0,
        'vaccines': 0
    }
    recent_sales = []

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Fetch Stats
        cursor.execute("SELECT COUNT(*) as count FROM Perro WHERE estado = 'DISPONIBLE'")
        stats['dogs'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COALESCE(SUM(total), 0) as total FROM Venta")
        stats['sales'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as count FROM Dueno")
        stats['clients'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Vacuna")
        stats['vaccines'] = cursor.fetchone()['count']

        # Fetch Recent Sales
        cursor.execute("""
            SELECT v.id_venta, d.nombre as dueno, v.fecha, v.total 
            FROM Venta v 
            JOIN Dueno d ON v.id_dueno = d.id_dueno 
            ORDER BY v.fecha DESC LIMIT 5
        """)
        recent_sales = cursor.fetchall()
        
        conn.close()

    return render_template('dashboard.html', user_name=session.get('user_name', 'Usuario'), stats=stats, sales=recent_sales)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def create_admin_user():
    """Creates a default admin user if none exists."""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Vendedor LIMIT 1')
            if not cursor.fetchone():
                # No users exist, create default admin
                hashed_password = generate_password_hash('admin123')
                cursor.execute(
                    'INSERT INTO Vendedor (nombre, usuario, password) VALUES (%s, %s, %s)',
                    ('Administrador', 'admin', hashed_password)
                )
                conn.commit()
                print("Default admin user created: admin / admin123")
            conn.close()
    except Exception as e:
        print(f"Error creating default user: {e}")

if __name__ == '__main__':
    # Ensure tables exist (simple call to the init script logic or just rely on manual run)
    # For now, we assume init_db.py has been run. 
    # Attempt to create a default admin user for convenience
    create_admin_user()
    
    app.run(debug=True, port=5000)
