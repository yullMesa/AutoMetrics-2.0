import os
import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile,Qt, QSize
from PySide6.QtWidgets import (QTreeWidgetItem,QTableWidgetItem, 
                               QAbstractItemView,QHeaderView,QVBoxLayout,QMessageBox,QToolButton,
                               QSizePolicy,QDialog,QLabel,QHBoxLayout,QPushButton,QMessageBox,QWidget)
from PySide6.QtGui import QColor,QIcon, QPixmap,QPainter , QFont
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtGui import QPixmap
from PySide6.QtCore import QFile, Qt , QSize , QTimer , QRect , QPoint
import random
from datetime import datetime
import numpy as np


class Comprar(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        
        # 1. Cargar el archivo .ui
        loader = QUiLoader()
        archivo_ui = QFile("Comprar.ui")
        
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
            self.setWindowTitle("Análisis de Rendimiento del Mercado")
            self.conectar_menu()
            self.ui = self.ui_content
            self.actualizar_catalogo()


        #Financiamiento
        self.cargar_combos_financiamiento()
        self.precio_seleccionado = 0
        self.ui.push_evaluar.clicked.connect(self.evaluar_financiamiento)

        #test drive
        
        self.inicializar_test_drive()
        # Hace que el juego escuche el teclado apenas inicie
        self.juego.setFocus()
        # En tu __init__
        self.ui.stackedWidget.currentChanged.connect(self.gestionar_recursos_pestanas)

        #comparador
        self.cargar_combos_excluyentes()
        self.ui.push_comparar.clicked.connect(self.mostrar_imagen_comparar)
        self.ui.push_comparar.clicked.connect(self.mostrar_comparativa_completa)

        #venta
        self.ui.pushButton_3.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(1))

        # Botón 2 va al índice 2 (ej: Vista de Presupuesto/Gráficos)
        self.ui.pushButton_2.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(2))
        self.cargar_datos_carros()
        # Conexión del botón de venta al proceso de evaluación y guardado
        self.ui.pushButton_venta.clicked.connect(self.procesar_compra_vehiculo)
        # Al hacer clic en la tabla, se ejecutan la función de autocompletado
        self.ui.tableWidget_carros.clicked.connect(self.autocompletar_compra)
        # Conexión del botón de compra final
        self.ui.push_compra.clicked.connect(self.procesar_transaccion_final)


        #dashboard
        self.graficar_combustible()
        self.graficar_analisis_calidad()
        self.graficar_valor_por_marca()
        self.graficar_tendencia_compras()
        self.actualizar_indicadores_principales()
        self.graficar_perfil_inventario()


    def gestionar_recursos_pestanas(self, index):
        # Supongamos que el índice del Test Drive es el 2 (ajústalo al tuyo)
        INDICE_TEST_DRIVE = 2 
            
        if index == INDICE_TEST_DRIVE:
            print("Entrando al Test Drive: Iniciando motor de juego...")
            self.timer_juego.start(16) # 60 FPS aprox
        else:
            if self.timer_juego.isActive():
                print("Saliendo: Deteniendo motor de juego para ahorrar CPU.")
                self.timer_juego.stop()
        # -------------------------------

        #Certificados
        self.cargar_marcas_inicial()
        self.ui.push_certificar.clicked.connect(self.certificar_vehiculo)


        #Estado del vehiculo
        self.configurar_combos_estado()
        self.ui.push_mirar.clicked.connect(self.consultar_estado_vehiculo)


    def inicializar_test_drive(self):
        # 1. Creamos un Layout para el QFrame del Designer
        # Esto sirve para que el juego se estire y ocupe todo el cuadro
        self.layout_juego = QVBoxLayout(self.ui.frame_juego)
        self.layout_juego.setContentsMargins(0, 0, 0, 0) # Sin bordes feos
        
        # 2. Instanciamos la clase del juego
        self.juego = MiniJuegoTestDrive()
        
        # 3. Metemos el objeto del juego dentro del layout del Frame
        self.layout_juego.addWidget(self.juego)
        
        print("Sistema de Test Drive (Gamificación) cargado en el Frame.")


    #pasar paginas
    def conectar_menu(self):
        # Usamos lambda para pasar el número de página deseado
        
        # Dashboard -> Página 0
        self.ui_content.actionGRAFICA.triggered.connect(lambda: self.cambiar_pagina(0))
        
        # Reportes (actionCrud) -> Página 1
        self.ui_content.menuCatalogo.triggered.connect(lambda: self.cambiar_pagina(1))
        
        # Operaciones (actionCrud_3) -> Página 2
        self.ui_content.menuFinanciamiento.triggered.connect(lambda: self.cambiar_pagina(2))
        
        # Análisis (actionCrud_2) -> Página 3
        self.ui_content.menuTest.triggered.connect(lambda: self.cambiar_pagina(3))

        #
        self.ui_content.menuCertificados.triggered.connect(lambda: self.cambiar_pagina(4))
        #
        self.ui_content.menuEstado.triggered.connect(lambda: self.cambiar_pagina(5))
        #
        self.ui_content.menuComparador.triggered.connect(lambda: self.cambiar_pagina(6))
        #
        self.ui_content.menuVENTA.triggered.connect(lambda: self.cambiar_pagina(7))

        # El botón Volver ya te funciona, mantenlo así
        self.ui_content.menuVOLVER.triggered.connect(self.regresar_inicio)

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

    
    
    #Cátalogo

    def actualizar_catalogo(self):
        # 1. Obtener datos de la DB
        datos_carros = self.obtener_datos_db()
        if not datos_carros:
            return

        columnas_max = 4
        num_filas = (len(datos_carros) + 3) // columnas_max
        
        # Configurar el contenedor y el grid
        self.ui.scrollAreaWidgetContents.setMinimumHeight(num_filas * 350)
        self.ui.gridLayout_carros.setAlignment(Qt.AlignTop)
        self.ui.gridLayout_carros.setSpacing(10)

        for i, datos in enumerate(datos_carros):
            marca, modelo, precio = datos 
            fila = i // columnas_max
            columna = i % columnas_max

            # --- A. DEFINIR EL BOTÓN ---
            if i < 8:
                btn = self.ui.gridLayout_carros.itemAt(i).widget()
            else:
                btn = QToolButton()
                btn.setStyleSheet(self.ui.btn_maestro.styleSheet())
                # Aplicamos Expanding para que rellene el grid
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                btn.setMinimumSize(250, 320)
                btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                self.ui.gridLayout_carros.addWidget(btn, fila, columna)

            # --- B. CARGA DE IMAGEN (Directo en el método) ---
            ruta_base = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Carros"
            nombre_limpio = modelo.strip().lower()
            # Probamos con .png y .jpg para asegurar que encuentre el archivo
            archivo_foto = None
            for ext in [".png", ".jpg", ".jpeg"]:
                posible_ruta = os.path.join(ruta_base, f"{nombre_limpio}{ext}")
                if os.path.exists(posible_ruta):
                    archivo_foto = posible_ruta
                    break
            
            # DEBUG: Esto te dirá en la terminal qué está buscando el programa
            if not archivo_foto:
                print(f"DEBUG: No se encontró la foto para: '{nombre_limpio}' en la ruta: {ruta_base}")

            if archivo_foto:
                pixmap = QPixmap(archivo_foto)
                btn.setIcon(QIcon(pixmap))
                btn.setIconSize(QSize(320, 200)) # Tamaño grande para el Expanding
            else:
                # Si no la encuentra, carga la de respaldo
                btn.setIcon(QIcon("assets/default_car.png"))
                btn.setIconSize(QSize(120, 120))

            # --- C. TEXTO Y ACCIÓN ---
            btn.setText(f"{marca}\n{modelo}\n${precio:,}")
            
            # Desconectar para evitar el error de recursión/clicks infinitos
            try:
                btn.clicked.disconnect()
            except:
                pass
                
            btn.clicked.connect(lambda ch=False, m=modelo: self.ventana_emergencia(m))


    def obtener_datos_db(self):
        try:
            import sqlite3
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            # Solo pedimos 3 columnas: Marca, Modelo y Precio
            cursor.execute("SELECT marca, modelo, precio FROM carros")
            datos = cursor.fetchall()
            conn.close()
            return datos
        except Exception as e:
            print(f"Error Base de Datos: {e}")
            return []


    def ventana_emergencia(self, modelo_carro):
        # 1. Consultar TODOS los datos del carro seleccionado
        conn = sqlite3.connect("ingenieria.db")
        cursor = conn.cursor()
        # Traemos más info para la ficha técnica
        cursor.execute("""
            SELECT marca, modelo, año, precio, combustible, transmision, origen 
            FROM carros WHERE modelo = ?""", (modelo_carro,))
        carro = cursor.fetchone()
        conn.close()

        if not carro: return

        # 2. Crear una ventana personalizada (QDialog)
        dialogo = QDialog(self)
        dialogo.setWindowTitle(f"Ficha Técnica: {carro[0]} {carro[1]}")
        dialogo.setMinimumWidth(400)
        dialogo.setStyleSheet("background-color: #121212; color: white; font-family: Segoe UI;")

        layout_principal = QVBoxLayout(dialogo)

        # 3. Contenido de la Ficha Técnica
        titulo = QLabel(f"{carro[0].upper()} {carro[1]}")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ffcc; margin-bottom: 10px;")
        layout_principal.addWidget(titulo)

        info_text = (
            f"<b>Año:</b> {carro[2]}<br>"
            f"<b>Precio:</b> ${carro[3]:,}<br>"
            f"<b>Combustible:</b> {carro[4]}<br>"
            f"<b>Transmisión:</b> {carro[5]}<br>"
            f"<b>Origen:</b> {carro[6]}<br><br>"
            "<i>¿Qué deseas hacer con este vehículo?</i>"
        )
        
        label_info = QLabel(info_text)
        label_info.setStyleSheet("font-size: 14px; line-height: 150%;")
        layout_principal.addWidget(label_info)

        # 4. Botones de Acción (Test Drive y Comprar)
        layout_botones = QHBoxLayout()
        
        btn_test = QPushButton("SOLICITAR TEST DRIVE")
        btn_buy = QPushButton("COMPRAR AHORA")
        
        # Estilo neón para los botones
        estilo_btn = """
            QPushButton { 
                background-color: #1e1e1e; border: 2px solid #00ffcc; color: #00ffcc; 
                padding: 10px; font-weight: bold; border-radius: 5px; 
            }
            QPushButton:hover { background-color: #00ffcc; color: black; }
        """
        btn_test.setStyleSheet(estilo_btn)
        btn_buy.setStyleSheet(estilo_btn)

        # 5. Lógica de Navegación (Usa tu función cambiar_pagina)
        # Asumiendo que Test Drive es página 3 y Venta es página 7
        btn_test.clicked.connect(lambda: [dialogo.accept(), self.cambiar_pagina(3)])
        btn_buy.clicked.connect(lambda: [dialogo.accept(), self.cambiar_pagina(7)])

        layout_botones.addWidget(btn_test)
        layout_botones.addWidget(btn_buy)
        layout_principal.addLayout(layout_botones)

        dialogo.exec()

       

    def obtener_lista_de_carros(self):
        try:
            import sqlite3
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            # Traemos marca, modelo y precio (que son los que usas en el texto del botón)
            cursor.execute("SELECT marca, modelo, precio FROM carros")
            datos = cursor.fetchall()
            conn.close()
            return datos # <--- Esto es lo que evita el error de NoneType
        except Exception as e:
            print(f"Error al obtener datos: {e}")
            return []


    #Financiacion

    def cargar_combos_financiamiento(self):
        # 1. CAMBIO DE RUTA AL ARCHIVO CORRECTO
        ruta_db = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db"
        
        if not os.path.exists(ruta_db):
            print(f"--- ERROR: No se encuentra el archivo {ruta_db} ---")
            return

        try:
            conn = sqlite3.connect(ruta_db)
            cursor = conn.cursor()
            
            # 2. CONSULTA A LA TABLA 'carros' DENTRO DE 'Ingenieria.db'
            cursor.execute("SELECT DISTINCT marca FROM carros WHERE marca IS NOT NULL ORDER BY marca ASC")
            datos = cursor.fetchall()
            
            if datos:
                self.ui.combo_Marca.clear()
                # Limpiamos los datos de la tupla
                marcas = [str(fila[0]) for fila in datos]
                self.ui.combo_Marca.addItems(marcas)
                print(f"CONECTADO A Ingenieria.db: {len(marcas)} marcas cargadas.")
            else:
                print("Conectado a Ingenieria.db, pero la tabla 'carros' parece estar vacía.")

            conn.close()
            
            # Conectar el evento para actualizar modelos
            # Usamos try/except para evitar conexiones duplicadas si llamas la función varias veces
            # Conexión limpia del primer combo (Marca)
            try:
                self.ui.combo_Marca.currentIndexChanged.disconnect()
            except:
                pass
                
            self.ui.combo_Marca.currentIndexChanged.connect(self.actualizar_modelos_financiamiento)
            
            # Forzar la carga inicial de modelos
            self.actualizar_modelos_financiamiento()
            self.actualizar_foto_financiamiento()

        except sqlite3.Error as e:
            print(f"Error de SQLite: {e}")

    def actualizar_modelos_financiamiento(self):
        marca_seleccionada = self.ui.combo_Marca.currentText()
        if not marca_seleccionada:
            return

        ruta_db = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db"
        
        try:
            conn = sqlite3.connect(ruta_db)
            cursor = conn.cursor()
            
            # Filtramos por la marca seleccionada
            cursor.execute("SELECT modelo FROM carros WHERE marca = ? ORDER BY modelo ASC", (marca_seleccionada,))
            datos = cursor.fetchall()
            
            self.ui.combo_Modelo.clear()
            if datos:
                modelos = [str(fila[0]) for fila in datos]
                self.ui.combo_Modelo.addItems(modelos)

            
            conn.close()
            
            # Una vez que hay modelo, actualizamos la foto en el ToolButton
            self.actualizar_foto_financiamiento()
            self.ui.combo_Modelo.currentIndexChanged.disconnect()
            self.ui.combo_Modelo.currentIndexChanged.connect(self.actualizar_foto_financiamiento)
            self.actualizar_foto_financiamiento()
            
        except sqlite3.Error as e:
            print(f"Error al cargar modelos: {e}")

    #imagen 

    def actualizar_foto_financiamiento(self):
        modelo = self.ui.combo_Modelo.currentText()
        if not modelo:
            return

        # 1. Obtener Precio de la DB
        try:
            conn = sqlite3.connect(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db")
            cursor = conn.cursor()
            # Buscamos el precio del modelo seleccionado
            cursor.execute("SELECT precio FROM carros WHERE modelo = ?", (modelo,))
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado:
                self.precio_seleccionado = float(resultado[0])
                print(f"DEBUG: Modelo {modelo} seleccionado. Precio: ${self.precio_seleccionado}")
            else:
                self.precio_seleccionado = 0
        except Exception as e:
            print(f"Error al consultar precio: {e}")

        # 2. Cargar Imagen (Tu código que ya funciona)
        ruta_base = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Carros"
        nombre_archivo = modelo.strip()
        # ... (Aquí va tu lógica de búsqueda de archivo que ya tienes lista) ...
        
        archivo_encontrado = None
        extensiones = [".png", ".jpg", ".jpeg"]

        # Buscamos combinaciones (Exacto, minúsculas, etc.) para asegurar el "match"
        intentos = [nombre_archivo, nombre_archivo.lower(), nombre_archivo.upper()]

        for intento in intentos:
            for ext in extensiones:
                ruta_posible = os.path.join(ruta_base, f"{intento}{ext}")
                if os.path.exists(ruta_posible):
                    archivo_encontrado = ruta_posible
                    break
            if archivo_encontrado: break

        if archivo_encontrado:
            pixmap = QPixmap(archivo_encontrado)
            # IMPORTANTE: Escalar con suavizado para que el carro se vea bien
            pixmap_escalado = pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.ui.toolImagen.setIcon(QIcon(pixmap_escalado))
            self.ui.toolImagen.setIconSize(QSize(300, 200))
            print(f"DEBUG: Imagen cargada -> {archivo_encontrado}")
        else:
            print(f"DEBUG: No se encontró imagen para '{modelo}' en la carpeta Carros")
            self.ui.toolImagen.setIcon(QIcon()) # Limpiar si no hay foto

    #si o no

    def evaluar_financiamiento(self):
        try:
            # 1. DEFINIR EL MODELO (Indispensable para el mensaje final)
            modelo = self.ui.combo_Modelo.currentText()
            
            # 2. Extraer datos de la UI
            ingreso = float(self.ui.lbl_ingreso.text() or 0)
            gastos = float(self.ui.lbl_gastos.text() or 0)
            historial = self.ui.combo_crediticio.currentText()
            
            # Validación de selección de vehículo
            if not hasattr(self, 'precio_seleccionado') or self.precio_seleccionado == 0:
                QMessageBox.warning(self, "Error", "Primero selecciona un vehículo en la imagen.")
                return

            # 3. Lógica de analista: Cuota y capacidad
            cuota = (self.precio_seleccionado / 48) + (self.precio_seleccionado * 0.015)
            sobrante = ingreso - gastos
            
            # 4. Configuración del Veredicto (QMessageBox)
            msg = QMessageBox(self)
            msg.setWindowTitle("Veredicto AutoMetrics")
            
            # Aplicamos la regla de negocio: Historial y capacidad de pago
            if historial in ["Excelente", "Buena"] and cuota <= (sobrante * 0.35):
                msg.setIcon(QMessageBox.Information)
                msg.setText("✅ CRÉDITO PRE-APROBADO")
                # Aquí ya no dará error porque 'modelo' está definido arriba
                msg.setInformativeText(f"El cliente aplica para el {modelo}.\n\nCuota mensual: ${cuota:,.2f}")
            else:
                msg.setIcon(QMessageBox.Critical)
                msg.setText("❌ CRÉDITO NO APROBADO")
                msg.setInformativeText(f"El nivel de riesgo o capacidad de pago para el {modelo} no cumple los requisitos.")
            
            msg.exec() # En PySide6 es .exec()

        except ValueError:
            QMessageBox.warning(self, "Datos Inválidos", "Por favor ingresa montos numéricos en ingresos y gastos.")
    

    #certifiado

    def cargar_marcas_inicial(self):
        try:
            conn = sqlite3.connect(r"Ingenieria.db")
            cursor = conn.cursor()
            
            # Obtenemos solo valores únicos de la columna marca
            cursor.execute("SELECT DISTINCT marca FROM carros ORDER BY marca ASC")
            marcas = [fila[0] for fila in cursor.fetchall()]
            conn.close()

            self.ui.combo_marca.clear()
            self.ui.combo_marca.addItems(marcas)
            
            # Conectamos el evento: cuando cambie la marca, actualizamos los modelos
            self.ui.combo_marca.currentIndexChanged.connect(self.actualizar_modelos_filtrados)
            
            # Ejecutamos una vez para cargar los modelos de la primera marca que aparezca
            self.actualizar_modelos_filtrados()
            
        except Exception as e:
            print(f"Error cargando marcas: {e}")

    def actualizar_modelos_filtrados(self):
        marca_seleccionada = self.ui.combo_marca.currentText()
        
        if not marca_seleccionada:
            return

        try:
            # Bloqueamos señales para evitar que se disparen eventos mientras limpiamos
            self.ui.combo_modelo.blockSignals(True)
            self.ui.combo_modelo.clear()
            
            conn = sqlite3.connect(r"Ingenieria.db")
            cursor = conn.cursor()
            
            # Filtramos modelos que pertenezcan a la marca seleccionada
            cursor.execute("SELECT modelo FROM carros WHERE marca = ? ORDER BY modelo ASC", (marca_seleccionada,))
            modelos = [fila[0] for fila in cursor.fetchall()]
            conn.close()

            self.ui.combo_modelo.addItems(modelos)
            self.ui.combo_modelo.blockSignals(False)
            
            # Opcional: Actualizar la foto y el certificado automáticamente al cambiar el modelo
            if hasattr(self, 'actualizar_foto_financiamiento'):
                self.actualizar_foto_financiamiento()
                
        except Exception as e:
            print(f"Error filtrando modelos: {e}")




    def certificar_vehiculo(self):
        ruta_plantilla = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\certificado\certificado.png"
        pixmap = QPixmap(ruta_plantilla)
        
        if pixmap.isNull():
            print("Error: No se encontró la imagen.")
            return

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 1. Configurar la fuente (ajusté el tamaño a 30 para que quepa bien en el cuadro)
        font = QFont("Arial", 30, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#1a1a1a")) 

        # 2. Obtener datos
        marca = self.ui.combo_marca.currentText().upper()
        modelo = self.ui.combo_modelo.currentText().upper()
        texto = f"{marca} - {modelo}"

        # 3. DEFINIR EL ÁREA DEL RECUADRO BLANCO
        # Basado en tu imagen, el cuadro blanco está cerca del final (80% hacia abajo)
        ancho_img = pixmap.width()
        alto_img = pixmap.height()
        
        # Coordenadas calculadas para el cuadro blanco inferior:
        # X: 0 (usamos todo el ancho para centrar)
        # Y: alto_img * 0.82 (Baja el texto al 82% de la altura de la imagen)
        # Ancho: ancho_img
        # Alto: 100 (altura del área de escritura)
        posicion_y = int(alto_img * 0.82) 
        rectangulo_blanco = QRect(0, posicion_y, ancho_img, 100)

        # 4. Dibujar centrado en ese rectángulo específico
        painter.drawText(rectangulo_blanco, Qt.AlignCenter, texto)
        
        painter.end()

        # 5. Mostrar en la UI
        pixmap_redimensionado = pixmap.scaled(
            self.ui.lblVistaCertificado.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.ui.lblVistaCertificado.setPixmap(pixmap_redimensionado)


    #estado

    def configurar_combos_estado(self):
        """Carga inicial de marcas para la pestaña de Estado del Vehículo"""
        try:
            conn = sqlite3.connect(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db")
            cursor = conn.cursor()
            
            # Obtenemos las marcas únicas
            cursor.execute("SELECT DISTINCT marca FROM carros ORDER BY marca ASC")
            marcas = [fila[0] for fila in cursor.fetchall()]
            conn.close()

            self.ui.combo_marca_3.clear()
            self.ui.combo_marca_3.addItems(marcas)
            
            # Conectamos el cambio de marca para que filtre los modelos
            self.ui.combo_marca_3.currentIndexChanged.connect(self.filtrar_modelos_estado)
            
            # Cargamos los modelos de la primera marca por defecto
            self.filtrar_modelos_estado()
            
        except Exception as e:
            print(f"Error en combo_marca_3: {e}")

    def filtrar_modelos_estado(self):
        """Filtra el combo_modelo_3 según lo que diga combo_marca_3"""
        marca_sel = self.ui.combo_marca_3.currentText()
        
        if not marca_sel:
            return

        try:
            # Bloqueamos señales para que no intente disparar otros eventos mientras limpia
            self.ui.combo_modelo_3.blockSignals(True)
            self.ui.combo_modelo_3.clear()
            
            conn = sqlite3.connect(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT modelo FROM carros WHERE marca = ? ORDER BY modelo ASC", (marca_sel,))
            modelos = [fila[0] for fila in cursor.fetchall()]
            conn.close()

            self.ui.combo_modelo_3.addItems(modelos)
            self.ui.combo_modelo_3.blockSignals(False)
            
        except Exception as e:
            print(f"Error en combo_modelo_3: {e}")

    
    #treewidget

    def consultar_estado_vehiculo(self):
        marca = self.ui.combo_marca_3.currentText()
        modelo = self.ui.combo_modelo_3.currentText()

        try:
            conn = sqlite3.connect(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db")
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM carros WHERE marca = ? AND modelo = ?", (marca, modelo))
            carro = cursor.fetchone()
            conn.close()

            if carro:
                self.llenar_tree_mirar(carro)
            else:
                print("No se encontraron datos para este vehículo.")

        except Exception as e:
            print(f"Error al consultar estado: {e}")

    def llenar_tree_mirar(self, datos):
        tree = self.ui.tree_mirar
        
        # 1. Configuración de espacio (Solo la primera vez)
        tree.setColumnCount(2)
        tree.setHeaderLabels(["Componente / Carro", "Valor Detallado"])
        # Ajustar columnas al contenido
        tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        # 2. CREAR NODO PADRE (Carpeta del Carro)
        # Usamos la marca y modelo como título de la carpeta
        titulo_carro = f"🚗 {datos['marca']} {datos['modelo']}"
        carro_root = QTreeWidgetItem(tree, [titulo_carro, "Consultado ahora"])
        
        # Estilo visual para resaltar el título (opcional)
        carro_root.setBackground(0, QColor("#00f2ff"))
        carro_root.setForeground(0, QColor("#000000"))

        # 3. AGREGAR TODA LA DATA DE LA TABLA (Basado en tu imagen de la DB)
        # Categoría: Especificaciones
        cat_specs = QTreeWidgetItem(carro_root, ["⚙️ Especificaciones Técnicas"])
        QTreeWidgetItem(cat_specs, ["Año", str(datos['año'])])
        QTreeWidgetItem(cat_specs, ["Combustible", str(datos['combustible'])])
        QTreeWidgetItem(cat_specs, ["Transmisión", str(datos['transmision'])])
        QTreeWidgetItem(cat_specs, ["Origen", str(datos['origen'])])
        
        # Categoría: Estado y Mercado
        cat_estado = QTreeWidgetItem(carro_root, ["📊 Análisis de Estado"])
        QTreeWidgetItem(cat_estado, ["Kilometraje", f"{datos['kilometraje']:,} km"])
        QTreeWidgetItem(cat_estado, ["Estado Certificación", str(datos['estado_certificacion'])])
        QTreeWidgetItem(cat_estado, ["Stock Disponible", str(datos['stock_disponible'])])
        
        # Categoría: Precio
        cat_money = QTreeWidgetItem(carro_root, ["💰 Información Comercial"])
        precio_formateado = f"${datos['precio']:,.2f}"
        QTreeWidgetItem(cat_money, ["Precio de Lista", precio_formateado])

        # 4. Mostrar el nuevo carro arriba de todo
        tree.insertTopLevelItem(0, carro_root)
        carro_root.setExpanded(True) # Abrir la carpeta del nuevo automáticamente


    #Comparador

    def cargar_combos_excluyentes(self):
        try:
            conn = sqlite3.connect(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT marca FROM carros ORDER BY marca ASC")
            marcas = [fila[0] for fila in cursor.fetchall()]
            conn.close()

            # Llenamos todos los combos de marca (4 y 5)
            combos_marca = [self.ui.combo_marca_4, self.ui.combo_marca_5]
            for combo in combos_marca:
                combo.blockSignals(True)
                combo.clear()
                combo.addItems(marcas)
                combo.blockSignals(False)

            # Conectamos los eventos de cambio
            self.ui.combo_marca_4.currentIndexChanged.connect(lambda: self.filtrar_modelos_y_excluir(4))
            self.ui.combo_marca_5.currentIndexChanged.connect(lambda: self.filtrar_modelos_y_excluir(5))
            
        except Exception as e:
            print(f"Error cargando combos 4 y 5: {e}")

    def filtrar_modelos_y_excluir(self, pestaña_num):
        # Definimos cuál es el combo actual y cuál el "rival"
        if pestaña_num == 4:
            combo_m = self.ui.combo_marca_4
            combo_mod = self.ui.combo_modelo_4
            rival_mod = self.ui.combo_modelo_5.currentText()
        else:
            combo_m = self.ui.combo_marca_5
            combo_mod = self.ui.combo_modelo_5
            rival_mod = self.ui.combo_modelo_4.currentText()

        marca_sel = combo_m.currentText()
        
        try:
            conn = sqlite3.connect(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("SELECT modelo FROM carros WHERE marca = ?", (marca_sel,))
            modelos = [fila[0] for fila in cursor.fetchall()]
            conn.close()

            combo_mod.blockSignals(True)
            combo_mod.clear()
            
            # EL FILTRO: Si el modelo está en el otro combo, no lo agregamos aquí
            modelos_filtrados = [m for m in modelos if m != rival_mod]
            
            combo_mod.addItems(modelos_filtrados)
            combo_mod.blockSignals(False)

        except Exception as e:
            print(f"Error filtrando modelos en pestaña {pestaña_num}: {e}")

   
    def mostrar_imagen_comparar(self):
        # 1. Obtener los datos directamente de los combos
        marca = self.ui.combo_marca_4.currentText()
        modelo = self.ui.combo_modelo_4.currentText()

        # 2. Ruta de la carpeta de imágenes (Usa la ruta absoluta que ya tienes)
        carpeta_fotos = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Carros"
        
        # 3. Construir la ruta usando el nombre del MODELO
        # f"{modelo}.png" buscará "M4 Competition.png"
        ruta_final = os.path.join(carpeta_fotos, f"{modelo}.png")
        
        print(f"Buscando imagen por modelo: {ruta_final}")

        try:
            if os.path.exists(ruta_final):
                pixmap = QPixmap(ruta_final)
                if not pixmap.isNull():
                    # Ajustar al label_133
                    self.ui.label_133.setPixmap(pixmap.scaled(
                        self.ui.label_133.size(), 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    ))
                    self.ui.label_133.setAlignment(Qt.AlignCenter)
                else:
                    print("Error: El archivo existe pero el formato no es válido.")
                    self.ui.label_133.setText("Error de Formato")
            else:
                print(f"⚠️ No se encontró: {modelo}.png en la carpeta Carros")
                self.ui.label_133.setText("Imagen no encontrada")
                
        except Exception as e:
            print(f"Error al cargar imagen: {e}")
    
    def mostrar_comparativa_completa(self):
        # Carpeta donde están tus PNGs
        carpeta_fotos = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Carros"

        # --- VEHÍCULO 1 (Pestaña 4 -> label_133) ---
        modelo_4 = self.ui.combo_modelo_4.currentText()
        ruta_4 = os.path.join(carpeta_fotos, f"{modelo_4}.png")
        self.cargar_imagen_en_label(ruta_4, self.ui.label_133)

        # --- VEHÍCULO 2 (Pestaña 5 -> label_134) ---
        modelo_5 = self.ui.combo_modelo_5.currentText()
        ruta_5 = os.path.join(carpeta_fotos, f"{modelo_5}.png")
        self.cargar_imagen_en_label(ruta_5, self.ui.label_134)

    def cargar_imagen_en_label(self, ruta, label_destino):
        """Función auxiliar para evitar repetir código (Poka-Yoke)"""
        try:
            if os.path.exists(ruta):
                pixmap = QPixmap(ruta)
                if not pixmap.isNull():
                    label_destino.setPixmap(pixmap.scaled(
                        label_destino.size(), 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    ))
                    label_destino.setAlignment(Qt.AlignCenter)
                else:
                    label_destino.setText("Error de Formato")
            else:
                label_destino.setText("No encontrado")
                print(f"⚠️ Archivo no encontrado: {ruta}")
        except Exception as e:
            print(f"Error cargando imagen: {e}")
            
    #Venta

    def calcular_score_compra(self):
        # 1. Capturar datos de la encuesta y LineEdits
        estetico = self.ui.combo_estetico.currentIndex() 
        papeles = self.ui.combo_papeles.currentIndex()   
        mantenimiento = self.ui.combo_mant.currentIndex() 
        test_drive = self.ui.combo_test.currentIndex()
        
        marca = self.ui.line_marca_v.text()
        modelo = self.ui.line_modelo_v.text()
        anio = self.ui.line_anio_v.text()
        km = self.ui.line_km_v.text()

        # 2. Inicializar y calcular puntos (IMPORTANTE: Hacer esto ANTES del IF)
        self.puntos_calculados = 0 
        
        # Evaluación Estética
        if estetico == 0: self.puntos_calculados += 30      # Excelente
        elif estetico == 1: self.puntos_calculados += 20    # Bueno
        
        # Evaluación Papeles (Crítico)
        if papeles == 0: self.puntos_calculados += 30      # Al día
        else: self.puntos_calculados -= 50                 # Penalización deudas
        
        # Evaluación Mecánica y Ruta
        if mantenimiento == 0: self.puntos_calculados += 20 
        if test_drive == 0: self.puntos_calculados += 20

        # 3. Lógica de decisión de compra (Basada en los puntos recién calculados)
        try:
            km_int = int(km) if km else 0
            if km_int < 100000 and self.puntos_calculados >= 80:
                print(f"✅ Compra aprobada para {marca} {modelo}")
                # Aquí llamarías a tu método de guardar en SQL
                self.ejecutar_transaccion_sql(marca, modelo, anio, km_int)
            else:
                print("❌ El vehículo no cumple los estándares de calidad.")
        except ValueError:
            print("⚠️ Error: El kilometraje debe ser un número válido.")

        # 4. Mostrar Veredicto dinámico en la UI
        label_resultado = self.ui.lbl_resultado_encuesta
        if self.puntos_calculados >= 80:
            label_resultado.setText(f"✅ COMPRA SEGURA ({self.puntos_calculados} pts)")
            label_resultado.setStyleSheet("color: #00ff00; font-weight: bold;")
        elif self.puntos_calculados >= 50:
            label_resultado.setText(f"⚠️ COMPRA RIESGOSA ({self.puntos_calculados} pts)")
            label_resultado.setStyleSheet("color: #ffff00; font-weight: bold;")
        else:
            label_resultado.setText(f"❌ RECHAZADO ({self.puntos_calculados} pts)")
            label_resultado.setStyleSheet("color: #ff4444; font-weight: bold;")
   
   
    def guardar_encuesta_compra(self):
        # Capturar datos de los nuevos 4 LineEdits
        marca = self.ui.line_marca_v.text()      # Ajusta el nombre según tu .ui
        modelo = self.ui.line_modelo_v.text()
        año = self.ui.line_año_v.text()
        km = self.ui.line_km_v.text()
        
        puntos = self.puntos_calculados
        # Usamos strip() para limpiar espacios en blanco de las observaciones
        observaciones = self.ui.txt_observaciones.toPlainText().strip()

        try:
            conn = sqlite3.connect(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db")
            cursor = conn.cursor()
            
            # Tabla extendida para incluir los nuevos datos técnicos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auditoria_compras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    marca TEXT,
                    modelo TEXT,
                    año TEXT,
                    kilometraje TEXT,
                    puntaje INTEGER,
                    fecha TEXT,
                    comentario TEXT
                )
            """)
            
            cursor.execute("""
                INSERT INTO auditoria_compras 
                (marca, modelo, año, kilometraje, puntaje, fecha, comentario) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (marca, modelo, año, km, puntos, datetime.now().isoformat(), observaciones))
            
            conn.commit()
            conn.close()
            print(f"Auditoría guardada: {marca} {modelo} con {puntos} puntos.")
            
        except Exception as e:
            print(f"Error al guardar auditoría: {e}")


    def procesar_decision_compra(self):
        # 1. Obtener datos técnicos y financieros
        marca = self.ui.line_marca_v.text()
        modelo = self.ui.line_modelo_v.text()
        año = int(self.ui.line_año_v.text() or 0)
        km = int(self.ui.line_km_v.text() or 0)
        valor_oferta = float(self.ui.line_valor_oferta.text() or 0) # Debes crear este LineEdit
        
        # 2. Validar Criterios de Calidad (Poka-Yoke)
        # Compramos si: Score > 75 Y el KM < 100,000 Y el carro no es muy viejo (ej: > 2015)
        score = self.puntos_calculados
        
        es_buen_carro = score >= 75 and km < 100000 and año >= 2016
        
        if not es_buen_carro:
            self.ui.lbl_veredicto.setText("❌ RECHAZADO: No cumple estándares de calidad.")
            return

        # 3. Validar Presupuesto Disponible
        try:
            conn = sqlite3.connect(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT monto_total FROM presupuesto_empresa WHERE id = 1")
            presupuesto_actual = cursor.fetchone()[0]
            
            if valor_oferta > presupuesto_actual:
                self.ui.lbl_veredicto.setText("❌ RECHAZADO: Presupuesto insuficiente.")
                conn.close()
                return

            # 4. EJECUTAR COMPRA (Transacción Atómica)
            # Restar del presupuesto
            cursor.execute("UPDATE presupuesto_empresa SET monto_total = monto_total - ? WHERE id = 1", (valor_oferta,))
            
            # Registrar en historial
            cursor.execute("""
                INSERT INTO compras_aprobadas (marca, modelo, año, kilometraje, puntaje_inspeccion, valor_pagado, fecha_compra)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (marca, modelo, año, km, score, valor_oferta, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            conn.commit()
            conn.close()
            
            self.ui.lbl_veredicto.setText(f"✅ COMPRA EXITOSA: {marca} {modelo} añadido al inventario.")
            print(f"Transacción completada. Nuevo presupuesto: {presupuesto_actual - valor_oferta}")

        except Exception as e:
            print(f"Error en la transacción financiera: {e}")

    def navegar_panels(self, indice):
        # Aquí puedes agregar lógica Poka-Yoke
        # Ejemplo: Si va al índice 2 (Presupuesto), refrescar los datos de SQL
        if indice == 2:
            self.actualizar_vista_presupuesto()
            print("Cargando datos financieros...")
            
        self.ui.stackedWidget_2.setCurrentIndex(indice)


    def cargar_datos_carros(self):
        try:
            conn = sqlite3.connect(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db")
            cursor = conn.cursor()
            
            # Traemos el ID de primero para tenerlo como referencia, aunque no se vea
            cursor.execute("""
                SELECT id_carro, marca, modelo, año, precio, combustible, 
                    transmision, origen, kilometraje, estado_certificacion, stock_disponible 
                FROM carros
            """)
            datos = cursor.fetchall()
            
            # Etiquetas de cabecera (Sin el ID)
            columnas = ["MARCA", "MODELO", "AÑO", "PRECIO", "MOTOR", "CAJA", "ORIGEN", "KM", "ESTADO", "STOCK"]
            
            self.ui.tableWidget_carros.setRowCount(len(datos))
            self.ui.tableWidget_carros.setColumnCount(11) # Mantenemos 11 columnas
            # Seteamos las etiquetas empezando desde la columna 1 para saltar el ID visualmente
            self.ui.tableWidget_carros.setHorizontalHeaderLabels(["ID"] + columnas)
            # Oculta la columna 0 (donde está el ID)
            self.ui.tableWidget_carros.setColumnHidden(0, True)

            # Oculta los números de fila de la izquierda (1, 2, 3...)
            self.ui.tableWidget_carros.verticalHeader().setVisible(False)

            for row_number, row_data in enumerate(datos):
                for column_number, data in enumerate(row_data):
                    # Formateo de datos
                    if column_number == 4: # Precio
                        valor = f"${float(data):,.0f}"
                    elif column_number == 8: # KM
                        valor = f"{int(data):,} km"
                    else:
                        valor = str(data)
                    
                    self.ui.tableWidget_carros.setItem(row_number, column_number, QTableWidgetItem(valor))
            
            # --- CONFIGURACIÓN VISUAL FINAL ---
            # 1. Ocultar el ID (columna 0)
            self.ui.tableWidget_carros.setColumnHidden(0, True)
            
            # 2. Ocultar números de fila
            self.ui.tableWidget_carros.verticalHeader().setVisible(False)
            
            # 3. Estirar columnas para ocupar todo el espacio
            header = self.ui.tableWidget_carros.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)
            
            conn.close()
            
        except Exception as e:
            print(f"Error: {e}")

    
    #verificacion de si se compra el auto

    def procesar_compra_vehiculo(self):
        try:
            # 1. Captura de datos
            marca = self.ui.txt_marca.text()
            modelo = self.ui.txt_modelo.text()
            anio = self.ui.txt_ano.text()
            km_txt = self.ui.txt_kilometraje.text()

            if not all([marca, modelo, anio, km_txt]):
                self.mostrar_mensaje_personalizado("Error", "Todos los campos son obligatorios.", False)
                return

            puntaje = 0
            # Evaluación por Combobox
            if self.ui.combo_estado.currentIndex() == 0: puntaje += 30
            if self.ui.combo_papeleria.currentIndex() == 0: puntaje += 30
            if self.ui.combo_historia.currentIndex() == 0: puntaje += 20
            if self.ui.combo_prueba.currentIndex() == 0: puntaje += 20

            # 2. Lógica de decisión
            aprobado = puntaje >= 80 and int(km_txt) < 100000

            if aprobado:
                self.ejecutar_guardado_db(marca, modelo, int(anio), int(km_txt), puntaje)
                self.mostrar_mensaje_personalizado("Éxito", f"COMPRA APROBADA\n{marca} {modelo}\nPuntaje: {puntaje} pts", True)
            else:
                self.mostrar_mensaje_personalizado("Rechazado", f"EL VEHÍCULO NO CUMPLE\nPuntaje: {puntaje} pts", False)

        except ValueError:
            self.mostrar_mensaje_personalizado("Error", "Año y KM deben ser números.", False)

    def mostrar_mensaje_personalizado(self, titulo, mensaje, es_exito):
        msg = QMessageBox(self)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        
        # Color verde neón de tu UI
        color_neon = "#00ffcc" if es_exito else "#ff4444"
        
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: #1e1e2e;
                border: 2px solid {color_neon};
            }}
            QLabel {{
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }}
            QPushButton {{
                background-color: #2d2d3d;
                color: {color_neon};
                border: 1px solid {color_neon};
                padding: 5px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color_neon};
                color: #1e1e2e;
            }}
        """)
        msg.exec()

    def ejecutar_guardado_db(self, marca, modelo, anio, km, puntaje):
        try:
            conn = sqlite3.connect(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db")
            cursor = conn.cursor()
            
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Insertamos en la tabla con la estructura correcta
            query = """
                INSERT INTO compras_aprobadas (marca, modelo, año, kilometraje, puntaje_inspeccion, valor_pagado, fecha_compra)
                VALUES (?, ?, ?, ?, ?, 0.0, ?)
            """
            cursor.execute(query, (marca, modelo, anio, km, puntaje, fecha))
            
            conn.commit()
            conn.close()
            print("💾 Datos guardados exitosamente en la base de datos.")
            
        except Exception as e:
            print(f"❌ Error de base de datos: {e}")

    def autocompletar_compra(self):
        fila = self.ui.tableWidget_carros.currentRow()
        # Extraemos datos de las columnas (ajusta los índices según tu SELECT)
        self.ui.txt_marca_2.setText(self.ui.tableWidget_carros.item(fila, 1).text())
        self.ui.txt_modelo_2.setText(self.ui.tableWidget_carros.item(fila, 2).text())
        self.ui.txt_ano_2.setText(self.ui.tableWidget_carros.item(fila, 3).text())
        self.ui.txt_precio.setText(self.ui.tableWidget_carros.item(fila, 4).text())

    def procesar_transaccion_final(self):
        fila = self.ui.tableWidget_carros.currentRow()
        if fila == -1:
            self.mostrar_mensaje_personalizado("Error", "Selecciona un carro de la tabla primero.", False)
            return

        # Obtenemos el ID (oculto en col 0) y el stock actual
        id_carro = self.ui.tableWidget_carros.item(fila, 0).text()
        # Limpiamos el texto del stock (por si tiene decimales o strings)
        stock_actual = float(self.ui.tableWidget_carros.item(fila, 10).text()) 

        if stock_actual <= 0:
            self.mostrar_mensaje_personalizado("SIN STOCK", "Lo sentimos, no quedan unidades de este vehículo.", False)
            return

        try:
            conn = sqlite3.connect(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db")
            cursor = conn.cursor()

            # 1. Descontar stock en la tabla 'carros'
            cursor.execute("UPDATE carros SET stock_disponible = stock_disponible - 1 WHERE id_carro = ?", (id_carro,))
            
            conn.commit()
            conn.close()

            # 2. Notificar éxito y refrescar tabla
            self.mostrar_mensaje_personalizado("Éxito", "¡Compra realizada con éxito!", True)
            self.cargar_datos_carros() # Recarga la tabla para ver el stock actualizado
            
        except Exception as e:
            self.mostrar_mensaje_personalizado("Error DB", f"No se pudo procesar: {e}", False)

    
    #grafica de dashboard

    def graficar_combustible(self):
        try:
            # 1. Conexión y Extracción de Datos
            conn = sqlite3.connect(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("SELECT combustible, COUNT(*) FROM carros GROUP BY combustible")
            datos = cursor.fetchall()
            conn.close()

            combustibles = [row[0] for row in datos]
            cantidades = [row[1] for row in datos]

            # 2. Configuración del Gráfico (Estilo Dark Neón)
            fig, ax = plt.subplots(figsize=(5, 4), tight_layout=True)
            fig.patch.set_facecolor('#1e1e2e')  # Fondo del canvas
            ax.set_facecolor('#1e1e2e')
            
            # Colores cian neón consistentes con tu UI
            barras = ax.bar(combustibles, cantidades, color='#00ffcc', edgecolor='white', linewidth=0.5)
            
            # Etiquetas y Estética
            ax.set_title("Distribución por Combustible", color='white', fontsize=12, fontweight='bold')
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_color('#3c3c4c')

            # 3. Embeber en el frame_3
            # Limpiamos el frame por si ya tiene un gráfico previo
            if self.ui.frame_3.layout() is not None:
                # Eliminar layout viejo de forma segura
                while self.ui.frame_3.layout().count():
                    child = self.ui.frame_3.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
            else:
                layout = QVBoxLayout(self.ui.frame_3)
                self.ui.frame_3.setLayout(layout)

            canvas = FigureCanvas(fig)
            self.ui.frame_3.layout().addWidget(canvas)
            canvas.draw()

        except Exception as e:
            print(f"Error al graficar: {e}")

    def graficar_analisis_calidad(self):
        try:
            # 1. Extracción de datos cruzados
            conn = sqlite3.connect(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db")
            cursor = conn.cursor()
            
            # Obtenemos puntaje vs kilometraje de las compras aprobadas
            cursor.execute("SELECT kilometraje, puntaje_inspeccion FROM compras_aprobadas")
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                print("No hay datos en compras_aprobadas para graficar.")
                return

            kms = [row[0] for row in datos]
            puntajes = [row[1] for row in datos]

            # 2. Creación del gráfico de dispersión (Scatter Plot)
            fig, ax = plt.subplots(figsize=(5, 4), tight_layout=True)
            fig.patch.set_facecolor('#1e1e2e') # Fondo oscuro de tu UI
            ax.set_facecolor('#1e1e2e')
            
            # Puntos en verde neón
            ax.scatter(kms, puntajes, color='#00ffcc', s=100, alpha=0.7, edgecolors='white')
            
            # Configuración estética
            ax.set_title("Calidad vs. Kilometraje (Compras)", color='white', fontweight='bold')
            ax.set_xlabel("Kilometraje", color='white')
            ax.set_ylabel("Puntaje Inspección", color='white')
            ax.tick_params(colors='white')
            ax.grid(True, linestyle='--', alpha=0.2)

            # 3. Limpiar y refrescar frame_4
            if self.ui.frame_4.layout() is not None:
                while self.ui.frame_4.layout().count():
                    child = self.ui.frame_4.layout().takeAt(0)
                    if child.widget(): child.widget().deleteLater()
            else:
                layout = QVBoxLayout(self.ui.frame_4)
                self.ui.frame_4.setLayout(layout)

            canvas = FigureCanvas(fig)
            self.ui.frame_4.layout().addWidget(canvas)
            canvas.draw()

        except Exception as e:
            print(f"Error en gráfico frame_4: {e}")
    
    def graficar_valor_por_marca(self):
        try:
            # 1. Extracción de datos financieros
            conn = sqlite3.connect(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db")
            cursor = conn.cursor()
            
            # Sumamos el precio total agrupado por marca
            cursor.execute("SELECT marca, SUM(precio) FROM carros GROUP BY marca ORDER BY SUM(precio) DESC")
            datos = cursor.fetchall()
            conn.close()

            if not datos: return

            marcas = [row[0] for row in datos]
            valores = [row[1] for row in datos]

            # 2. Creación del gráfico de barras horizontales
            fig, ax = plt.subplots(figsize=(5, 4), tight_layout=True)
            fig.patch.set_facecolor('#1e1e2e') 
            ax.set_facecolor('#1e1e2e')
            
            # Usamos el color de la sección de VENTAS
            ax.barh(marcas, valores, color='#00ffcc', alpha=0.8)
            
            # Estética de Dashboard Profesional
            ax.set_title("Capital Invertido por Marca", color='white', fontweight='bold', fontsize=12)
            ax.set_xlabel("Valor Total ($)", color='white')
            ax.tick_params(colors='white', labelsize=9)
            
            # Eliminar bordes innecesarios (estilo minimalista)
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.xaxis.grid(True, linestyle='--', alpha=0.2)

            # 3. Insertar en frame_2
            if self.ui.frame_2.layout() is not None:
                while self.ui.frame_2.layout().count():
                    child = self.ui.frame_2.layout().takeAt(0)
                    if child.widget(): child.widget().deleteLater()
            else:
                layout = QVBoxLayout(self.ui.frame_2)
                self.ui.frame_2.setLayout(layout)

            canvas = FigureCanvas(fig)
            self.ui.frame_2.layout().addWidget(canvas)
            canvas.draw()

        except Exception as e:
            print(f"Error en gráfico frame_2: {e}")


    def graficar_tendencia_compras(self):
        try:
            # 1. Extracción de datos por fecha
            conn = sqlite3.connect(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db")
            cursor = conn.cursor()
            
            # Extraemos solo el Año-Mes para agrupar
            cursor.execute("""
                SELECT strftime('%Y-%m', fecha_compra) as mes, COUNT(*) 
                FROM compras_aprobadas 
                GROUP BY mes 
                ORDER BY mes ASC
            """)
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                # Si no hay datos, mostrar un mensaje o un gráfico vacío
                print("Esperando datos de compras para graficar tendencia...")
                return

            meses = [row[0] for row in datos]
            conteos = [row[1] for row in datos]

            # 2. Creación del gráfico de líneas
            fig, ax = plt.subplots(figsize=(5, 4), tight_layout=True)
            fig.patch.set_facecolor('#1e1e2e')
            ax.set_facecolor('#1e1e2e')
            
            # Línea en cian neón con marcadores circulares
            ax.plot(meses, conteos, color='#00ffcc', marker='o', linewidth=2, markersize=8, label='Unidades Compradas')
            ax.fill_between(meses, conteos, color='#00ffcc', alpha=0.1) # Sombreado bajo la línea
            
            # Estética de Dashboard
            ax.set_title("Flujo Mensual de Adquisiciones", color='white', fontweight='bold')
            ax.tick_params(colors='white', labelsize=8)
            ax.set_ylim(0, max(conteos) + 2) # Margen superior
            
            # Limpieza de bordes
            for spine in ax.spines.values():
                spine.set_color('#3c3c4c')
            ax.grid(True, linestyle=':', alpha=0.3, color='gray')

            # 3. Insertar en frame_5
            if self.ui.frame_5.layout() is not None:
                while self.ui.frame_5.layout().count():
                    child = self.ui.frame_5.layout().takeAt(0)
                    if child.widget(): child.widget().deleteLater()
            else:
                layout = QVBoxLayout(self.ui.frame_5)
                self.ui.frame_5.setLayout(layout)

            canvas = FigureCanvas(fig)
            self.ui.frame_5.layout().addWidget(canvas)
            canvas.draw()

        except Exception as e:
            print(f"Error en gráfico frame_5: {e}")


    def actualizar_indicadores_principales(self):
        try:
            conn = sqlite3.connect(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db")
            cursor = conn.cursor()
            
            # 1. Obtener Valor Total del Inventario
            cursor.execute("SELECT SUM(precio * stock_disponible) FROM carros")
            total_dinero = cursor.fetchone()[0] or 0
            
            # 2. Obtener Promedio de Calidad de Compras
            cursor.execute("SELECT AVG(puntaje_inspeccion) FROM compras_aprobadas")
            promedio_calidad = cursor.fetchone()[0] or 0
            
            conn.close()

            # 3. Crear el contenido visual para el frame
            fig, ax = plt.subplots(figsize=(4, 2))
            fig.patch.set_facecolor('#1e1e2e')
            ax.axis('off') # Ocultamos los ejes para que parezca una tarjeta de datos

            # Texto del Valor Total
            ax.text(0.5, 0.7, "VALOR TOTAL INVENTARIO", color='#aaaaaa', 
                    fontsize=10, ha='center', fontweight='bold')
            ax.text(0.5, 0.4, f"${total_dinero:,.0f}", color='#00ffcc', 
                    fontsize=20, ha='center', fontweight='bold')
            
            # Texto de Calidad Promedio
            ax.text(0.5, 0.15, f"⭐ CALIDAD PROMEDIO: {promedio_calidad:.1f} pts", 
                    color='white', fontsize=11, ha='center')

            # 4. Insertar en el widget llamado 'frame'
            if self.ui.frame.layout() is not None:
                while self.ui.frame.layout().count():
                    child = self.ui.frame.layout().takeAt(0)
                    if child.widget(): child.widget().deleteLater()
            else:
                layout = QVBoxLayout(self.ui.frame)
                self.ui.frame.setLayout(layout)

            canvas = FigureCanvas(fig)
            self.ui.frame.layout().addWidget(canvas)
            canvas.draw()

        except Exception as e:
            print(f"Error en indicadores de frame: {e}")


    def graficar_perfil_inventario(self):
        try:
            conn = sqlite3.connect(r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Ingenieria.db")
            cursor = conn.cursor()
            
            # Extraemos promedios de variables clave (Normalizadas para el ejemplo)
            # En un caso real, aquí harías cálculos estadísticos sobre tu DB
            cursor.execute("""
                SELECT AVG(precio), AVG(año), AVG(kilometraje), AVG(stock_disponible) 
                FROM carros
            """)
            res = cursor.fetchone()
            conn.close()

            # Datos de ejemplo normalizados (Escala 0-10) para el Radar
            # Esto representa: [Precio, Reciente, Bajo KM, Disponibilidad, Variedad]
            categorias = ['Precio', 'Novedad', 'Bajo KM', 'Stock', 'Gama']
            valores = [7, 8, 9, 5, 6] # Estos valores vendrían de tu análisis estadístico
            valores += valores[:1] # Cerramos el círculo del radar

            angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
            angulos += angulos[:1]

            # Configuración del gráfico
            fig, ax = plt.subplots(figsize=(5, 4), subplot_kw=dict(polar=True))
            fig.patch.set_facecolor('#1e1e2e')
            ax.set_facecolor('#1e1e2e')

            # Dibujar el área del radar en color neón
            ax.fill(angulos, valores, color='#00ffcc', alpha=0.3)
            ax.plot(angulos, valores, color='#00ffcc', linewidth=2, marker='o')

            # Estética de las etiquetas
            ax.set_xticks(angulos[:-1])
            ax.set_xticklabels(categorias, color='white', size=10)
            ax.set_yticklabels([]) # Ocultar escalas numéricas para limpieza
            ax.spines['polar'].set_color('#3c3c4c')
            ax.grid(color='#3c3c4c', linestyle='--')

            # Insertar en frame_6
            if self.ui.frame_6.layout() is not None:
                while self.ui.frame_6.layout().count():
                    child = self.ui.frame_6.layout().takeAt(0)
                    if child.widget(): child.widget().deleteLater()
            else:
                layout = QVBoxLayout(self.ui.frame_6)
                self.ui.frame_6.setLayout(layout)

            canvas = FigureCanvas(fig)
            self.ui.frame_6.layout().addWidget(canvas)
            canvas.draw()

        except Exception as e:
            print(f"Error en gráfico de radar frame_6: {e}")

    

class MiniJuegoTestDrive(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Estado del jugador
        self.carro_x = 20
        self.carro_y = 100
        self.ancho_carro = 40
        self.alto_carro = 25
        
        # Gestión de Enemigos y Dificultad
        self.enemigos = []
        self.velocidad_base = 5
        self.puntos = 0
        self.nivel = 1
        
        # Timer de actualización
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_logica)
        self.timer.start(20) # 50 FPS aproximadamente

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fondo estilo asfalto
        painter.fillRect(self.rect(), QColor("#1a1a1a"))
        
        # Dibujar líneas de carretera (opcional para estética)
        painter.setPen(QColor("#555555"))
        for i in range(0, self.height(), 40):
            painter.drawLine(0, i, self.width(), i)

        # Dibujar Jugador (Color Cian Neón como tu UI)
        painter.fillRect(self.carro_x, self.carro_y, self.ancho_carro, self.alto_carro, QColor("#00f2ff"))
        
        # Dibujar Enemigos (Cuadros Rojos)
        for enenigo in self.enemigos:
            painter.fillRect(enenigo['rect'], QColor("#ff4b2b"))
        
        # Dibujar UI del juego
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(10, 25, f"Score: {self.puntos}  |  Nivel: {self.nivel}")

    def actualizar_logica(self):
        # 1. Aumentar dificultad según puntos
        self.nivel = (self.puntos // 10) + 1
        velocidad_actual = self.velocidad_base + self.nivel
        
        # 2. Generar enemigos según el nivel
        # Si hay pocos enemigos en pantalla, creamos uno nuevo
        max_enemigos = min(2 + self.nivel, 8) # Máximo 8 enemigos para que no sea imposible
        if len(self.enemigos) < max_enemigos and random.randint(0, 100) < 5:
            ancho_e = random.randint(20, 40)
            alto_e = random.randint(20, 40)
            nuevo_enemigo = {
                'rect': QRect(self.width(), random.randint(0, self.height() - alto_e), ancho_e, alto_e)
            }
            self.enemigos.append(nuevo_enemigo)

        # 3. Mover enemigos y detectar colisiones
        rect_jugador = QRect(self.carro_x, self.carro_y, self.ancho_carro, self.alto_carro)
        
        for enemigo in self.enemigos[:]:
            # Mover hacia la izquierda
            enemigo['rect'].translate(-velocidad_actual, 0)
            
            # Si sale de la pantalla, sumamos puntos
            if enemigo['rect'].right() < 0:
                self.enemigos.remove(enemigo)
                self.puntos += 1
            
            # Detectar colisión
            if rect_jugador.intersects(enemigo['rect']):
                self.reset_juego()

        self.update()

    def reset_juego(self):
        self.puntos = 0
        self.enemigos = []
        self.carro_y = self.height() // 2
        print("Game Over - Reiniciando...")

    def keyPressEvent(self, event):
        paso = 15
        if event.key() == Qt.Key_Up and self.carro_y > 0:
            self.carro_y -= paso
        if event.key() == Qt.Key_Down and self.carro_y < self.height() - self.alto_carro:
            self.carro_y += paso

    def resizeEvent(self, event):
        # Esto asegura que el juego sepa que el QFrame cambió de tamaño
        super().resizeEvent(event)