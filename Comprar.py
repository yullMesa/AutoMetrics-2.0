import os
import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile,Qt, QSize
from PySide6.QtWidgets import (QTreeWidgetItem,QTableWidgetItem, 
                               QAbstractItemView,QHeaderView,QVBoxLayout,QMessageBox,QToolButton,
                               QSizePolicy,QDialog,QLabel,QHBoxLayout,QPushButton,QMessageBox)
from PySide6.QtGui import QColor,QIcon, QPixmap
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtGui import QPixmap
from PySide6.QtCore import QFile, Qt , QSize
import Exportar

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