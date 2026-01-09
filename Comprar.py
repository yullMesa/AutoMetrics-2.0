import os
import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile,Qt, QSize
from PySide6.QtWidgets import (QTreeWidgetItem,QTableWidgetItem, 
                               QAbstractItemView,QHeaderView,QVBoxLayout,QMessageBox,QToolButton,
                               QSizePolicy,QDialog,QLabel,QHBoxLayout,QPushButton)
from PySide6.QtGui import QColor,QIcon, QPixmap
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtGui import QPixmap
from PySide6.QtCore import QFile, Qt
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
        self.cargar_combos_financiamiento
            

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
        try:
            # 1. Obtener Marcas Únicas
            # Usamos DISTINCT para no repetir marcas en el combo
            query_marcas = "SELECT DISTINCT marca FROM carros ORDER BY marca ASC"
            marcas = self.ejecutar_consulta(query_marcas) 
            
            if marcas:
                self.ui.combo_Marca.clear()
                # Extraemos el primer elemento de cada tupla: (Marca,) -> Marca
                lista_marcas = [str(m[0]) for m in marcas]
                self.ui.combo_Marca.addItems(lista_marcas)
                print(f"DEBUG: Marcas cargadas: {len(lista_marcas)}")
            
            # 2. Conectar el evento para que al cambiar Marca se actualice el Modelo
            # Importante: Desconectar antes si ya existe para no duplicar llamadas
            try: self.ui.combo_Marca.currentIndexChanged.disconnect()
            except: pass
            
            self.ui.combo_Marca.currentIndexChanged.connect(self.actualizar_modelos_financiamiento)
            
            # Cargar modelos de la primera marca por defecto
            self.actualizar_modelos_financiamiento()

        except Exception as e:
            print(f"ERROR al cargar combos: {e}")

    def actualizar_modelos_financiamiento(self):
        marca_seleccionada = self.ui.combo_Marca.currentText()
        if not marca_seleccionada:
            return

        query_modelos = f"SELECT modelo FROM carros WHERE marca = '{marca_seleccionada}' ORDER BY modelo ASC"
        modelos = self.ejecutar_consulta(query_modelos)
        
        self.ui.combo_Modelo.clear()
        if modelos:
            lista_modelos = [str(mo[0]) for mo in modelos]
            self.ui.combo_Modelo.addItems(lista_modelos)
            print(f"DEBUG: Modelos cargados para {marca_seleccionada}: {len(lista_modelos)}")

    #imagen 
    def actualizar_foto_financiamiento(self):
        modelo = self.ui.combo_Modelo.currentText()
        if not modelo:
            return

        ruta_base = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Carros"
        nombre_archivo = modelo.lower().strip()
        archivo_encontrado = None

        # Buscamos el archivo (igual que en el catálogo)
        for ext in [".png", ".jpg", ".jpeg"]:
            ruta_posible = os.path.join(ruta_base, f"{nombre_archivo}{ext}")
            if os.path.exists(ruta_posible):
                archivo_encontrado = ruta_posible
                break

        if archivo_encontrado:
            pixmap = QPixmap(archivo_encontrado)
            # Ajustamos el icono al tamaño del QToolButton (aprox 300x200)
            self.ui.toolButton_foto_carro.setIcon(QIcon(pixmap))
            self.ui.toolButton_foto_carro.setIconSize(QSize(300, 200))
        else:
            self.ui.toolButton_foto_carro.setIcon(QIcon("assets/no_image.png"))