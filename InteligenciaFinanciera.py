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


class InteligenciaFinanciera(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        
        # 1. Cargar el archivo .ui
        loader = QUiLoader()
        archivo_ui = QFile("inteligenciafinanciera.ui")
        
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
            self.setWindowTitle("Riesgo Operacional")
            self.conectar_menu()

            #calculadora de valor futuro
            self.cargar_inventario_financiero()
            self.cargar_selector_carros()
            self.ui_content.pushButton_evaluar.clicked.connect(self.ejecutar_evaluacion_financiera)

            #Rankings de mercado
            self.iniciar_auto_refresh()

            #Simulador de escenarios financieros
            self.cargar_selector_autos()
            self.ui_content.push_observar.clicked.connect(self.evaluar_negocio_reventa)
            self.ui_content.treeWidget_eleccion.setColumnCount(2)
            self.ui_content.treeWidget_eleccion.setHeaderLabels(["Concepto", "Valor"])
            # Ajuste de proporciones
            self.ui_content.treeWidget_eleccion.setColumnWidth(0, 220) # Más espacio para el nombre del auto
            self.ui_content.treeWidget_eleccion.setIndentation(20)      # Espacio para que el sub-nodo se vea adentro

            #balance
            self.ui_content.action_BALANCE.triggered.connect(self.analizar_balance_historico)

            #Dashboard
            self.graficar_resumen_aprobado()
            self.graficar_distribucion_inventario()
            self.graficar_analisis_mercado()
            self.graficar_oferta_mercado()
            
            
            
            

    #pasar paginas
    def conectar_menu(self):
        # Usamos lambda para pasar el número de página deseado
        
        # Dashboard -> Página 0
        self.ui_content.actionGRAFICO.triggered.connect(lambda: self.cambiar_pagina(0))
        
        # Reportes (actionCrud) -> Página 1
        self.ui_content.action_CALCULADORA.triggered.connect(lambda: self.cambiar_pagina(1))
        
        # Operaciones (actionCrud_3) -> Página 2
        self.ui_content.action_RANKING.triggered.connect(lambda: self.cambiar_pagina(2))
        
        # Análisis (actionCrud_2) -> Página 3
        self.ui_content.action_SIMULADOR.triggered.connect(lambda: self.cambiar_pagina(3))

        #
        self.ui_content.action_BALANCE.triggered.connect(lambda: self.cambiar_pagina(4))

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


    #Calculadora De Valor futuro
    def cargar_inventario_financiero(self):
        try:
            # 1. Conexión a la base de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Seleccionamos las columnas clave para el análisis financiero
            query = "SELECT marca, modelo, año, kilometraje, valor_pagado, fecha_compra FROM compras_aprobadas"
            cursor.execute(query)
            datos = cursor.fetchall()
            conn.close()

            # 2. Configuración de la Tabla
            tabla = self.ui_content.tableWidget_carros
            tabla.setRowCount(len(datos))
            tabla.setColumnCount(6)
            
            # Ocultar el índice vertical (los números de fila a la izquierda)
            tabla.verticalHeader().setVisible(False)
            
            # Encabezados basados en tu diseño
            headers = ["MARCA", "MODELO", "AÑO", "KILOMETRAJE", "VALOR PAGADO", "FECHA"]
            tabla.setHorizontalHeaderLabels(headers)

            # 3. Llenado de datos
            for row_number, row_data in enumerate(datos):
                for column_number, data in enumerate(row_data):
                    # Formatear el valor pagado con símbolo de moneda si es la columna 4
                    item_text = f"${data:,.2f}" if column_number == 4 else str(data)
                    tabla.setItem(row_number, column_number, QTableWidgetItem(item_text))

            # 4. Ajustes estéticos finales
            header = tabla.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch) # Expandir columnas
            tabla.setSelectionBehavior(QAbstractItemView.SelectRows) # Seleccionar fila completa
            tabla.setEditTriggers(QAbstractItemView.NoEditTriggers) # Solo lectura

        except Exception as e:
            print(f"Error al cargar tableWidget_carros: {e}")

    def cargar_selector_carros(self):
        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Seleccionamos marca y modelo de la tabla
            query = "SELECT marca, modelo FROM compras_aprobadas"
            cursor.execute(query)
            unidades = cursor.fetchall()
            conn.close()

            self.ui_content.comboBox_carro.clear()
            self.ui_content.comboBox_carro.addItem("Seleccione un vehículo...")
            
            for marca, modelo in unidades:
                # Combinamos ambos campos para una mejor visualización
                self.ui_content.comboBox_carro.addItem(f"{marca.upper()} - {modelo}")

        except Exception as e:
            print(f"Error al cargar comboBox_carro: {e}")

    def ejecutar_evaluacion_financiera(self):
        try:
            # 1. Obtener el Valor Pagado del carro seleccionado en la tabla
            fila_seleccionada = self.ui_content.tableWidget_carros.currentRow()
            if fila_seleccionada == -1:
                self.ui_content.textEdit_mercado.setText("<h2 style='color:red;'>Error: Seleccione un carro en la tabla primero.</h2>")
                return
            
            # Extraemos el valor_pagado (Limpiando el símbolo $ y comas del QTableWidgetItem)
            texto_valor = self.ui_content.tableWidget_carros.item(fila_seleccionada, 4).text()
            valor_pagado = float(texto_valor.replace('$', '').replace(',', ''))

            # 2. Capturar valores de los ComboBox
            # Extraemos solo los números de los strings (ej: "12 meses" -> 12)
            meses = int(self.ui_content.comboBox_tiempo.currentText().split()[0])
            tasa_depreciacion = float(self.ui_content.comboBox_tasa.currentText().split('%')[0]) / 100
            tasa_inflacion = float(self.ui_content.comboBox_inflacion.currentText().split('%')[0]) / 100
            costo_fijo_mensual = float(self.ui_content.comboBox_costo.currentText().replace('$', ''))

            # 3. CÁLCULOS MATEMÁTICOS
            # A. Valor Futuro del Carro (Depreciación + Costos fijos acumulados)s
            valor_futuro_carro = valor_pagado * (1 - (tasa_depreciacion / 12)) ** meses
            total_costos_fijos = costo_fijo_mensual * meses
            valor_real_carro = valor_futuro_carro - total_costos_fijos

            # B. Ganancia en Inversión Alternativa (Costo de Oportunidad)
            # Usamos una tasa de retorno del 10% anual como estándar de mercado
            rendimiento_alterno = valor_pagado * (1 + (0.10 / 12)) ** meses
            ganancia_perdida_neta = valor_real_carro - rendimiento_alterno

            # 4. ACTUALIZAR INTERFAZ (LCD y HTML)
            self.ui_content.lcd_rojo.display(valor_real_carro) # Valor final del activo
            self.ui_content.lcd_verde.display(rendimiento_alterno) # Lo que pudo ganar

            # Generar Reporte HTML para textEdit_mercado
            color_resultado = "#9ece6a" if ganancia_perdida_neta > 0 else "#f7768e"
            veredicto = "RENTABLE" if ganancia_perdida_neta > 0 else "PÉRDIDA DE CAPITAL"

            html_reporte = f"""
            <div style='font-family: Arial; color: #a9b1d6;'>
                <h2 style='color: #7aa2f7; border-bottom: 1px solid #414868;'>REPORTE DE INTELIGENCIA</h2>
                <p><b>Activo Evaluado:</b> {self.ui_content.comboBox_carro.currentText()}</p>
                <p><b>Valor Inicial:</b> <span style='color: white;'>${valor_pagado:,.2f}</span></p>
                <hr>
                <p>Al cabo de <b>{meses} meses</b>:</p>
                <ul>
                    <li>El vehículo valdrá: <b>${valor_real_carro:,.2f}</b></li>
                    <li>La inversión alterna valdría: <b>${rendimiento_alterno:,.2f}</b></li>
                </ul>
                <h3 style='color: {color_resultado};'>RESULTADO NETO: ${ganancia_perdida_neta:,.2f}</h3>
                <div style='background-color: #24283b; padding: 10px; border-radius: 5px;'>
                    <b style='color: white;'>VEREDICTO ESTRATÉGICO:</b> 
                    <span style='color: {color_resultado};'>{veredicto}</span>
                </div>
            </div>
            """
            self.ui_content.textEdit_mercado.setHtml(html_reporte)

        except Exception as e:
            print(f"Error en evaluación: {e}")

    

    #Rankings de mercado
    def actualizar_ranking_rentabilidad(self):
        try:
            # Conexión a la base de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Query: Traemos los datos de la tabla 'carros'
            # Ordenamos por año (de más nuevo a más viejo) y luego por menos KM
            query = """
                SELECT marca, modelo, año, kilometraje, precio 
                FROM carros 
                ORDER BY año DESC, kilometraje ASC
            """
            cursor.execute(query)
            datos = cursor.fetchall()
            conn.close()

            # Configuración del tableWidget_ranking
            tabla = self.ui_content.tableWidget_ranking # Asegúrate que se llame así en Qt Designer
            tabla.setRowCount(len(datos))
            tabla.setColumnCount(5)
            
            # Estética: Sin números de fila (índices) y solo lectura
            tabla.verticalHeader().setVisible(False)
            tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
            tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
            
            # Encabezados
            headers = ["MARCA", "MODELO", "AÑO", "KM", "PRECIO"]
            tabla.setHorizontalHeaderLabels(headers)

            # Llenado de datos
            for row_idx, row_data in enumerate(datos):
                for col_idx, valor in enumerate(row_data):
                    # Formatear precio con signo de dólar
                    texto = f"${valor:,.2f}" if col_idx == 4 else str(valor)
                    item = QTableWidgetItem(texto)
                    
                    # Opcional: Centrar el texto para que se vea más ordenado
                    item.setTextAlignment(Qt.AlignCenter) 
                    
                    tabla.setItem(row_idx, col_idx, item)

            # Ajustar columnas al ancho del widget
            tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        except Exception as e:
            print(f"Error al actualizar el ranking: {e}")

    def iniciar_auto_refresh(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_ranking_rentabilidad)
        self.timer.start(10000) # 10 segundos
        
        # Llamada inicial para que no aparezca vacía al abrir
        self.actualizar_ranking_rentabilidad()


    
    #simulador de escenarios financieros

    def cargar_selector_autos(self):
        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Consultamos la tabla 'carros'
            query = "SELECT marca, modelo FROM carros"
            cursor.execute(query)
            unidades = cursor.fetchall()
            conn.close()

            self.ui_content.cb_autos.clear()
            self.ui_content.cb_autos.addItem("Seleccione un vehículo...")

            for marca, modelo in unidades:
                # Mantenemos el formato para el split posterior
                self.ui_content.cb_autos.addItem(f"{marca.upper()} - {modelo}")
                
        except Exception as e:
            print(f"Error al cargar combo_carros: {e}")


    def evaluar_negocio_reventa(self):
        print("Iniciando evaluación...")
        try:
            # 1. Obtener selección y limpiar espacios
            seleccion = self.ui_content.cb_autos.currentText()
            if "Seleccione" in seleccion or not seleccion:
                self.ui_content.textEdit_texto.setHtml("<h2 style='color:#f7768e;'>Seleccione un auto primero</h2>")
                return

            partes = seleccion.split(" - ")
            marca = partes[0].strip().lower()  # Convertimos a minúsculas para comparar
            modelo = partes[1].strip().lower() # Convertimos a minúsculas para comparar
            print(f"Buscando en DB (Normalizado): {marca} {modelo}")

            # 2. Consulta SQL Insensible a Mayúsculas
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Usamos LOWER() en la consulta para que coincida siempre
            query = 'SELECT precio, "año", kilometraje FROM carros WHERE LOWER(marca)=? AND LOWER(modelo)=?'
            cursor.execute(query, (marca, modelo))
            resultado = cursor.fetchone()
            conn.close()

            if not resultado:
                # Si aún no lo encuentra, mostramos un aviso en el TextEdit para debug
                self.ui_content.textEdit_texto.setHtml(f"<b style='color:orange;'>Auto {marca} {modelo} no hallado en inventario.</b>")
                print(f"No se encontró el resultado para: {marca} {modelo}")
                return

            # 3. Extraer datos con seguridad
            precio_base = float(resultado[0])
            anio = resultado[1]
            km = resultado[2]

            # 4. Obtener valores de los simuladores
            meses_txt = self.ui_content.cb_tiempo.currentText()
            meses = int(meses_txt.split()[0]) if meses_txt else 1
            
            # Tasa de depreciación según el combo
            tasa_txt = self.ui_content.comboBox_tasa.currentText()
            tasa_anual = float(tasa_txt.split('%')[0]) / 100 if tasa_txt else 0.05
            
            # 5. Cálculos de Escenario
            costo_almacenamiento = 50.0  # Según tu UI
            total_gastos = meses * costo_almacenamiento
            
            # Depreciación proyectada
            valor_final = precio_base * (1 - (tasa_anual * (meses/12)))
            utilidad = valor_final - precio_base - total_gastos

            # 6. Mostrar Reporte Visual
            color_res = "#9ece6a" if utilidad > 0 else "#f7768e"
            html = f"""
            <div style='font-family: Arial; color: #a9b1d6;'>
                <h2 style='color: #7aa2f7;'>RESULTADO DE SIMULACIÓN</h2>
                <p>Vehículo: <b style='color:white;'>{seleccion}</b></p>
                <hr style='border: 1px solid #414868;'>
                <p>Precio Base: ${precio_base:,.2f}</p>
                <p>Gastos Operativos: ${total_gastos:,.2f}</p>
                <h1 style='color: {color_res};'>UTILIDAD: ${utilidad:,.2f}</h1>
            </div>
            """
            self.ui_content.textEdit_texto.setHtml(html)
            # 1. Primero muestras el resultado en el texto
            self.ui_content.textEdit_texto.setHtml(html)

            # 2. AHORA llamas al historial pasando las variables correctas
            self.agregar_al_historial(seleccion, utilidad)
            # Llamada a la gráfica (usa las variables que ya calculaste)
            self.graficar_escenario(precio_base, meses, 0.08)
            
            print("Historial actualizado correctamente.")

        except Exception as e:
            print(f"Error detallado: {e}")

    
    #tree widget historial

    def agregar_al_historial(self, auto, utilidad):
        # Necesitamos estas herramientas de PySide6 para colores y estilos
        from PySide6.QtGui import QColor, QBrush
        from PySide6.QtWidgets import QTreeWidgetItem
        from datetime import datetime

        tree = self.ui_content.treeWidget_eleccion
        

        # 2. Control de límite (15 registros)
        if tree.topLevelItemCount() >= 15:
            tree.takeTopLevelItem(tree.topLevelItemCount() - 1)

        # 3. Crear el Registro (Padre)
        hora = datetime.now().strftime("%H:%M:%S")
        item_padre = QTreeWidgetItem()
        # Insertar siempre al principio para que el último se vea arriba
        tree.insertTopLevelItem(0, item_padre)
        
        item_padre.setText(0, f"🚗 {auto}")
        item_padre.setText(1, f"Hora: {hora}")

        # 4. SOLUCIÓN AL ERROR: Convertir texto a QColor
        color_hex = "#9ece6a" if utilidad > 0 else "#f7768e"
        item_padre.setForeground(0, QBrush(QColor(color_hex))) 
        item_padre.setForeground(1, QBrush(QColor("#7aa2f7")))

        # 5. Detalle Interno
        detalle = QTreeWidgetItem(item_padre)
        detalle.setText(0, "   → Resultado Financiero:")
        detalle.setText(1, f"${utilidad:,.2f}")
        
        # Color del sub-item
        detalle.setForeground(1, QBrush(QColor("white")))
        
        # Mantener las carpetas cerradas para orden
        item_padre.setExpanded(False)
       

    def graficar_escenario(self, precio_inicial, meses, tasa_depreciacion):
        # 1. Obtener el layout del frame_12 o crearlo si no existe
        layout = self.ui_content.frame_12.layout()
        
        if layout is None:
            # Si el frame no tiene layout en Designer, lo creamos por código
            from PySide6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(self.ui_content.frame_12)
            self.ui_content.frame_12.setLayout(layout)
        else:
            # Si ya existe, limpiamos lo que haya (gráficas viejas)
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # 2. Cálculos para la curva de depreciación
        meses_x = np.linspace(0, meses, 10)
        # Fórmula: Valor = Inicial * (1 - tasa_mensual)^mes
        valores_y = [precio_inicial * (0.992 ** m) for m in meses_x]

        # 3. Diseño de la gráfica (Estilo Dark)
        fig, ax = plt.subplots(figsize=(4, 3), dpi=80)
        fig.patch.set_facecolor('#1a1b26') # Fondo exterior
        ax.set_facecolor('#1a1b26')        # Fondo interior

        ax.plot(meses_x, valores_y, color='#7aa2f7', linewidth=3, marker='o', markersize=4)
        ax.fill_between(meses_x, valores_y, color='#7aa2f7', alpha=0.1) # Sombreado

        # Estética de los ejes
        ax.set_title("DEPRECIACIÓN PROYECTADA", color='white', fontsize=9, fontweight='bold')
        ax.tick_params(axis='both', colors='#565f89', labelsize=8)
        ax.grid(True, linestyle='--', alpha=0.1)
        
        for spine in ax.spines.values():
            spine.set_visible(False) # Quitar bordes para que se vea moderno

        # 4. Mostrar en el UI
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        plt.close(fig) # Liberar memoria



    #Balance
    def analizar_balance_historico(self):

        ruta = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Sentimiento"
        
        try:
            # 1. Obtener archivos y ordenar por fecha
            archivos = [os.path.join(ruta, f) for f in os.listdir(ruta) if f.endswith('.xlsx')]
            archivos.sort(key=os.path.getctime)

            if len(archivos) < 2:
                print("Se necesitan al menos 2 reportes para comparar.")
                return

            # 2. Leer extremos: El primero de la historia y el último generado
            df_ancla = pd.read_excel(archivos[0])
            df_actual = pd.read_excel(archivos[-1])

            # Extraer Balance Neto de AutoMetrics Labs
            v_inicial = df_ancla[df_ancla['Empresa'] == 'AutoMetrics Labs']['Balance Neto'].iloc[0]
            v_actual = df_actual[df_actual['Empresa'] == 'AutoMetrics Labs']['Balance Neto'].iloc[0]

            # 3. Limpiar frame_13
            layout = self.ui_content.frame_13.layout()
            if layout is None:
                from PySide6.QtWidgets import QVBoxLayout
                layout = QVBoxLayout(self.ui_content.frame_13)
            else:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget(): child.widget().deleteLater()

            # 4. Crear Gráfica con Matplotlib
            fig, ax = plt.subplots(figsize=(5, 4), dpi=90)
            fig.patch.set_facecolor('#1a1b26')
            # Centrar y ajustar márgenes automáticamente
            fig.tight_layout()
            ax.set_facecolor('#1a1b26')

            etiquetas = ['Histórico (Ancla)', 'Actual']
            valores = [v_inicial, v_actual]
            colores = ['#414868', '#7aa2f7' if v_actual >= v_inicial else '#f7768e']

            ax.bar(etiquetas, valores, color=colores, width=0.5)
            ax.set_title("EVOLUCIÓN DE BALANCE NETO", color='white', fontweight='bold')
            ax.tick_params(axis='both', colors='#a9b1d6')
            
            # Eliminar bordes para que se vea más limpio
            for spine in ax.spines.values(): spine.set_visible(False)

            # 5. Renderizar en el frame y cerrar figura
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)
            plt.close(fig) # Previene el error de las 20 figuras

        except Exception as e:
            print(f"Error al actualizar balance: {e}")


    #Dashboard
    def graficar_resumen_aprobado(self):

        try:
            conn = sqlite3.connect('ingenieria.db')
            
            # Query basado en tu tabla real: compras_aprobadas
            # Agrupamos por marca y sumamos el valor_pagado
            query = """
                SELECT marca, SUM(valor_pagado) as inversion_total 
                FROM compras_aprobadas 
                GROUP BY marca 
                ORDER BY inversion_total DESC 
                LIMIT 5
            """
            df_resumen = pd.read_sql_query(query, conn)
            conn.close()

            if df_resumen.empty:
                print("No hay compras aprobadas para mostrar.")
                return

            # Configuración del Layout en frame_aprobado
            layout = self.ui_content.frame_aprobado.layout()
            if layout is None:
                from PySide6.QtWidgets import QVBoxLayout
                layout = QVBoxLayout(self.ui_content.frame_aprobado)
                self.ui_content.frame_aprobado.setLayout(layout)
            else:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget(): child.widget().deleteLater()

            # Crear Gráfica de Barras (Inversión por Marca)
            fig, ax = plt.subplots(figsize=(5, 4), dpi=90)
            fig.patch.set_facecolor('#1a1b26')
            ax.set_facecolor('#1a1b26')

            # Usamos un color verde esmeralda para representar "Inversión/Dinero"
            ax.bar(df_resumen['marca'], df_resumen['inversion_total'], color='#73daca', width=0.6)
            
            ax.set_title("INVERSIÓN TOTAL POR MARCA", color='white', fontweight='bold', pad=20)
            ax.tick_params(axis='x', colors='white', labelsize=8)
            ax.tick_params(axis='y', colors='#565f89', labelsize=8)
            
            # Quitar bordes innecesarios
            for spine in ax.spines.values():
                spine.set_visible(False)

            fig.tight_layout()
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)
            plt.close(fig)

        except Exception as e:
            print(f"Error en dashboard de compras: {e}")

    def graficar_distribucion_inventario(self):

        try:
            conn = sqlite3.connect('ingenieria.db')
            # Traemos marca y modelo para contar cuántos vehículos hay de cada uno
            query = "SELECT marca, modelo FROM compras_aprobadas"
            df_inventario = pd.read_sql_query(query, conn)
            conn.close()

            if df_inventario.empty:
                print("No hay datos en compras_aprobadas para el frame_2.")
                return

            # Contamos cuántos carros hay por marca
            conteo_marcas = df_inventario['marca'].value_counts()

            # Configuración del Layout en frame_2
            layout = self.ui_content.frame_2.layout()
            if layout is None:
                from PySide6.QtWidgets import QVBoxLayout
                layout = QVBoxLayout(self.ui_content.frame_2)
            else:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget(): child.widget().deleteLater()

            # Crear Gráfica de Donut
            fig, ax = plt.subplots(figsize=(5, 4), dpi=90)
            fig.patch.set_facecolor('#1a1b26')
            ax.set_facecolor('#1a1b26')

            # Colores modernos (paleta Tokyo Night)
            colores = ['#7aa2f7', '#bb9af7', '#7dcfff', '#e0af68', '#9ece6a']

            # Dibujar el gráfico de pastel
            wedges, texts, autotexts = ax.pie(
                conteo_marcas, 
                labels=conteo_marcas.index, 
                autopct='%1.1f%%', 
                startangle=140, 
                colors=colores,
                pctdistance=0.85,
                textprops={'color':"w", 'fontsize': 8}
            )

            # Dibujar el círculo blanco en medio para que parezca un Donut
            centre_circle = plt.Circle((0,0), 0.70, fc='#1a1b26')
            fig.gca().add_artist(centre_circle)

            ax.set_title("COMPOSICIÓN DEL INVENTARIO", color='white', fontweight='bold', pad=10)
            
            fig.tight_layout()
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)
            plt.close(fig)

        except Exception as e:
            print(f"Error en dashboard (frame_2): {e}")

    def graficar_analisis_mercado(self):

        try:
            conn = sqlite3.connect('ingenieria.db')
            # Query de tu tabla de mercado general (carros)
            query = """
                SELECT marca, modelo, año, kilometraje, precio 
                FROM carros 
                ORDER BY año DESC, kilometraje ASC
            """
            df_carros = pd.read_sql_query(query, conn)
            conn.close()

            if df_carros.empty:
                print("No hay datos en la tabla carros para el frame_4.")
                return

            # Configuración del Layout
            layout = self.ui_content.frame_4.layout()
            if layout is None:
                from PySide6.QtWidgets import QVBoxLayout
                layout = QVBoxLayout(self.ui_content.frame_4)
            else:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget(): child.widget().deleteLater()

            # Crear Gráfica de Dispersión
            fig, ax = plt.subplots(figsize=(5, 4), dpi=90)
            fig.patch.set_facecolor('#1a1b26')
            ax.set_facecolor('#1a1b26')

            # Graficar Kilometraje vs Precio
            # El color (c) varía según el año para dar una tercera dimensión visual
            scatter = ax.scatter(
                df_carros['kilometraje'], 
                df_carros['precio'], 
                c=df_carros['año'], 
                cmap='viridis', 
                alpha=0.7, 
                edgecolors='w',
                s=80 # Tamaño de los puntos
            )

            # Estética
            ax.set_title("PRECIO VS. KILOMETRAJE (POR AÑO)", color='white', fontweight='bold')
            ax.set_xlabel("Kilometraje", color='#a9b1d6', fontsize=8)
            ax.set_ylabel("Precio ($)", color='#a9b1d6', fontsize=8)
            ax.tick_params(axis='both', colors='#565f89', labelsize=8)
            
            # Añadir barra de color para identificar el año
            cbar = plt.colorbar(scatter)
            cbar.ax.set_ylabel('Año del Vehículo', color='white', rotation=270, labelpad=15)
            cbar.ax.yaxis.set_tick_params(color='white', labelcolor='white')

            ax.grid(True, linestyle='--', alpha=0.1)
            for spine in ax.spines.values(): spine.set_visible(False)

            fig.tight_layout()
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)
            plt.close(fig)

        except Exception as e:
            print(f"Error en dashboard (frame_4): {e}")

    def graficar_oferta_mercado(self):

        try:
            # 1. Obtener datos de la tabla confirmada
            conn = sqlite3.connect('ingenieria.db')
            query = "SELECT marca FROM carros"
            df_mercado = pd.read_sql_query(query, conn)
            conn.close()

            if df_mercado.empty:
                return

            conteo_oferta = df_mercado['marca'].value_counts().head(6)

            # 2. Limpieza de interfaz
            layout = self.ui_content.frame_3.layout()
            if layout is None:
                from PySide6.QtWidgets import QVBoxLayout
                layout = QVBoxLayout(self.ui_content.frame_3)
            else:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget(): child.widget().deleteLater()

            # 3. Creación de la Gráfica
            # Ajustamos el tamaño para que quepa bien en el frame_3
            fig, ax = plt.subplots(figsize=(4, 3), dpi=90)
            
            # EL COLOR VA EN LA FIGURA (fig) Y EN EL AREA DE DIBUJO (ax)
            fig.patch.set_facecolor('#1a1b26') 
            ax.set_facecolor('#1a1b26')

            # Gráfico de barras simple para evitar errores de complejidad
            colores_neon = ['#bb9af7', '#7aa2f7', '#7dcfff', '#e0af68', '#9ece6a', '#f7768e']
            ax.bar(conteo_oferta.index, conteo_oferta.values, color=colores_neon)

            # Estética
            ax.set_title("OFERTA POR MARCA", color='white', fontsize=10, fontweight='bold')
            ax.tick_params(axis='x', colors='#a9b1d6', labelsize=7, rotation=30)
            ax.tick_params(axis='y', colors='#a9b1d6', labelsize=7)
            
            # Eliminar bordes (spines)
            for spine in ax.spines.values():
                spine.set_visible(False)

            # 4. PASO CRÍTICO: El canvas NO recibe configuración de color
            fig.tight_layout()
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)
            
            # 5. SOLUCIÓN AL ERROR DE MEMORIA
            plt.close(fig) 

        except Exception as e:
            print(f"Error final en frame_3: {e}")