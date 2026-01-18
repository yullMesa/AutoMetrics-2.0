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


class capitalhumano(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        
        # 1. Cargar el archivo .ui
        loader = QUiLoader()
        archivo_ui = QFile("capitalhumano.ui")
        
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
            self.setWindowTitle("humano capital ")
            self.conectar_menu()

            #Directorio De Empleados
            self.cargar_tabla_empleados()
            self.ui_content.tableWidget_EMPLEADOS.itemClicked.connect(self.evento_seleccionar_empleado)
            self.configurar_grafico()
            
            self.ui_content.pushButton_anadir.clicked.connect(self.añadir_empleado)
            self.ui_content.pushButton_actualizar.clicked.connect(self.actualizar_empleado)
            self.ui_content.btn_eliminar.clicked.connect(self.eliminar_empleado)
            self.ui_content.pushButton_exportar.clicked.connect(self.exportar_pdf)

        #Datos De Nomina

    #pasar paginas
    def conectar_menu(self):
        # Usamos lambda para pasar el número de página deseado
        
        # Dashboard -> Página 0
        self.ui_content.actionGRAFICA.triggered.connect(lambda: self.cambiar_pagina(0))
        
        # Reportes (actionCrud) -> Página 1
        self.ui_content.action_directorio.triggered.connect(lambda: self.cambiar_pagina(1))
        
        # Operaciones (actionCrud_3) -> Página 2
        self.ui_content.action_nomina.triggered.connect(lambda: self.cambiar_pagina(2))
        
        # Análisis (actionCrud_2) -> Página 3
        self.ui_content.action_desempeno.triggered.connect(lambda: self.cambiar_pagina(3))

        #
        self.ui_content.action_turnos.triggered.connect(lambda: self.cambiar_pagina(4))

        #
        self.ui_content.action_registro.triggered.connect(lambda: self.cambiar_pagina(5))

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

    

    #Directorio De Empleados
    def cargar_tabla_empleados(self):
        conn = sqlite3.connect('ingenieria.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id_empleado, nombre, cargo, departamento, salario_base, f_tecnica, f_ventas, f_analisis, f_servicio, f_liderazgo FROM empleados")
        self.datos_empleados = cursor.fetchall()
        
        self.ui_content.tableWidget_EMPLEADOS.setRowCount(0)
        # Ocultar los índices de las filas (1, 2, 3...)
        self.ui_content.tableWidget_EMPLEADOS.verticalHeader().setVisible(False)
        
        for row_number, row_data in enumerate(self.datos_empleados):
            self.ui_content.tableWidget_EMPLEADOS.insertRow(row_number)
            
            # Datos básicos
            self.ui_content.tableWidget_EMPLEADOS.setItem(row_number, 0, QTableWidgetItem(str(row_data[1])))
            self.ui_content.tableWidget_EMPLEADOS.setItem(row_number, 1, QTableWidgetItem(str(row_data[2])))
            
            # --- LIMPIEZA DE SALARIO ---
            try:
                # Si el dato viene como '$ 2,500', quitamos el '$' y la ',' para que float() no falle
                dato_limpio = str(row_data[4]).replace('$', '').replace(',', '').strip()
                salario_num = float(dato_limpio)
                salario_formateado = f"$ {salario_num:,.0f}"
            except:
                # Si falla la conversión, mostramos el dato crudo para no romper el programa
                salario_formateado = str(row_data[4])
                
            self.ui_content.tableWidget_EMPLEADOS.setItem(row_number, 2, QTableWidgetItem(salario_formateado))
        
        conn.close()
            


    #radar de fortalezas

    def evento_seleccionar_empleado(self):
        fila_seleccionada = self.ui_content.tableWidget_EMPLEADOS.currentRow()
        if fila_seleccionada != -1:
            # Recuperamos los datos de la lista que guardamos en memoria
            emp = self.datos_empleados[fila_seleccionada]
            
            # Llenamos los QLineEdit según tus nombres de objeto
            self.ui_content.txt_empleado.setText(str(emp[0])) # ID
            self.ui_content.txt_nombre.setText(str(emp[1]))   # Nombre
            self.ui_content.txt_cargo.setText(str(emp[2]))    # Cargo
            self.ui_content.txt_salario.setText(str(emp[4]))  # Salario base
            
            # Fortalezas (0-99)
            self.ui_content.txt_tecnica.setText(str(emp[5]))
            self.ui_content.txt_ventas.setText(str(emp[6]))
            self.ui_content.txt_analisis.setText(str(emp[7]))
            self.ui_content.txt_servicio.setText(str(emp[8]))
            self.ui_content.txt_iderazgo.setText(str(emp[9])) # Nota: corregí el typo 'iderazgo' según tu imagen

            self.ui_content.txt_empleado.setReadOnly(True)
            
            # 1. Extraemos los valores de las fortalezas en una lista
            valores = [emp[5], emp[6], emp[7], emp[8], emp[9]]
            
            # 2. Llamamos al método pasando el nombre (emp[1]) y la lista
            self.actualizar_radar(emp[1], valores)
            self.actualizar_pictograma(emp[2])

    #actualizar radar
            
    def actualizar_radar(self, nombre, valores_fortaleza):
        self.ax.clear()
        
        categorias = ['Técnica', 'Ventas', 'Análisis', 'Servicio', 'Liderazgo']
        N = len(categorias)

        # Cerrar el círculo para evitar errores de tamaño
        valores = list(valores_fortaleza)
        valores += valores[:1]
        
        angulos = [n / float(N) * 2 * np.pi for n in range(N)]
        angulos += angulos[:1]

        # Dibujado con el color turquesa de AutoMetrics
        self.ax.fill(angulos, valores, color='#73daca', alpha=0.3)
        self.ax.plot(angulos, valores, color='#73daca', linewidth=2, marker='o')

        # Configuración de ejes y fondo oscuro
        self.ax.set_xticks(angulos[:-1])
        self.ax.set_xticklabels(categorias, color='#c0caf5', size=9)
        self.ax.set_yticklabels([]) # Limpia los números del centro
        
        self.ax.spines['polar'].set_color('#414868')
        self.ax.grid(color='#414868', linestyle='--')
        
        self.ax.set_title(f"Perfil: {nombre}", color='#7aa2f7', size=12, pad=20)
        self.canvas.draw()


    def configurar_grafico(self):
        # Creamos la figura de Matplotlib con el estilo de tu dashboard
        self.fig, self.ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
        self.fig.patch.set_facecolor('#1a1b26') # Fondo oscuro
        self.ax.set_facecolor('#1a1b26')
        
        self.canvas = FigureCanvas(self.fig)
        layout = QVBoxLayout(self.ui_content.frame_10)
        layout.addWidget(self.canvas)

    
    #label

    def actualizar_pictograma(self, cargo):
        # Ruta base exacta según tu sistema
        ruta_base = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Rol"
        
        # Ahora buscamos por CARGO (ej: "Gerente General.png")
        nombre_archivo = f"{cargo}.png"
        ruta_completa = os.path.join(ruta_base, nombre_archivo)
        
        if os.path.exists(ruta_completa):
            pixmap = QPixmap(ruta_completa)
            self.ui_content.label_pictograma.setPixmap(
                pixmap.scaled(
                    self.ui_content.label_pictograma.size(), 
                    aspectMode=Qt.KeepAspectRatio, 
                    mode=Qt.SmoothTransformation
                )
            )
        else:
            self.ui_content.label_pictograma.clear()
            # Esto te ayudará a ver en consola qué nombre exacto está fallando
            print(f"Error: No se encontró la imagen para el cargo: {cargo}")

    
    #pushbutton
    def añadir_empleado(self):
        # 1. Recolectar datos de la interfaz
        ide = self.ui_content.txt_empleado.text()
        nom = self.ui_content.txt_nombre.text()
        car = self.ui_content.txt_cargo.text()
        
        try:
            # CONVERSIÓN CRÍTICA: Convertir strings de QLineEdit a números
            # Si el campo está vacío, ponemos 0 para evitar que SQL falle
            sal = float(self.ui_content.txt_salario.text() or 0)
            f_tec = int(self.ui_content.txt_tecnica.text() or 0)
            f_ven = int(self.ui_content.txt_ventas.text() or 0)
            f_ana = int(self.ui_content.txt_analisis.text() or 0)
            f_ser = int(self.ui_content.txt_servicio.text() or 0)
            f_lid = int(self.ui_content.txt_iderazgo.text() or 0) #

            # 2. Conectar e insertar en SQL
            conn = sqlite3.connect('ingenieria.db')
            cursor = conn.cursor()
            
            # Nota: Asegúrate de que el orden coincida con tu tabla empleados
            query = """INSERT INTO empleados 
                    (id_empleado, nombre, cargo, salario_base, f_tecnica, f_ventas, f_analisis, f_servicio, f_liderazgo) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            
            cursor.execute(query, (ide, nom, car, sal, f_tec, f_ven, f_ana, f_ser, f_lid))
            conn.commit()
            conn.close()

            # 3. Refrescar la tabla y limpiar campos
            self.cargar_tabla_empleados() 
            self.limpiar_campos()
            QMessageBox.information(self, "Éxito", f"Empleado {nom} añadido correctamente.")
            
        except ValueError:
            QMessageBox.warning(self, "Error de Formato", "Salario y Fortalezas deben ser números.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")


    def limpiar_campos(self):
        # Limpia todos los QLineEdit
        self.ui_content.txt_empleado.clear()
        self.ui_content.txt_nombre.clear()
        self.ui_content.txt_cargo.clear()
        self.ui_content.txt_salario.clear()
        self.ui_content.txt_tecnica.clear()
        self.ui_content.txt_ventas.clear()
        self.ui_content.txt_analisis.clear()
        self.ui_content.txt_servicio.clear()
        self.ui_content.txt_iderazgo.clear()
        
        # Limpia lo visual
        self.ui_content.label_pictograma.clear()
        if hasattr(self, 'ax'):
            self.ax.clear()
            self.canvas.draw()

    
    def actualizar_empleado(self):
        # 1. Recolectar datos de la interfaz
        ide = self.ui_content.txt_empleado.text()  # El ID es la clave para actualizar
        nom = self.ui_content.txt_nombre.text()
        car = self.ui_content.txt_cargo.text()
        
        # Validamos que haya un ID seleccionado
        if not ide:
            QMessageBox.warning(self, "Atención", "Por favor, seleccione un empleado de la tabla para actualizar.")
            return

        try:
            # Convertimos los valores a números (limpiando posibles símbolos)
            sal = float(self.ui_content.txt_salario.text().replace('$', '').replace(',', '') or 0)
            f_tec = int(self.ui_content.txt_tecnica.text() or 0)
            f_ven = int(self.ui_content.txt_ventas.text() or 0)
            f_ana = int(self.ui_content.txt_analisis.text() or 0)
            f_ser = int(self.ui_content.txt_servicio.text() or 0)
            f_lid = int(self.ui_content.txt_iderazgo.text() or 0)

            # 2. Conexión y ejecución SQL
            conn = sqlite3.connect('ingenieria.db')
            cursor = conn.cursor()
            
            query = """UPDATE empleados SET 
                    nombre = ?, 
                    cargo = ?, 
                    salario_base = ?, 
                    f_tecnica = ?, 
                    f_ventas = ?, 
                    f_analisis = ?, 
                    f_servicio = ?, 
                    f_liderazgo = ?
                    WHERE id_empleado = ?"""
            
            cursor.execute(query, (nom, car, sal, f_tec, f_ven, f_ana, f_ser, f_lid, ide))
            
            conn.commit()
            conn.close()

            # 3. Refrescar la interfaz
            self.cargar_tabla_empleados()
            QMessageBox.information(self, "Éxito", f"Datos de {nom} actualizados correctamente.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar: {e}")

    def eliminar_empleado(self):
        # 1. Obtener el ID del campo de texto
        ide = self.ui_content.txt_empleado.text()
        nombre = self.ui_content.txt_nombre.text()

        if not ide:
            QMessageBox.warning(self, "Atención", "Por favor, selecciona un empleado de la tabla para eliminar.")
            return

        # 2. Ventana de confirmación (Estilo profesional)
        respuesta = QMessageBox.question(
            self, 
            "Confirmar Eliminación", 
            f"¿Estás seguro de que deseas eliminar a {nombre}?\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            try:
                # 3. Conexión y ejecución en la base de datos
                conn = sqlite3.connect('ingenieria.db')
                cursor = conn.cursor()
                
                # Borramos usando la llave primaria
                cursor.execute("DELETE FROM empleados WHERE id_empleado = ?", (ide,))
                
                conn.commit()
                conn.close()

                # 4. Refrescar la interfaz
                self.cargar_tabla_empleados()
                self.limpiar_campos() # Limpia los txt_line, el radar y el pictograma
                
                QMessageBox.information(self, "Eliminado", f"El registro de {nombre} ha sido borrado.")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el registro: {e}")

    def exportar_pdf(self):
        # 1. Obtener datos actuales de la interfaz
        nombre = self.ui_content.txt_nombre.text()
        if not nombre:
            QMessageBox.warning(self, "Error", "Seleccione un empleado para exportar.")
            return

        # Definir ruta de guardado
        ruta_pdf = rf"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\PDF\{nombre}_Reporte.pdf"
        ruta_temp_radar = "temp_radar.png"

        try:
            # 2. Guardar la gráfica actual como imagen temporal
            self.fig.savefig(ruta_temp_radar, transparent=True, dpi=100)

            # 3. Crear el PDF
            c = canvas.Canvas(ruta_pdf, pagesize=letter)
            ancho, alto = letter

            # Título del Reporte
            c.setFont("Helvetica-Bold", 20)
            c.drawString(50, alto - 50, f"REPORTE DE DESEMPEÑO: {nombre.upper()}")
            
            # Línea divisoria
            c.setStrokeColorRGB(0.1, 0.46, 0.85) # Color azul
            c.line(50, alto - 60, 550, alto - 60)

            # 4. Insertar Datos del Empleado
            c.setFont("Helvetica", 12)
            datos = [
                f"ID Empleado: {self.ui_content.txt_empleado.text()}",
                f"Cargo: {self.ui_content.txt_cargo.text()}",
                f"Salario Base: {self.ui_content.txt_salario.text()}",
                "",
                "PUNTUACIONES DE COMPETENCIAS:",
                f"• Técnica: {self.ui_content.txt_tecnica.text()}",
                f"• Ventas: {self.ui_content.txt_ventas.text()}",
                f"• Análisis: {self.ui_content.txt_analisis.text()}",
                f"• Servicio: {self.ui_content.txt_servicio.text()}",
                f"• Liderazgo: {self.ui_content.txt_iderazgo.text()}" # Typo corregido
            ]

            y_pos = alto - 100
            for linea in datos:
                c.drawString(50, y_pos, linea)
                y_pos -= 20

            # 5. Insertar Gráfica de Radar
            # Posicionamos la imagen del radar en la parte inferior o lateral
            c.drawImage(ruta_temp_radar, 300, alto - 350, width=250, height=250, mask='auto')

            # Finalizar y Guardar
            c.showPage()
            c.save()

            # Eliminar imagen temporal
            if os.path.exists(ruta_temp_radar):
                os.remove(ruta_temp_radar)

            QMessageBox.information(self, "Éxito", f"PDF generado en:\n{ruta_pdf}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear el PDF: {e}")


    #Nomina 

    def cargar_clasificacion_por_cargo(self):
        # 1. Limpiar el TreeWidget antes de cargar
        self.ui_content.treeWidget_clasificacion.clear()
        self.ui_content.treeWidget_clasificacion.setHeaderLabels(["CARGOS / EMPLEADOS", "ID", "SALARIO"])
        
        # 2. Conectar a la base de datos para obtener los empleados
        conn = sqlite3.connect('ingenieria.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id_empleado, nombre, cargo, salario_base FROM empleados ORDER BY cargo ASC")
        empleados = cursor.fetchall()
        conn.close()

        # 3. Diccionario para rastrear qué carpetas de cargos ya hemos creado
        carpetas_cargos = {}

        for emp in empleados:
            id_emp = str(emp[0])
            nombre = str(emp[1])
            cargo = str(emp[2])
            salario = f"$ {float(emp[3]):,.0f}"

            # 4. Si el cargo no tiene carpeta, la creamos
            if cargo not in carpetas_cargos:
                # Crear el nodo padre (Carpeta)
                carpeta = QTreeWidgetItem(self.ui_content.treeWidget_clasificacion)
                carpeta.setText(0, cargo.upper())
                # Opcional: ponerle un color diferente al texto de la carpeta
                carpeta.setForeground(0, QColor("#bb9af7")) 
                carpetas_cargos[cargo] = carpeta
            
            # 5. Crear el nodo hijo (Empleado) dentro de su carpeta correspondiente
            item_empleado = QTreeWidgetItem(carpetas_cargos[cargo])
            item_empleado.setText(0, nombre)
            item_empleado.setText(1, id_emp)
            item_empleado.setText(2, salario)
            # Añadir un icono de usuario si lo deseas
            # item_empleado.setIcon(0, QIcon("ruta/user_icon.png"))

        # Expandir todas las carpetas al iniciar
        self.ui_content.treeWidget_clasificacion.expandAll()