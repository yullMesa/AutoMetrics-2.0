import sqlite3

def crear_base_datos(self):
    # Conectamos a la base de datos (se creará el archivo si no existe)
    conn = sqlite3.connect("ingenieria.db")
    cursor = conn.cursor()
    
    # Creamos la tabla con las columnas exactas de tu diseño
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requisitos (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            peticion TEXT,
            prioridad TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print("Base de datos verificada y lista.")

if __name__ == "__main__":
    crear_base_datos()