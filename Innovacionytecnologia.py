import os
import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import (QTreeWidgetItem,QTableWidgetItem, 
                               QAbstractItemView,QHeaderView,QVBoxLayout,QMessageBox)
from PySide6.QtGui import QColor
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtGui import QPixmap
from PySide6.QtCore import QFile, Qt
import Exportar


class InnovacionWidget(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        
        # 1. Cargar el archivo .ui
        loader = QUiLoader()
        archivo_ui = QFile("innovacionytecnologia.ui")
        
        if not archivo_ui.open(QFile.ReadOnly):
            print(f"Error: No se pudo abrir el archivo UI")
            return
            
        # 2. CARGA CRÍTICA: Cargamos el UI como un objeto independiente primero
        # En innovacionytecnologia.py, modifica estas líneas (31-33 aprox):
        self.ui_content = loader.load(archivo_ui)
        self.ui = self.ui_content  # <--- CAMBIO CRÍTICO: Ahora self.ui ya no es None
        archivo_ui.close()
        
        # 3. Integrar el contenido en la ventana principal
        if self.ui_content:
            self.setCentralWidget(self.ui_content)
            # Opcional: Ajustar el tamaño de la ventana al diseño original
            self.resize(self.ui_content.size())
            self.setWindowTitle("Análisis de iinovación del Mercado")
            self.conectar_menu()
            self.configurar_navegacion()
            self.configurar_navegacion_comando()

    #pasar paginas
    def conectar_menu(self):
        # Usamos lambda para pasar el número de página deseado
        
        # Dashboard -> Página 0
        self.ui_content.actiongRAFICA.triggered.connect(lambda: self.cambiar_pagina(0))
        
        # Reportes (actionCrud) -> Página 1
        self.ui_content.actionCRUD.triggered.connect(lambda: self.cambiar_pagina(1))
        
        # Operaciones (actionCrud_3) -> Página 2
        self.ui_content.actionCRUD_2.triggered.connect(lambda: self.cambiar_pagina(2))
        
        # Análisis (actionCrud_2) -> Página 3
        self.ui_content.actionCRUD_3.triggered.connect(lambda: self.cambiar_pagina(3))

        #
        self.ui_content.actionCRUD_4.triggered.connect(lambda: self.cambiar_pagina(4))

        #
        self.ui_content.actionCRUD_5.triggered.connect(lambda: self.cambiar_pagina(5))

        #
        self.ui_content.actionCRUD_6.triggered.connect(lambda: self.cambiar_pagina(6))

        # El botón Volver ya te funciona, mantenlo así
        self.ui_content.actionINICIO.triggered.connect(self.regresar_inicio)

    def cambiar_pagina(self, indice):
        # Cambia el índice del stackedWidget de forma dinámica
        self.ui_content.stackedWidget.setCurrentIndex(indice)
        print(f"Navegando a la página índice: {indice}")

    def regresar_inicio(self):
        print("Regresando a inicio.ui...")
        try:
            # Verifica el nombre exacto de la clase en App.py
            from App import VentanaInicio
            self.nueva_ventana = VentanaInicio()
            self.nueva_ventana.show()
            self.close() 
        except ImportError:
            print("Error: El nombre 'VentanaPrincipal' no existe en App.py. Revisa el archivo.")


    #Comando De consola


    def configurar_navegacion(self):
        # Ahora que self.ui ya no es None, esto funcionará:
        self.ui.push_ayuda.clicked.connect(lambda: self.ui.Visual.setCurrentIndex(0))
        #
        self.ui.push_ingestion.clicked.connect(lambda: self.ui.Visual.setCurrentIndex(1))
        #
        self.ui.push_limpieza.clicked.connect(lambda: self.ui.Visual.setCurrentIndex(2))
        #
        self.ui.push_analisis.clicked.connect(lambda: self.ui.Visual.setCurrentIndex(3))
        #
        self.ui.push_salida.clicked.connect(lambda: self.ui.Visual.setCurrentIndex(4))

    def configurar_navegacion_comando(self):
        # Ahora que self.ui ya no es None, esto funcionará:
        self.ui.push_ayuda.clicked.connect(lambda: self.ui.Comando.setCurrentIndex(0))
        #
        self.ui.push_ingestion.clicked.connect(lambda: self.ui.Comando.setCurrentIndex(1))
        #
        self.ui.push_limpieza.clicked.connect(lambda: self.ui.Comando.setCurrentIndex(2))
        #
        self.ui.push_analisis.clicked.connect(lambda: self.ui.Comando.setCurrentIndex(3))
        #
        self.ui.push_salida.clicked.connect(lambda: self.ui.Comando.setCurrentIndex(4))