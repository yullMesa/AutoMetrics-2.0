import os
import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import (QTreeWidgetItem,QTableWidgetItem, 
                               QAbstractItemView,QHeaderView,QVBoxLayout,QMessageBox,QFileDialog)
from PySide6.QtGui import QColor,QFont
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtGui import QPixmap
from PySide6.QtCore import QFile, Qt
import Exportar
import pandas as pd
from datetime import datetime



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

            #Datos De Reporte De Errores Criticos
            self.mostrar_inventario_tablas()
            # Conecta el doble clic de la tabla con la función de resumen
            self.ui.tabla_tablas.cellDoubleClicked.connect(self.generar_resumen_criticos)  
            self.ui.tabla_tablas.cellDoubleClicked.connect(self.generar_resumen_critico)
            # Dentro de generar_resumen_critico, al final:
            self.calcular_tabla_mas_inestable() 
            self.ui.push_actualizar.clicked.connect(self.ejecutar_actualizacion_maestra)

            #Datos De Historial De Versiones
            # Configurar columnas del TreeWidget
            self.ui.treeWidget_2.setColumnCount(2)
            self.ui.treeWidget_2.setHeaderLabels(["Componente / Versión", "Estado / Registro"])
            self.ui.treeWidget_2.setColumnWidth(0, 300)

            # Cargar los datos
            self.cargar_control_versiones()
            # Dentro de tu __init__
            self.ui.treeWidget_2.itemClicked.connect(self.visualizar_datos_seleccionados)
            self.ui.push_Exportar.clicked.connect(self.exportar_a_excel)
            
            
            

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

    
    #Reporte De Erorres

    def mostrar_inventario_tablas(self):
        try:
            path_db = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            conexion = sqlite3.connect(path_db)
            cursor = conexion.cursor()

            # Consultar nombres de tablas creadas por el usuario
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tablas = cursor.fetchall()

            # Configurar el QTableWidget (tabla_tablas)
            self.ui.tabla_tablas.setColumnCount(2)
            self.ui.tabla_tablas.setHorizontalHeaderLabels(["NOMBRE DE TABLA", "TOTAL REGISTROS"])
            self.ui.tabla_tablas.setRowCount(len(tablas))

            for fila, (nombre,) in enumerate(tablas):
                # Obtener conteo de registros por tabla para darle más utilidad
                cursor.execute(f"SELECT COUNT(*) FROM {nombre}")
                total_filas = cursor.fetchone()[0]

                # Insertar en la tabla neón
                self.ui.tabla_tablas.setItem(fila, 0, QTableWidgetItem(nombre))
                self.ui.tabla_tablas.setItem(fila, 1, QTableWidgetItem(str(total_filas)))

            conexion.close()
            
            # Ajuste visual: que las columnas ocupen todo el ancho
            self.ui.tabla_tablas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            self.registrar_log(f"Inventario cargado: {len(tablas)} tablas detectadas.", "SUCCESS")

        except Exception as e:
            self.registrar_log(f"Error al listar tablas: {e}", "ERROR")
    
    
    def registrar_log(self, mensaje, tipo="INFO"):
        from datetime import datetime
        hora = datetime.now().strftime("%H:%M:%S")
        
        # Formatear el mensaje según el tipo
        if tipo == "SUCCESS":
            formato = f"[{hora}] [OK] > {mensaje}"
        elif tipo == "ERROR":
            formato = f"[{hora}] [ERROR] > {mensaje}"
        else:
            formato = f"[{hora}] [SISTEMA] > {mensaje}"
            
        # Suponiendo que tu consola se llama plainTextEdit (ajusta si es necesario)
        self.ui.plainTextEdit.appendPlainText(formato)

    #resumen
    def generar_resumen_critico(self, fila, columna):
        nombre_tabla = self.ui.tabla_tablas.item(fila, 0).text()
        self.ui.plainTextEdit_2.clear()
        
        try:
            path_db = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            conexion = sqlite3.connect(path_db)
            cursor = conexion.cursor()

            # 1. Obtener información de las columnas (Define total_columnas)
            cursor.execute(f"PRAGMA table_info({nombre_tabla})")
            columnas_info = cursor.fetchall()
            total_columnas = len(columnas_info) # <--- AQUÍ SE DEFINE

            # 2. Obtener conteo de filas (Define total_filas)
            cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
            total_filas = cursor.fetchone()[0] # <--- AQUÍ SE DEFINE

            # 3. Auditoría de Nulos (Define errores_totales)
            errores_totales = 0
            lista_errores = []
            
            for col in columnas_info:
                nombre_col = col[1]
                cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla} WHERE {nombre_col} IS NULL OR {nombre_col} = ''")
                n = cursor.fetchone()[0]
                if n > 0:
                    errores_totales += n
                    lista_errores.append(f"[{nombre_col.upper()}: {n}]")

            conexion.close()

            # 4. Construcción del Reporte Centrado (Panorámico)
            ancho_total = 110 
            separador = "═" * (ancho_total - 2)
            relleno_vertical = "\n" * 2
            
            reporte = [
                f"╔{separador}╗".center(ancho_total),
                f"║ AUDITORÍA DE INTEGRIDAD DE DATOS - AUTOMETRICS 2.0 ║".center(ancho_total),
                f"╠{separador}╣".center(ancho_total),
                f"║ TABLA ANALIZADA: {nombre_tabla.upper().center(30)} ║".center(ancho_total),
                f"║ FILAS: {str(total_filas).ljust(8)} | COLUMNAS: {str(total_columnas).ljust(8)} | FALLOS: {str(errores_totales).ljust(8)} ║".center(ancho_total),
                f"╠{separador}╣".center(ancho_total),
                f"║ {('  •  '.join(lista_errores) if lista_errores else 'SISTEMA LIMPIO').center(ancho_total-4)} ║".center(ancho_total),
                f"╚{separador}╝".center(ancho_total)
            ]

            self.ui.plainTextEdit_2.setPlainText(relleno_vertical + "\n".join(reporte))
            self.generar_grafica_estadistica(nombre_tabla, errores_totales, total_filas, total_columnas)
            
            # 5. ACTUALIZAR LCD (Rojo)
            if hasattr(self.ui, 'lcd_total'):
                self.ui.lcd_total.display(errores_totales)

            # 6. LLAMAR A LA GRÁFICA (Ahora las variables sí existen)
            self.graficar_calidad_tabla(nombre_tabla, errores_totales, total_filas, total_columnas)

        except Exception as e:
            self.ui.plainTextEdit_2.setPlainText(f"\n\n ERROR: {str(e)}".center(100))
    

    #grafica

    def graficar_calidad_tabla(self, nombre_tabla, errores_totales, total_filas, total_columnas):
        # 1. Limpiar el frame_8 antes de dibujar
        layout = self.ui.frame_8.layout()
        if layout is None:
            from PySide6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(self.ui.frame_8)
            self.ui.frame_8.setLayout(layout)
        
        # Eliminar gráficos anteriores
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # 2. Calcular datos para la gráfica
        # Total de celdas = filas * columnas
        celdas_totales = total_filas * total_columnas
        datos_buenos = celdas_totales - errores_totales

        # 3. Crear la figura de Matplotlib con estilo oscuro
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#050610') # Fondo igual a tu UI
        ax.set_facecolor('#050610')

        etiquetas = ['CORRECTOS', 'NULOS']
        valores = [datos_buenos, errores_totales]
        colores = ['#00e5ff', '#ff0055'] # Cian y Rojo Neón
        
        # Gráfica de Pastel (Pie Chart)
        wedges, texts, autotexts = ax.pie(
            valores, 
            labels=etiquetas, 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=colores,
            explode=(0.1, 0) if errores_totales > 0 else (0, 0), # Resaltar errores
            textprops={'color':"w", 'weight':'bold'}
        )

        ax.set_title(f"INTEGRIDAD: {nombre_tabla.upper()}", color='#00e5ff', fontsize=12, pad=20)

        # 4. Integrar en PySide6
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        canvas.draw()

    
    #LCD

    def generar_resumen_criticos(self, fila, columna):
        nombre_tabla = self.ui.tabla_tablas.item(fila, 0).text()
        self.ui.plainTextEdit_2.clear()
        
        try:
            path_db = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            conexion = sqlite3.connect(path_db)
            cursor = conexion.cursor()

            # 1. Obtener info de columnas y filas
            cursor.execute(f"PRAGMA table_info({nombre_tabla})")
            columnas_info = cursor.fetchall()
            total_columnas = len(columnas_info)

            cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
            total_filas = cursor.fetchone()[0]

            # 2. Conteo de errores
            errores_totales = 0
            for col in columnas_info:
                nombre_col = col[1]
                cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla} WHERE {nombre_col} IS NULL OR {nombre_col} = ''")
                errores_totales += cursor.fetchone()[0]

            conexion.close()

            # --- LÓGICA DE RIESGO PARA lcdNumber ---
            # El riesgo es: (Errores / Celdas Totales) * 100
            celdas_totales = total_filas * total_columnas
            
            if celdas_totales > 0:
                porcentaje_riesgo = (errores_totales / celdas_totales) * 100
            else:
                porcentaje_riesgo = 0

            # Mostrar en el LCD llamado 'lcdNumber'
            # round(porcentaje_riesgo, 1) para tener un decimal (ej: 15.5)
            self.ui.lcdNumber.display(round(porcentaje_riesgo, 1))
            
            # Opcional: Cambiar color del LCD según el riesgo
            if porcentaje_riesgo > 15:
                # Rojo si es muy alto
                self.ui.lcdNumber.setStyleSheet("color: #ff0055; border: 2px solid #ff0055; background: rgba(20,0,0,0.5);")
            else:
                # Violeta original si es aceptable
                self.ui.lcdNumber.setStyleSheet("color: #bc13fe; border: 2px solid #bc13fe; background: rgba(15,0,20,0.5);")
            # ---------------------------------------

            # (Aquí sigue tu código del reporte centrado y la gráfica...)
            self.ui.lcdNumber.display(errores_totales)
            self.graficar_calidad_tabla(nombre_tabla, errores_totales, total_filas, total_columnas)
            

        except Exception as e:
            print(f"Error: {e}")

    def calcular_tabla_mas_inestable(self):
        try:
            path_db = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            conexion = sqlite3.connect(path_db)
            cursor = conexion.cursor()

            # 1. Obtener lista de todas las tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas = cursor.fetchall()

            max_errores_encontrados = 0
            tabla_critica = ""

            # 2. Escaneo rápido de cada tabla
            for (nombre_tabla,) in tablas:
                # Obtener columnas
                cursor.execute(f"PRAGMA table_info({nombre_tabla})")
                columnas = [col[1] for col in cursor.fetchall()]
                
                # Contar errores totales en esta tabla
                errores_tabla = 0
                for col in columnas:
                    cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla} WHERE {col} IS NULL OR {col} = ''")
                    errores_tabla += cursor.fetchone()[0]
                
                # Comparar para encontrar el máximo
                if errores_tabla > max_errores_encontrados:
                    max_errores_encontrados = errores_tabla
                    tabla_critica = nombre_tabla

            conexion.close()

            # 3. Mostrar el número máximo de errores en el LCD Naranja (lcdNumber_2)
            self.ui.lcdNumber_2.display(max_errores_encontrados)
            
            # Opcional: Registrar en el log quién es la culpable
            if tabla_critica:
                self.registrar_log(f"Alerta: Tabla '{tabla_critica}' detectada como la más inestable.", "ERROR")

        except Exception as e:
            print(f"Error al calcular inestabilidad: {e}")


    def actualizar_indicadores_panel(self, errores_totales, total_filas, total_columnas):
        """
        Actualiza los 3 LCDs del panel superior usando los datos recibidos.
        """
        try:
            # --- 1. LCD PÚRPURA (lcdNumber): Nivel de Riesgo % ---
            celdas_totales = total_filas * total_columnas
            porcentaje_riesgo = (errores_totales / celdas_totales * 100) if celdas_totales > 0 else 0
            self.ui.lcdNumber.display(round(porcentaje_riesgo, 1))
            
            # --- 2. LCD CIAN (lcdNumber_3): Total de Errores de la Tabla ---
            # Efectivamente, aquí usamos el _3 para el conteo cian
            self.ui.lcdNumber_3.display(errores_totales)

            # --- 3. LCD NARANJA (lcdNumber_2): Tabla más inestable de la DB ---
            self.calcular_tabla_mas_inestable()

        except Exception as e:
            self.registrar_log(f"Error actualizando LCDs: {str(e)}", "ERROR")


    def ejecutar_actualizacion_maestra(self):
        """
        Refresca todos los indicadores globales y limpia el área de trabajo.
        """
        try:
            # 1. Volver a escanear toda la DB para el LCD Naranja (Inestabilidad)
            self.calcular_tabla_mas_inestable()
            
            # 2. Resetear los LCDs de la tabla seleccionada a cero 
            # (Hasta que el usuario vuelva a elegir una)
            self.ui.lcdNumber.display(0)    # Riesgo %
            self.ui.lcdNumber_3.display(0)  # Total Errores
            
            # 3. Limpiar el área de reporte y gráficos
            self.ui.plainTextEdit_2.clear()
            self.ui.plainTextEdit_2.setPlainText("SISTEMA SINCRONIZADO. SELECCIONE UNA TABLA PARA ANALIZAR.")
            
            # Opcional: Si tienes un método para cargar la tabla de inventario, llámalo aquí
            # self.cargar_inventario_tablas()

            print("Actualización maestra completada con éxito.")

        except Exception as e:
            self.registrar_log(f"Error en actualización manual: {e}", "ERROR")


    def generar_grafica_estadistica(self, nombre_tabla, errores_totales, total_filas, total_columnas):
        """
        Crea una gráfica de pastel en el frame_8 comparando datos limpios vs nulos.
        """
        try:
            # 1. Liberar memoria de gráficas anteriores
            plt.close('all') 

            # 2. Configurar el layout del frame_8 si no existe
            layout = self.ui.frame_8.layout()
            if layout is None:
                from PySide6.QtWidgets import QVBoxLayout
                layout = QVBoxLayout(self.ui.frame_8)
                self.ui.frame_8.setLayout(layout)

            # 3. Limpiar widgets anteriores del frame (gráficas viejas)
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # 4. Preparar datos
            celdas_totales = total_filas * total_columnas
            datos_correctos = celdas_totales - errores_totales
            
            # Evitar gráfica vacía si no hay datos
            if celdas_totales == 0: return

            # 5. Crear la figura estilo Neón/Dark
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
            fig.patch.set_facecolor('#050610') # Color de fondo de tu UI
            ax.set_facecolor('#050610')

            labels = ['VÁLIDOS', 'NULOS']
            sizes = [datos_correctos, errores_totales]
            colors = ['#00e5ff', '#ff0055'] # Cian y Rojo Neón
            explode = (0, 0.1) if errores_totales > 0 else (0, 0)

            ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                shadow=False, startangle=140, colors=colors,
                textprops={'color':"w", 'weight':'bold', 'fontsize':8})

            ax.set_title(f"ESTADO: {nombre_tabla.upper()}", color='#bc13fe', fontsize=10)

            # 6. Integrar en PySide6
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)
            canvas.draw()

        except Exception as e:
            print(f"Error al generar gráfico: {e}")


    #Control De Versiones
    def cargar_control_versiones(self):
        """
        Puebla el treeWidget_2 comparando la versión actual vs el historial.
        """
        try:
            self.ui.treeWidget_2.clear()
            
            path_actual = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            path_historial = os.path.join(os.path.dirname(__file__), "historial_versiones.db")

            # 1. Obtener tablas de la base ACTUAL
            conn_act = sqlite3.connect(path_actual)
            cursor_act = conn_act.cursor()
            cursor_act.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas_actuales = [t[0] for t in cursor_act.fetchall() if t[0] != 'sqlite_sequence']
            conn_act.close()

            # 2. Obtener registro de commits del HISTORIAL
            conn_hist = sqlite3.connect(path_historial)
            cursor_hist = conn_hist.cursor()
            
            # Asegurarnos de que existe la tabla de registro
            cursor_hist.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='registro_commits'")
            if not cursor_hist.fetchone():
                conn_hist.close()
                return

            for tabla in tablas_actuales:
                # Crear el Nodo Padre (Nombre de la Tabla)
                item_tabla = QTreeWidgetItem(self.ui.treeWidget_2)
                item_tabla.setText(0, f"📁 {tabla.upper()}")
                item_tabla.setForeground(0, QColor("#bc13fe")) # Morado Neón
                
                # Sub-nodo: Versión Más Reciente (La que está en ingenieria.db)
                item_actual = QTreeWidgetItem(item_tabla)
                item_actual.setText(0, "● Versión Actual (Productiva)")
                item_actual.setText(1, "En Tiempo Real")
                item_actual.setForeground(0, QColor("#00e5ff")) # Cian Neón
                
                # Sub-nodos: Versiones Anteriores (Desde historial_versiones.db)
                cursor_hist.execute("""
                    SELECT nombre_version_db, fecha, comentario 
                    FROM registro_commits 
                    WHERE tabla_original = ? 
                    ORDER BY id DESC
                """, (tabla,))
                
                versiones_pasadas = cursor_hist.fetchall()
                for v_db, fecha, nota in versiones_pasadas:
                    item_v = QTreeWidgetItem(item_tabla)
                    # Formateamos el nombre para que no parezca un nombre de tabla SQL
                    fecha_limpia = fecha.replace("_", " ")
                    item_v.setText(0, f"○ Versión Anterior ({fecha_limpia})")
                    item_v.setText(1, nota if nota else "Respaldo del Sistema")
                    item_v.setData(0, Qt.UserRole, v_db) # Guardamos el nombre real oculto para usarlo luego

            conn_hist.close()
            self.ui.treeWidget_2.expandAll()

        except Exception as e:
            print(f"Error al cargar el árbol de versiones: {e}")

    def visualizar_datos_seleccionados(self, item, columna):
        # 1. Verificar que no sea el nodo padre (el que tiene el icono de carpeta)
        if not item.parent():
            return 
            
        try:
            # 2. Identificar la tabla original (Nombre del padre)
            nombre_tabla_original = item.parent().text(0).replace("📁 ", "").lower()
            
            # 3. Determinar qué base de datos y qué tabla leer
            texto_seleccionado = item.text(0)
            
            if "Actual" in texto_seleccionado:
                # LEER DE INGENIERIA.DB
                db_path = os.path.join(os.path.dirname(__file__), "ingenieria.db")
                tabla_a_consultar = nombre_tabla_original
                color_resalte = "#00e5ff" # Cian para lo nuevo
            else:
                # LEER DE HISTORIAL_VERSIONES.DB
                db_path = os.path.join(os.path.dirname(__file__), "historial_versiones.db")
                # Recuperamos el nombre real (ej: transporte_v_2026...) que guardamos en setData
                tabla_a_consultar = item.data(0, Qt.UserRole)
                color_resalte = "#bc13fe" # Morado para lo viejo

            # 4. Consulta SQL y Carga de Datos
            conexion = sqlite3.connect(db_path)
            query = f"SELECT * FROM {tabla_a_consultar}"
            df = pd.read_sql_query(query, conexion)
            conexion.close()

            # 5. Llenar el tableWidget_Versiones
            self.mostrar_en_tabla_versiones(df, color_resalte)

        except Exception as e:
            print(f"Error al visualizar versión: {e}")
            

    def mostrar_en_tabla_versiones(self, df, color_borde):
        """
        Renderiza el DataFrame con estilo avanzado y colores condicionales.
        """
        tabla = self.ui.tableWidget_Versiones
        tabla.setRowCount(df.shape[0])
        tabla.setColumnCount(df.shape[1])
        tabla.setHorizontalHeaderLabels([col.upper() for col in df.columns])

        # 1. Hacer que la tabla ocupe todo el ancho disponible
        header = tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch) # Estira todas las columnas por igual
        
        # 2. Aplicar el estilo dinámico al borde según la versión seleccionada
        tabla.setStyleSheet(f"""
            QTableWidget {{ 
                border: 2px solid {color_borde}; 
                background-color: #050610; 
                gridline-color: #1c1e33;
                color: #e0e0e0;
            }}
        """)

        # 3. Llenado de datos con lógica de colores
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                raw_value = df.iat[i, j]
                # Detectar si es nulo, vacío o "ERROR"
                es_nulo = pd.isna(raw_value) or str(raw_value).strip() == "" or "ERROR" in str(raw_value).upper()
                
                valor_texto = str(raw_value) if not es_nulo else "⚠️ VACÍO"
                item = QTableWidgetItem(valor_texto)
                item.setTextAlignment(Qt.AlignCenter)

                # --- LÓGICA DE COLORES POR CONTENIDO ---
                if j == 0: # Primera columna (usualmente IDs)
                    item.setForeground(QColor("#00e5ff")) # Cian Neón
                    item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                elif es_nulo:
                    item.setForeground(QColor("#ff0055")) # Rojo Neón para errores
                    item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                else:
                    item.setForeground(QColor("#ffffff")) # Blanco para datos normales

                tabla.setItem(i, j, item)


    def exportar_a_excel(self):
        """Exporta la versión seleccionada a XLSX de forma silenciosa."""
        try:
            # 1. Obtener la selección actual del árbol
            item = self.ui.treeWidget_2.currentItem()
            if not item:
                self.ui.plainTextEdit_2.appendPlainText("⚠️ SISTEMA: Selecciona una versión en el árbol.")
                return

            # Construir nombres basados en la jerarquía del árbol
            nombre_nodo = item.text(0).replace(" ", "_").replace("(", "").replace(")", "")
            nombre_tabla = item.parent().text(0) if item.parent() else "General"
            
            # 2. Extraer datos del tableWidget_Versiones
            tabla_ui = self.ui.tableWidget_Versiones
            filas = tabla_ui.rowCount()
            columnas = tabla_ui.columnCount()

            if filas == 0:
                self.ui.plainTextEdit_2.appendPlainText("⚠️ SISTEMA: La tabla no contiene datos para exportar.")
                return

            # 3. Preparar DataFrame
            headers = [tabla_ui.horizontalHeaderItem(c).text() for c in range(columnas)]
            datos_lista = []
            for f in range(filas):
                fila = [tabla_ui.item(f, c).text() if tabla_ui.item(f, c) else "" for c in range(columnas)]
                datos_lista.append(fila)

            df_export = pd.DataFrame(datos_lista, columns=headers)
            
            # 4. Ruta y Guardado
            ruta_base = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\AutoMetricsCSV"
            if not os.path.exists(ruta_base): os.makedirs(ruta_base)

            timestamp = datetime.now().strftime("%H%M%S")
            nombre_final = f"REP_{nombre_tabla}_{timestamp}.xlsx"
            ruta_final = os.path.join(ruta_base, nombre_final)

            df_export.to_excel(ruta_final, index=False)

            # 5. Notificación solo por Terminal (Sin abrir carpetas)
            self.ui.plainTextEdit_2.appendPlainText("-----------------------------------------")
            self.ui.plainTextEdit_2.appendPlainText(f"🚀 EXPORTACIÓN COMPLETADA")
            self.ui.plainTextEdit_2.appendPlainText(f"📦 TABLA: {nombre_tabla}")
            self.ui.plainTextEdit_2.appendPlainText(f"📄 ARCHIVO: {nombre_final}")
            self.ui.plainTextEdit_2.appendPlainText(f"📊 REGISTROS: {len(datos_lista)}")
            self.ui.plainTextEdit_2.appendPlainText("-----------------------------------------")

        except Exception as e:
            self.ui.plainTextEdit_2.appendPlainText(f"❌ ERROR CRÍTICO: {str(e)}")

      