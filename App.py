import sys
import os
# Importamos los componentes necesarios directamente del módulo QtWidgets
from PySide6.QtWidgets import (QApplication, QDialog, QMainWindow, QVBoxLayout, 
                               QToolBar,QTableWidget,QTabWidget,QStackedWidget,QPushButton,
                               QToolButton,QFileDialog,QMessageBox,QTreeWidgetItem)

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtGui import QAction,QPixmap,QIcon, QColor
from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui
import sqlite3
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import Exportar
from collections import Counter
import recursos_rc
from Ingenieria import VentanaIngenieria


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
            if hasattr(self.ui, 'toolIngenieria'):
                self.ui.toolIngenieria.clicked.connect(self.abrir_ingenieria)
            else:
                print("Error: No se encontró el objeto 'toolIngenieria' en Inicio.ui")

    def abrir_ingenieria(self):
        # Creamos la instancia del QMainWindow
        self.nueva_ventana = VentanaIngenieria()
        self.nueva_ventana.show()
        # Cerramos el diálogo de inicio
        self.close()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    ventana_principal = VentanaInicio()
    ventana_principal.show()
    
    sys.exit(app.exec())





