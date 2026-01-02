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

class Inicio(QDialog):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        ui_file = QFile("Inicio.ui")
        
        
        if not ui_file.open(QFile.ReadOnly):
            print(f"Error al abrir Inicio.ui")
            return
            
        self.ui = loader.load(ui_file)
        ui_file.close()

        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)
        layout.setContentsMargins(0, 0, 0, 0)
        self.resize(self.ui.size())
        # CONEXIÓN: Al presionar el botón OK del ButtonBox, abrimos Ingeniería
        # Suponiendo que usas el standard button box
        self.btn_ingenieria = self.ui.findChild(QToolButton, "toolIngenieria")
        if self.btn_ingenieria:
            self.btn_ingenieria.clicked.connect(self.abrir_ingenieria)
        else:
            print("No se encontró el botón 'toolIngenieria' en Inicio.ui")
        
        
        self.btn_logistica = self.ui.findChild(QToolButton, "toolGestion") # Asegúrate que el nombre en QtDesigner coincida
        if self.btn_logistica:
            self.btn_logistica.clicked.connect(self.abrir_logistica)

        else:
            print("No se encontró el botón 'toolGestion' en Inicio.ui")


        # Dentro del __init__ de tu Dialog inicial
        self.btn_rendimiento = self.ui.findChild(QToolButton, "toolRendimiento") # Localiza el botón por su nombre
        if self.btn_rendimiento:
            self.btn_rendimiento.clicked.connect(self.abrir_rendimiento) # Conecta la señal

        

    def abrir_ingenieria(self):
        # Creamos la ventana y la guardamos en una variable para que no muera
        self.nueva_ventana = IngenieriaWindow()
        self.nueva_ventana.show()
        
        # IMPORTANTE: Usamos close() en lugar de accept() para no disparar el main
        self.close()
        # Cerramos el diálogo y abrimos la ventana principal
        self.accept()



    # Nuevo método en InicioDialog
    def abrir_logistica(self):
        self.nueva_ventana = ModuloCadenaValor()
        self.nueva_ventana.show()
        self.close() # Cierra el menú de inicio
        self.accept()


    def abrir_rendimiento(self):
        # Usar 'self.' evita que el recolector de basura de Python cierre la ventana al terminar la función
        self.nueva_ventana = RendimientoMercado() 
        self.nueva_ventana.show()
        
        # Gestionar el cierre del menú de inicio
        self.accept() # Finaliza el diálogo con éxito
        self.hide()   # Oculta el menú para limpiar la pantalla