import os
import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile,Qt, QSize
from PySide6.QtWidgets import (QTreeWidgetItem,QTableWidgetItem, 
                               QAbstractItemView,QHeaderView,QVBoxLayout,QMessageBox,QToolButton,
                               QSizePolicy,QDialog,QLabel,QHBoxLayout,QPushButton,QMessageBox,QWidget,
                                 QPlainTextEdit)
from PySide6.QtGui import QColor,QIcon, QPixmap,QPainter , QFont , QTextCursor
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtGui import QPixmap
from PySide6.QtCore import QFile, Qt , QSize , QTimer , QRect , QPoint 
import random
from datetime import datetime
import numpy as np
import hashlib
from matplotlib.figure import Figure
import mplfinance as mpf
import pandas as pd
from PySide6.QtCore import QTimer, QDateTime 

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

    
