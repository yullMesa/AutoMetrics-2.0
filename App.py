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

    



if __name__ == "__main__":
    app = QApplication(sys.argv) # Única instancia de PySide6
    window = VentanaInicio()
    window.show()
    sys.exit(app.exec()) # En PySide6 es .exec(), no .exec_()





