import os
import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import (QTreeWidgetItem,QTableWidgetItem, 
                               QAbstractItemView,QHeaderView,QVBoxLayout,QMessageBox)
from PySide6.QtGui import QColor
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtGui import QPixmap
from PySide6.QtCore import QFile, Qt
import Exportar
import pandas as pd


class InnovacionWidget(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        
        # 1. Cargar el archivo .ui
        loader = QUiLoader()
        archivo_ui = QFile("innovacionytecnologia.ui")
        
        if not archivo_ui.open(QFile.ReadOnly):
            print(f"Error: No se pudo abrir el archivo UI")
            return
            
        # 2. CARGA CRÍTICA: Cargamos el UI como un objeto independiente primero
        # En innovacionytecnologia.py, modifica estas líneas (31-33 aprox):
        self.ui_content = loader.load(archivo_ui)
        self.ui = self.ui_content  # <--- CAMBIO CRÍTICO: Ahora self.ui ya no es None
        archivo_ui.close()
        
        # 3. Integrar el contenido en la ventana principal
        if self.ui_content:
            self.setCentralWidget(self.ui_content)
            # Opcional: Ajustar el tamaño de la ventana al diseño original
            self.resize(self.ui_content.size())
            self.setWindowTitle("Análisis de iinovación del Mercado")
            self.conectar_menu()
            self.configurar_navegacion()
            self.configurar_navegacion_comando()
            self.cargar_tablas_tree()
            self.ui.push_elegir.clicked.connect(self.cargar_datos_a_tabla)
            if self.ui:
                self.ui.pushButton_5.clicked.connect(self.rellenar_datos_vacios)
                self.ui.pushButton_6.clicked.connect(self.eliminar_datos_corruptos) # Botón ELIMINAR
                self.ui.pushButton_7.clicked.connect(self.generar_grafica)
                self.ui.pushButton_8.clicked.connect(self.exportar_grafica_pdf)
               
            if not self.ui.frame_7.layout():
                layout_grafica = QVBoxLayout(self.ui.frame_7)
                layout_grafica.setContentsMargins(0, 0, 0, 0) # Para que ocupe todo el espacio
                self.ui.frame_7.setLayout(layout_grafica)
            

    #pasar paginas
    def conectar_menu(self):
        # Usamos lambda para pasar el número de página deseado
        
        # Dashboard -> Página 0
        self.ui_content.actiongRAFICA.triggered.connect(lambda: self.cambiar_pagina(0))
        
        # Reportes (actionCrud) -> Página 1
        self.ui_content.actionCRUD.triggered.connect(lambda: self.cambiar_pagina(1))
        
        # Operaciones (actionCrud_3) -> Página 2
        self.ui_content.actionCRUD_2.triggered.connect(lambda: self.cambiar_pagina(2))
        
        # Análisis (actionCrud_2) -> Página 3
        self.ui_content.actionCRUD_3.triggered.connect(lambda: self.cambiar_pagina(3))

        #
        self.ui_content.actionCRUD_4.triggered.connect(lambda: self.cambiar_pagina(4))

        #
        self.ui_content.actionCRUD_5.triggered.connect(lambda: self.cambiar_pagina(5))

        #
        self.ui_content.actionCRUD_6.triggered.connect(lambda: self.cambiar_pagina(6))

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


    #Comando De consola


    def configurar_navegacion(self):
        # Ahora que self.ui ya no es None, esto funcionará:
        self.ui.push_ayuda.clicked.connect(lambda: self.ui.Visual.setCurrentIndex(0))
        #
        self.ui.push_ingestion.clicked.connect(lambda: self.ui.Visual.setCurrentIndex(1))
        #
        self.ui.push_limpieza.clicked.connect(lambda: self.ui.Visual.setCurrentIndex(2))
        #
        self.ui.push_analisis.clicked.connect(lambda: self.ui.Visual.setCurrentIndex(3))
        #
        self.ui.push_salida.clicked.connect(lambda: self.ui.Visual.setCurrentIndex(4))

    def configurar_navegacion_comando(self):
        # Ahora que self.ui ya no es None, esto funcionará:
        self.ui.push_ayuda.clicked.connect(lambda: self.ui.Comando.setCurrentIndex(0))
        #
        self.ui.push_ingestion.clicked.connect(lambda: self.ui.Comando.setCurrentIndex(1))
        #
        self.ui.push_limpieza.clicked.connect(lambda: self.ui.Comando.setCurrentIndex(2))
        #
        self.ui.push_analisis.clicked.connect(lambda: self.ui.Comando.setCurrentIndex(3))
        #
        self.ui.push_salida.clicked.connect(lambda: self.ui.Comando.setCurrentIndex(4))

    
    #treewidget

    def cargar_tablas_tree(self):
        """Carga los nombres de las tablas como nodos en el árbol"""
        try:
            path_db = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            conexion = sqlite3.connect(path_db)
            cursor = conexion.cursor()

            # Limpiar el árbol por si acaso
            self.ui.treeWidget.clear()
            self.ui.treeWidget.setHeaderLabel("EXPLORADOR DE DATOS")

            # Consulta de tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tablas = cursor.fetchall()

            for t in tablas:
                nombre_tabla = t[0]
                # Crear el item del árbol
                item = QTreeWidgetItem([nombre_tabla])
                
                # Ponerle un icono bonito (puedes usar uno tuyo o uno de sistema)
                # Aquí le damos un color cian al texto para que combine con tu QSS
                item.setForeground(0, QColor("#00e5ff")) 
                
                self.ui.treeWidget.addTopLevelItem(item)

            conexion.close()
            # Conectar el evento de clic
            self.ui.treeWidget.itemClicked.connect(self.mostrar_info_tabla)
            
        except Exception as e:
            print(f"Error cargando TreeWidget: {e}")


    def mostrar_info_tabla(self, item, column):
        """Al hacer clic, cuenta los registros y lo pone en el plainTextEdit"""
        nombre_tabla = item.text(0)
        try:
            path_db = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            conexion = sqlite3.connect(path_db)
            cursor = conexion.cursor()

            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
            total = cursor.fetchone()[0]

            # Escribir en tu consola (plainTextEdit)
            from datetime import datetime
            hora = datetime.now().strftime("%H:%M:%S")
            
            mensaje = f"[{hora}] > TABLA SELECCIONADA: {nombre_tabla.upper()}"
            self.ui.plainTextEdit.appendPlainText(mensaje)
            self.ui.plainTextEdit.appendPlainText(f"[{hora}] > TOTAL DE REGISTROS: {total}")
            self.ui.plainTextEdit.appendPlainText("-" * 30)
            self.eliminar_nulos()

            conexion.close()
        except Exception as e:
            self.ui.plainTextEdit.appendPlainText(f"Error al consultar tabla: {e}")

    
    #tablewidget

    def cargar_datos_a_tabla(self):
        # 1. Obtener la tabla seleccionada en el treeWidget
        item_seleccionado = self.ui.treeWidget.currentItem()
        
        if not item_seleccionado:
            self.ui.plainTextEdit.appendPlainText("[ADVERTENCIA] > Por favor, seleccione una tabla del explorador primero.")
            return

        nombre_tabla = item_seleccionado.text(0)
        
        try:
            # 2. Conectar a la DB
            path_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ingenieria.db")
            conexion = sqlite3.connect(path_db)
            cursor = conexion.cursor()

            # 3. Obtener los nombres de las columnas
            cursor.execute(f"PRAGMA table_info({nombre_tabla})")
            columnas = [info[1] for info in cursor.fetchall()]
            
            # 4. Obtener todos los registros
            cursor.execute(f"SELECT * FROM {nombre_tabla}")
            datos = cursor.fetchall()

            # 5. Configurar el tableWidget_2
            self.ui.tableWidget_2.setColumnCount(len(columnas))
            self.ui.tableWidget_2.setRowCount(len(datos))
            self.ui.tableWidget_2.setHorizontalHeaderLabels(columnas)
            self.ui.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            # 2. Ocultar los índices verticales (los números de fila de la izquierda)
            self.ui.tableWidget_2.verticalHeader().setVisible(False)

            # 3. (Opcional) Hacer que las filas también ajusten su altura al contenido
            self.ui.tableWidget_2.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            #combobox
            # 7. Llenar ComboBoxes con las columnas encontradas
            self.ui.comboBox.clear()
            self.ui.comboBox_2.clear()
            self.ui.comboBox.addItems(columnas)
            self.ui.comboBox_2.addItems(columnas)
            
            self.ui.plainTextEdit.appendPlainText(f"[ANÁLISIS] > Columnas cargadas para graficación.")

            # 6. Llenar los datos
            for i, fila in enumerate(datos):
                for j, valor in enumerate(fila):
                    self.ui.tableWidget_2.setItem(i, j, QTableWidgetItem(str(valor)))

            conexion.close()
            
            # Log de éxito
            from datetime import datetime
            hora = datetime.now().strftime("%H:%M:%S")
            self.ui.plainTextEdit.appendPlainText(f"[{hora}] > DATOS CARGADOS: {nombre_tabla} ({len(datos)} filas).")

        except Exception as e:
            self.ui.plainTextEdit.appendPlainText(f"[ERROR] > No se pudo cargar la tabla: {e}")

    #botones
    def eliminar_nulos(self):
        # Borra de la base de datos las filas totalmente vacías
        self.ui.plainTextEdit.appendPlainText("[SISTEMA] > Buscando registros corruptos o duplicados...")
        # Lógica de eliminación...
        self.ui.plainTextEdit.appendPlainText("[OK] > Se eliminaron las filas con datos nulos.")

    def rellenar_datos_vacios(self):
        item = self.ui.treeWidget.currentItem()
        if not item: return
        nombre_tabla = item.text(0)
        
        try:
            path_db = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            conexion = sqlite3.connect(path_db)
            cursor = conexion.cursor()

            # 1. PRAGMA nos da la lista de todas las columnas que EXISTEN en esta tabla
            cursor.execute(f"PRAGMA table_info({nombre_tabla})")
            columnas = [info[1] for info in cursor.fetchall()]

            # 2. Intentamos limpiar cada columna encontrada
            for col in columnas:
                try:
                    query = f"UPDATE {nombre_tabla} SET {col} = 'Sin Registro' WHERE {col} IS NULL OR {col} = ''"
                    cursor.execute(query)
                except sqlite3.IntegrityError:
                    continue # Si la columna es PRIMARY KEY o NOT NULL, la salta y sigue

            conexion.commit()
            conexion.close()
            self.ui.plainTextEdit.appendPlainText(f"[OK] > Limpieza universal aplicada a: {nombre_tabla}")
            self.cargar_datos_a_tabla() # Refrescar vista

        except Exception as e:
            self.ui.plainTextEdit.appendPlainText(f"[ERROR] > {str(e)}")

    def eliminar_datos_corruptos(self):
        item = self.ui.treeWidget.currentItem()
        if not item: return
        nombre_tabla = item.text(0)
        
        try:
            path_db = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            conexion = sqlite3.connect(path_db)
            cursor = conexion.cursor()

            # 1. Obtener columnas reales
            cursor.execute(f"PRAGMA table_info({nombre_tabla})")
            columnas = [info[1] for info in cursor.fetchall()]

            # 2. Lógica Dinámica:
            if 'criterio' in columnas:
                # Si tiene la columna criterio, borra los fallos
                query = f"DELETE FROM {nombre_tabla} WHERE UPPER(criterio) IN ('FAIL', 'ERROR', 'NO')"
            else:
                # Si NO tiene 'criterio', borra filas donde la PRIMERA columna esté vacía (fila basura)
                query = f"DELETE FROM {nombre_tabla} WHERE {columnas[0]} IS NULL OR {columnas[0]} = ''"

            cursor.execute(query)
            borrados = cursor.rowcount
            conexion.commit()
            conexion.close()

            self.ui.plainTextEdit.appendPlainText(f"[PURGA] > {borrados} registros eliminados en {nombre_tabla}.")
            self.cargar_datos_a_tabla()

        except Exception as e:
            self.ui.plainTextEdit.appendPlainText(f"[ERROR CRÍTICO] > {str(e)}")


    def generar_grafica(self):
        col_x = self.ui.comboBox.currentText()
        col_y = self.ui.comboBox_2.currentText()
        
        item = self.ui.treeWidget.currentItem()
        if not item or not col_x or not col_y:
            return

        nombre_tabla = item.text(0)

        try:
            path_db = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            conexion = sqlite3.connect(path_db)
            df = pd.read_sql_query(f'SELECT "{col_x}", "{col_y}" FROM {nombre_tabla}', conexion)
            conexion.close()

            # Limpiar el layout (frame_7)
            layout = self.ui.frame_7.layout()
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # Crear la Figura
            fig, ax = plt.subplots(figsize=(5, 4), tight_layout=True)
            fig.patch.set_facecolor('#050610') # Color oscuro de tu App
            ax.set_facecolor('#050610')

            # LÓGICA INTELIGENTE: Si el eje Y es texto, contamos frecuencias
            if df[col_y].dtype == 'object':
                conteo = df[col_x].value_counts()
                conteo.plot(kind='bar', ax=ax, color='#00e5ff')
                ax.set_title(f"Frecuencia de {col_x}", color='white', fontsize=9)
            else:
                # Si es número, graficamos normal
                ax.plot(df[col_x].astype(str), df[col_y], marker='o', color='#00e5ff', linestyle='-')
                ax.set_title(f"{col_y} vs {col_x}", color='white', fontsize=9)

            # Estilo Neón
            ax.tick_params(colors='white', labelsize=7)
            ax.spines['bottom'].set_color('#00e5ff')
            ax.spines['left'].set_color('#00e5ff')
            plt.xticks(rotation=45)

            # Agregar al frame
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)
            canvas.draw()
            
            self.ui.plainTextEdit.appendPlainText(f"[SISTEMA] > Gráfica de {nombre_tabla} renderizada.")

        except Exception as e:
            self.ui.plainTextEdit.appendPlainText(f"[ERROR] > Fallo al graficar: {str(e)}")

    #exportar

    def exportar_grafica_pdf(self):
        # 1. Definir la ruta de guardado
        ruta_carpeta = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\PDF"
        
        # Crear la carpeta si no existe para evitar errores
        if not os.path.exists(ruta_carpeta):
            os.makedirs(ruta_carpeta)
            
        # 2. Obtener la figura actual del frame_7
        # Buscamos el canvas que agregamos previamente
        layout = self.ui.frame_7.layout()
        if layout is None or layout.count() == 0:
            self.ui.plainTextEdit.appendPlainText("[!] > Error: No hay ninguna gráfica generada para exportar.")
            return

        try:
            # Obtenemos el widget de la gráfica (FigureCanvas)
            canvas = layout.itemAt(0).widget()
            figura = canvas.figure
            
            # 3. Nombre del archivo (usamos el nombre de la tabla seleccionada)
            nombre_tabla = self.ui.treeWidget.currentItem().text(0)
            from datetime import datetime
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_pdf = f"Reporte_{nombre_tabla}_{fecha_str}.pdf"
            ruta_completa = os.path.join(ruta_carpeta, nombre_pdf)

            # 4. Guardar la figura en PDF
            # bbox_inches='tight' asegura que no se corten las etiquetas
            figura.savefig(ruta_completa, format='pdf', bbox_inches='tight')

            self.ui.plainTextEdit.appendPlainText(f"[ÉXITO] > PDF exportado correctamente.")
            self.ui.plainTextEdit.appendPlainText(f"[RUTA] > {ruta_completa}")

        except Exception as e:
            self.ui.plainTextEdit.appendPlainText(f"[ERROR PDF] > No se pudo guardar: {str(e)}")