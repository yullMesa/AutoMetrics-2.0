import sys
import os
# Importamos los componentes necesarios directamente del módulo QtWidgets
from PySide6.QtWidgets import (QApplication, QDialog, QMainWindow, QVBoxLayout, 
                               )

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import sqlite3
from collections import Counter
import recursos_rc
from Ingenieria import VentanaIngenieria
from Gestion import VentanaGestion # Importamos la lógica que haremos ahora
from Rendimiento import RendimientoMercado
from Innovacionytecnologia import InnovacionWidget
import sqlite3
import datetime
from Comprar import Comprar



class VentanaInicio(QDialog):
    def __init__(self):
        super().__init__()
        
        # 1. Cargar el archivo .ui
        loader = QUiLoader()
        ui_file = QFile("Inicio.ui") # Verifica que el nombre sea exacto
        
        if not ui_file.open(QFile.ReadOnly):
            print(f"No se pudo abrir el archivo .ui")
            return

        # 2. Cargar la UI. 
        # Importante: No pasamos 'self' como segundo argumento aquí para manejarlo manualmente
        self.ui = loader.load(ui_file)
        ui_file.close()
        
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-gpu-rasterization --ignore-gpu-blocklist --disable-web-security"

        if self.ui:
            # 3. CREAR UN LAYOUT para que la interfaz no salga en blanco
            # Esto "pega" el contenido del .ui a los bordes de tu ventana QDialog
            layout = QVBoxLayout(self)
            layout.addWidget(self.ui)
            layout.setContentsMargins(0, 0, 0, 0) # Quita bordes blancos extra
            
            # Ajustar el tamaño de la ventana al tamaño que definiste en Qt Designer
            self.resize(self.ui.size())
            self.setWindowTitle("AutoMetrics 2.0")
            
            # Conectamos el botón
            self.ui.toolIngenieria.clicked.connect(self.abrir_ingenieria)

            self.ui.toolGestion.clicked.connect(self.abrir_gestion_valor)

            self.ui.toolRendimiento.clicked.connect(self.Abrir_rendimiento)

            self.ui.toolInnovacion.clicked.connect(self.abrir_innovacion)

            self.ui.toolComprar.clicked.connect(self.abrir_Comprar)

            #self.respaldo_automatico_inicio()
            #self.reset_sistema_versiones() activar cuando se necesita reiniciar la base de datos


                

    def abrir_ingenieria(self):
        # Creamos la instancia del QMainWindow
        self.nueva_ventana = VentanaIngenieria()
        self.nueva_ventana.show()
        # Cerramos el diálogo de inicio
        self.close()


    
    def abrir_gestion_valor(self):
        try:
            # Aquí enviamos el objeto VentanaInicio (self)
            self.ventana_gestion = VentanaGestion(self) 
            self.ventana_gestion.show()
            self.hide()
        except Exception as e:
            # Esto te dirá si el error cambió a otro tipo
            print(f"Error detectado: {e}")


    def Abrir_rendimiento(self):
        try:
   
            self.ventana_gestion = RendimientoMercado(self) 
            self.ventana_gestion.show()
            self.hide()
        except Exception as e:
            # Esto te dirá si el error cambió a otro tipo
            print(f"Error detectado: {e}")

    # En App.py, dentro de tu función del botón toolInnovacion
    def abrir_innovacion(self):
        try:
            
            # Instanciar y guardar como atributo de clase para que no desaparezca de memoria
            self.ventana_gestion = InnovacionWidget() 
            self.ventana_gestion.show()
            self.hide()
            
            # No ocultes la principal todavía hasta confirmar que la otra abrió
            # self.hide() 
            
        except Exception as e:
            print(f"Error al intentar abrir Innovación: {e}")

    def abrir_Comprar(self):
        try:
            
            # Instanciar y guardar como atributo de clase para que no desaparezca de memoria
            self.ventana_gestion = Comprar() 
            self.ventana_gestion.show()
            self.hide()
            
            # No ocultes la principal todavía hasta confirmar que la otra abrió
            # self.hide() 
            
        except Exception as e:
            print(f"Error al intentar abrir Innovación: {e}")


    def respaldo_automatico_inicio(self):
        try:
            # --- CONTROL DE SESIONES ROBUSTO ---
            archivo_contador = os.path.join(os.path.dirname(__file__), "sesiones.txt")
            
            # 1. Leer o Inicializar el contador
            if not os.path.exists(archivo_contador):
                aperturas = 0
            else:
                with open(archivo_contador, "r") as f:
                    contenido = f.read().strip()
                    # Si el archivo está vacío, usamos 0, sino convertimos el texto
                    aperturas = int(contenido) if contenido else 0
            
            aperturas += 1
            
            # 2. Guardar el nuevo número inmediatamente
            with open(archivo_contador, "w") as f:
                f.write(str(aperturas))
                
            print(f">>> SESIÓN DETECTADA: {aperturas}")

            # 3. Lógica de Respaldo: Solo en sesiones 2, 4, 6... o múltiplos de 5
            if aperturas % 2 != 0 and aperturas % 5 != 0:
                print(f"Sesión {aperturas}: No se requiere respaldo aún.")
                return

            # --- INICIO DEL CÓDIGO DE RESPALDO ORIGINAL ---
            path_actual = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            
            if aperturas % 5 == 0:
                path_destino = os.path.join(os.path.dirname(__file__), "archivo_maestro.db")
                tag = "CADA_5_SESIONES"
            else:
                path_destino = os.path.join(os.path.dirname(__file__), "historial_versiones.db")
                tag = "CADA_2_SESIONES"

            # Conectar y realizar el respaldo
            conn = sqlite3.connect(path_actual)
            cursor = conn.cursor()
            cursor.execute(f"ATTACH DATABASE '{path_destino}' AS dest")

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas = [f[0] for f in cursor.fetchall() if f[0] != 'sqlite_sequence']

            for tabla in tablas:
                nom_v = f"{tabla}_v_{timestamp}"
                cursor.execute(f"CREATE TABLE IF NOT EXISTS dest.{nom_v} AS SELECT * FROM {tabla}")
                
                # Registrar el commit
                cursor.execute(f"CREATE TABLE IF NOT EXISTS dest.registro_commits (id INTEGER PRIMARY KEY AUTOINCREMENT, tabla_original TEXT, nombre_version_db TEXT, fecha TEXT, comentario TEXT)")
                cursor.execute("INSERT INTO dest.registro_commits (tabla_original, nombre_version_db, fecha, comentario) VALUES (?, ?, ?, ?)", 
                            (tabla, nom_v, timestamp, f"Respaldo {tag}"))

            conn.commit()
            conn.close()
            print(f"✅ Respaldo {tag} completado con éxito.")

        except Exception as e:
            print(f"Error crítico en rotación de versiones: {e}")

    # Busca esta función en tu código y agrégale el (self)
    def reset_sistema_versiones(self): # <--- Asegúrate de que tenga 'self'
        import os
        archivos_a_eliminar = ["sesiones.txt", "historial_versiones.db", "archivo_maestro.db"]
        for archivo in archivos_a_eliminar:
            if os.path.exists(archivo):
                try:
                    os.remove(archivo)
                    print(f"Eliminado con éxito: {archivo}")
                except Exception as e:
                    print(f"No se pudo eliminar {archivo}: {e}")


    



if __name__ == "__main__":
    app = QApplication(sys.argv) # Única instancia de PySide6
    window = VentanaInicio()
    window.show()
    sys.exit(app.exec()) # En PySide6 es .exec(), no .exec_()





