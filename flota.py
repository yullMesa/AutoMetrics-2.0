import os
import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile,Qt, QSize
from PySide6.QtWidgets import (QTreeWidgetItem,QTableWidgetItem, 
                               QAbstractItemView,QHeaderView,QVBoxLayout,QMessageBox,QToolButton,
                               QSizePolicy,QDialog,QLabel,QHBoxLayout,QPushButton,QMessageBox,QWidget,
                                 QPlainTextEdit,QStyle)
from PySide6.QtGui import QColor,QIcon, QPixmap,QPainter , QFont , QTextCursor
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtGui import QPixmap,QBrush
from PySide6.QtCore import QFile, Qt , QSize , QTimer , QRect , QPoint 
import random
from datetime import datetime
import numpy as np
import hashlib
from matplotlib.figure import Figure
import mplfinance as mpf
import pandas as pd
from PySide6.QtCore import QTimer, QDateTime 
import time
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image, ImageDraw, ImageFont
from PySide6 import QtGui
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class flota(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        
        # 1. Cargar el archivo .ui
        loader = QUiLoader()
        archivo_ui = QFile("flota.ui")
        
        if not archivo_ui.open(QFile.ReadOnly):
            print(f"Error: No se pudo abrir el archivo UI")
            return
            
        # 2. CARGA CRÍTICA: Cargamos el UI como un objeto independiente primero
        self.ui_content = loader.load(archivo_ui)
        archivo_ui.close()
        
        # 3. Integrar el contenido en la ventana principal
        if self.ui_content:
            self.setCentralWidget(self.ui_content)
            # Opcional: Ajustar el tamaño de la ventana al diseño original
            self.resize(self.ui_content.size())
            self.setWindowTitle("flota  ")
            self.conectar_menu()

            self.cargar_treewidget_flota()
            self.cargar_tabla_empleados()
            self.cargar_catalogo_dinamico()

    #pasar paginas
    def conectar_menu(self):
        # Usamos lambda para pasar el número de página deseado
        
        # Dashboard -> Página 0
        self.ui_content.actionVista.triggered.connect(lambda: self.cambiar_pagina(0))
        
        # El botón Volver ya te funciona, mantenlo así
        self.ui_content.actioninicio.triggered.connect(self.regresar_inicio)

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
        


    #treewidget flota
    def cargar_treewidget_flota(self):
        # 1. Limpieza y configuración inicial
        self.ui_content.treeWidget_flota.clear()
        self.ui_content.treeWidget_flota.setHeaderLabels(["ACTIVO / PLACA", "ESTADO", "ASIGNACIÓN"])
        # 1. Obtener el encabezado
        header = self.ui_content.treeWidget_flota.header()

        # 2. Forzar a que las columnas se repartan el espacio
        from PySide6.QtWidgets import QHeaderView
        header.setSectionResizeMode(QHeaderView.Stretch) # Estira todas por igual

        # 3. Opcional: Si quieres que la primera columna sea más ancha
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # El estado solo ocupa lo necesario
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # La asignación solo lo necesario

        # 4. Aumentar la indentación para que las carpetas se distingan bien
        self.ui_content.treeWidget_flota.setIndentation(25)
        
        # 2. Definición de carpetas (Categorías Logísticas)
        categorias = {
            "Montacargas": QTreeWidgetItem(self.ui_content.treeWidget_flota, ["🏗️ MONTACARGAS"]),
            "Pesados": QTreeWidgetItem(self.ui_content.treeWidget_flota, ["🚛 TRANSPORTE PESADO (TRACTOS/VOLQUETAS)"]),
            "Maquinaria": QTreeWidgetItem(self.ui_content.treeWidget_flota, ["🚧 MAQUINARIA AMARILLA"]),
            "Furgones": QTreeWidgetItem(self.ui_content.treeWidget_flota, ["📦 FURGONES Y REPARTO"]),
            "Especiales": QTreeWidgetItem(self.ui_content.treeWidget_flota, ["🛰️ EQUIPOS ESPECIALES (DRONES/GEN)"]),
            "Fluvial": QTreeWidgetItem(self.ui_content.treeWidget_flota, ["🚢 TRANSPORTE FLUVIAL"]),
            "Otros": QTreeWidgetItem(self.ui_content.treeWidget_flota, ["🔧 OTROS ACTIVOS"])
        }

        # 3. Consulta a la base de datos
        import sqlite3
        conn = sqlite3.connect('ingenieria.db')
        cursor = conn.cursor()
        # Cruzamos con empleados para ver quién tiene asignado el equipo
        query = """
            SELECT v.marca, v.modelo, v.placa, v.tipo_vehiculo, v.soat_activo, v.buen_estado, e.nombre 
            FROM flota v
            LEFT JOIN empleados e ON v.id_conductor = e.id_empleado
        """
        cursor.execute(query)
        activos = cursor.fetchall()
        conn.close()

        # 4. Clasificación Lógica
        for marca, modelo, placa, tipo, soat, estado, conductor in activos:
            # Determinar en qué carpeta entra
            tipo_low = tipo.lower()
            if "montacarga" in tipo_low:
                parent = categorias["Montacargas"]
            elif tipo_low in ["volqueta", "tractomula", "tanque", "mezcladora"]:
                parent = categorias["Pesados"]
            elif "maquinaria" in tipo_low or "grúa" in tipo_low or "cargador" in tipo_low:
                parent = categorias["Maquinaria"]
            elif "furgón" in tipo_low or "reparto" in tipo_low:
                parent = categorias["Furgones"]
            elif "fluvial" in tipo_low:
                parent = categorias["Fluvial"]
            elif tipo_low in ["drone", "generador", "plataforma"]:
                parent = categorias["Especiales"]
            else:
                parent = categorias["Otros"]

            # 5. Crear el Item del Activo
            item = QTreeWidgetItem(parent)
            item.setText(0, f"{marca} {modelo} ({placa})")
            
            # Estado visual (SOAT y Mecánica)
            if soat == 0 or estado == 0:
                item.setText(1, "🔴 FUERA DE SERVICIO")
                item.setForeground(1, QColor("#f7768e")) # Rojo neón
            else:
                item.setText(1, "🟢 OPERATIVO")
                item.setForeground(1, QColor("#73daca")) # Verde neón

            # Asignación
            item.setText(2, conductor if conductor else "DISPONIBLE")
            if not conductor:
                item.setForeground(2, QColor("#bb9af7")) # Púrpura para disponibles

        # Ajustes de visualización
        self.ui_content.treeWidget_flota.expandAll()


    def cargar_tabla_empleados(self):
        # 1. Configuración de columnas (Eliminando índices feos)
        columnas = ["ID EMPLEADO", "NOMBRE", "TIPO LICENCIA", "PUNTOS", "ESTADO"]
        self.ui_content.tableWidget_empleados.setColumnCount(len(columnas))
        self.ui_content.tableWidget_empleados.setHorizontalHeaderLabels(columnas)
        self.ui_content.tableWidget_empleados.verticalHeader().setVisible(False)

        # 2. Consulta con JOIN para vincular conductores y empleados
        import sqlite3
        conn = sqlite3.connect('ingenieria.db')
        cursor = conn.cursor()
        
        # Esta consulta filtra solo a quienes están en la tabla conductores
        query = """
            SELECT e.id_empleado, e.nombre, c.tipo_licencia, c.puntos_seguridad, 
                CASE WHEN c.estado_activo = 1 THEN 'ACTIVO' ELSE 'INACTIVO' END
            FROM conductores c
            JOIN empleados e ON c.id_empleado_ref = e.id_empleado
        """
        cursor.execute(query)
        conductores = cursor.fetchall()
        conn.close()

        # 3. Llenado de la tabla con formato condicional
        self.ui_content.tableWidget_empleados.setRowCount(0)
        for row_number, row_data in enumerate(conductores):
            self.ui_content.tableWidget_empleados.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Color según el estado (Activo/Inactivo)
                if column_number == 4: # Columna ESTADO
                    if data == 'ACTIVO':
                        item.setForeground(QColor("#73daca")) # Verde neón
                    else:
                        item.setForeground(QColor("#f7768e")) # Rojo neón
                
                self.ui_content.tableWidget_empleados.setItem(row_number, column_number, item)

        # 4. Ajuste de espacios para evitar "apeñuscamiento"
        header = self.ui_content.tableWidget_empleados.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

    
    #toolbuttons

    def cargar_catalogo_dinamico(self):
        # 1. Limpiar el grid antes de regenerar
        while self.ui_content.gridLayout_catalogo.count():
            child = self.ui_content.gridLayout_catalogo.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 2. Conexión y consulta a la base de datos
        conn = sqlite3.connect('ingenieria.db')
        cursor = conn.cursor()
        # Traemos los datos necesarios para el mensaje y para la ruta de la imagen
        cursor.execute("SELECT marca, modelo, placa, kilometraje, tipo_vehiculo FROM flota")
        vehiculos = cursor.fetchall()
        conn.close()

        # Configuración de ruta y grid
        ruta_base = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\flota"
        columnas_max = 6
        fila, columna = 0, 0

        for marca, modelo, placa, km, tipo in vehiculos:
            # 3. Crear el botón único para este vehículo
            btn = QToolButton()
            btn.setText(f"{marca}\n{modelo}")
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            
            # Expanding para que no se vean pequeños
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setMinimumSize(140, 160)
            
            # Heredar estilo visual (colores/bordes) del botón plantilla
            btn.setStyleSheet(self.ui_content.toolButton_main.styleSheet())

            # 4. CARGA DE IMAGEN ÚNICA (modelo.png)
            # Construimos el nombre del archivo: ej. "NPR Cargo.png"
            nombre_img = f"{modelo}.png"
            ruta_completa = os.path.join(ruta_base, nombre_img)
            
            if os.path.exists(ruta_completa):
                pixmap = QPixmap(ruta_completa)
                btn.setIcon(QIcon(pixmap))
                btn.setIconSize(QSize(120, 100))
            else:
                # Si no existe, podrías poner un icono de advertencia o dejarlo vacío
                print(f"Advertencia: No se encontró la imagen para {modelo}")

            # 5. ASIGNAR EVENTO CLICK (QMessageBox)
            # Usamos valores por defecto en lambda para capturar el estado actual del bucle
            btn.clicked.connect(lambda ch=None, ma=marca, mo=modelo, pl=placa, kl=km, ti=tipo: 
                                self.mostrar_detalles(ma, mo, pl, kl, ti))

            # 6. Posicionar en el grid
            self.ui_content.gridLayout_catalogo.addWidget(btn, fila, columna)
            
            columna += 1
            if columna >= columnas_max:
                columna = 0
                fila += 1

    def mostrar_detalles(self, marca, modelo, placa, km, tipo):
        # Ventana de información con los valores de la tabla
        msg = QMessageBox(self)
        msg.setWindowTitle(f"Ficha Técnica - {modelo}")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"<b>DETALLES DEL VEHÍCULO</b>")
        
        detalles = (
            f"<b>Marca:</b> {marca}<br>"
            f"<b>Modelo:</b> {modelo}<br>"
            f"<b>Placa:</b> {placa}<br>"
            f"<b>Kilometraje:</b> {km} KM<br>"
            f"<b>Categoría:</b> {tipo}"
        )
        
        msg.setInformativeText(detalles)
        msg.setStandardButtons(QMessageBox.Ok)
        # Estilo para que combine con tu tema oscuro
        msg.setStyleSheet("QLabel{ min-width: 250px; color: white;} QMessageBox{ background-color: #1a1b26; }")
        msg.exec()