import subprocess
import time

def main():
    print("--- INICIANDO ARQUITECTURA DE MICROSERVICIOS ---")
    
    print("[1/2] Iniciando Microservicio 'PERROS' (Puerto 5001)...")
    # Launch in independent process
    proc_perros = subprocess.Popen(['python', 'servicio_perros.py'], shell=True)
    
    time.sleep(2) # Wait for it to initialize
    
    print("[2/2] Iniciando Microservicio 'VENTAS' (Puerto 5002)...")
    print("      Este es tu nuevo punto de entrada para el usuario.")
    
    try:
        # Launch Sales service foreground (or background)
        # We'll run it directly here to keep the window open for this one
        subprocess.run(['python', 'servicio_ventas.py'], shell=True)
    except KeyboardInterrupt:
        print("\nDeteniendo servicios...")
        proc_perros.terminate()

if __name__ == '__main__':
    main()
