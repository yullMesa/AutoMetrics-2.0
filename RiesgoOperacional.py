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
        # 1. Calcular tiempo transcurrido en segundos
        tiempo_total = time.time() - self.hora_inicio_mercado
        un_minuto = 60
        cinco_minutos = 300

        # 2. Condición: Guardar solo si duró entre 1 y 5 minutos
        if un_minuto <= tiempo_total <= cinco_minutos:
            try:
                ruta_excel = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Sentimiento"
                nombre_archivo = f"analisis_mercado_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
                path_completo = os.path.join(ruta_excel, nombre_archivo)

                # Convertir el diccionario de análisis a una lista para Pandas
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
                print(f"📊 Reporte de Data Analysis guardado: {nombre_archivo}")

            except Exception as e:
                print(f"Error al guardar Excel: {e}")
        else:
            print("⚠️ Sesión fuera de rango (1-5 min). No se generó reporte Excel.")

        event.accept() # Cerrar la ventana definitivamente

    

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

    