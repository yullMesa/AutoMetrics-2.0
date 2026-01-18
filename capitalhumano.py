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
        self.cargar_clasificacion_por_cargo()
        self.actualizar_vista_nomina()
        self.dibujar_dona_presupuesto(0, 500000)  # Inicializamos la gráfica con 0 gastado

        #Evaluar desempeño
        self.ui_content.tableWidget_EMPLEADOS_2.itemClicked.connect(self.seleccionar_empleado_evaluacion)

        #jornada laboral 
        self.cargar_horarios_semanales()

        #dashboard
        self.graficar_analisis_competencias()
        self.graficar_salarios_por_cargo()
        self.graficar_estado_financiero_real()
        self.graficar_viabilidad_contratacion()
        



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
        # 1. Conexión y Limpieza
        conn = sqlite3.connect('ingenieria.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id_empleado, nombre, cargo, departamento, salario_base, f_tecnica, f_ventas, f_analisis, f_servicio, f_liderazgo FROM empleados")
        self.datos_empleados = cursor.fetchall()
        conn.close()

        self.ui_content.tableWidget_EMPLEADOS.setRowCount(0)
        self.ui_content.tableWidget_EMPLEADOS_2.setRowCount(0)
        
        # Ocultar índices feos
        self.ui_content.tableWidget_EMPLEADOS.verticalHeader().setVisible(False)
        self.ui_content.tableWidget_EMPLEADOS_2.verticalHeader().setVisible(False)

        for row_number, row_data in enumerate(self.datos_empleados):
            self.ui_content.tableWidget_EMPLEADOS.insertRow(row_number)
            self.ui_content.tableWidget_EMPLEADOS_2.insertRow(row_number)

            # 2. Procesamiento Seguro de Salario
            try:
                # Quitamos cualquier símbolo para convertir a float antes de formatear
                dato_sucio = str(row_data[4]).replace('$', '').replace(',', '').strip()
                salario_num = float(dato_sucio)
                salario_formateado = f"$ {salario_num:,.0f}" # Aquí daba el error si era str
            except (ValueError, TypeError):
                salario_formateado = str(row_data[4])

            # 3. Llenado de Tabla 1
            self.ui_content.tableWidget_EMPLEADOS.setItem(row_number, 0, QTableWidgetItem(str(row_data[1])))
            self.ui_content.tableWidget_EMPLEADOS.setItem(row_number, 1, QTableWidgetItem(str(row_data[2])))
            self.ui_content.tableWidget_EMPLEADOS.setItem(row_number, 2, QTableWidgetItem(salario_formateado))

            # 4. Llenado de Tabla 2
            self.ui_content.tableWidget_EMPLEADOS_2.setItem(row_number, 0, QTableWidgetItem(str(row_data[1])))
            self.ui_content.tableWidget_EMPLEADOS_2.setItem(row_number, 1, QTableWidgetItem(str(row_data[2])))
            self.ui_content.tableWidget_EMPLEADOS_2.setItem(row_number, 2, QTableWidgetItem(salario_formateado))

        # IMPORTANTE: Saca las funciones de graficar fuera del bucle 'for'
        # No deben ejecutarse mientras se llena la tabla.
            


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
        self.ui_content.treeWidget_clasificacion.setIndentation(25) # Más espacio de sangría para hijos
        # Obtener el encabezado
        header = self.ui_content.treeWidget_clasificacion.header()
        
        # 1. Distribución de espacio:
        # La columna 0 (Nombre) se expande para ocupar todo el espacio sobrante
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Las columnas 1 (ID) y 2 (Salario) se ajustan a su contenido + un margen
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.resizeSection(1, 100) # Ancho fijo para el ID
        
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.resizeSection(2, 120) # Ancho fijo para el Salario
        
        # 2. Alineación y espacio visual
        header.setDefaultAlignment(Qt.AlignCenter) # Centra los títulos
        self.ui_content.treeWidget_clasificacion.setIndentation(30) # Más espacio para la jerarquía
        
        # 3. Quitar los puntos de las líneas para un look más moderno
        self.ui_content.treeWidget_clasificacion.setRootIsDecorated(True)
        
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

    #gráfica
    def actualizar_vista_nomina(self):
        # Obtener datos financieros reales
        presupuesto, gasto = self.calcular_balance_presupuesto()
        disponible = presupuesto - gasto
        
        # Obtener empleados para el análisis de aumento
        conn = sqlite3.connect('ingenieria.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, f_tecnica, f_ventas, f_analisis, f_servicio, f_liderazgo FROM empleados")
        empleados = cursor.fetchall()
        conn.close()

        informe = "<h2 style='color: #7aa2f7;'>ANÁLISIS DE MÉRITOS Y PRESUPUESTO</h2>"
        informe += f"<p style='color: #cfc9c2;'>Presupuesto Restante: <b>${disponible:,.2f}</b></p><br>"
        informe += "<hr style='border: 1px solid #414868;'><br>"

        candidatos = []
        for emp in empleados:
            nombre = emp[0]
            # Promedio de las 5 fortalezas
            promedio = sum(emp[1:]) / 5
            
            if promedio >= 90:
                candidatos.append(f"<li><b style='color: #73daca;'>{nombre}</b>: Promedio {promedio:.1f}% (Digno de aumento)</li>")
            elif promedio >= 80:
                candidatos.append(f"<li><b style='color: #e0af68;'>{nombre}</b>: Promedio {promedio:.1f}% (Bono recomendado)</li>")

        if candidatos:
            informe += "<ul style='color: #a9b1d6;'>" + "".join(candidatos) + "</ul>"
        else:
            informe += "<p style='color: #f7768e;'>No se identifican candidatos para aumento bajo los criterios actuales.</p>"

        # Insertar como HTML para colores y negritas
        self.ui_content.textEdit_x.setHtml(informe)
        
    def dibujar_dona_presupuesto(self, gastado, total):
        if not hasattr(self, 'canvas_p'):
            self.fig_p, self.ax_p = plt.subplots(figsize=(4, 4))
            self.fig_p.patch.set_facecolor('#1a1b26')
            self.canvas_p = FigureCanvas(self.fig_p)
            layout = QVBoxLayout(self.ui_content.frame_12)
            layout.addWidget(self.canvas_p)
        
        self.ax_p.clear()
        restante = max(0, total - gastado)
        
        self.ax_p.pie([gastado, restante], labels=['Gastado', 'Disponible'], 
                    colors=['#f7768e', '#73daca'], autopct='%1.1f%%', 
                    startangle=90, textprops={'color':"w"}, pctdistance=0.8)
        
        centro = plt.Circle((0,0), 0.70, fc='#1a1b26')
        self.ax_p.add_artist(centro)
        self.canvas_p.draw()

    def calcular_balance_presupuesto(self):
        try:
            conn = sqlite3.connect('ingenieria.db')
            cursor = conn.cursor()

            # 1. Obtener el presupuesto total configurado
            cursor.execute("SELECT monto_total FROM presupuesto_empresa WHERE id = 1")
            resultado_p = cursor.fetchone()
            presupuesto_total = resultado_p[0] if resultado_p else 500000.0

            # 2. Sumar todos los salarios de la nómina
            cursor.execute("SELECT SUM(salario_base) FROM empleados")
            gasto_total = cursor.fetchone()[0] or 0.0
            
            conn.close()

            # 3. Actualizar la gráfica de dona con valores reales
            self.dibujar_dona_presupuesto(gasto_total, presupuesto_total)
            
            return presupuesto_total, gasto_total

        except Exception as e:
            print(f"Error financiero: {e}")
            return 500000.0, 0.0
        
    
    
    #Evaluar desempeño
    def configurar_tabla_evaluacion(self):
        # Definir columnas: Nombre, Cargo, Salario
        self.ui_content.tableWidget_EMPLEADOS_2.setColumnCount(3)
        self.ui_content.tableWidget_EMPLEADOS_2.setHorizontalHeaderLabels(["NOMBRE", "CARGO", "SALARIO"])
        
        # Estética profesional
        self.ui_content.tableWidget_EMPLEADOS_2.verticalHeader().setVisible(False)
        header = self.ui_content.tableWidget_EMPLEADOS_2.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        # Activar selección de fila completa
        self.ui_content.tableWidget_EMPLEADOS_2.setSelectionBehavior(QAbstractItemView.SelectRows)

    def graficar_cumplimiento_cargo(self, nombre, fortalezas):
        # 1. Gestionar el Layout para evitar el error de duplicidad
        if not hasattr(self, 'canvas_cumplimiento'):
            self.fig_c, self.ax_c = plt.subplots(figsize=(5, 3))
            self.fig_c.patch.set_facecolor('#1a1b26')
            self.canvas_c = FigureCanvas(self.fig_c)
            
            # Crear layout solo la primera vez
            layout = QVBoxLayout(self.ui_content.frame_13)
            layout.addWidget(self.canvas_c)
            self.canvas_cumplimiento = True # Bandera para no repetir el proceso
        
        # 2. Limpiar y redibujar
        self.ax_c.clear()
        categorias = ['Técnica', 'Ventas', 'Análisis', 'Servicio', 'Liderazgo']
        umbral = 70 
        colores = ['#73daca' if v >= umbral else '#f7768e' for v in fortalezas]

        self.ax_c.barh(categorias, fortalezas, color=colores, alpha=0.8)
        self.ax_c.axvline(umbral, color='#bb9af7', linestyle='--')
        
        # Estética y refresco del lienzo
        self.ax_c.set_title(f"Métricas de Retención: {nombre}", color='white')
        self.ax_c.tick_params(axis='both', colors='white')
        self.fig_c.tight_layout()
        self.canvas_c.draw()

    def analizar_permanencia(self, nombre, fortalezas):
        promedio = sum(fortalezas) / len(fortalezas)
        bajo_el_umbral = [f for f in fortalezas if f < 70]
        
        # 1. Definir el veredicto con formato HTML para colores
        if promedio >= 75 and not bajo_el_umbral:
            resultado = f"<b style='color: #73daca;'>✅ APTO:</b> {nombre} cumple con todas las métricas."
        elif promedio >= 70:
            resultado = f"<b style='color: #e0af68;'>⚠️ EN OBSERVACIÓN:</b> {nombre} tiene promedio aceptable pero debilidades puntuales."
        else:
            resultado = f"<b style='color: #f7768e;'>❌ NO APTO:</b> {nombre} no alcanza las métricas mínimas del cargo."
            
        # 2. Enviar el mensaje al widget correcto
        self.ui_content.textEdit_x_2.setHtml(f"<div style='font-size: 14px;'>{resultado}</div>")


    def seleccionar_empleado_evaluacion(self):
        fila = self.ui_content.tableWidget_EMPLEADOS_2.currentRow()
        if fila != -1:
            emp = self.datos_empleados[fila]
            nombre = emp[1]
            # Índices correctos de fortalezas según tu SELECT
            fortalezas = [emp[5], emp[6], emp[7], emp[8], emp[9]]
            
            # Ahora sí, llamamos a las funciones con sus datos
            self.graficar_cumplimiento_cargo(nombre, fortalezas)
            self.analizar_permanencia(nombre, fortalezas)


    #jornada laboral

    def cargar_horarios_semanales(self):
        # 1. Limpiar y configurar encabezados
        self.ui_content.treeWidget_clasificacion_2.clear()
        self.ui_content.treeWidget_clasificacion_2.setHeaderLabels(["DÍA / EMPLEADO", "HORARIO", "ESTADO"])
        
        # --- SOLUCIÓN PARA EL ESPACIO ---
        header = self.ui_content.treeWidget_clasificacion_2.header()
        header.setSectionResizeMode(QHeaderView.Stretch) 
        # --------------------------------
        
        dias_semana = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO"]
        carpetas = {}

        # 2. Crear las carpetas de los días
        for dia in dias_semana:
            parent = QTreeWidgetItem(self.ui_content.treeWidget_clasificacion_2)
            parent.setText(0, dia)
            parent.setForeground(0, QColor("#7aa2f7"))
            carpetas[dia] = parent

        # 3. Distribuir empleados
        for i, emp in enumerate(self.datos_empleados):
            nombre = str(emp[1])
            cargo = str(emp[2])
            
            for dia in dias_semana:
                item_emp = QTreeWidgetItem(carpetas[dia])
                item_emp.setText(0, f"{nombre} ({cargo})")
                
                # Horario Colombia
                if dia == "SÁBADO":
                    item_emp.setText(1, "08:00 AM - 12:00 PM")
                    item_emp.setForeground(1, QColor("#e0af68"))
                else:
                    item_emp.setText(1, "08:00 AM - 05:00 PM")
                
                item_emp.setText(2, "ACTIVO")
                item_emp.setForeground(2, QColor("#73daca"))

        self.ui_content.treeWidget_clasificacion_2.setIndentation(20)
        # self.ui_content.treeWidget_clasificacion_2.expandAll() # Opcional

    #dashboard
    def graficar_analisis_competencias(self):
        # 1. Obtener los datos
        conn = sqlite3.connect('ingenieria.db')
        cursor = conn.cursor()
        # Query solicitada
        cursor.execute("SELECT nombre, f_tecnica, f_ventas, f_analisis, f_servicio, f_liderazgo FROM empleados LIMIT 10")
        datos = cursor.fetchall()
        conn.close()

        if not datos: return

        # 2. Preparar el Canvas en frame_x
        if not hasattr(self, 'canvas_analisis'):
            self.fig_a, self.ax_a = plt.subplots(figsize=(8, 4))
            self.fig_a.patch.set_facecolor('#1a1b26')
            self.canvas_a = FigureCanvas(self.fig_a)
            layout = QVBoxLayout(self.ui_content.frame_x)
            layout.addWidget(self.canvas_a)
        
        self.ax_a.clear()

        # 3. Estructurar datos para las barras
        nombres = [d[0] for d in datos]
        f_tec = [d[1] for d in datos]
        f_ven = [d[2] for d in datos]
        f_ana = [d[3] for d in datos]
        f_ser = [d[4] for d in datos]
        f_lid = [d[5] for d in datos]

        x = np.arange(len(nombres))
        width = 0.15  # Ancho de las barras

        # 4. Dibujar las 5 barras por empleado
        self.ax_a.bar(x - 2*width, f_tec, width, label='Técnica', color='#7aa2f7')
        self.ax_a.bar(x - width, f_ven, width, label='Ventas', color='#73daca')
        self.ax_a.bar(x, f_ana, width, label='Análisis', color='#e0af68')
        self.ax_a.bar(x + width, f_ser, width, label='Servicio', color='#f7768e')
        self.ax_a.bar(x + 2*width, f_lid, width, label='Liderazgo', color='#bb9af7')

        # 5. Estética Tokyo Night
        self.ax_a.set_title("Comparativa de Competencias por Empleado", color='white', pad=15)
        self.ax_a.set_xticks(x)
        self.ax_a.set_xticklabels(nombres, rotation=45, ha='right', color='white', fontsize=8)
        self.ax_a.tick_params(axis='y', colors='white')
        self.ax_a.legend(loc='upper right', fontsize='small', framealpha=0.3)
        
        self.fig_a.tight_layout()
        self.canvas_a.draw()

    def graficar_salarios_por_cargo(self):
        # 1. Obtener los datos según tu query específica
        conn = sqlite3.connect('ingenieria.db')
        cursor = conn.cursor()
        query = "SELECT nombre, cargo, salario_base FROM empleados ORDER BY cargo ASC LIMIT 15"
        cursor.execute(query)
        datos = cursor.fetchall()
        conn.close()

        if not datos: return

        # 2. Configurar el Canvas en frame_2
        if not hasattr(self, 'canvas_salarios'):
            self.fig_s, self.ax_s = plt.subplots(figsize=(7, 5))
            self.fig_s.patch.set_facecolor('#1a1b26') # Fondo Tokyo Night
            self.canvas_s = FigureCanvas(self.fig_s)
            layout = QVBoxLayout(self.ui_content.frame_2)
            layout.addWidget(self.canvas_s)
        
        self.ax_s.clear()

        # 3. Preparar etiquetas combinadas (Nombre + Cargo)
        nombres_cargos = [f"{d[0]}\n({d[1]})" for d in datos]
        salarios = [d[2] for d in datos]
        
        # 4. Crear barras horizontales con gradiente de color
        y_pos = np.arange(len(nombres_cargos))
        bars = self.ax_s.barh(y_pos, salarios, color='#bb9af7', edgecolor='#7aa2f7', alpha=0.8)

        # 5. Estética y Formato
        self.ax_s.set_yticks(y_pos)
        self.ax_s.set_yticklabels(nombres_cargos, color='white', fontsize=8)
        self.ax_s.set_title("Distribución Salarial por Cargo", color='#73daca', pad=15, fontweight='bold')
        self.ax_s.invert_yaxis()  # El primer cargo arriba
        
        # Añadir el valor del salario al final de cada barra
        for bar in bars:
            width = bar.get_width()
            self.ax_s.text(width, bar.get_y() + bar.get_height()/2, f' ${width:,.0f}', 
                        va='center', color='#cfc9c2', fontsize=8)

        self.ax_s.tick_params(axis='x', colors='white')
        self.ax_s.spines['bottom'].set_color('#414868')
        self.ax_s.spines['left'].set_color('#414868')
        self.ax_s.set_facecolor('#16161e')

        self.fig_s.tight_layout()
        self.canvas_s.draw()

    def graficar_estado_financiero_real(self):
        # 1. Obtener datos de la base de datos
        conn = sqlite3.connect('ingenieria.db')
        cursor = conn.cursor()
        
        # Obtener el presupuesto (Ej: 500,000,000)
        cursor.execute("SELECT monto_total FROM presupuesto_empresa WHERE id = 1")
        presupuesto_total = cursor.fetchone()[0]
        
        # Obtener la suma de todos los salarios
        cursor.execute("SELECT SUM(salario_base) FROM empleados")
        gasto_nomina = cursor.fetchone()[0] or 0
        conn.close()

        # --- OPERACIÓN CLAVE: CÁLCULO DEL RESTANTE ---
        presupuesto_restante = presupuesto_total - gasto_nomina

        # 2. Configurar Canvas en frame_4
        if not hasattr(self, 'canvas_financiero'):
            self.fig_f, self.ax_f = plt.subplots(figsize=(5, 4))
            self.fig_f.patch.set_facecolor('#1a1b26')
            self.canvas_f = FigureCanvas(self.fig_f)
            layout = QVBoxLayout(self.ui_content.frame_4)
            layout.addWidget(self.canvas_f)
        
        self.ax_f.clear()

        # 3. Graficar: Presupuesto vs Gasto vs Restante
        labels = ['Presupuesto', 'Gasto Nómina', 'Disponible']
        valores = [presupuesto_total, gasto_nomina, presupuesto_restante]
        # El disponible cambia a rojo si es negativo
        colores = ['#7aa2f7', '#f7768e', '#73daca' if presupuesto_restante > 0 else '#ff0033']

        self.ax_f.bar(labels, valores, color=colores, alpha=0.8)
        
        # Estética y Etiquetas
        self.ax_f.set_title("Balance Mensual de Nómina", color='white', fontweight='bold')
        self.ax_f.tick_params(axis='both', colors='white', labelsize=8)
        
        # Añadir los números sobre las barras con formato de moneda
        for i, v in enumerate(valores):
            self.ax_f.text(i, v + (presupuesto_total * 0.01), f'${v:,.0f}', 
                        ha='center', color='white', fontsize=7, fontweight='bold')

        self.fig_f.tight_layout()
        self.canvas_f.draw()

    def graficar_viabilidad_contratacion(self):
        # 1. Obtener datos financieros
        conn = sqlite3.connect('ingenieria.db')
        cursor = conn.cursor()
        
        # Presupuesto total
        cursor.execute("SELECT monto_total FROM presupuesto_empresa WHERE id = 1")
        presupuesto = cursor.fetchone()[0]
        
        # Gasto actual y salario promedio
        cursor.execute("SELECT SUM(salario_base), AVG(salario_base) FROM empleados")
        datos_nomina = cursor.fetchone()
        gasto_actual = datos_nomina[0] or 0
        salario_promedio = datos_nomina[1] or 1 # Evitar división por cero
        conn.close()

        # 2. Cálculos de viabilidad
        disponible = presupuesto - gasto_actual
        # Cuántos empleados "promedio" caben en lo que sobra
        vacantes_posibles = max(0, int(disponible / salario_promedio))

        # 3. Configurar el Canvas en frame_3
        if not hasattr(self, 'canvas_viabilidad'):
            self.fig_v, self.ax_v = plt.subplots(figsize=(5, 4))
            self.fig_v.patch.set_facecolor('#1a1b26')
            self.canvas_v = FigureCanvas(self.fig_v)
            layout = QVBoxLayout(self.ui_content.frame_3)
            layout.addWidget(self.canvas_v)
        
        self.ax_v.clear()

        # 4. Crear visualización (Donut Chart con texto central)
        labels = ['Ocupado', 'Disponible']
        porcentaje_uso = (gasto_actual / presupuesto) * 100
        porcentaje_libre = 100 - porcentaje_uso if presupuesto > gasto_actual else 0
        
        colores = ['#f7768e', '#73daca'] if porcentaje_uso < 90 else ['#f7768e', '#e0af68']
        if porcentaje_uso >= 100: colores = ['#ff0033', '#414868']

        self.ax_v.pie([porcentaje_uso, porcentaje_libre], colors=colores, 
                    startangle=90, counterclock=False, wedgeprops={'width': 0.3})
        
        # Texto central con la decisión
        color_texto = '#73daca' if vacantes_posibles > 0 else '#f7768e'
        self.ax_v.text(0, 0, f"{vacantes_posibles}\nVacantes", ha='center', va='center', 
                    fontsize=18, fontweight='bold', color=color_texto)
        
        self.ax_v.set_title("Capacidad de Contratación", color='white', pad=10)
        self.canvas_v.draw()