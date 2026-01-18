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
from situaciones import DICCIONARIO_BRECHAS , MANIFESTACIONES
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image, ImageDraw, ImageFont


class riesgo(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        
        # 1. Cargar el archivo .ui
        loader = QUiLoader()
        archivo_ui = QFile("RiesgoOperacional.ui")
        
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

        #análisis de liquidez
        self.actualizar_inventario_riesgo()# Para que se vean las carpetas abiertas
        self.ui_content.treeWidget_aprobado.itemClicked.connect(self.mostrar_detalles_carro)
        self.ui_content.tableWidget_riesgo.itemClicked.connect(self.detalles_desde_tabla)
        self.cargar_tabla_riesgo()
        self.ui_content.horizontalSlider_2.setRange(0, 365)
        self.ui_content.horizontalSlider_2.valueChanged.connect(self.cargar_tabla_riesgo)
        self.ui_content.btn_evaluar.clicked.connect(self.evaluar_descuento_riesgo)
        self.cargar_tabla_carros()


        #CiberSeguridad
        # 1. Creamos el temporizador y lo vinculamos a la clase
        self.consola_seguridad = self.ui_content.findChild(QPlainTextEdit, "plainTextEdit_2")
        self.timer_seguridad = QTimer(self)
        self.timer_seguridad.timeout.connect(self.generar_flujo_datos)
        
        # Iniciar el flujo (100ms es una buena velocidad hacker)
        self.timer_seguridad.start(2400)
        # Reemplaza 'btn_comprobar' por el ID real que le pusiste en Qt Designer
        self.ui_content.btn_comprobar.clicked.connect(self.interceptar_ataque)

        header = self.ui_content.tableWidget_persona.horizontalHeader()

        # Esto obliga a las columnas a estirarse para llenar el cuadro negro
        header.setSectionResizeMode(QHeaderView.Stretch) 

        # Si quieres que la tabla no tenga scroll horizontal innecesario:
        self.ui_content.tableWidget_persona.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cargar_tabla_personas()
        self.conectar_db()
        self.ui_content.btn_comprobar.clicked.connect(self.procesar_seguridad)
        self.ui_content.push_anadir.clicked.connect(self.administrador_anadir_usuario)


        #Datos De Mercado Inteligente
        
        self.timer_noticias = QTimer(self)
        self.timer_noticias.timeout.connect(self.ciclo_inteligencia_mercado)
        self.timer_noticias.start(7000)
        self.historial_velas = []
        self.precio_accion_actual = 50000.0
        self.acciones_rivales = {}
        self.mercado_actual = 500000.0  # El mercado empieza en medio millón
        self.indice_tiempo = 0
        self.analisis_empresas = {} 
        # Estructura: {'Nombre': {'ganado': 0, 'perdido': 0, 'sentimiento': 'NEUTRAL'}}
        self.hora_inicio_mercado = time.time()
        self.ui_content.treeWidget_sentimiento.itemClicked.connect(self.mostrar_detalle_empresa)
        self.ui_content.treeWidget_sentimiento.setHeaderLabels(["Empresa", "Ganado", "Perdido", "Sentimiento"])
        self.ui_content.treeWidget_sentimiento.setColumnCount(4)
        # 1. Hacer que las columnas se estiren automáticamente
        header = self.ui_content.treeWidget_sentimiento.header()
        header.setSectionResizeMode(QHeaderView.Stretch) # Todas las columnas iguales

        # Opcional: Si quieres que la columna "Empresa" sea más ancha que las demás:
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)


        #gestion De Cumplmiento
        # Configura los títulos de las columnas
        self.ui_content.treeWidget_empleados.setHeaderLabels(["Empleado", "Cargo", "Velocidad"])
        # Ajusta el ancho para que el texto no se corte
        self.ui_content.treeWidget_empleados.setColumnWidth(0, 150)
        self.ui_content.treeWidget_empleados.setColumnWidth(1, 150)
        self.cargar_empleados_en_tree()

        self.ui_content.tableWidget_clientes.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui_content.tableWidget_clientes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cargar_clientes_en_tabla()

        # Si el usuario elige en la tabla, el combo se actualiza
        self.ui_content.tableWidget_clientes.itemClicked.connect(
            lambda item: self.ui_content.comboBox_cliente.setCurrentText(
                self.ui_content.tableWidget_clientes.item(item.row(), 0).text()
            )
        )
        self.cargar_combos_datos()
        self.cargar_emociones_unicas()

        self.ui_content.push_conversa.clicked.connect(self.iniciar_simulacion_chat)


        #stock
        # --- NUEVA LÓGICA DE SIMULACIÓN FINANCIERA ---
        self.presupuesto = 50000.0  # Dinero inicial
        self.mes_multiplicador = 1.0
        
        # Mapeo exacto de tus Sliders de Designer
        self.mapa_sliders = {
            1: self.ui_content.verticalSlider_vehiculo,
            2: self.ui_content.verticalSlider_repuestos,
            3: self.ui_content.verticalSlider_ti,
            4: self.ui_content.verticalSlider_oficina,
            5: self.ui_content.verticalSlider_flota,
            6: self.ui_content.verticalSlider_aseo,
            7: self.ui_content.verticalSlider_epp,
            8: self.ui_content.verticalSlider_marketing
        }

        # Timer para el "latido" de la empresa (cada 3 segundos)
        self.timer_simulador = QTimer(self)
        self.timer_simulador.timeout.connect(self.ejecutar_ciclo_empresarial)
        self.timer_simulador.start(3000)

        # Mapeo de los LCDNumbers de Designer
        self.mapa_lcds = {
            1: self.ui_content.lcdNumber_vehiculo,
            2: self.ui_content.lcdNumber_repuestos,
            3: self.ui_content.lcdNumber_ti,
            4: self.ui_content.lcdNumber_oficina,
            5: self.ui_content.lcdNumber_flota,
            6: self.ui_content.lcdNumber_aseo,
            7: self.ui_content.lcdNumber_epp,
            8: self.ui_content.lcdNumber_marketing
        }
        
        # Historial para gráficos
        self.historial_ganancias = []
        self.historial_gastos = []
    
        
        #continuacion empresa
       
        self.cargar_empresas_banco() 
        # Conecta el cambio de selección para que las cantidades se actualicen solas
        self.ui_content.comboBox_empresa.currentIndexChanged.connect(self.actualizar_opciones_prestamo)
        # Llama una vez al inicio para llenar el primer valor
        self.actualizar_opciones_prestamo()
       
        self.ui_content.pushButton_evaluar.clicked.connect(self.evaluar_prestamo_bancario)


        #Dashboard
        self.obtener_datos_liquidez_db()
        self.refrescar_dashboard_liquidez()
        self.graficar_confianza_mercado()
        self.graficar_frecuencia_compras_db()
        self.graficar_seguridad_activos_db()
        self.graficar_eficiencia_empleados_db()
        self.graficar_analisis_casos_clientes()
        
        

        


    #pasar paginas
    def conectar_menu(self):
        # Usamos lambda para pasar el número de página deseado
        
        # Dashboard -> Página 0
        self.ui_content.actionGRAF_CA.triggered.connect(lambda: self.cambiar_pagina(0))
        
        # Reportes (actionCrud) -> Página 1
        self.ui_content.action_iquidez.triggered.connect(lambda: self.cambiar_pagina(1))
        
        # Operaciones (actionCrud_3) -> Página 2
        self.ui_content.action_accesos.triggered.connect(lambda: self.cambiar_pagina(2))
        
        # Análisis (actionCrud_2) -> Página 3
        self.ui_content.action_inteligencia.triggered.connect(lambda: self.cambiar_pagina(3))

        #
        self.ui_content.action_gestion.triggered.connect(lambda: self.cambiar_pagina(4))
        #
        self.ui_content.action_inventario.triggered.connect(lambda: self.cambiar_pagina(5))
        #
        self.ui_content.action_negocio.triggered.connect(lambda: self.cambiar_pagina(6))
        #
        

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

    
    
    #anälisis de liquidez 


    def actualizar_inventario_riesgo(self):
        # Usamos self.ui_content porque ahí se cargó tu archivo .ui
        tabla = self.ui_content.treeWidget_aprobado 
        tabla.clear()
        
        # 1. Crear carpetas principales
        root_verde = QTreeWidgetItem(tabla, ["NUEVOS (Alta Liquidez)"])
        root_amarillo = QTreeWidgetItem(tabla, ["EN OBSERVACIÓN (30-60 días)"])
        root_rojo = QTreeWidgetItem(tabla, ["RIESGO CRÍTICO (+60 días)"])
        
        # 2. Conexión (Asegúrate que el nombre de la DB sea exacto)
        conn = sqlite3.connect('Ingenieria.db') 
        cursor = conn.cursor()
        cursor.execute("SELECT marca, modelo, año, fecha_compra, valor_pagado FROM compras_aprobadas")
        
        fecha_actual = datetime.now() # Hoy es 2026-01-11
        
        for fila in cursor.fetchall():
            marca, modelo, año, fecha_str, valor = fila
            fecha_compra = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
            
            # Diferencia de días real
            dias_en_stock = (fecha_actual - fecha_compra).days
            
            item = QTreeWidgetItem([f"{marca} {modelo}", f"{dias_en_stock} días", f"${valor:,.2f}"])
            
            # 3. Clasificación por colores
            if dias_en_stock < 30:
                root_verde.addChild(item)
                item.setForeground(0, QColor("#00ffcc"))
            elif 30 <= dias_en_stock <= 60:
                root_amarillo.addChild(item)
                item.setForeground(0, QColor("#ffcc00"))
            else:
                root_rojo.addChild(item)
                item.setForeground(0, QColor("#ff4d4d"))
                
        conn.close()
        tabla.expandAll()


    def mostrar_detalles_carro(self, item, column):
        # Evitar carpetas raíz
        if item.childCount() > 0:
            return

        nombre_carro = item.text(0)
        dias = item.text(1)
        valor = item.text(2)
        
        try:
            conn = sqlite3.connect('Ingenieria.db')
            cursor = conn.cursor()
            marca_modelo = nombre_carro.split(" (")[0] 
            cursor.execute("SELECT fecha_compra FROM compras_aprobadas WHERE marca || ' ' || modelo = ?", (marca_modelo,))
            resultado = cursor.fetchone()
            
            if resultado:
                fecha_exacta = resultado[0]
                
                # --- Formato Centrado y Grande ---
                # Usamos separadores visuales para centrar el contenido a la vista
                separador = "=" * 40
                espacio = " " * 10 # Simulación de centrado manual
                
                mensaje = (
                    f"\n{separador}\n"
                    f"{espacio} 📝 REGISTRO DE AUDITORÍA\n"
                    f"{separador}\n"
                    f"  VEHÍCULO: {nombre_carro.upper()}\n"
                    f"  ADQUISICIÓN: {fecha_exacta}\n"
                    f"  ESTANCAMIENTO: {dias}\n"
                    f"  VALOR EN RIESGO: {valor}\n"
                    f"{separador}\n"
                )
                
                # .appendPlainText mantiene lo anterior y añade lo nuevo al final
                self.ui_content.plainTextEdit.appendPlainText(mensaje)
                
                # Auto-scroll al final para ver el último reporte
                self.ui_content.plainTextEdit.verticalScrollBar().setValue(
                    self.ui_content.plainTextEdit.verticalScrollBar().maximum()
                )
                
            conn.close()
        except Exception as e:
            print(f"Error al recuperar fecha: {e}")

    #tablewwidget

    def cargar_tabla_riesgo(self):
        # 1. Referencia a la tabla y limpieza inicial
        tabla = self.ui_content.tableWidget_riesgo
        tabla.setRowCount(0)
        
        # 2. Configuración visual fija (Evita que se encoja)
        tabla.verticalHeader().setVisible(False)
        tabla.setColumnCount(7)
        tabla.setHorizontalHeaderLabels(["Marca", "Modelo", "Año", "KM", "Puntaje", "Precio", "Fecha Compra"])
        
        # IMPORTANTE: Solo usar Stretch una vez para que no recalcule el tamaño erróneamente
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 3. Obtener el valor del slider para el filtro
        dias_minimos = self.ui_content.horizontalSlider_2.value()
        
        try:
            conn = sqlite3.connect('Ingenieria.db')
            cursor = conn.cursor()
            cursor.execute("SELECT marca, modelo, año, kilometraje, puntaje_inspeccion, valor_pagado, fecha_compra FROM compras_aprobadas")
            
            datos = cursor.fetchall()
            fecha_actual = datetime.now() # Hoy es 2026-01-11
            
            for fila in datos:
                fecha_str = fila[6]
                fecha_compra = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
                
                # Calcular antigüedad
                dias_en_stock = (fecha_actual - fecha_compra).days
                
                # FILTRO DINÁMICO
                if dias_en_stock >= dias_minimos:
                    row_idx = tabla.rowCount()
                    tabla.insertRow(row_idx)
                    
                    for col_idx, valor in enumerate(fila):
                        item = QTableWidgetItem(str(valor))
                        
                        # Color base blanco para visibilidad
                        item.setForeground(QColor("#ffffff"))
                        
                        # Estilización por antigüedad (Filas Rojas/Amarillas)
                        if dias_en_stock > 60:
                            item.setForeground(QColor("#ff4d4d")) # Rojo Crítico
                        elif dias_en_stock > 30:
                            item.setForeground(QColor("#ffcc00")) # Amarillo Alerta
                            
                        # Validación adicional por puntaje de inspección (Puntaje < 80)
                        if col_idx == 4 and int(valor) < 80:
                            item.setBackground(QColor(255, 77, 77, 40)) # Fondo rojizo sutil
                        
                        tabla.setItem(row_idx, col_idx, item)
                        
            conn.close()
            
        except Exception as e:
            print(f"Error en el filtrado de tabla: {e}")
            

    def detalles_desde_tabla(self, item):
        row = item.row()
        # Obtenemos los datos de la fila seleccionada
        marca = self.ui_content.tableWidget_riesgo.item(row, 0).text()
        modelo = self.ui_content.tableWidget_riesgo.item(row, 1).text()
        fecha = self.ui_content.tableWidget_riesgo.item(row, 6).text()
        
        # Mandamos a la consola con el formato grande y centrado que creamos
        separador = "=" * 40
        mensaje = (
            f"\n{separador}\n"
            f"       🔍 INSPECCIÓN DE TABLA\n"
            f"{separador}\n"
            f"  ACTIVO: {marca} {modelo}\n"
            f"  FECHA REGISTRO: {fecha}\n"
            f"{separador}\n"
        )
        self.ui_content.plainTextEdit.appendPlainText(mensaje)


    #evaluar Descuento

    def evaluar_descuento_riesgo(self):
        # 1. Capturar respuestas
        respuestas = [
            self.ui_content.comboBox_Costo.currentText().lower(),
            self.ui_content.comboBox_Bajado.currentText().lower(),
            self.ui_content.comboBox_Tiempo.currentText().lower(),
            self.ui_content.comboBox_Existe.currentText().lower()
        ]
        
        conteo_si = respuestas.count("si")
        
        # 2. Definir variables para la ventana
        titulo = "Resultado de Evaluación de Riesgo"
        descuento = 0
        icono = QMessageBox.Information

        if conteo_si == 4:
            descuento = 80
            mensaje = f"⚠️ ALERTA CRÍTICA\n\nEl activo presenta un riesgo operacional máximo.\nSe recomienda un descuento del {descuento}% para salida inmediata."
            icono = QMessageBox.Critical
        elif conteo_si == 3:
            descuento = 50
            mensaje = f"🔸 RIESGO ELEVADO\n\nLa mayoría de factores son negativos.\nSe sugiere un descuento del {descuento}%."
            icono = QMessageBox.Warning
        elif conteo_si == 2:
            descuento = 20
            mensaje = f"🔹 RIESGO MODERADO\n\nEvaluación balanceada.\nSe sugiere un descuento promocional del {descuento}%."
            icono = QMessageBox.Question
        elif conteo_si == 1:
            descuento = 10
            mensaje = f"✅ RIESGO BAJO\n\nSolo un factor de riesgo detectado.\nDescuento mínimo opcional del {descuento}%."
        else:
            mensaje = "🌟 EXCELENTE ESTADO\n\nNo se detectaron factores de riesgo. Mantener precio de lista."
            icono = QMessageBox.Information

        # 3. Crear y mostrar la ventana emergente
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(icono)
        
        # Aplicar un poco de estilo neón a la ventana emergente para que combine
        msg_box.setStyleSheet("""
            QMessageBox { background-color: #1e1e2e; }
            QLabel { color: #ffffff; font-size: 14px; font-weight: bold; }
            QPushButton { background-color: #00ffcc; color: #1e1e2e; border-radius: 5px; padding: 5px 15px; }
        """)
        
        msg_box.exec()


    
    #Seguridad De Datos y Accesos



    def generar_llave_vehiculo(self, marca, modelo, año):
        # Creamos una cadena única basada en los datos del carro
        semilla = f"{marca}{modelo}{año}2026_SECRET_KEY"
        
        # Generamos el Hash SHA-256
        hash_objeto = hashlib.sha256(semilla.encode())
        hash_resultado = hash_objeto.hexdigest()
        
        # Este es el código que iría en la "Tarjeta" del cliente
        return hash_resultado[:16].upper() # Usamos los primeros 16 caracteres para que sea manejable
    


    def generar_flujo_datos(self):
        
        
        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            # Pedimos los datos exactos que manejas en tu formulario/encuesta
            cursor.execute("SELECT carro_hash, usuario_asignado, ip_ultimo_acceso, nivel_riesgo_acceso FROM seguridad_activos")
            datos_reales = cursor.fetchall()
            conn.close()

            if datos_reales:
                # Seleccionamos un registro para mostrar sus datos
                h_real, dueño, ip, riesgo = random.choice(datos_reales)
                
                # PROBABILIDAD DEL 10% (EL DATO "CORRECTO" O EN PELIGRO)
                if random.random() < 0.10:
                    # Este mensaje debe resaltar lo que pide la encuesta (el Hash y el Riesgo)
                    linea = f">>> [ALERTA] CRÍTICO: {h_real} | USUARIO: {dueño.upper()} | RIESGO: {riesgo}"
                    self.ultimo_hash_real = h_real 
                else:
                    # TRÁFICO NORMAL: Muestra los mismos datos pero como logs de rutina
                    plantillas = [
                        f"[LOG] Validando IP: {ip} ... ACCESO OK",
                        f"[LOG] Usuario: {dueño} | Hash: {h_real[:10]}... | ESTADO: SEGURO",
                        f"[LOG] Monitoreando Nivel de Riesgo: {riesgo}",
                        f"[LOG] Hash de seguridad activo: {h_real}"
                    ]
                    linea = random.choice(plantillas)
                    self.ultimo_hash_real = None 
            else:
                linea = "[SISTEMA] No hay datos en la base de datos de seguridad..."

            # Mostrar en la consola vinculada
            if self.consola_seguridad:
                self.consola_seguridad.appendPlainText(linea)
                self.consola_seguridad.ensureCursorVisible()

        except Exception as e:
            print(f"Error en el flujo: {e}")
    
    
    def interceptar_ataque(self):
        # Verificamos si hay un hash real activo en pantalla
        if hasattr(self, 'ultimo_hash_real') and self.ultimo_hash_real is not None:
            # ¡ÉXITO! El usuario atrapó un hash real de la tabla
            self.ui_content.plainTextEdit_2.appendPlainText(">>> SISTEMA DEFENDIDO: ACCESO BLOQUEADO <<<")
            
            # Cambiamos el color del frame a verde (Estilo Ciberseguridad)
            # Nota: Asegúrate que el frame se llame así en tu .ui o usa el nombre correcto
        else:
            # ¡ERROR! El usuario presionó en un momento donde el hash era basura
            self.ui_content.plainTextEdit_2.appendPlainText(">>> ERROR: FALSA ALARMA - SISTEMA SOBRECARGADO <<<")

    
    #tablewidget


    def cargar_tabla_personas(self):
        import sqlite3
        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Seleccionamos Nombre, Rol y el Hash (que ocultaremos)
            cursor.execute("SELECT usuario_asignado, nivel_riesgo_acceso, carro_hash FROM seguridad_activos")
            datos = cursor.fetchall()
            conn.close()

            # Configurar 3 columnas: Nombre, Rol, y Hash (Censurado)
            self.ui_content.tableWidget_persona.setRowCount(len(datos))
            self.ui_content.tableWidget_persona.setColumnCount(3)
            self.ui_content.tableWidget_persona.setHorizontalHeaderLabels(["NOMBRE", "ROL / RIESGO", "ID DE SEGURIDAD"])
            # Oculta la cabecera vertical (los números de la izquierda)
            self.ui_content.tableWidget_persona.verticalHeader().setVisible(False)

            # Hacer que ocupe toda la tabla
            header = self.ui_content.tableWidget_persona.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)

            for fila, (nombre, rol, hash_real) in enumerate(datos):
                # Estos se ven normales
                self.ui_content.tableWidget_persona.setItem(fila, 0, QTableWidgetItem(str(nombre)))
                self.ui_content.tableWidget_persona.setItem(fila, 1, QTableWidgetItem(str(rol)))
                
                # Este se ve con asteriscos para seguridad
                hash_censurado = "*" * 15 
                self.ui_content.tableWidget_persona.setItem(fila, 2, QTableWidgetItem(hash_censurado))

        except Exception as e:
            print(f"Error cargando tabla: {e}")

    def cargar_tabla_carros(self):
        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Consultamos Modelo y Marca (ajusta los nombres de columna si son distintos en tu DB)
            cursor.execute("SELECT modelo, marca FROM seguridad_activos")
            carros = cursor.fetchall()
            conn.close()

            # Configurar filas y columnas
            self.ui_content.tableWidget_Carro.setRowCount(len(carros))
            self.ui_content.tableWidget_Carro.setColumnCount(2)
            self.ui_content.tableWidget_Carro.setHorizontalHeaderLabels(["MODELO DEL ACTIVO", "MARCA / FABRICANTE"])

            # 1. Ocultar los números de fila (índices verticales)
            self.ui_content.tableWidget_Carro.verticalHeader().setVisible(False)

            # 2. Estirar columnas para que ocupen todo el ancho
            header = self.ui_content.tableWidget_Carro.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)

            for fila, (modelo, marca) in enumerate(carros):
                item_modelo = QTableWidgetItem(str(modelo))
                item_marca = QTableWidgetItem(str(marca))
                
                # Centrar el texto para que se vea ordenado
                item_modelo.setTextAlignment(Qt.AlignCenter)
                item_marca.setTextAlignment(Qt.AlignCenter)
                
                self.ui_content.tableWidget_Carro.setItem(fila, 0, item_modelo)
                self.ui_content.tableWidget_Carro.setItem(fila, 1, item_marca)

        except Exception as e:
            print(f"Error cargando tabla de carros: {e}")
            
    
    #Cambio de indice


    def conectar_db(self):
        try:
            # Usamos la ruta de tu base de datos
            self.conn = sqlite3.connect("ingenieria.db")
            # MUY IMPORTANTE: Asegúrate de que tenga los paréntesis () al final
            self.cursor = self.conn.cursor() 
            print("Conexión exitosa a la base de datos")
        except Exception as e:
            print(f"Error al conectar: {e}")

    # Llama a esta función al inicio de tu __init__
    # 

    def procesar_seguridad(self):
        user = self.ui_content.txt_usuario.text()
        password = self.ui_content.txt_clave.text()
        marca = self.ui_content.txt_marca.text()
        modelo = self.ui_content.txt_modelo.text()
        carro_hash = self.ui_content.txt_hash.text()

        # --- RUTA 1: EL ADMINISTRADOR (Sebas) ---
        if user == "sebas" and password == "tian":
            self.ui_content.stackedWidget_2.setCurrentIndex(1)
            return

        # --- RUTA 2: EL HACKER (Eliminación, Imagen y Bloqueo) ---
        try:
            query = """
                SELECT id FROM seguridad_activos 
                WHERE usuario_asignado = ? AND pin_seguridad = ? 
                AND marca = ? AND modelo = ? AND carro_hash = ?
            """
            self.cursor.execute(query, (user, password, marca, modelo, carro_hash))
            resultado = self.cursor.fetchone()

            if resultado:
                id_victima = resultado[0]
                self.cursor.execute("DELETE FROM seguridad_activos WHERE id = ?", (id_victima,))
                self.conn.commit()

                # --- CARGAR IMAGEN DE HACKEO ---
                ruta_imagen = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\hacking\hackeoCompleto.png"
                pixmap = QPixmap(ruta_imagen)
                
                if not pixmap.isNull():
                    # Ajustamos la imagen al tamaño del label sin perder calidad
                    self.ui_content.lbl_hackeo.setPixmap(pixmap)
                    self.ui_content.lbl_hackeo.setScaledContents(True)
                else:
                    print("Error: No se pudo encontrar la imagen en la ruta especificada.")

                # --- ALERTA Y CAMBIO DE PANTALLA ---
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("SISTEMA COMPROMETIDO")
                msg.setText("¡ATAQUE EXITOSO!")
                msg.setInformativeText(f"Has borrado a {user}. Conexión cerrada.")
                msg.exec()

                # Bloqueo total: Pasamos al índice 2
                self.ui_content.stackedWidget_2.setCurrentIndex(2)
                
                # Refrescar tablas
                self.cargar_tabla_personas()
                self.cargar_tabla_carros()
            else:
                self.ui_content.plainTextEdit_2.appendPlainText("[ERROR] Datos incorrectos.")

        except Exception as e:
            print(f"Error en el núcleo de seguridad: {e}")

    #añadir

    def administrador_anadir_usuario(self):
        # 1. Datos capturados del formulario del Admin
        marca = self.ui_content.txt_marca_admin.text()
        modelo = self.ui_content.txt_modelo_admin.text()
        anio = self.ui_content.txt_anio_admin.text()
        carro_hash = self.ui_content.txt_hash_admin.text()
        usuario = self.ui_content.txt_usuario_admin.text()
        pin = self.ui_content.txt_pin_admin.text()
        riesgo = self.ui_content.txt_riesgo_admin.text() # Nivel de riesgo

        # 2. Validación de seguridad mínima
        if not (usuario and pin and marca and anio):
            QMessageBox.warning(self, "Campos Obligatorios", "Marca, Año, Usuario y PIN no pueden estar vacíos.")
            return

        try:
            # 3. LA QUERY TOTAL (16 COLUMNAS)
            # El ID no se pone porque es AUTOINCREMENT
            query = """
                INSERT INTO seguridad_activos (
                    marca, modelo, año, carro_hash, usuario_asignado, 
                    rol_usuario, correo_institucional, password_hash, tarjeta_token, 
                    pin_seguridad, ip_ultimo_acceso, intentos_fallidos, vinculo_status, 
                    ultima_validacion, nivel_riesgo_acceso
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            # 4. RELLENO AUTOMÁTICO PARA NOT NULL
            # Aquí asignamos valores a lo que el admin no escribe
            valores = (
                marca,                                  # 1. marca
                modelo,                                 # 2. modelo
                int(anio),                              # 3. año
                carro_hash if carro_hash else "PENDIENTE", # 4. carro_hash
                usuario,                                # 5. usuario_assigned
                "Operador",                             # 6. rol_usuario (fijo)
                f"{usuario.lower()}@autometrics.com",   # 7. correo_institucional
                "pbkdf2:sha256:250000$val",            # 8. password_hash (dummy)
                f"TK-{random.randint(1000, 9999)}",     # 9. tarjeta_token
                pin,                                    # 10. pin_seguridad
                "192.168.1." + str(random.randint(2, 254)), # 11. ip_ultimo_acceso
                0,                                      # 12. intentos_fallidos
                "ACTIVO",                               # 13. vinculo_status
                datetime.now().strftime("%Y-%m-%d"),    # 14. ultima_validacion
                riesgo                                # 15. nivel_riesgo_accesc
                                                 
            )

            # 5. Ejecución
            self.cursor.execute(query, valores)
            self.conn.commit()

            QMessageBox.information(self, "Éxito", f"Activo {marca} asignado a {usuario} correctamente.")
            
            # Limpiar campos y refrescar tablas
            self.cargar_tabla_personas()
            self.cargar_tabla_carros()

        except Exception as e:
            QMessageBox.critical(self, "Fallo de Inserción", f"Error: {e}\n\nAsegúrate de que todos los campos NOT NULL tengan valor.")

    
    #mercado Inteligente
    
    #velas

    def actualizar_grafico_velas(self, impacto):
        # 1. Calcular valores de la nueva vela
        open_p = self.mercado_actual
        close_p = open_p * (1 + impacto)
        high_p = max(open_p, close_p) + (open_p * 0.01) # Mecha superior
        low_p = min(open_p, close_p) - (open_p * 0.01)  # Mecha inferior
        
        self.mercado_actual = close_p # Actualizar para la siguiente noticia
        color = '#00ff00' if impacto > 0 else '#ff3131'
        
        # 2. Gestionar el desplazamiento (Scroll)
        self.indice_tiempo += 1
        self.historial_velas.append((self.indice_tiempo, open_p, high_p, low_p, close_p, color))
        
        # Si hay más de 20 velas, borramos la más antigua para que la gráfica "corra"
        if len(self.historial_velas) > 20:
            self.historial_velas.pop(0)

        # 3. Configurar Canvas si no existe
        if not hasattr(self, 'canvas'):
            self.fig, self.ax = plt.subplots(figsize=(5, 4), facecolor='#0d1117')
            self.canvas = FigureCanvas(self.fig)
            layout = QVBoxLayout(self.ui_content.frame_grafico)
            layout.addWidget(self.canvas)
        
        self.ax.clear()
        self.ax.set_facecolor('#0d1117') # Fondo oscuro tipo trading

        # 4. Dibujar cada vela del historial
        for t, op, hi, lo, cl, col in self.historial_velas:
            # Dibujar la mecha (línea fina)
            self.ax.vlines(t, lo, hi, color=col, linewidth=1)
            
            # Dibujar el cuerpo (Diagrama de caja / vela)
            # Rectangle((x_inferior_izquierda, y_inferior_izquierda), ancho, alto)
            alto = cl - op
            rect = plt.Rectangle((t - 0.3, op), 0.6, alto, color=col, alpha=0.9)
            self.ax.add_patch(rect)

        # 5. Ajustar ejes para el efecto de movimiento
        self.ax.set_xlim(self.indice_tiempo - 21, self.indice_tiempo + 1)
        
        # Ajuste dinámico del eje Y para que siempre se vean las velas
        precios = [v[2] for v in self.historial_velas] + [v[3] for v in self.historial_velas]
        if precios:
            margin = (max(precios) - min(precios)) * 0.1
            self.ax.set_ylim(min(precios) - margin, max(precios) + margin)

        # Estética final
        self.ax.tick_params(colors='white', labelsize=8)
        self.ax.grid(True, color='#1f2937', linestyle='--', alpha=0.3)
        self.ax.spines['bottom'].set_color('#1f2937')
        self.ax.spines['left'].set_color('#1f2937')
        
        self.canvas.draw()


    #plaintext
    def ciclo_inteligencia_mercado(self):
        # Rutas (usa la 'r' para evitar problemas con las barras de Windows)
        ruta_base = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\noticias"
        ruta_buenas = os.path.join(ruta_base, "Buenas")
        ruta_malas = os.path.join(ruta_base, "Malas")
        if self.ui_content.plainTextEdit_3.blockCount() > 50:
            # Borra la noticia más vieja si hay más de 50
            cursor = self.ui_content.plainTextEdit_3.textCursor()
            cursor.movePosition(QTextCursor.Start)
            cursor.select(QTextCursor.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar() # Borra el salto de línea

        # 1. Lógica de Escasez: 60% Buenas, 40% Malas
        azar = random.randint(1, 10)
        if azar <= 6:
            tipo = "BUENA"
            color = "#00FF00" # Verde neón
            carpeta = ruta_buenas
            impacto_mercado = random.uniform(0.02, 0.08) # Sube 2-8%
        else:
            tipo = "MALA"
            color = "#FF3131" # Rojo brillante
            carpeta = ruta_malas
            impacto_mercado = random.uniform(-0.15, -0.05) # Baja 5-15% (caídas fuertes)

        try:
            # 2. Leer archivo aleatorio
            archivos = os.listdir(carpeta)
            if not archivos: return
            
            archivo_elegido = random.choice(archivos)
            with open(os.path.join(carpeta, archivo_elegido), 'r', encoding='utf-8') as f:
                contenido = f.read().strip()

            # 3. Formatear y mostrar en plainTextEdit_3
            # Creamos un encabezado con la hora y el tipo de noticia
            hora = QDateTime.currentDateTime().toString("hh:mm:ss")
            
            self.ui_content.plainTextEdit_3.appendHtml(
                f"<b style='color: white;'>[{hora}]</b> "
                f"<span style='color: {color}; font-weight: bold;'>FLASH {tipo}:</span> "
                f"<span style='color: #CCCCCC;'>{contenido}</span>"
            )

            # Mover el scroll al final automáticamente
            self.ui_content.plainTextEdit_3.ensureCursorVisible()

            # 4. DISPARAR EL CAMBIO EN EL GRÁFICO Y PRESUPUESTO
            # Aquí llamarías a tu método de velas pasando el impacto_mercado
            self.actualizar_grafico_velas(impacto_mercado)
            self.simular_ia_rivales(tipo)    
            self.actualizar_tree_competencia()             # IA compra o vende
    
            # Mostrar la noticia en la terminal
            #self.ui_content.plainTextEdit_3.appendHtml(...)

        except Exception as e:
            print(f"Error cargando noticia: {e}")

    
    #rivales


    def simular_ia_rivales(self, tipo_noticia):
        # 1. Normalizar la noticia (por si acaso viene en minúsculas)
        noticia = str(tipo_noticia).upper()
        
        # Ajuste de precio
        variacion = 1.05 if noticia == "BUENA" else 0.95
        self.precio_accion_actual *= variacion

        # 2. Obtener competidores
        self.cursor.execute("SELECT nombre_empresa, presupuesto_actual FROM inteligencia_mercado WHERE id != 1")
        rivales_db = self.cursor.fetchall()

        for nombre, presupuesto in rivales_db:
            # Inicializar diccionarios
            if nombre not in self.analisis_empresas:
                self.analisis_empresas[nombre] = {'ganado': 0, 'perdido': 0, 'emocion': 'Neutral'}
            if nombre not in self.acciones_rivales:
                self.acciones_rivales[nombre] = 0

            # Lógica de Inteligencia (ahora sí se usa)
            es_inteligente = random.random() > 0.15 
            transaccion_realizada = False

            # --- LÓGICA DE COMPRA ---
            if (noticia == "BUENA" and es_inteligente) or (noticia == "MALA" and not es_inteligente):
                # FORZAR PRESUPUESTO: Si el rival no tiene dinero, le damos un "crédito" para que la simulación no se detenga
                if presupuesto < self.precio_accion_actual:
                    presupuesto += self.precio_accion_actual * 2 

                presupuesto -= self.precio_accion_actual
                self.acciones_rivales[nombre] += 1
                self.analisis_empresas[nombre]['perdido'] += self.precio_accion_actual
                self.analisis_empresas[nombre]['emocion'] = random.choice(["Codicia", "Optimismo", "Confianza"])
                transaccion_realizada = True

            # --- LÓGICA DE VENTA ---
            elif (noticia == "MALA" and es_inteligente) or (noticia == "BUENA" and not es_inteligente):
                if self.acciones_rivales[nombre] > 0:
                    presupuesto += self.precio_accion_actual
                    self.acciones_rivales[nombre] -= 1
                    self.analisis_empresas[nombre]['ganado'] += self.precio_accion_actual
                    self.analisis_empresas[nombre]['emocion'] = random.choice(["Pánico", "Miedo", "Cautela"])
                    transaccion_realizada = True

            # Si no hubo transacción, marcamos indiferencia
            if not transaccion_realizada:
                self.analisis_empresas[nombre]['emocion'] = "Indiferencia"

            # 3. Actualizar la base de datos
            self.cursor.execute("UPDATE inteligencia_mercado SET presupuesto_actual = ? WHERE nombre_empresa = ?", 
                                (presupuesto, nombre))
        
        self.conn.commit()
        print(f"DEBUG: Mercado procesado. Noticia: {noticia} | Precio: {self.precio_accion_actual}")
        self.actualizar_tree_sentimiento()

    #treewidget

    def actualizar_tree_competencia(self):
        # 1. Limpiar el widget para refrescar los datos
        self.ui_content.treeWidget_competencia.clear()
        
        # 2. Obtener los datos actuales de la DB (Liquidez de cada empresa)
        self.cursor.execute("SELECT nombre_empresa, presupuesto_actual FROM inteligencia_mercado")
        todas_las_empresas = self.cursor.fetchall()

        # 3. Calcular el VALOR TOTAL (Presupuesto + (Acciones * Precio Mercado))
        # Usamos el diccionario self.acciones_rivales que creamos para no tocar la DB
        ranking = sorted(
            todas_las_empresas, 
            key=lambda x: x[1] + (self.acciones_rivales.get(x[0], 0) * self.precio_accion_actual), 
            reverse=True
        )[:10] # Solo tomamos los 10 mejores

        # 4. Insertar en el TreeWidget con formato de Ranking
        for i, (nombre, presupuesto) in enumerate(ranking):
            acciones = self.acciones_rivales.get(nombre, 0)
            valor_total = presupuesto + (acciones * self.precio_accion_actual)
            
            # Item de Nivel 1: Posición y Nombre
            item_principal = QTreeWidgetItem(self.ui_content.treeWidget_competencia)
            item_principal.setText(0, f"Rank #{i+1} - {nombre}")
            
            # Estética: El Rank #1 resaltará más
            if i == 0:
                item_principal.setForeground(0, QColor("#FFD700")) # Color Dorado para el líder
            
            # Item de Nivel 2: Detalles financieros
            detalles = QTreeWidgetItem(item_principal)
            detalles.setText(0, f"📦 Acciones: {acciones} | 💰 Liquidez: ${presupuesto:,.2f}")
            
        # Expandir todo para que se vea el ranking completo de inmediato
        self.ui_content.treeWidget_competencia.expandAll()
        # Dentro de actualizar_tree_competencia, asegúrate de que el ranking tome a TODOS
        self.cursor.execute("SELECT nombre_empresa, presupuesto_actual FROM inteligencia_mercado") # Sin el "WHERE id != 1"
        # Y en el diccionario:
       

    
    #Historia

 
    def actualizar_tree_sentimiento(self):
        self.ui_content.treeWidget_sentimiento.clear()
        
        # Configurar encabezados si no lo has hecho en el Designer
        self.ui_content.treeWidget_sentimiento.setHeaderLabels(["EMPRESA", "GANADO", "PERDIDO", "SENTIMIENTO"])

        for nombre, datos in self.analisis_empresas.items():
            item = QTreeWidgetItem(self.ui_content.treeWidget_sentimiento)
            
            # Insertar datos en las 4 columnas
            item.setText(0, nombre)
            item.setText(1, f"$ {datos['ganado']:,.2f}")
            item.setText(2, f"$ {datos['perdido']:,.2f}")
            item.setText(3, datos['emocion'])

            # Colores de Data Analyst
            item.setForeground(1, QColor("#00FF00")) # Ganado siempre verde neón
            item.setForeground(2, QColor("#FF3131")) # Perdido siempre rojo brillante
            
            # Centrar los textos de las columnas numéricas
            item.setTextAlignment(1, Qt.AlignCenter)
            item.setTextAlignment(2, Qt.AlignCenter)
            item.setTextAlignment(3, Qt.AlignCenter)


    def closeEvent(self, event):

        print("--- Ejecutando protocolos de guardado antes de cerrar ---")

        # 1. LÓGICA DEL EXCEL (Sentimiento del Mercado)
        tiempo_total = time.time() - self.hora_inicio_mercado
        un_minuto = 60
        cinco_minutos = 300

        # Guardar solo si la sesión duró entre 1 y 5 minutos
        if un_minuto <= tiempo_total <= cinco_minutos:
            try:
                ruta_excel = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Sentimiento"
                os.makedirs(ruta_excel, exist_ok=True)
                nombre_archivo = f"analisis_mercado_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
                path_completo = os.path.join(ruta_excel, nombre_archivo)

                data_para_excel = []
                for nombre, datos in self.analisis_empresas.items():
                    data_para_excel.append({
                        'Empresa': nombre,
                        'Inversión Total (Perdido)': datos['perdido'],
                        'Retorno Total (Ganado)': datos['ganado'],
                        'Balance Neto': datos['ganado'] - datos['perdido'],
                        'Último Sentimiento': datos['emocion']
                    })
                
                df = pd.DataFrame(data_para_excel)
                df.to_excel(path_completo, index=False)
                print(f"✅ Excel generado: {nombre_archivo}")
            except Exception as e:
                print(f"❌ Error al guardar Excel: {e}")
        else:
            print("⚠️ Sesión fuera de rango de tiempo. No se generó reporte Excel.")

        # 2. LÓGICA DEL PDF (Reportes de Gráficas)
        try:
            ruta_pdf = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\PDF\Reporte_Final.pdf"
            os.makedirs(os.path.dirname(ruta_pdf), exist_ok=True)

            with PdfPages(ruta_pdf) as pdf:
                # Gráfico de Ganancias
                plt.figure(figsize=(8, 6))
                plt.plot(self.historial_ganancias, color='green')
                plt.title("Reporte de Ganancias Totales - AutoMetrics 2.0")
                plt.grid(True)
                pdf.savefig()
                plt.close() # Vital para la memoria

                # Gráfico de Gastos
                plt.figure(figsize=(8, 6))
                plt.plot(self.historial_gastos, color='red')
                plt.title("Reporte de Gastos Operativos")
                plt.grid(True)
                pdf.savefig()
                plt.close() # Libera la figura
            
            print(f"✅ PDF generado exitosamente en: {ruta_pdf}")
        except Exception as e:
            print(f"❌ Error al guardar PDF: {e}")

        # 3. Finalizar el evento
        event.accept()

    

    def mostrar_detalle_empresa(self, item, column):
        nombre = item.text(0)
        datos = self.analisis_empresas.get(nombre)
        if datos:
            print(f"Análisis para {nombre}: Ganó {datos['ganado']} | Emoción: {datos['emocion']}")

    

    #Gestion De Cumplimiento


    #trewidget
  
    def cargar_empleados_en_tree(self):
        # 1. Limpiar el TreeWidget antes de cargar
        self.ui_content.treeWidget_empleados.clear()
        
        try:
            # 2. Conexión a la base de datos
            conn = sqlite3.connect('Ingenieria.db')
            cursor = conn.cursor()
            
            # 3. Consulta de las columnas: nombre, cargo y velocidad_respuesta
            query = "SELECT nombre, cargo, velocidad_respuesta FROM empleados_cumplimiento"
            cursor.execute(query)
            empleados = cursor.fetchall()
            
            # 4. Insertar datos en el TreeWidget
            for fila in empleados:
                nombre, cargo, velocidad = fila
                # Crear un nuevo item para el árbol
                item = QTreeWidgetItem(self.ui_content.treeWidget_empleados)
                item.setText(0, str(nombre))    # Columna Nombre
                item.setText(1, str(cargo))     # Columna Cargo
                item.setText(2, str(velocidad)) # Columna Velocidad de Respuesta
                
            conn.close()
            
        except Exception as e:
            print(f"Error al cargar empleados: {e}")

    
    #tablewwidget
    def cargar_clientes_en_tabla(self):
        # 1. Configurar columnas y limpiar la tabla
        self.ui_content.tableWidget_clientes.setColumnCount(3)
        self.ui_content.tableWidget_clientes.setHorizontalHeaderLabels(
            ["Cliente", "Tipo Solicitud", "Perfil"]
        )
        self.ui_content.tableWidget_clientes.setRowCount(0)
        self.ui_content.tableWidget_clientes.verticalHeader().setVisible(False)
        
        try:
            # 2. Conexión a la base de datos
            conn = sqlite3.connect('Ingenieria.db')
            cursor = conn.cursor()
            
            # 3. Consulta de las columnas especificadas
            query = """SELECT nombre_cliente, tipo_solicitud, perfil_cliente
                    FROM casos_clientes"""
            cursor.execute(query)
            casos = cursor.fetchall()
            
            # 4. Insertar los datos fila por fila
            for row_number, row_data in enumerate(casos):
                self.ui_content.tableWidget_clientes.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    
                    # Centrar el texto en las columnas de Prioridad y Emoción
                    if column_number >= 3:
                        item.setTextAlignment(Qt.AlignCenter)
                    
                    self.ui_content.tableWidget_clientes.setItem(row_number, column_number, item)
            
            conn.close()
            
            # Ajustar el ancho de las columnas al contenido
            self.ui_content.tableWidget_clientes.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error al cargar clientes: {e}")

    
    #Combobox
    def cargar_combos_datos(self):
        try:
            conn = sqlite3.connect('Ingenieria.db')
            cursor = conn.cursor()

            # --- Cargar Empleados ---
            self.ui_content.comboBox_empleado.clear()
            cursor.execute("SELECT nombre FROM empleados_cumplimiento")
            empleados = cursor.fetchall()
            for emp in empleados:
                self.ui_content.comboBox_empleado.addItem(str(emp[0]))

            # --- Cargar Clientes ---
            self.ui_content.comboBox_cliente.clear()
            # Usamos nombre_cliente (corregido)
            cursor.execute("SELECT nombre_cliente FROM casos_clientes")
            clientes = cursor.fetchall()
            for cli in clientes:
                self.ui_content.comboBox_cliente.addItem(str(cli[0]))

            conn.close()
            print("ComboBoxes cargados exitosamente.")

        except Exception as e:
            print(f"Error al cargar ComboBoxes: {e}")


    def cargar_emociones_unicas(self):
        ruta_base = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Conversaciones"
        emociones_lista = set() # Usamos un set para evitar duplicados automáticamente

        try:
            archivos = [f for f in os.listdir(ruta_base) if f.endswith('.txt')]
            for archivo in archivos:
                # Quitamos el .txt y separamos por "_"
                partes = archivo.replace('.txt', '').split('_')
                for emocion in partes:
                    emociones_lista.add(emocion.strip())

            # Convertimos a lista ordenada para los combos
            opciones = sorted(list(emociones_lista))
            
            self.ui_content.comboBox_emocionE.clear()
            self.ui_content.comboBox_emocionC.clear()
            self.ui_content.comboBox_emocionE.addItems(opciones)
            self.ui_content.comboBox_emocionC.addItems(opciones)
            
            print(f"Emociones cargadas: {opciones}")
        except Exception as e:
            print(f"Error al procesar emociones: {e}")


    #conversacion

    def iniciar_simulacion_chat(self):
        # 1. Obtener datos de identidad y emociones
        self.registrar_interes_analista()
        empleado = self.ui_content.comboBox_empleado.currentText()
        cliente = self.ui_content.comboBox_cliente.currentText()
        emo_e = self.ui_content.comboBox_emocionE.currentText()
        emo_c = self.ui_content.comboBox_emocionC.currentText()

        # 2. Lógica de Velocidad (Basada en tu columna 'velocidad')
        # Obtenemos la velocidad del empleado seleccionado (puedes traerla de la DB o del Tree)
        # Ejemplo: Si la velocidad es 'Alta' -> 3s, si es 'Baja' -> 10s
        velocidad_texto = "Alta" # Aquí deberías mapear el valor real de tu tabla empleados
        ms_espera = 3000 if velocidad_texto == "Alta" else 10000

        # 3. Localizar archivo
        nombre_archivo = f"{emo_e}_{emo_c}.txt"
        ruta = os.path.join(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Conversaciones", nombre_archivo)

        if not os.path.exists(ruta):
            self.ui_content.TextEdit_Arbol.setHtml("<b style='color:red;'>Guion no encontrado.</b>")
            return

        # 4. Preparar el escenario
        self.ui_content.TextEdit_Arbol.clear()
        with open(ruta, 'r', encoding='utf-8') as f:
            self.lineas_chat = [l.strip() for l in f.readlines() if "|" in l]

        self.indice_actual = 0
        self.inicio_atencion = time.time() # Inicia cronómetro de "chisme"

        # 5. Timer de PySide6 para la carga secuencial
        if hasattr(self, 'timer_chat'): self.timer_chat.stop() # Limpiar timer previo
        
        self.timer_chat = QTimer(self)
        self.timer_chat.timeout.connect(lambda: self.renderizar_linea(empleado, cliente))
        self.timer_chat.start(ms_espera)
        

    def renderizar_linea(self, emp, cli):
        if self.indice_actual < len(self.lineas_chat):
            linea = self.lineas_chat[self.indice_actual]
            rol, texto = linea.split("|")
            
            # Ajustes de diseño: Letra grande (18px) y colores de analista
            font_size = "18px"
            nombre_display = emp if rol == "ASESOR" else cli
            texto_final = texto.replace("&", f"<b>{nombre_display}</b>")

            if rol == "ASESOR":
                # Alineación Izquierda (Empleado)
                html = f"""
                <div align="left" style="margin-bottom: 25px;">
                    <div style="background-color: #313244; color: #cdd6f4; padding: 15px; border-radius: 15px; 
                                border-left: 10px solid #89b4fa; width: 80%; font-size: {font_size};">
                        <b style="color: #89b4fa; font-size: 20px;">{emp}:</b><br>{texto_final}
                    </div>
                </div>
                """
            else:
                # Alineación Derecha (Cliente)
                html = f"""
                <div align="right" style="margin-bottom: 25px;">
                    <div style="background-color: #45475a; color: #cdd6f4; padding: 15px; border-radius: 15px; 
                                border-right: 10px solid #fab387; width: 80%; text-align: left; font-size: {font_size};">
                        <b style="color: #fab387; font-size: 20px;">{cli}:</b><br>{texto_final}
                    </div>
                </div>
                """
            
            self.ui_content.TextEdit_Arbol.append(html)
            self.indice_actual += 1
        else:
            self.timer_chat.stop()
            self.registrar_metrica_chisme()

    def registrar_metrica_chisme(self):
        tiempo_total = round(time.time() - self.inicio_atencion, 2)
        emociones = f"{self.ui_content.comboBox_emocionE.currentText()}_{self.ui_content.comboBox_emocionC.currentText()}"
        print(f"--- REPORTE DE ANALISTA ---")
        print(f"Escena: {emociones}")
        print(f"Tiempo de permanencia: {tiempo_total} segundos")
        # Aquí puedes hacer un INSERT INTO tabla_metricas si lo deseas

    #registrar emociones en sql
   

    def registrar_interes_analista(self):
        try:
            # Extraer datos de los ComboBoxes
            emp_nom = self.ui_content.comboBox_empleado.currentText()
            emp_emo = self.ui_content.comboBox_emocionE.currentText()
            cli_nom = self.ui_content.comboBox_cliente.currentText()
            cli_emo = self.ui_content.comboBox_emocionC.currentText()

            # Añadimos timeout=10 para esperar si la DB está ocupada
            conn = sqlite3.connect('Ingenieria.db', timeout=10) 
            cursor = conn.cursor()
            
            query = '''INSERT INTO metricas_analisis 
                    (empleado_nombre, emocion_empleado, cliente_nombre, emocion_cliente) 
                    VALUES (?, ?, ?, ?)'''
            
            cursor.execute(query, (emp_nom, emp_emo, cli_nom, cli_emo))
            
            conn.commit()
            # Es vital cerrar siempre la conexión para liberar el bloqueo
            conn.close() 
            print(f"Métrica guardada exitosamente: {emp_emo} vs {cli_emo}")
            
        except sqlite3.OperationalError as e:
            print(f"Error de SQLite (posible bloqueo): {e}")
        except Exception as e:
            print(f"Error general: {e}")

    
    #optimizacion de stock


    def ejecutar_ciclo_empresarial(self):
        try:
            conn = sqlite3.connect('Ingenieria.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM finanzas_inventario")
            sectores = cursor.fetchall()
            
            total_ingresos = 0
            # Variabilidad económica: 25% de probabilidad de cambio de clima
            if random.random() < 0.25:
                # Multiplicadores que van desde crisis (0.6) hasta super bonanza (3.0)
                self.mes_multiplicador = random.choice([0.6, 1.0, 1.5, 2.2, 3.0])
                
            # Parámetros de gestión para evitar la muerte súbita
            objetivo_stock = 90  # La empresa intentará reponer hasta este nivel
            presupuesto_reserva = 5000 # Solo compra stock si tiene este fondo mínimo

            for fila in sectores:
                id_inv, nombre, stock_db, prioridad, costo, roi, caida = fila
                slider = self.mapa_sliders.get(id_inv)
                lcd = self.mapa_lcds.get(id_inv) # Sincronización con LCD
                
                if slider and lcd:
                    valor_actual = slider.value()
                    
                    # 1. DESGASTE: Se reduce a la mitad en meses buenos
                    factor_desgaste = 0.5 if self.mes_multiplicador > 1 else 1.0
                    desgaste = random.randint(0, int(caida * factor_desgaste))
                    nuevo_stock = max(0, valor_actual - desgaste)
                    
                    # 2. REPOSICIÓN AUTOMÁTICA: Si hay dinero, el stock SUBE
                    if nuevo_stock < objetivo_stock and self.presupuesto > presupuesto_reserva:
                        cantidad_compra = 5 # Incremento por ciclo
                        costo_total = cantidad_compra * costo * 0.4 
                        
                        if self.presupuesto >= costo_total:
                            self.presupuesto -= costo_total
                            nuevo_stock = min(100, nuevo_stock + cantidad_compra)

                    # 3. EVENTO DE STOCK DEFECTUOSO (2% de probabilidad)
                    if random.random() < 0.02: 
                        nuevo_stock = int(nuevo_stock * 0.98) 
                    
                    # 4. INGRESOS: El ROI premia el stock alto
                    ganancia = (nuevo_stock * roi) * self.mes_multiplicador
                    total_ingresos += ganancia
                    
                    # Actualización visual simultánea
                    slider.setValue(nuevo_stock)
                    lcd.display(nuevo_stock)
            
            # Actualización del presupuesto general
            self.presupuesto += total_ingresos
            
            if hasattr(self.ui_content, 'lcdNumber_presupuesto'):
                self.ui_content.lcdNumber_presupuesto.display(int(self.presupuesto))

            # CONDICIÓN DE QUIEBRA
            if self.presupuesto <= 0:
                self.timer_simulador.stop()
                self.ui_content.lcdNumber_presupuesto.display(0)
                print("LA EMPRESA QUEBRÓ: Fondos insuficientes para operar.")
                # Opcional: Mostrar mensaje en la consola de la UI si existe
                if hasattr(self, 'consola_seguridad'):
                    self.consola_seguridad.appendPlainText(">>> ESTADO: QUIEBRA TOTAL.")
            # Al final de ejecutar_ciclo_empresarial, antes de conn.close()
            self.historial_ganancias.append(total_ingresos)
            # Calcula el gasto total del ciclo (mantenimiento + reposición)
            gasto_total = sum((slider.value() * costo) * 0.0005 for id_inv, _, _, _, costo, _, _ in sectores)
            self.historial_gastos.append(gasto_total)

            # Llamar a la función de dibujo (necesitas importar matplotlib)
            self.actualizar_graficos_ui()

            conn.close()
        except Exception as e:
            print(f"Error en simulación: {e}")

    
    #graficas


    def actualizar_graficos_ui(self):
        # Función simplificada para graficar en los frames
        for frame, datos, titulo, color in [
            (self.ui_content.frame_ganancia, self.historial_ganancias, "Ingresos", "green"),
            (self.ui_content.frame_perdida, self.historial_gastos, "Egresos", "red")
        ]:
            # Limpiar frame y añadir canvas
            if frame.layout() is None:
                layout = QVBoxLayout(frame)
                frame.setLayout(layout)
            
            # Eliminar gráfico viejo
            for i in reversed(range(frame.layout().count())): 
                frame.layout().itemAt(i).widget().setParent(None)

            fig, ax = plt.subplots(figsize=(4, 2), dpi=80)
            fig.patch.set_facecolor('#1e1e2e') # Color oscuro de tu UI
            ax.plot(datos, color=color, linewidth=2)
            ax.set_title(titulo, color='white')
            ax.axis('off') # Estética limpia
            
            canvas = FigureCanvas(fig)
            frame.layout().addWidget(canvas)

    
    


    #continuacion Empresa
    def cargar_empresas_banco(self):
        try:
            # Conexión a tu base de datos (usando la ruta de tus imágenes)
            conn = sqlite3.connect('Ingenieria.db') 
            cursor = conn.cursor()
            
            # Seleccionamos solo los nombres de la tabla inteligencia_mercado
            cursor.execute("SELECT nombre_empresa FROM inteligencia_mercado")
            empresas = cursor.fetchall()
            
            self.ui_content.comboBox_empresa.clear()
            self.ui_content.comboBox_empresa.addItem("--- Seleccione Empresa ---")
            
            for emp in empresas:
                self.ui_content.comboBox_empresa.addItem(emp[0])
                
            conn.close()
        except Exception as e:
            print(f"Error al cargar empresas: {e}")

    def actualizar_opciones_prestamo(self):
        empresa_seleccionada = self.ui_content.comboBox_empresa.currentText()
        
        # Validación: Si no hay selección real, no continuar
        if not empresa_seleccionada or empresa_seleccionada == "--- Seleccione Empresa ---":
            self.ui_content.comboBox_cantidad.clear()
            return

        try:
            conn = sqlite3.connect('Ingenieria.db')
            cursor = conn.cursor()
            cursor.execute("SELECT presupuesto_actual FROM inteligencia_mercado WHERE nombre_empresa=?", (empresa_seleccionada,))
            resultado = cursor.fetchone()
            conn.close()

            # AQUÍ ESTABA EL ERROR: Verificar si 'resultado' no es None antes de usar [0]
            if resultado:
                presupuesto = resultado[0]
                self.ui_content.comboBox_cantidad.clear()
                
                escalas = [
                    ("Crédito Operativo (10%)", 0.10),
                    ("Inyección de Stock (25%)", 0.25),
                    ("Expansión de Flota (50%)", 0.50),
                    ("Rescate Total (100%)", 1.00)
                ]

                for nombre, porcentaje in escalas:
                    monto = int(presupuesto * porcentaje)
                    # Almacenamos el monto numérico como userData para usarlo luego en el banco
                    self.ui_content.comboBox_cantidad.addItem(f"{nombre}: ${monto:,}", monto)
            else:
                print(f"Advertencia: No se encontró presupuesto para {empresa_seleccionada}")
                
        except Exception as e:
            print(f"Error en base de datos: {e}")

    

    def evaluar_prestamo_bancario(self):
        # VALIDACIÓN INICIAL: Evita el error si el combo está vacío
        if self.ui_content.comboBox_cantidad.currentIndex() == -1:
            print("Error: Seleccione primero una empresa y una cantidad válida.")
            return

        empresa = self.ui_content.comboBox_empresa.currentText()
        # Aquí es donde fallaba si el combo estaba vacío
        monto_solicitado = self.ui_content.comboBox_cantidad.currentData()
        
        if not empresa or empresa == "--- Seleccione Empresa ---" or monto_solicitado is None:
            return

        try:
            conn = sqlite3.connect('Ingenieria.db')
            cursor = conn.cursor()
            # Traemos los signos vitales de la empresa desde inteligencia_mercado
            cursor.execute("""
                SELECT presupuesto_actual, sentimiento_mercado, nivel_confianza 
                FROM inteligencia_mercado WHERE nombre_empresa=?
            """, (empresa,))
            datos = cursor.fetchone()
            conn.close()

            if datos:
                presupuesto, sentimiento, confianza = datos
                
                # --- LÓGICA DE DECISIÓN DEL BANCO ---
                es_aprobado = True
                
                # El banco rechaza si la confianza es muy baja o si pide mucho en mercado Bearish
                if confianza < 40:
                    es_aprobado = False
                elif sentimiento == "BEARISH" and monto_solicitado > (presupuesto * 0.3):
                    es_aprobado = False
                elif monto_solicitado > (presupuesto * 0.8) and confianza < 60:
                    es_aprobado = False

                # Ejecutar la magia visual
                self.procesar_imagen_certificado(empresa, es_aprobado)
                
        except Exception as e:
            print(f"Error en la lógica del banco: {e}")
                
     
            

    def procesar_imagen_certificado(self, nombre_empresa, aprobado):
        # 1. Rutas (Asegúrate de que sean .png como mencionaste)
        base_path = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\certificado"
        archivo_base = "Aprobado.png" if aprobado else "Denegado.png"
        ruta_imagen = os.path.join(base_path, archivo_base)
        ruta_salida = os.path.join(base_path, "Certificado_Temporal.png")

        try:
            # Abrir la imagen original
            img = Image.open(ruta_imagen)
            # Si el PNG tiene transparencia (RGBA), lo convertimos a RGB para evitar errores al guardar
            if img.mode == 'RGBA':
                img = img.convert('RGB')
                
            draw = ImageDraw.Draw(img)
            
            # 2. Configuración de la fuente (Arial 50 para buena visibilidad)
            try:
                font = ImageFont.truetype("arial.ttf", 50)
            except:
                font = ImageFont.load_default()

            # 3. AJUSTE DE COORDENADAS (Más a la derecha y más abajo)
            # Antes: (ancho // 5, alto // 2.8)
            # Ahora: Aumentamos el primer valor (X) y el segundo divisor (Y) para bajarlo
            ancho_img, alto_img = img.size
            
            # X: ancho_img // 3.5 (lo mueve a la derecha)
            # Y: alto_img // 2.5 (lo mueve hacia abajo)
            posicion = (int(ancho_img // 3.5), int(alto_img // 2.5)) 
            
            # Color profesional: Azul oscuro para éxito, Gris oscuro/Rojo para denegado
            color_texto = (26, 35, 126) if aprobado else (60, 60, 60)
            
            # Dibujar nombre
            draw.text(posicion, nombre_empresa.upper(), fill=color_texto, font=font)

            # 4. Guardar y mostrar
            img.save(ruta_salida)

            pixmap = QPixmap(ruta_salida)
            pixmap_escalado = pixmap.scaled(
                self.ui_content.label_38.width(), 
                self.ui_content.label_38.height(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            self.ui_content.label_38.setPixmap(pixmap_escalado)
            self.ui_content.label_38.setAlignment(Qt.AlignCenter)
            
            print(f"Certificado generado para: {nombre_empresa}")
            
        except Exception as e:
            print(f"Error en el proceso visual del certificado: {e}")


    #dashboard
    def obtener_datos_liquidez_db(self):
        """Obtiene el resumen de inversión por marca de la base de datos."""
        try:
            # Conexión exacta a tu DB
            conn = sqlite3.connect('Ingenieria.db')
            cursor = conn.cursor()
            
            # Consultamos la tabla de compras aprobadas
            query = "SELECT marca, SUM(valor_pagado) FROM compras_aprobadas GROUP BY marca"
            cursor.execute(query)
            datos = cursor.fetchall()
            conn.close()
            
            return datos # Retorna lista de tuplas [(Marca, Total), ...]
        except Exception as e:
            print(f"Error al leer liquidez de DB: {e}")
            return []

    def refrescar_dashboard_liquidez(self):
        """Limpia el frame_n y dibuja la nueva gráfica basada en la DB."""
        datos = self.obtener_datos_liquidez_db()
        
        if not datos:
            print("No hay datos para graficar en el Dashboard.")
            return

        marcas = [fila[0] for fila in datos]
        valores = [fila[1] for fila in datos]

        # Gestión del layout en frame_n
        frame = self.ui_content.frame_n
        if frame.layout() is None:
            layout = QVBoxLayout(frame)
            frame.setLayout(layout)
        
        # Limpiar contenido previo para evitar sobreposición
        for i in reversed(range(frame.layout().count())): 
            frame.layout().itemAt(i).widget().setParent(None)

        # Configuración del estilo del gráfico
        fig, ax = plt.subplots(figsize=(5, 3), dpi=80)
        fig.patch.set_facecolor('#1a1b26') # Fondo oscuro
        ax.set_facecolor('#1a1b26')

        # Gráfico de barras horizontales
        ax.barh(marcas, valores, color='#7aa2f7', edgecolor='white')
        
        # Estética de Dashboard profesional
        ax.set_title("RESUMEN DE INVERSIÓN (LIQUIDEZ)", color='white', fontweight='bold')
        ax.tick_params(colors='white', labelsize=9)
        ax.xaxis.grid(True, color='#414868', linestyle='--', alpha=0.5)
        
        for spine in ax.spines.values():
            spine.set_visible(False)

        plt.tight_layout()

        # Integración final
        canvas = FigureCanvas(fig)
        frame.layout().addWidget(canvas)
        plt.close(fig)

    def graficar_confianza_mercado(self):
        try:
            # 1. Conexión y extracción de datos
            conn = sqlite3.connect('Ingenieria.db')
            cursor = conn.cursor()
            # Traemos el nombre y la confianza de las primeras 10 empresas
            cursor.execute("SELECT nombre_empresa, nivel_confianza FROM inteligencia_mercado LIMIT 10")
            datos = cursor.fetchall()
            conn.close()

            if not datos: return

            empresas = [d[0] for d in datos]
            confianza = [d[1] for d in datos]

            # 2. Configuración del frame_2
            frame = self.ui_content.frame_2
            if frame.layout() is None:
                layout = QVBoxLayout(frame)
                frame.setLayout(layout)
            
            for i in reversed(range(frame.layout().count())): 
                frame.layout().itemAt(i).widget().setParent(None)

            # 3. Creación del gráfico
            fig, ax = plt.subplots(figsize=(5, 3), dpi=80)
            fig.patch.set_facecolor('#1a1b26') # Fondo oscuro
            ax.set_facecolor('#1a1b26')

            # Generar colores dinámicos: Verde > 70, Amarillo > 40, Rojo el resto
            colores = ['#4fd6be' if c > 70 else '#ff9e64' if c > 40 else '#f7768e' for c in confianza]

            # Gráfico de barras
            bars = ax.bar(empresas, confianza, color=colores)
            
            # Estética
            ax.set_title("NIVEL DE CONFIANZA DEL MERCADO (%)", color='white', fontweight='bold', fontsize=10)
            ax.tick_params(axis='x', rotation=45, colors='white', labelsize=7)
            ax.tick_params(axis='y', colors='white')
            ax.set_ylim(0, 100) # La confianza es de 0 a 100
            
            for spine in ax.spines.values():
                spine.set_visible(False)

            plt.tight_layout()

            canvas = FigureCanvas(fig)
            frame.layout().addWidget(canvas)
            plt.close(fig)

        except Exception as e:
            print(f"Error al graficar confianza: {e}")

    def graficar_frecuencia_compras_db(self):
        try:
            # 1. Conexión y consulta SQL
            conn = sqlite3.connect('Ingenieria.db')
            cursor = conn.cursor()
            
            # Seleccionamos las fechas de todas las compras aprobadas
            query = "SELECT fecha_compra FROM compras_aprobadas"
            cursor.execute(query)
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                print("No hay datos de fechas para graficar en frame_3.")
                return

            # 2. Procesamiento de datos (Contar compras por día)
            fechas = [fila[0] for fila in datos]
            from collections import Counter
            conteo_fechas = Counter(fechas)
            
            # Ordenar por fecha para que la línea tenga sentido cronológico
            fechas_ordenadas = sorted(conteo_fechas.keys())
            cantidades = [conteo_fechas[f] for f in fechas_ordenadas]

            # 3. Configuración del frame_3
            frame = self.ui_content.frame_3
            if frame.layout() is None:
                layout = QVBoxLayout(frame)
                frame.setLayout(layout)
            
            for i in reversed(range(frame.layout().count())): 
                frame.layout().itemAt(i).widget().setParent(None)

            # 4. Creación del gráfico de líneas (Series de Tiempo)
            fig, ax = plt.subplots(figsize=(5, 3), dpi=80)
            fig.patch.set_facecolor('#1a1b26') # Estilo dark
            ax.set_facecolor('#1a1b26')

            ax.plot(fechas_ordenadas, cantidades, color='#bb9af7', linewidth=2, marker='o', markersize=4)
            ax.fill_between(fechas_ordenadas, cantidades, color='#bb9af7', alpha=0.1)

            # Estética profesional
            ax.set_title("HISTORIAL CRONOLÓGICO DE COMPRAS", color='white', fontweight='bold', fontsize=10)
            ax.tick_params(axis='x', rotation=30, colors='white', labelsize=7)
            ax.tick_params(axis='y', colors='white')
            
            # Grid tenue
            ax.grid(True, color='#414868', linestyle=':', alpha=0.3)
            
            for spine in ax.spines.values():
                spine.set_visible(False)

            plt.tight_layout()

            canvas = FigureCanvas(fig)
            frame.layout().addWidget(canvas)
            plt.close(fig)

        except Exception as e:
            print(f"Error al graficar frecuencia en frame_3: {e}")
    
    def graficar_seguridad_activos_db(self):
        try:
            # 1. Conexión y consulta a seguridad_activos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Consultamos los niveles de riesgo registrados
            query = "SELECT nivel_riesgo_acceso FROM seguridad_activos"
            cursor.execute(query)
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                print("No hay datos de seguridad para graficar en frame_4.")
                return

            # 2. Procesamiento: Contar frecuencias de cada nivel
            niveles = [fila[0] for fila in datos]
            from collections import Counter
            conteo = Counter(niveles)
            
            labels = list(conteo.keys())
            sizes = list(conteo.values())

            # 3. Configuración del frame_4
            frame = self.ui_content.frame_4
            if frame.layout() is None:
                layout = QVBoxLayout(frame)
                frame.setLayout(layout)
            
            for i in reversed(range(frame.layout().count())): 
                frame.layout().itemAt(i).widget().setParent(None)

            # 4. Creación del gráfico circular (Estilo Dashboard)
            fig, ax = plt.subplots(figsize=(5, 3), dpi=80)
            fig.patch.set_facecolor('#1a1b26') # Fondo oscuro coherente
            
            # Colores temáticos: Rojo para Alto, Amarillo para Medio, Verde para Bajo
            colores_map = {'Alto': '#f7768e', 'Medio': '#e0af68', 'Bajo': '#9ece6a'}
            colores = [colores_map.get(label, '#7aa2f7') for label in labels]

            # Dibujar Pie Chart
            wedges, texts, autotexts = ax.pie(
                sizes, 
                labels=labels, 
                autopct='%1.1f%%', 
                startangle=140, 
                colors=colores,
                textprops={'color':"w", 'fontsize': 8},
                pctdistance=0.85
            )

            # Convertir en "Donut Chart" para un look más moderno
            centre_circle = plt.Circle((0,0), 0.70, fc='#1a1b26')
            fig.gca().add_artist(centre_circle)

            ax.set_title("DISTRIBUCIÓN DE RIESGO TÉCNICO", color='white', fontweight='bold', fontsize=10)
            
            plt.tight_layout()

            # Integración en la interfaz
            canvas = FigureCanvas(fig)
            frame.layout().addWidget(canvas)
            plt.close(fig)

        except Exception as e:
            print(f"Error al graficar seguridad en frame_4: {e}")

    def graficar_eficiencia_empleados_db(self):
        try:
            # 1. Conexión y consulta a empleados_cumplimiento
            conn = sqlite3.connect("Ingenieria.db")
            cursor = conn.cursor()
            
            # Consultamos el promedio de velocidad por cargo
            query = """
                SELECT cargo, AVG(velocidad_respuesta) 
                FROM empleados_cumplimiento 
                GROUP BY cargo
            """
            cursor.execute(query)
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                print("No hay datos en empleados_cumplimiento para graficar.")
                return

            cargos = [fila[0] for fila in datos]
            velocidades = [fila[1] for fila in datos]

            # 2. Configuración del frame_5
            frame = self.ui_content.frame_5
            if frame.layout() is None:
                layout = QVBoxLayout(frame)
                frame.setLayout(layout)
            
            for i in reversed(range(frame.layout().count())): 
                frame.layout().itemAt(i).widget().setParent(None)

            # 3. Creación del gráfico de barras horizontales (Estilo Dashboard)
            # Cambia el figsize a uno más pequeño si el error persiste
            fig, ax = plt.subplots(figsize=(4, 2.5), dpi=80)
            fig.patch.set_facecolor('#1a1b26')
            ax.set_facecolor('#1a1b26')

            # Usamos un color púrpura/neón para representar el factor humano
            bars = ax.barh(cargos, velocidades, color='#9ece6a', edgecolor='white')
            
            # Añadir etiquetas de valor al final de cada barra
            for bar in bars:
                width = bar.get_width()
                ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                        f'{width:.1f}ms', color='white', va='center', fontsize=8)

            # Estética
            ax.set_title("VELOCIDAD DE RESPUESTA POR CARGO", color='white', fontweight='bold', fontsize=10)
            ax.tick_params(axis='both', colors='white', labelsize=8)
            
            # Quitar bordes
            for spine in ax.spines.values():
                spine.set_visible(False)

            plt.tight_layout()

            # 4. Integrar en la UI
            canvas = FigureCanvas(fig)
            frame.layout().addWidget(canvas)
            plt.close(fig)

        except Exception as e:
            print(f"Error al graficar empleados en frame_5: {e}")

    def graficar_analisis_casos_clientes(self):
        try:
            # 1. Conexión y consulta a la tabla casos_clientes
            conn = sqlite3.connect("Ingenieria.db")
            cursor = conn.cursor()
            
            # Consultamos el tipo de solicitud para ver la carga de trabajo
            query = "SELECT tipo_solicitud, COUNT(*) FROM casos_clientes GROUP BY tipo_solicitud"
            cursor.execute(query)
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                print("No hay datos en casos_clientes para el frame_6.")
                return

            tipos = [fila[0] for fila in datos]
            cantidades = [fila[1] for fila in datos]

            # 2. Configuración del frame_6
            frame = self.ui_content.frame_6
            if frame.layout() is None:
                layout = QVBoxLayout(frame)
                frame.setLayout(layout)
            
            for i in reversed(range(frame.layout().count())): 
                frame.layout().itemAt(i).widget().setParent(None)

            # 3. Creación del gráfico de barras (Estilo Dashboard Moderno)
            fig, ax = plt.subplots(figsize=(5, 3), dpi=80)
            fig.patch.set_facecolor('#1a1b26')
            ax.set_facecolor('#1a1b26')

            # Usamos una paleta de colores vibrante para distinguir los tipos
            colores = ['#7aa2f7', '#bb9af7', '#e0af68', '#f7768e', '#9ece6a']
            bars = ax.bar(tipos, cantidades, color=colores, edgecolor='white', linewidth=0.5)

            # Añadir etiquetas de cantidad sobre las barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}', ha='center', va='bottom', color='white', fontsize=8)

            # Estética de cierre del Dashboard
            ax.set_title("DISTRIBUCIÓN POR TIPO DE SOLICITUD", color='white', fontweight='bold', fontsize=10)
            ax.tick_params(axis='x', rotation=30, colors='white', labelsize=8)
            ax.tick_params(axis='y', colors='white')
            
            # Eliminar bordes para minimalismo
            for spine in ax.spines.values():
                spine.set_visible(False)

            plt.tight_layout()

            # 4. Integrar en la UI
            canvas = FigureCanvas(fig)
            frame.layout().addWidget(canvas)
            plt.close(fig)

        except Exception as e:
            print(f"Error al graficar casos en frame_6: {e}")