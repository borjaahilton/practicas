import threading
import time
import random

# Simulación de Base de Datos (Memoria Compartida)
# En un caso real, esto sería la fila en la BD, protegida por transacciones.
inventario_db = {
    'id_perro_1': {
        'raza': 'Rottweiler',
        'precio': 1000.00,
        'estado': 'DISPONIBLE'
    }
}

# Candado (Lock) para controlar el acceso concurrente
candado_venta = threading.Lock()

def intento_venta(vendedor, id_perro, precio_oferta):
    global inventario_db
    
    print(f"[{vendedor}] Intentando vender perro {id_perro} a ${precio_oferta}...")
    
    # --- INICIO DE LA SECCIÓN CRÍTICA ---
    with candado_venta:
        print(f"[{vendedor}] <BLOQUEO ADQUIRIDO> Revisando inventario...")
        time.sleep(1) # Simular latencia de red/BD
        
        perro = inventario_db.get(id_perro)
        
        if not perro:
            print(f"[{vendedor}] Error: Perro no existe.")
            return

        if perro['estado'] != 'DISPONIBLE':
            print(f"[{vendedor}] Error: El perro YA FUE VENDIDO a otro cliente.")
        elif precio_oferta < perro['precio']:
            print(f"[{vendedor}] Error: Precio ${precio_oferta} es muy bajo. Mínimo: ${perro['precio']}")
        else:
            print(f"[{vendedor}] ¡VENTA EXITOSA! Procesando...")
            perro['estado'] = 'VENDIDO'
            # Aquí se registraría en la BD real
            print(f"[{vendedor}] Estado actualizado a VENDIDO.")
            
    # --- FIN DE LA SECCIÓN CRÍTICA ---
    print(f"[{vendedor}] Operación finalizada.\n")

if __name__ == "__main__":
    print("--- INICIO DE SIMULACIÓN DE CONCURRENCIA ---\n")
    print("Estado Inicial:", inventario_db)
    print("-" * 50)

    # Crear hilos simulando 2 vendedores al mismo tiempo
    # Vendedor A trata de venderlo al precio correcto
    hilo_vendedor_a = threading.Thread(target=intento_venta, args=("Vendedor A", "id_perro_1", 1000))
    
    # Vendedor B trata de venderlo (quizás más barato o al mismo tiempo)
    hilo_vendedor_b = threading.Thread(target=intento_venta, args=("Vendedor B", "id_perro_1", 1000))

    # Iniciar hilos
    hilo_vendedor_a.start()
    hilo_vendedor_b.start()

    # Esperar a que terminen
    hilo_vendedor_a.join()
    hilo_vendedor_b.join()

    print("-" * 50)
    print("Estado Final:", inventario_db)
    print("\n--- FIN DE SIMULACIÓN ---")
