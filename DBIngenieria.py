import sqlite3

def crear_base_datos():
    # Se crea el archivo si no existe
    conexion = sqlite3.connect("ingenieria.db")
    cursor = conexion.cursor()
    
    # Creamos la tabla para el Aseguramiento de Calidad
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inspecciones (
            id_prueba INTEGER PRIMARY KEY,
            persona TEXT NOT NULL,
            criterio TEXT NOT NULL,
            descripcion TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conexion.commit()
    conexion.close()
    print("Base de datos 'ingenieria' creada exitosamente.")

if __name__ == "__main__":
    crear_base_datos()