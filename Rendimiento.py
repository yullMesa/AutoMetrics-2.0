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


class RendimientoMercado(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        
        # 1. Cargar el archivo .ui
        loader = QUiLoader()
        archivo_ui = QFile("RendiminetoDelMercado.ui")
        
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

            #Datos-Archivo
            self.configurar_tabla_mercado()
            self.cargar_datos_tableWidget()
            self.ui_content.tableWidget.itemSelectionChanged.connect(self.obtener_datos_seleccionados)
            self.actualizar_treeWidget()
            self.graficar_estados_servidores()
            self.ui_content.tableWidget.itemSelectionChanged.connect(self.actualizar_monitor_con_imagen)
            self.ui_content.pushButton_4.clicked.connect(self.agregar_nuevo_servidor)
            self.ui_content.pushButton_3.clicked.connect(self.eliminar_servidor)
            self.ui_content.pushButton_2.clicked.connect(self.actualizar_servidor_db)
            self.ui_content.pushButton.clicked.connect(self.importa)

            #Datos operaciones  
            self.cargar_datos_operaciones()
            self.graficar_operaciones()
            self.cargar_tree_operaciones_detallado()
            self.ui_content.tableWidget_2.itemClicked.connect(self.obtener_datos_de_tabla)
            self.ui_content.tableWidget_2.itemSelectionChanged.connect(self.obtener_imagen_de_tabla)
            self.ui_content.pushButton_5.clicked.connect(self.registrar_operacion)
            self.ui_content.pushButton_6.clicked.connect(self.eliminar_operacion)
            self.ui_content.pushButton_7.clicked.connect(self.actualizar_operacion)
            self.ui_content.pushButton_8.clicked.connect(self.importa)

            #Datos Analisis
            self.cargar_datos_analisis()
            self.graficar_analisis_mercado()
            # 1. Configuramos primero el esqueleto (columnas y espacio)
            self.configurar_tree_analisis()

            # 2. Luego llenamos el árbol con los datos de SQL
            self.cargar_tree_analisis_jerarquico()
            self.ui_content.tableWidget_3.itemClicked.connect(self.al_hacer_click_en_tabla)
            # Conectar el evento de clic de la tabla
            self.ui_content.tableWidget_3.cellClicked.connect(self.seleccionar_datos_analisis)
            # Conectar el botón de Añadir (pushButton_9)
            self.ui_content.pushButton_9.clicked.connect(self.agregar_datos_analisis)
            # Al final de tu def __init__(self):
            self.refrescar_todo_analisis()
            # Conectar el botón de Eliminar (pushButton_10)
            self.ui_content.pushButton_10.clicked.connect(self.eliminar_datos_analisis)
            # Conectar el botón de Actualizar (pushButton_11)
            self.ui_content.pushButton_11.clicked.connect(self.actualizar_datos_analisis)
            self.ui_content.pushButton_12.clicked.connect(self.importa)

            #Reportes
            # Al final de tu def __init__(self):
            self.actualizar_tabla_reportes()
            self.agregar_nuevo_reporte()
            # Conexión para que al tocar la tabla se llenen los campos
            self.ui_content.tableWidget_4.itemClicked.connect(self.seleccionar_reporte_tabla)
            # Conexión del botón Añadir en la pestaña de reportes
            self.ui_content.pushButton_13.clicked.connect(self.agregar_datos_reporte)
            # Conexión del botón Eliminar
            self.ui_content.pushButton_14.clicked.connect(self.eliminar_datos_reporte)
            # Conexión del botón Actualizar
            self.ui_content.pushButton_15.clicked.connect(self.actualizar_datos_reporte)
            self.ui_content.pushButton_16.clicked.connect(self.importa)
            self.seleccionar_reporte_tabla()
            self.graficar_gestion_mercado()
            self.graficar_operaciones_mercado()
            self.graficar_analisis_mercado()
            self.graficar_operaciones_sistema()
            self.comparar_rendimiento_mercado()
            self.graficar_estado_salud_sistema()
            
            
            
        print("Interfaz y componentes renderizados correctamente.")

    #pasar paginas
    def conectar_menu(self):
        # Usamos lambda para pasar el número de página deseado
        
        # Dashboard -> Página 0
        self.ui_content.actionGraf_ca.triggered.connect(lambda: self.cambiar_pagina(0))
        
        # Reportes (actionCrud) -> Página 1
        self.ui_content.actionCrud_4.triggered.connect(lambda: self.cambiar_pagina(1))
        
        # Operaciones (actionCrud_3) -> Página 2
        self.ui_content.actionCrud_3.triggered.connect(lambda: self.cambiar_pagina(2))
        
        # Análisis (actionCrud_2) -> Página 3
        self.ui_content.actionCrud_2.triggered.connect(lambda: self.cambiar_pagina(3))

        #
        self.ui_content.actionCrud.triggered.connect(lambda: self.cambiar_pagina(4))

        # El botón Volver ya te funciona, mantenlo así
        self.ui_content.actionInicio.triggered.connect(self.regresar_inicio)

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

    # Archivo

    def configurar_tabla_mercado(self):
        # Definir columnas
        columnas = ["ID", "Nombre", "Ruta Directorio", "Versión", "Fecha Acción", "Estado Servidor"]
        self.ui_content.tableWidget.setColumnCount(len(columnas))
        self.ui_content.tableWidget.setHorizontalHeaderLabels(columnas)
        
        # Estética profesional para cautivar a RRHH
        self.ui_content.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui_content.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui_content.tableWidget.horizontalHeader().setStretchLastSection(True)
        # Oculta los números de fila (1, 2, 3...) de la izquierda
        self.ui_content.tableWidget.verticalHeader().setVisible(False)

        # Toque extra: Hacer que las columnas se ajusten al contenido automáticamente
        self.ui_content.tableWidget.resizeColumnsToContents()


    def cargar_datos_tableWidget(self):
        try:
            conn = sqlite3.connect("ingenieria.db") #
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gestion_mercado") #
            datos = cursor.fetchall()

            self.ui_content.tableWidget.setRowCount(0) # Limpiar tabla visual

            for row_number, row_data in enumerate(datos):
                self.ui_content.tableWidget.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data)) #

                    # Resaltar estados críticos (Columna 5: Estado Servidor)
                    if column_number == 5:
                        if data == "Error Crítico":
                            item.setForeground(QColor("#ff4444")) # Rojo Neón
                        elif data == "Activo":
                            item.setForeground(QColor("#00e5ff")) # Cian Neón

                    self.ui_content.tableWidget.setItem(row_number, column_number, item)

            conn.close()
            # IMPORTANTE: Llama a la gráfica después de cargar los datos para que se sincronice
            self.graficar_estados_servidores()
            
            print("🔄 Interfaz actualizada desde la base de datos.")

        except Exception as e:
            print(f"❌ Error al cargar tableWidget: {e}") # Revisa este mensaje en la terminal
            

    #obtener datos tablewidget

    def obtener_datos_seleccionados(self):
        # Obtener las filas seleccionadas
        seleccion = self.ui_content.tableWidget.selectedItems()
        
        if not seleccion:
            return

        # Como seleccionamos por filas, tomamos los datos de la primera fila seleccionada
        # El orden depende de tus columnas: ID(0), Nombre(1), Ruta(2), Versión(3), Fecha(4), Estado(5)
        fila_actual = seleccion[0].row()
        
        # Mapeo directo a tus objetos QLineEdit
        self.ui_content.lbl_id.setText(self.ui_content.tableWidget.item(fila_actual, 0).text())
        self.ui_content.lbl_confi.setText(self.ui_content.tableWidget.item(fila_actual, 1).text()) # Nombre de config
        self.ui_content.lbl_ruta.setText(self.ui_content.tableWidget.item(fila_actual, 2).text())
        self.ui_content.lbl_version.setText(self.ui_content.tableWidget.item(fila_actual, 3).text())
        self.ui_content.lbl_fecha.setText(self.ui_content.tableWidget.item(fila_actual, 4).text()) # Fecha Acción
        self.ui_content.lbl_estado.setText(self.ui_content.tableWidget.item(fila_actual, 5).text())

    
    #treewidget  

    def actualizar_treeWidget(self):
        try:
            self.ui_content.treeWidget.clear()
            # Definimos 3 columnas claras
            self.ui_content.treeWidget.setColumnCount(3)
            self.ui_content.treeWidget.setHeaderLabels(["Nombre / Categoría", "Estado", "Versión"])
            self.ui_content.treeWidget.setColumnWidth(0, 250)
            
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # 1. Obtenemos los estados para las carpetas
            cursor.execute("SELECT DISTINCT estado_servidor FROM gestion_mercado")
            estados = cursor.fetchall()

            for (estado,) in estados:
                # Creamos el PADRE (La carpeta de estado)
                parent = QTreeWidgetItem(self.ui_content.treeWidget)
                parent.setText(0, f"📁 {estado.upper()}")
                
                # 2. Buscamos los servidores de ese estado con su versión
                # Asegúrate que los nombres de columna coincidan con tu SQL
                cursor.execute("SELECT nombre, estado_servidor, version FROM gestion_mercado WHERE estado_servidor = ?", (estado,))
                servidores = cursor.fetchall()

                for nom, est, ver in servidores:
                    # Creamos el HIJO con los 3 datos solicitados
                    child = QTreeWidgetItem(parent)
                    child.setText(0, nom) # Nombre
                    child.setText(1, est) # Estado
                    child.setText(2, ver) # Versión
                    
                    # Toque Neon: Si es error, pintamos el texto del hijo
                    if est == "Error Crítico":
                        child.setForeground(0, QColor("#ff4444"))
                
            self.ui_content.treeWidget.expandAll() # Para que no tengas que presionar para ver
            conn.close()
        except Exception as e:
            print(f"Error detectado en treeWidget: {e}")


    #grafica

    def graficar_estados_servidores(self):
        try:
            # 1. Obtener datos de la base de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("SELECT estado_servidor, COUNT(*) FROM gestion_mercado GROUP BY estado_servidor")
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                return

            estados = [d[0] for d in datos]
            cantidades = [d[1] for d in datos]

            # 2. Crear la figura de Matplotlib con estilo oscuro
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
            fig.patch.set_facecolor('#0b0b0b') # Fondo igual a tu UI
            ax.set_facecolor('#0b0b0b')

            # Crear barras con colores neon
            barras = ax.bar(estados, cantidades, color='#00e5ff', edgecolor='white', linewidth=0.5)
            ax.set_title("Estado Actual de Servidores", color='#00e5ff', fontsize=10)

            # 3. Limpiar el frame_7 e insertar la gráfica
            # Si el frame ya tiene un layout, lo usamos; si no, creamos uno
            if self.ui_content.frame_7.layout() is None:
                layout = QVBoxLayout(self.ui_content.frame_7)
            else:
                # Limpiar contenido previo para no encimar gráficas
                layout = self.ui_content.frame_7.layout()
                for i in reversed(range(layout.count())): 
                    layout.itemAt(i).widget().setParent(None)

            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)
            
        except Exception as e:
            print(f"Error al generar gráfica: {e}")

    
    #imagen


    def actualizar_monitor_con_imagen(self):
        print("\n[1] --- ENTRANDO A LA FUNCIÓN ---") 
        try:
            # Verificamos fila
            seleccion = self.ui_content.tableWidget.currentRow()
            print(f"[2] Fila seleccionada: {seleccion}")
            if seleccion == -1: return

            # Verificamos si la celda existe antes de pedir el .text()
            item_celda = self.ui_content.tableWidget.item(seleccion, 5)
            if item_celda is None:
                print("[X] ERROR: La celda de la columna 5 es nula (está vacía)")
                return
                
            estado_texto = item_celda.text().strip()
            print(f"[3] Texto detectado: '{estado_texto}'")

            # Construcción de ruta
            ruta_base = "Mercado/Archivo/"
            img_nombre = f"{estado_texto}.png"
            img_path = os.path.join(os.getcwd(), ruta_base, img_nombre)
            print(f"[4] Buscando en: {img_path}")

            # Intentar cargar Pixmap
            pixmap = QPixmap(img_path)
            
            if not pixmap.isNull():
                print("[5] ✅ Imagen encontrada. Ajustando al tamaño del label...")
                
                # 1. Forzamos que el label acepte el escalado automático
                self.ui_content.label.setScaledContents(True) 
                
                # 2. Asignamos el pixmap directamente (el scaledContents hará el resto)
                # Opcional: Si quieres mantener la calidad al estirar, usa SmoothTransformation
                self.ui_content.label.setPixmap(pixmap.scaled(
                    self.ui_content.label.size(), 
                    Qt.IgnoreAspectRatio, # Esto hace que rellene TODO el cuadro
                    Qt.SmoothTransformation
                ))
            else:
                print(f"[X] ❌ Pixmap NULO. El archivo existe pero no es una imagen válida o ruta mal escrita.")
                self.ui_content.label.setText(f"Error: {estado_texto}")

        except Exception as e:
            # Este print DEBE salir si algo falla adentro
            print(f"!!! ERROR CRÍTICO EN TRY: {str(e)}")

    
    #botones

    def agregar_nuevo_servidor(self):
        try:
            # 1. Capturar datos de los QLineEdit
            id_rol = self.ui_content.lbl_id.text()
            nombre = self.ui_content.lbl_confi.text()
            ruta = self.ui_content.lbl_ruta.text()
            version = self.ui_content.lbl_version.text()
            fecha = self.ui_content.lbl_fecha.text()
            estado = self.ui_content.lbl_estado.text()

            # 2. Validar campos obligatorios
            if not id_rol or not nombre or not estado:
                print("⚠️ Por favor, rellena los campos obligatorios.")
                return

            # 3. Insertar en la Base de Datos
            # Usamos el nombre de tu db según la estructura de archivos
            conexion = sqlite3.connect("ingenieria.db")
            cursor = conexion.cursor()
            
            # Ajusta los nombres de las columnas según tu tabla en la DB
            query = """INSERT INTO gestion_mercado 
                    (id, nombre, ruta_directorio, version, fecha_accion, estado_servidor) 
                    VALUES (?, ?, ?, ?, ?, ?)"""
            
            cursor.execute(query, (id_rol, nombre, ruta, version, fecha, estado))
            conexion.commit()
            conexion.close()

            print(f"✅ Servidor '{nombre}' guardado en DB exitosamente.")

            # 4. Refrescar la interfaz visual
            self.limpiar_campos() 
            self.graficar_estados_servidores() # Este método debe recargar la tabla desde la DB

        except Exception as e:
            print(f"❌ Error al añadir a la DB: {e}")


    def limpiar_campos(self):
        """Limpia todos los campos de entrada de la interfaz"""
        # Usamos una lista para iterar y limpiar de forma más elegante
        campos = [
            self.ui_content.lbl_id,
            self.ui_content.lbl_confi,
            self.ui_content.lbl_ruta,
            self.ui_content.lbl_version,
            self.ui_content.lbl_fecha,
            self.ui_content.lbl_estado
            ]
            
        
        for campo in campos:
            campo.clear()
            
        # Opcional: Devolver el foco al primer campo para agilizar la carga
        self.ui_content.lbl_id.setFocus()
        self.cargar_datos_tableWidget()
        print("🧹 Campos de entrada limpiados.")


    def eliminar_servidor(self):
        try:
            # 1. Obtener la fila seleccionada
            fila = self.ui_content.tableWidget.currentRow()
            
            if fila == -1:
                print("⚠️ Selecciona una fila para eliminar.")
                return

            # 2. Obtener el ID de la columna 0 para la consulta SQL
            id_servidor = self.ui_content.tableWidget.item(fila, 0).text()
            nombre = self.ui_content.tableWidget.item(fila, 1).text()

            # 3. Eliminar de la Base de Datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM gestion_mercado WHERE id = ?", (id_servidor,))
            conn.commit()
            conn.close()
            
            print(f"🗑️ DB: Servidor '{nombre}' eliminado permanentemente.")

            # 4. Limpiar y refrescar
            self.limpiar_campos()
            self.ui_content.label.clear()
            self.cargar_datos_tableWidget()

        except Exception as e:
            print(f"❌ Error al eliminar en DB: {e}")


    def actualizar_servidor_db(self):
        try:
            # 1. Capturar los datos actuales de los campos
            # Usamos el ID como llave para saber qué registro cambiar
            id_rol = self.ui_content.lbl_id.text()
            nombre = self.ui_content.lbl_confi.text()
            ruta = self.ui_content.lbl_ruta.text()
            version = self.ui_content.lbl_version.text()
            fecha = self.ui_content.lbl_fecha.text()
            estado = self.ui_content.lbl_estado.text()

            if not id_rol:
                print("⚠️ El ID es necesario para identificar qué servidor actualizar.")
                return

            # 2. Ejecutar la actualización en la DB
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            query = """UPDATE gestion_mercado 
                    SET nombre = ?, ruta_directorio = ?, version = ?, fecha_accion = ?, estado_servidor = ?
                    WHERE id = ?"""
            
            cursor.execute(query, (nombre, ruta, version, fecha, estado, id_rol))
            conn.commit()
            conn.close()

            print(f"✅ DB: Servidor ID {id_rol} actualizado correctamente.")

            # 3. Refrescar la UI completa
            # Al llamar a este método, se actualiza la tabla y automáticamente la gráfica
            self.cargar_datos_tableWidget()
            
        except Exception as e:
            print(f"❌ Error al actualizar en DB: {e}")

    
    def importa(self):
        
        Exportar.seleccionar_y_convertir()


    # ------------------------ OPERACIONES----------------------

    def cargar_datos_operaciones(self):
        try:
            # 1. Conexión a la tabla de rendimiento
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM operaciones_mercado")
            datos = cursor.fetchall()

            # 2. Limpiar tableWidget_2 antes de cargar
            self.ui_content.tableWidget_2.setRowCount(0)
            # Oculta la columna de números a la izquierda
            self.ui_content.tableWidget_2.verticalHeader().setVisible(False)

            for row_number, row_data in enumerate(datos):
                self.ui_content.tableWidget_2.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    
                    # 3. Colores Neón según el Nivel de Servicio (Columna 5)
                    if column_number == 5: 
                        if data == "Crítico":
                            item.setForeground(QColor("#ff4444")) # Rojo Neón
                        elif data == "Óptimo":
                            item.setForeground(QColor("#00e5ff")) # Cian Neón
                        elif data == "Degradado":
                            item.setForeground(QColor("#ffaa00")) # Naranja Alerta

                    self.ui_content.tableWidget_2.setItem(row_number, column_number, item)

            conn.close()
            
            # 4. Sincronizar la gráfica automáticamente
            self.graficar_estados_servidores() 
            print("📈 Tabla de Operaciones actualizada correctamente.")

        except Exception as e:
            print(f"❌ Error al cargar tableWidget_2: {e}")


    def actualizar_tabla_analisis(self):
        try:
            # 1. Conexión a la base de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Seleccionamos todas las columnas relevantes
            cursor.execute("""
                SELECT id_nodo_cluster, metrica_pico_ms, umbral_carga_pct, 
                    uptime_total, ultimo_incidente, salud_global 
                FROM analisis_mercado
            """)
            datos = cursor.fetchall()
            conn.close()

            # 2. Configurar dimensiones del tableWidget_3
            self.ui_content.tableWidget_3.setRowCount(len(datos))
            self.ui_content.tableWidget_3.setColumnCount(6)
            self.graficar_analisis_mercado()

            # 3. Poblar la tabla con estilo condicional
            for fila_idx, fila_datos in enumerate(datos):
                for col_idx, valor in enumerate(fila_datos):
                    item = QTableWidgetItem(str(valor))
                    
                    # Aplicar color según el estado de salud (Columna 5)
                    salud = str(fila_datos[5])
                    if salud == "Crítico":
                        item.setForeground(QColor("#ff4444")) # Rojo neón
                    elif salud == "Degradado":
                        item.setForeground(QColor("#ffaa00")) # Naranja
                    else:
                        item.setForeground(QColor("#00e5ff")) # Cian

                    self.ui_content.tableWidget_3.setItem(fila_idx, col_idx, item)

            print("📊 Tabla de Análisis actualizada desde la base de datos.")

        except Exception as e:
            print(f"❌ Error al refrescar tabla: {e}")

    #grafica

    def graficar_operaciones(self):
        try:
            # 1. Obtener conteo de niveles de servicio
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("SELECT nivel_servicio, COUNT(*) FROM operaciones_mercado GROUP BY nivel_servicio")
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                return

            # 2. Configuración de la Figura (Sin pyplot para evitar la pestaña)
            from matplotlib.figure import Figure
            fig = Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)
            
            fig.patch.set_facecolor('#0b0b0b')
            ax.set_facecolor('#0b0b0b')

            # 3. Preparar datos y colores temáticos
            niveles = [d[0] for d in datos]
            conteos = [d[1] for d in datos]
            colores = ['#00e5ff' if n == 'Óptimo' else '#ffaa00' if n == 'Degradado' else '#ff4444' for n in niveles]

            # 4. Dibujar la gráfica
            ax.bar(niveles, conteos, color=colores, edgecolor='white', linewidth=0.5)
            ax.set_title("Rendimiento de Operaciones (SLA)", color='#00e5ff', fontsize=10)
            ax.tick_params(colors='white', labelsize=8)
            fig.tight_layout()

            # 5. Insertar en frame_8
            if self.ui_content.frame_8.layout() is None:
                from PySide6.QtWidgets import QVBoxLayout
                layout = QVBoxLayout(self.ui_content.frame_8)
            else:
                layout = self.ui_content.frame_8.layout()
                for i in reversed(range(layout.count())):
                    layout.itemAt(i).widget().setParent(None)

            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)

        except Exception as e:
            print(f"❌ Error al graficar en frame_8: {e}")

            
            

    def cargar_tree_operaciones_detallado(self):
        try:
            self.ui_content.treeWidget_2.clear()
            # Configurar encabezados
            self.ui_content.treeWidget_2.setHeaderLabels(["Categoría / Nodo", "Métricas", "SLA"])
            # 1. Hacer que las columnas se estiren automáticamente
            header = self.ui_content.treeWidget_2.header()
            header.setSectionResizeMode(0, QHeaderView.Stretch)      # La columna de Nombre se estira
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # Métricas según el texto
            header.setSectionResizeMode(2, QHeaderView.Fixed)       # SLA con ancho fijo
            self.ui_content.treeWidget_2.setColumnWidth(2, 100)     # Espacio suficiente para 'Degradado'

            # 2. Agregar margen interno (Indenta los hijos más a la derecha)
            self.ui_content.treeWidget_2.setIndentation(25)
            
            # 1. Crear Padres (Categorías)
            categorias = {
                "Crítico": QTreeWidgetItem(self.ui_content.treeWidget_2, ["🔴 CRÍTICO", "", ""]),
                "Degradado": QTreeWidgetItem(self.ui_content.treeWidget_2, ["🟠 DEGRADADO", "", ""]),
                "Óptimo": QTreeWidgetItem(self.ui_content.treeWidget_2, ["🔵 ÓPTIMO", "", ""])
            }

            # Aplicar colores a las categorías
            categorias["Crítico"].setForeground(0, QColor("#ff4444"))
            categorias["Degradado"].setForeground(0, QColor("#ffaa00"))
            categorias["Óptimo"].setForeground(0, QColor("#00e5ff"))

            # 2. Obtener datos de la base de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("SELECT nodo_destino, latencia_ms, capacidad_utilizada, ultimo_reporte, nivel_servicio FROM operaciones_mercado")
            datos = cursor.fetchall()
            conn.close()

            # 3. Insertar Hijos y Sub-hijos (Desglose)
            for nodo, lat, cap, reporte, sla in datos:
                if sla in categorias:
                    # Nodo del Servidor
                    item_nodo = QTreeWidgetItem(categorias[sla], [nodo, "", sla])
                    
                    # Sub-item con detalles técnicos (el desglose final)
                    detalles = f"Latencia: {lat}ms | Uso: {cap}% | Reporte: {reporte}"
                    QTreeWidgetItem(item_nodo, ["Detalles Técnicos", detalles, ""])

                # Dentro de tu bucle for, cuando creas el sub-ítem de detalles:
                detalles_text = f"📊 Lat: {lat}ms | 🧠 Uso: {cap}% | 🕒 {reporte}"
                sub_item = QTreeWidgetItem(item_nodo, ["   ↳ " + detalles_text]) # Añade un prefijo visual

                # Ponemos los detalles en un tono gris para que resalte el nombre del servidor
                sub_item.setForeground(0, QColor("#aaaaaa")) 
                font = sub_item.font(0)
                font.setItalic(True)
                font.setPointSize(9)
                sub_item.setFont(0, font)

            # Expandir automáticamente los Críticos para llamar la atención
            categorias["Crítico"].setExpanded(True)

        except Exception as e:
            print(f"❌ Error en TreeWidget_2: {e}")


    def obtener_datos_de_tabla(self):
        # 1. Obtener la fila seleccionada
        fila_seleccionada = self.ui_content.tableWidget_2.currentRow()
        
        if fila_seleccionada != -1:
            # 2. Extraer datos de las columnas
            # Columna 0 es el ID Servidor en tu tabla
            id_servidor = self.ui_content.tableWidget_2.item(fila_seleccionada, 0).text()
            nodo        = self.ui_content.tableWidget_2.item(fila_seleccionada, 1).text()
            latencia    = self.ui_content.tableWidget_2.item(fila_seleccionada, 2).text()
            capacidad   = self.ui_content.tableWidget_2.item(fila_seleccionada, 3).text()
            salud       = self.ui_content.tableWidget_2.item(fila_seleccionada, 4).text()
            nivel       = self.ui_content.tableWidget_2.item(fila_seleccionada, 5).text()

            # 3. Asignar a los QLineEdit correspondientes
            # Si no tienes un 'lbl_id' creado, puedes usar el nombre que le diste al ID Servidor
            self.ui_content.lbl_servidor.setText(id_servidor) 
            self.ui_content.lbl_nodo.setText(nodo)
            self.ui_content.lbl_ms.setText(latencia)
            self.ui_content.lbl_capacidad.setText(capacidad)
            self.ui_content.lbl_salud.setText(salud)
            self.ui_content.lbl_nivel.setText(nivel)
            
            print(f"🆔 ID {id_servidor} cargado correctamente.")

    
    # imagen

    def obtener_imagen_de_tabla(self):
        fila = self.ui_content.tableWidget_2.currentRow()
        if fila != -1:
            # 1. Extraer los datos técnicos de la tabla
            id_servidor = self.ui_content.tableWidget_2.item(fila, 0).text()
            nodo        = self.ui_content.tableWidget_2.item(fila, 1).text()
            # ... (puedes mantener el resto de las capturas aquí)

            # 2. Rellenar los LineEdits
            self.ui_content.lbl_id.setText(id_servidor)
            self.ui_content.lbl_nodo.setText(nodo)

            # 3. Lógica para cargar la imagen dinámica
            # Definimos la ruta de tu carpeta de operaciones
            ruta_base = r"C:\Users\yulls\Documents\youtube\AutoMetrics 2.0\Mercado\operaciones"
            nombre_archivo = f"{nodo}.png" # Asumiendo formato .png como en tus archivos
            ruta_completa = os.path.join(ruta_base, nombre_archivo)

            # 4. Verificar si la imagen existe antes de cargarla para evitar errores
            if os.path.exists(ruta_completa):
                pixmap = QPixmap(ruta_completa)
                # Escalamos la imagen para que quepa bien en el label_8 sin deformarse
                self.ui_content.label_8.setPixmap(pixmap.scaled(
                    self.ui_content.label_8.width(), 
                    self.ui_content.label_8.height(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                ))
                print(f"🖼️ Imagen cargada para el nodo: {nodo}")
            else:
                self.ui_content.label_8.setText("Imagen no encontrada")
                print(f"⚠️ No se encontró imagen en: {ruta_completa}")

    
    #botones
        
    def registrar_operacion(self):
        try:
            # 1. Capturar datos de los LineEdits
            nodo = self.ui_content.lbl_nodo.text()
            latencia = self.ui_content.lbl_ms.text()
            capacidad = self.ui_content.lbl_capacidad.text()
            reporte = self.ui_content.lbl_salud.text()
            sla = self.ui_content.lbl_nivel.text()

            # Validación simple: no permitir campos vacíos
            if not nodo or not latencia:
                print("⚠️ Complete los campos obligatorios (Nodo y Latencia).")
                return

            # 2. Insertar en la base de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            query = """
                INSERT INTO operaciones_mercado 
                (nodo_destino, latencia_ms, capacidad_utilizada, ultimo_reporte, nivel_servicio) 
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (nodo, latencia, capacidad, reporte, sla))
            
            conn.commit()
            conn.close()

            # 3. Actualizar la interfaz completa
            self.cargar_datos_operaciones() # Recarga la tabla tableWidget_2
            self.graficar_operaciones()    # Recarga la gráfica en frame_8
            self.cargar_tree_operaciones_detallado() # Recarga el TreeWidget
            
            # 4. Limpiar campos tras el éxito
            self.limpiar_campos_registro()
            print(f"✅ Nodo '{nodo}' registrado exitosamente.")

        except Exception as e:
            print(f"❌ Error al registrar en SQL: {e}")

    def limpiar_campos_registro(self):
        self.ui_content.lbl_servidor.clear()
        self.ui_content.lbl_nodo.clear()
        self.ui_content.lbl_ms.clear()
        self.ui_content.lbl_capacidad.clear()
        self.ui_content.lbl_salud.clear()
        self.ui_content.lbl_nivel.clear()


    def eliminar_operacion(self):
        # 1. Obtener el ID y el nombre del nodo para personalizar el mensaje
        id_a_borrar = self.ui_content.lbl_id.text()
        nombre_nodo = self.ui_content.lbl_nodo.text()

        if not id:
            print("⚠️ Seleccione una fila primero.")
            return

        # 2. Crear la Alerta de Seguridad (Cuadro de confirmación)
        pregunta = QMessageBox.question(
            self, 
            'Confirmar Eliminación', 
            f"¿Está seguro de que desea eliminar permanentemente el nodo '{nombre_nodo}' (ID: {id_a_borrar})?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )

        # 3. Solo proceder si el usuario presiona "Yes"
        if pregunta == QMessageBox.Yes:
            try:
                conn = sqlite3.connect("ingenieria.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM operaciones_mercado WHERE id_servidor = ?", (id_a_borrar,))
                conn.commit()
                conn.close()

                # Refrescar la interfaz
                self.cargar_datos_operaciones()
                self.graficar_operaciones()
                self.cargar_tree_operaciones_detallado()
                
                # Limpiar campos
                self.limpiar_campos_registro()
                self.ui_content.label_8.clear()
                
                # Mostrar mensaje de éxito (opcional)
                QMessageBox.information(self, "Éxito", f"El nodo {nombre_nodo} ha sido eliminado.")
                print(f"🗑️ Registro {id_a_borrar} eliminado.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el registro: {e}")
        else:
            # Si presiona "No", la función termina aquí y no pasa nada
            print("❌ Eliminación cancelada por el usuario.")


    def actualizar_operacion(self):
        # 1. Obtener el ID (esencial para saber qué registro cambiar)
        id_servidor = self.ui_content.lbl_id.text()
        
        if not id_servidor:
            print("⚠️ Error: Seleccione primero un registro de la tabla para actualizar.")
            return

        try:
            # 2. Capturar los nuevos valores de los campos
            nodo = self.ui_content.lbl_nodo.text()
            latencia = self.ui_content.lbl_ms.text()
            capacidad = self.ui_content.lbl_capacidad.text()
            reporte = self.ui_content.lbl_salud.text()
            sla = self.ui_content.lbl_nivel.text()

            # 3. Ejecutar el UPDATE en la base de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            query = """
                UPDATE operaciones_mercado 
                SET nodo_destino = ?, 
                    latencia_ms = ?, 
                    capacidad_utilizada = ?, 
                    ultimo_reporte = ?, 
                    nivel_servicio = ?
                WHERE id_servidor = ?
            """
            cursor.execute(query, (nodo, latencia, capacidad, reporte, sla, id_servidor))
            
            conn.commit()
            conn.close()

            # 4. Sincronizar toda la interfaz visual
            self.cargar_datos_operaciones()          # Refresca tableWidget_2
            self.graficar_operaciones()             # Refresca la gráfica en frame_8
            self.cargar_tree_operaciones_detallado() # Refresca treeWidget_2
            
            # Opcional: Confirmación visual al usuario
            QMessageBox.information(self, "Actualización", f"Nodo {nodo} actualizado correctamente.")
            print(f"🔄 Registro ID {id_servidor} modificado exitosamente.")

        except Exception as e:
            print(f"❌ Error al actualizar en SQL: {e}")


    #---------------------------ANALISIS---------------------------------------


    def cargar_datos_analisis(self):
        try:
            # 1. Conexión a la base de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # 2. Seleccionar los datos de la tabla de análisis
            query = "SELECT id_nodo_cluster, metrica_pico_ms, umbral_carga_pct, uptime_total, ultimo_incidente, salud_global FROM analisis_mercado"
            cursor.execute(query)
            datos = cursor.fetchall()
            
            # 3. Configurar dimensiones de tableWidget_3
            self.ui_content.tableWidget_3.setRowCount(len(datos))
            self.ui_content.tableWidget_3.setColumnCount(6)
            # 1. Ocultar los números de fila (índices verticales)
            self.ui_content.tableWidget_3.verticalHeader().setVisible(False)

            # 2. Opcional: Hacer que las columnas se ajusten automáticamente al ancho del widget
            
            self.ui_content.tableWidget_3.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            
            # 4. Llenar la tabla con estilo neón
            for fila_idx, fila_datos in enumerate(datos):
                for col_idx, valor in enumerate(fila_datos):
                    item = QTableWidgetItem(str(valor))
                    
                    # Aplicar color según la salud global (columna 5)
                    estado = str(fila_datos[5])
                    if estado == "Óptimo":
                        item.setForeground(QColor("#00e5ff")) # Cian neón
                    elif estado == "Crítico":
                        item.setForeground(QColor("#ff4444")) # Rojo alerta
                    elif estado == "Degradado" or estado == "En Riesgo":
                        item.setForeground(QColor("#ffaa00")) # Naranja advertencia
                    
                    self.ui_content.tableWidget_3.setItem(fila_idx, col_idx, item)

            conn.close()
            print("📊 Datos de Análisis cargados en tableWidget_3")

        except Exception as e:
            print(f"❌ Error al cargar tableWidget_3: {e}")

    
    #grafica

    def graficar_analisis_mercado(self):
        try:
            # 1. Validación de Layout para evitar NoneType
            if self.ui_content.frame_9.layout() is None:
                from PySide6.QtWidgets import QVBoxLayout
                self.ui_content.frame_9.setLayout(QVBoxLayout())

            # 2. Limpieza total del frame antes de redibujar
            while self.ui_content.frame_9.layout().count():
                child = self.ui_content.frame_9.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # 3. Obtención de datos actualizados
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id_nodo_cluster, metrica_pico_ms FROM analisis_mercado LIMIT 10")
            datos = cursor.fetchall()
            conn.close()

            if not datos: return

            nodos = [d[0] for d in datos][::-1]
            picos = [d[1] for d in datos][::-1]

            # 4. Creación del gráfico
            canvas = CanvasAnalisis()
            ax = canvas.ax
            ax.clear()
            
            # Estilo oscuro
            canvas.fig.patch.set_facecolor('#0b0d0e')
            ax.set_facecolor('#0b0d0e')

            # --- SOLUCIÓN AL ERROR DE CONSOLA ---
            posiciones = range(len(nodos))
            ax.set_yticks(posiciones) # Definimos primero las posiciones fijas
            ax.set_yticklabels(nodos, color='white', fontsize=8) # Ahora sí ponemos los nombres
            
            ax.barh(posiciones, picos, color='#00e5ff', edgecolor='#00838f')
            ax.tick_params(axis='x', colors='white')
            
            # 5. Dibujar en la interfaz
            self.ui_content.frame_9.layout().addWidget(canvas)
            canvas.draw()
            print("📈 QFrame (frame_9) actualizado con éxito.")

        except Exception as e:
            print(f"❌ Error al actualizar frame_9: {e}")


    def configurar_tree_analisis(self):
        # Definir encabezados relevantes
        self.ui_content.treeWidget_3.setHeaderLabels([
            "Jerarquía de Análisis", "Pico Latencia", "Uptime %", "Último Incidente"
        ])
        
        # Ajustar el ancho de las columnas para que tengan "un buen espacio"
        header = self.ui_content.treeWidget_3.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)      # La carpeta se estira
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # El valor ms es corto
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # El % es corto
        header.setSectionResizeMode(3, QHeaderView.Stretch)      # La fecha necesita espacio

    def cargar_tree_analisis_jerarquico(self):
        try:
            self.ui_content.treeWidget_3.clear()
            
            # 1. Crear las Carpetas de Categoría (Padres)
            categorias = {
                "Óptimo": QTreeWidgetItem(self.ui_content.treeWidget_3, ["SISTEMAS ESTABLES"]),
                "Degradado": QTreeWidgetItem(self.ui_content.treeWidget_3, ["SISTEMAS DEGRADADOS"]),
                "Crítico": QTreeWidgetItem(self.ui_content.treeWidget_3, ["ALERTA CRÍTICA"])
            }
            
            # Conexión a DB
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id_nodo_cluster, metrica_pico_ms, uptime_total, ultimo_incidente, salud_global FROM analisis_mercado")
            datos = cursor.fetchall()
            conn.close()

            # 2. Distribuir datos en las carpetas
            for nodo, pico, uptime, incidente, salud in datos:
                # Buscar la carpeta correcta (si no coincide con las 3 principales, va a Óptimo por defecto)
                padre = categorias.get(salud, categorias["Óptimo"])
                
                # Crear el hijo con los datos relevantes
                hijo = QTreeWidgetItem(padre, [
                    nodo, 
                    f"{pico} ms", 
                    uptime, 
                    incidente
                ])
                
                # Aplicar color al texto según la urgencia
                if salud == "Crítico":
                    hijo.setForeground(0, QColor("#ff4444"))
                elif salud == "Degradado":
                    hijo.setForeground(0, QColor("#ffaa00"))
                else:
                    hijo.setForeground(0, QColor("#00e5ff"))

            # Expandir todas las carpetas por defecto
            self.ui_content.treeWidget_3.expandAll()
            print("📁 Jerarquía de Análisis cargada en treeWidget_3")

        except Exception as e:
            print(f"❌ Error al cargar árbol jerárquico: {e}")


    def actualizar_imagen_nodo(self, nombre_nodo):
        # 1. Definir la ruta de la carpeta donde guardas tus imágenes (ej: 'imagenes_nodos')
        ruta_base = "Mercado/Analisis/" 
        extension = ".png"
        ruta_completa = os.path.join(ruta_base, f"{nombre_nodo}{extension}")

        # 2. Verificar si la imagen existe para evitar errores
        if os.path.exists(ruta_completa):
            pixmap = QPixmap(ruta_completa)
            # Ajustar la imagen al tamaño del label_15 sin deformarla
            self.ui_content.label_15.setPixmap(pixmap.scaled(
                self.ui_content.label_15.size(), 
                aspectMode=Qt.KeepAspectRatio, 
                mode=Qt.SmoothTransformation
            ))
            self.ui_content.label_15.setScaledContents(True)
        else:
            # Si no existe, puedes poner una imagen por defecto o limpiar el label
            self.ui_content.label_15.setText(f"Sin imagen para: {nombre_nodo}")
            print(f"⚠️ No se encontró la imagen en: {ruta_completa}")



    def al_hacer_click_en_tabla(self, item):
        # Obtener el nombre del nodo de la columna 0 (id_nodo_cluster)
        fila = item.row()
        nombre_nodo = self.ui_content.tableWidget_3.item(fila, 0).text()
        
        # Llamar a la función de la imagen
        self.actualizar_imagen_nodo(nombre_nodo)
        
       

    def seleccionar_datos_analisis(self, fila, columna):
        try:
            # Extraer datos de la fila seleccionada en tableWidget_3
            # Columna 0: ID DEL NODO / CLÚSTER
            nodo = self.ui_content.tableWidget_3.item(fila, 0).text()
            # Columna 1: MÉTRICA DE PICO (LATENCIA)
            pico = self.ui_content.tableWidget_3.item(fila, 1).text()
            # Columna 2: UMBRAL DE CARGA (%)
            umbral = self.ui_content.tableWidget_3.item(fila, 2).text()
            # Columna 3: TIEMPO DE ACTIVIDAD (UPTIME)
            uptime = self.ui_content.tableWidget_3.item(fila, 3).text()
            # Columna 4: HORA DEL ÚLTIMO INCIDENTE
            hora = self.ui_content.tableWidget_3.item(fila, 4).text()
            # Columna 5: ESTADO DE SALUD GLOBAL
            salud = self.ui_content.tableWidget_3.item(fila, 5).text()

            # Asignar a los QLineEdit correspondientes
            self.ui_content.txt_cluster.setText(nodo)
            self.ui_content.txt_pico.setText(pico)
            self.ui_content.txt_umbral.setText(umbral)
            self.ui_content.txt_uptime.setText(uptime)
            self.ui_content.txt_hora.setText(hora)
            self.ui_content.txt_global.setText(salud)

            # Cargar la imagen del nodo en label_15
            self.actualizar_imagen_nodo(nodo)
            
            print(f"✅ Datos de {nodo} cargados en los campos de edición.")

        except Exception as e:
            print(f"❌ Error al capturar datos de la tabla: {e}")


    def agregar_datos_analisis(self):
        # 1. Obtener los datos de los campos de la interfaz
        nodo = self.ui_content.txt_cluster.text()
        pico = self.ui_content.txt_pico.text()
        umbral = self.ui_content.txt_umbral.text()
        uptime = self.ui_content.txt_uptime.text()
        hora = self.ui_content.txt_hora.text()
        salud = self.ui_content.txt_global.text()

        # Validación básica: No permitir campos vacíos
        if not nodo or not pico:
            QMessageBox.warning(self, "Error", "El ID del Nodo y la Métrica de Pico son obligatorios.")
            return

        try:
            # 2. Conectar a la base de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Sentencia SQL basada en tu estructura de tabla
            query = """
            INSERT INTO analisis_mercado (id_nodo_cluster, metrica_pico_ms, umbral_carga_pct, uptime_total, ultimo_incidente, salud_global)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (nodo, pico, umbral, uptime, hora, salud))
            conn.commit()
            conn.close()

            # 3. Feedback y actualización de la interfaz
            QMessageBox.information(self, "Éxito", f"Nodo {nodo} agregado correctamente.")
            
            # Limpiar campos tras agregar
            self.limpiar_campos_analisis()
            
            # REFRESCAR TABLA Y ÁRBOL PARA VER LOS CAMBIOS
            self.refrescar_todo_analisis()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de DB", f"No se pudo insertar en la base de datos: {e}")

    def limpiar_campos_analisis(self):
        """Limpia los campos después de una operación exitosa"""
        self.ui_content.txt_cluster.clear()
        self.ui_content.txt_pico.clear()
        self.ui_content.txt_umbral.clear()
        self.ui_content.txt_uptime.clear()
        self.ui_content.txt_hora.clear()
        self.ui_content.txt_global.clear()

    
    def refrescar_todo_analisis(self):
        """Refresca todos los componentes visuales con datos reales de la DB"""
        # 1. Cargar datos en la tabla (tableWidget_3)
        self.actualizar_tabla_analisis()
        
        # 2. Cargar la jerarquía (treeWidget_3)
        self.cargar_tree_analisis_jerarquico()
        
        # 3. Forzar el redibujado de la gráfica en frame_9
        self.graficar_analisis_mercado()
        
        print("🔄 Sincronización completa: Tabla y QFrame actualizados.")



    def eliminar_datos_analisis(self):
        # 1. Obtener el ID del nodo desde el campo de texto
        nodo_a_borrar = self.ui_content.txt_cluster.text()

        if not nodo_a_borrar:
            QMessageBox.warning(self, "Atención", "Seleccione un nodo de la tabla para eliminar.")
            return

        # 2. Ventana de confirmación
        confirmacion = QMessageBox.question(
            self, "Confirmar Eliminación", 
            f"¿Está seguro de eliminar el nodo '{nodo_a_borrar}' de la base de datos?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmacion == QMessageBox.Yes:
            try:
                # 3. Conexión y ejecución
                conn = sqlite3.connect("ingenieria.db")
                cursor = conn.cursor()
                
                # Usamos el nombre del nodo como identificador
                cursor.execute("DELETE FROM analisis_mercado WHERE id_nodo_cluster = ?", (nodo_a_borrar,))
                
                conn.commit()
                conn.close()

                # 4. Feedback y Refresco Total
                QMessageBox.information(self, "Éxito", f"Nodo '{nodo_a_borrar}' eliminado correctamente.")
                
                # Limpiamos los campos y refrescamos tabla, gráfica y árbol
                self.limpiar_campos_analisis()
                self.refrescar_todo_analisis() 

            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")


    def actualizar_datos_analisis(self):
        # 1. Obtener los datos de los QLineEdit
        nodo = self.ui_content.txt_cluster.text()
        pico = self.ui_content.txt_pico.text()
        umbral = self.ui_content.txt_umbral.text()
        uptime = self.ui_content.txt_uptime.text()
        hora = self.ui_content.txt_hora.text()
        salud = self.ui_content.txt_global.text()

        if not nodo:
            QMessageBox.warning(self, "Error", "Debe seleccionar un nodo para actualizar.")
            return

        try:
            # 2. Conectar y ejecutar el UPDATE
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Sentencia SQL para actualizar todas las columnas basadas en el nombre del nodo
            query = """
            UPDATE analisis_mercado 
            SET metrica_pico_ms = ?, 
                umbral_carga_pct = ?, 
                uptime_total = ?, 
                ultimo_incidente = ?, 
                salud_global = ? 
            WHERE id_nodo_cluster = ?
            """
            
            cursor.execute(query, (pico, umbral, uptime, hora, salud, nodo))
            conn.commit()
            conn.close()

            # 3. Feedback y Refresco de Interfaz
            QMessageBox.information(self, "Éxito", f"Datos de '{nodo}' actualizados correctamente.")
            
            # Sincronizamos Tabla, Gráfica y Árbol al instante
            self.refrescar_todo_analisis()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de DB", f"No se pudo actualizar: {e}")

    # reportes


    def actualizar_tabla_reportes(self):
        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            # Seleccionamos las 7 columnas reales
            cursor.execute("""
                SELECT id_reporte, responsable, titulo_informe, destino_exportacion, 
                    tipo_documento, periodo_finalizado, prioridad_clasificacion 
                FROM reportes_sistema
            """)
            datos = cursor.fetchall()
            conn.close()

            # CONFIGURACIÓN CORRECTA:
            self.ui_content.tableWidget_4.setRowCount(len(datos))
            self.ui_content.tableWidget_4.setColumnCount(6) # Solo mostramos 6 al usuario
            self.ui_content.tableWidget_4.verticalHeader().setVisible(False)

            for fila_idx, fila_datos in enumerate(datos):
                # Empezamos desde col_idx 1 para saltar el ID en la visualización
                # Pero guardamos el ID en una columna oculta o en el UserData
                for col_idx in range(1, 7): 
                    valor = str(fila_datos[col_idx])
                    item = QTableWidgetItem(valor)
                    
                    # El ID real (fila_datos[0]) lo guardamos oculto en la columna 0 si es necesario
                    # Para esta visualización, mapeamos: Responsable(1)->Col0, Título(2)->Col1...
                    
                    # Aplicar color basado en PRIORIDAD (Índice 6 de la fila de datos)
                    prioridad = str(fila_datos[6])
                    if prioridad == "Crítico":
                        item.setForeground(QColor("#ff4444"))
                    elif prioridad == "Degradado":
                        item.setForeground(QColor("#ffaa00"))
                    else:
                        item.setForeground(QColor("#00e5ff"))

                    self.ui_content.tableWidget_4.setItem(fila_idx, col_idx - 1, item)

            # Guardar el ID de forma invisible para poder eliminar/actualizar luego
            # (O simplemente usa una columna oculta)
        except Exception as e:
            print(f"Error: {e}")

        except Exception as e:
            print(f"❌ Error al cargar reportes en tableWidget_4: {e}")


    def agregar_nuevo_reporte(self):
        # ... código de INSERT en reportes_sistema ...
        self.actualizar_tabla_reportes() # <--- Crucial para ver el cambio
        self.cargar_tree_reportes()
        self.graficar_estadisticas_reportes()
        self.graficar_gestion_mercado()
        self.graficar_operaciones_mercado()
        self.graficar_analisis_mercado()


    def cargar_tree_reportes(self):
        try:
            # 1. Conexión y obtención de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("SELECT tipo_documento, titulo_informe, responsable, prioridad_clasificacion FROM reportes_sistema")
            datos = cursor.fetchall()
            conn.close()

            # 2. Limpiar el árbol y configurar columnas
            self.ui_content.treeWidget_4.clear()
            self.ui_content.treeWidget_4.setHeaderLabels(["Estructura de Reportes", "Responsable", "Prioridad"])
            self.ui_content.treeWidget_4.setColumnWidth(0, 250)

            # 3. Agrupar por tipo (Diccionario de "Carpetas")
            carpetas = {}

            for tipo, titulo, responsable, prioridad in datos:
                # Si la carpeta (PDF, XLSX...) no existe, la creamos
                if tipo not in carpetas:
                    carpeta = QTreeWidgetItem(self.ui_content.treeWidget_4)
                    carpeta.setText(0, f"📁 Archivos {tipo}")
                    carpeta.setForeground(0, QColor("#ffffff"))
                    carpetas[tipo] = carpeta

                # 4. Crear el elemento hijo (el reporte)
                item_reporte = QTreeWidgetItem(carpetas[tipo])
                item_reporte.setText(0, titulo)
                item_reporte.setText(1, responsable)
                item_reporte.setText(2, prioridad)

                # Aplicar colores neón según prioridad
                if prioridad == "Crítico":
                    item_reporte.setForeground(0, QColor("#ff4444"))
                elif prioridad == "Degradado":
                    item_reporte.setForeground(0, QColor("#ffaa00"))
                else:
                    item_reporte.setForeground(0, QColor("#00e5ff"))

            # Expandir todas las carpetas por defecto
            self.ui_content.treeWidget_4.expandAll()
            print("🌳 Jerarquía de Reportes cargada en treeWidget_4.")

        except Exception as e:
            print(f"❌ Error al cargar árbol de reportes: {e}")

    def graficar_estadisticas_reportes(self):
        try:
            # 1. Preparar el Layout del frame_10
            if self.ui_content.frame_10.layout() is None:
                from PySide6.QtWidgets import QVBoxLayout
                self.ui_content.frame_10.setLayout(QVBoxLayout())

            # Limpiar gráfico anterior
            while self.ui_content.frame_10.layout().count():
                child = self.ui_content.frame_10.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # 2. Consultar datos de la nueva tabla
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            # Contamos cuántos reportes hay de cada tipo
            cursor.execute("SELECT tipo_documento, COUNT(*) FROM reportes_sistema GROUP BY tipo_documento")
            datos = cursor.fetchall()
            conn.close()

            if not datos: return

            tipos = [str(d[0]) for d in datos]
            cantidades = [int(d[1]) for d in datos]

            # 3. Crear el Canvas (puedes reutilizar tu clase CanvasAnalisis o crear una nueva)
            canvas = CanvasAnalisis() 
            ax = canvas.ax
            ax.clear()
            
            # Estilo visual coherente (Fondo negro, barras cian)
            canvas.fig.patch.set_facecolor('#0b0d0e')
            ax.set_facecolor('#0b0d0e')
            
            # Dibujar barras verticales
            ax.bar(tipos, cantidades, color='#00e5ff', edgecolor='white', width=0.5)
            
            # Configurar etiquetas
            ax.set_title("DISTRIBUCIÓN DE FORMATOS", color='white', fontsize=10, pad=15)
            ax.tick_params(axis='both', colors='white', labelsize=9)
            
            # 4. Insertar en la interfaz
            self.ui_content.frame_10.layout().addWidget(canvas)
            canvas.draw()
            print("📊 Gráfico de Reportes (frame_10) actualizado.")

        except Exception as e:
            print(f"❌ Error en gráfico de reportes: {e}")

    def seleccionar_reporte_tabla(self, item):
        # Obtenemos la fila en la que se hizo clic
        fila = item.row()
        
        # Extraemos los datos de las columnas
        responsable = self.ui_content.tableWidget_4.item(fila, 0).text()
        titulo      = self.ui_content.tableWidget_4.item(fila, 1).text()
        destino     = self.ui_content.tableWidget_4.item(fila, 2).text()
        tipo        = self.ui_content.tableWidget_4.item(fila, 3).text()
        periodo     = self.ui_content.tableWidget_4.item(fila, 4).text()
        prioridad   = self.ui_content.tableWidget_4.item(fila, 5).text()

        # Seteamos los valores en los QLineEdit correspondientes
        self.ui_content.txt_reporte.setText(responsable)   # Responsable del reporte
        self.ui_content.txt_informe.setText(titulo)        # Título del informe
        self.ui_content.txt_destino.setText(destino)       # Destino de exportación
        self.ui_content.txt_tipo.setText(tipo)             # Tipo de documento
        self.ui_content.txt_periodo.setText(periodo)       # Periodo finalizado
        self.ui_content.txt_prioridad.setText(prioridad)   # Prioridad / Clasificación

    
    #botones

    def agregar_datos_reporte(self):
        # 1. Recoger datos respetando el orden de tus Labels
        responsable = self.ui_content.txt_reporte.text()   # RESPONSABLE DEL REPORTE
        titulo      = self.ui_content.txt_informe.text()   # TÍTULO DEL INFORME
        destino     = self.ui_content.txt_destino.text()   # DESTINO DE EXPORTACIÓN
        tipo        = self.ui_content.txt_tipo.text()      # TIPO DE DOCUMENTO
        periodo     = self.ui_content.txt_periodo.text()   # PERIODO FINALIZADO
        prioridad   = self.ui_content.txt_prioridad.text() # PRIORIDAD / CLASIFICACIÓN

        # 2. Validación básica
        if not responsable or not titulo:
            QMessageBox.warning(self, "Campos Obligatorios", "Complete Responsable y Título.")
            return

        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # 3. Query con el orden exacto de las columnas en tu DB
            query = """
            INSERT INTO reportes_sistema (
                responsable, titulo_informe, destino_exportacion, 
                tipo_documento, periodo_finalizado, prioridad_clasificacion
            ) VALUES (?, ?, ?, ?, ?, ?)
            """
            
            # El orden en la tupla debe ser IDÉNTICO al de la query arriba
            cursor.execute(query, (responsable, titulo, destino, tipo, periodo, prioridad))
            
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Éxito", f"Reporte '{titulo}' guardado.")
            
            # 4. IMPORTANTE: Usar el refresco correcto
            self.refrescar_todo_reportes() 
            self.limpiar_campos_registro()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error de DB: {e}")


    def eliminar_datos_reporte(self):
        fila = self.ui_content.tableWidget_4.currentRow()

        if fila == -1:
            QMessageBox.warning(self, "Atención", "Seleccione una fila en la tabla.")
            return

        # 1. Recuperar el ID (Asegúrate que sea la columna 0)
        item_id = self.ui_content.tableWidget_4.item(fila, 0)
        if not item_id:
            QMessageBox.critical(self, "Error", "No se pudo recuperar el ID de la celda.")
            return
            
        id_a_borrar = item_id.text()
        print(f"DEBUG: Intentando borrar id_reporte = {id_a_borrar}") # Mira esto en tu terminal

        respuesta = QMessageBox.question(self, "Confirmar", f"¿Eliminar reporte con ID {id_a_borrar}?",
                                        QMessageBox.Yes | QMessageBox.No)

        if respuesta == QMessageBox.Yes:
            try:
                conn = sqlite3.connect("ingenieria.db")
                cursor = conn.cursor()
                
                # 2. Ejecutar el borrado usando el nombre exacto de la columna
                cursor.execute("DELETE FROM reportes_sistema WHERE id_reporte = ?", (id_a_borrar,))
                
                # 3. Verificar si realmente hubo cambios
                if cursor.rowcount > 0:
                    conn.commit()
                    QMessageBox.information(self, "Éxito", "Dato borrado físicamente.")
                else:
                    # Si llega aquí, es porque el ID en la tabla no coincide con la DB
                    QMessageBox.warning(self, "Fallo", f"El ID '{id_a_borrar}' no se encontró en la base de datos.")
                
                conn.close()
                
                # 4. Refrescar la interfaz para que desaparezca la fila
                self.limpiar_campos_registro() # Debes crear esta función para vaciar los QLineEdit
            
                # 5. REFRESCO TOTAL DE LA PESTAÑA
                self.agregar_nuevo_reporte()  

            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error SQL", f"No se pudo eliminar: {e}")


    def actualizar_datos_reporte(self):
        # 1. Obtener la fila seleccionada para saber qué ID actualizar
        fila = self.ui_content.tableWidget_4.currentRow()
        
        if fila == -1:
            QMessageBox.warning(self, "Atención", "Seleccione un reporte de la tabla para editar.")
            return

        # 2. Obtener el ID de la columna 0 (oculta o visible)
        id_reporte = self.ui_content.tableWidget_4.item(fila, 0).text()

        # 3. Recoger los nuevos datos de los QLineEdit
        responsable = self.ui_content.txt_reporte.text()
        titulo      = self.ui_content.txt_informe.text()
        destino     = self.ui_content.txt_destino.text()
        tipo        = self.ui_content.txt_tipo.text()
        periodo     = self.ui_content.txt_periodo.text()
        prioridad   = self.ui_content.txt_prioridad.text()

        try:
            # 4. Ejecutar la actualización en SQL
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            query = """
            UPDATE reportes_sistema 
            SET responsable = ?, titulo_informe = ?, destino_exportacion = ?, 
                tipo_documento = ?, periodo_finalizado = ?, prioridad_clasificacion = ?
            WHERE id_reporte = ?
            """
            
            cursor.execute(query, (responsable, titulo, destino, tipo, periodo, prioridad, id_reporte))
            conn.commit()
            
            if cursor.rowcount > 0:
                QMessageBox.information(self, "Éxito", f"Reporte '{titulo}' actualizado correctamente.")
            conn.close()

            self.limpiar_campos_registro() # Debes crear esta función para vaciar los QLineEdit
            
            # 5. REFRESCO TOTAL DE LA PESTAÑA
            self.agregar_nuevo_reporte()  

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar: {e}")

    def actualizar_imagen_tipo(self, tipo_documento):
        # 1. Normalizar el nombre (ej: "pdf" -> "PDF")
        formato = str(tipo_documento).upper().strip()
        
        # 2. Ruta a la carpeta Mercado/Reporte
        ruta_imagen = f"Mercado/Reporte/{formato}.png"
        
        if os.path.exists(ruta_imagen):
            pixmap = QPixmap(ruta_imagen)
            
            # CORRECCIÓN: Quitamos 'aspectRatioMode=' y pasamos los argumentos directamente
            ancho = self.ui_content.label_28.width()
            alto = self.ui_content.label_28.height()
            
            pixmap_escalado = pixmap.scaled(ancho, alto, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            self.ui_content.label_28.setPixmap(pixmap_escalado)
            self.ui_content.label_28.setScaledContents(True)
        else:
            print(f"⚠️ No se encontró la imagen en: {ruta_imagen}")
            self.ui_content.label_28.clear()

    def seleccionar_reporte_tabla(self):
        fila = self.ui_content.tableWidget_4.currentRow()
        if fila != -1:
            # Extraer el tipo de documento (Columna 3 en la visualización)
            tipo = self.ui_content.tableWidget_4.item(fila, 3).text()
            
            # Actualizar los QLineEdit
            self.ui_content.txt_tipo.setText(tipo)
            
            # CAMBIO: Actualizar el icono en label_28
            self.actualizar_imagen_tipo(tipo)

    #grafica

    def graficar_gestion_mercado(self):
        try:
            # 1. Conexión y obtención de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("SELECT estado_servidor, COUNT(*) FROM gestion_mercado GROUP BY estado_servidor")
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                return

            estados = [str(row[0]) for row in datos]
            cantidades = [row[1] for row in datos]

            # 2. Configuración de la figura con FONDO NEGRO
            # Usamos un color hexadecimal oscuro para el facecolor
            fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
            
            # Color de fondo del recuadro exterior e interior
            fig.patch.set_facecolor('#121212') 
            ax.set_facecolor('#121212')

            # 3. Dibujar barras con colores neón
            colores_neon = ['#00e5ff', '#ffaa00', '#ff4444', '#ccff00']
            barras = ax.bar(estados, cantidades, color=colores_neon[:len(estados)])

            # 4. Personalización de Textos y Ejes para legibilidad
            ax.set_title("ESTADO DE SERVIDORES (MERCADO)", color='#00e5ff', fontsize=10, fontweight='bold')
            
            # Cambiar color de los numeritos de los ejes (Ticks)
            ax.tick_params(axis='x', colors='#00e5ff', labelsize=8)
            ax.tick_params(axis='y', colors='#00e5ff', labelsize=8)

            # Cambiar color de las líneas de los bordes (Spines)
            for spine in ax.spines.values():
                spine.set_edgecolor('#00e5ff')
                spine.set_linewidth(0.5)

            # 5. Integración en el frame_2
            if self.ui_content.frame_2.layout() is None:
                from PySide6.QtWidgets import QVBoxLayout
                self.ui_content.frame_2.setLayout(QVBoxLayout())

            # Limpiar el layout antes de añadir el nuevo canvas
            for i in reversed(range(self.ui_content.frame_2.layout().count())): 
                widget = self.ui_content.frame_2.layout().itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            canvas = FigureCanvas(fig)
            self.ui_content.frame_2.layout().addWidget(canvas)

        except Exception as e:
            print(f"Error al graficar mercado: {e}")

    def graficar_operaciones_mercado(self):
        try:
            # 1. Conexión y consulta usando los nombres que TÚ proporcionaste
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Agrupamos por 'operacion' (ej: Venta, Compra, etc.)
            # Si prefieres ver por método de pago, cambia 'operacion' por 'metodo'
            cursor.execute("SELECT capacidad_utilizada, COUNT(*) FROM operaciones_mercado GROUP BY capacidad_utilizada")
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                print("⚠️ No hay datos en operaciones_mercado.")
                return

            nombres = [str(row[0]) for row in datos]
            cantidades = [row[1] for row in datos]

            # 2. Configuración Dark Mode (Legibilidad Máxima)
            fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
            fig.patch.set_facecolor('#121212') 
            ax.set_facecolor('#121212')

            # 3. Barras Magenta Neón para frame_3
            ax.bar(nombres, cantidades, color='#ff00ff', edgecolor='#00e5ff', linewidth=1)

            # 4. Estilo de ejes y títulos
            ax.set_title("ANÁLISIS POR TIPO DE OPERACIÓN", color='#00e5ff', fontsize=10, fontweight='bold')
            ax.tick_params(axis='x', colors='#00e5ff', labelsize=8)
            ax.tick_params(axis='y', colors='#00e5ff', labelsize=8)
            
            for spine in ax.spines.values():
                spine.set_edgecolor('#00e5ff')

            # 5. Integración en el frame_3
            if self.ui_content.frame_3.layout() is None:
                from PySide6.QtWidgets import QVBoxLayout
                self.ui_content.frame_3.setLayout(QVBoxLayout())

            # Limpiar el layout para que no se encimen los gráficos
            for i in reversed(range(self.ui_content.frame_3.layout().count())): 
                widget = self.ui_content.frame_3.layout().itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            canvas = FigureCanvas(fig)
            self.ui_content.frame_3.layout().addWidget(canvas)

        except sqlite3.Error as e:
            print(f"❌ Error de SQL (Verifica los nombres): {e}")
        except Exception as e:
            print(f"❌ Error general: {e}")


    def graficar_analisis_mercado(self):
        try:
            # 1. Conexión y consulta de datos relevantes
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Seleccionamos Producto y Precio (o Volumen) para analizar tendencias
            cursor.execute("SELECT salud_global, metrica_pico_ms FROM analisis_mercado LIMIT 10")
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                print("⚠️ No hay datos en analisis_mercado.")
                return

            productos = [str(row[0]) for row in datos]
            precios = [float(row[1]) for row in datos]

            # 2. Configuración Estética (Fondo Negro / Estilo Neón)
            fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
            fig.patch.set_facecolor('#121212') 
            ax.set_facecolor('#121212')

            # 3. Gráfico de Línea Neón (Tendencia de Precios)
            # Usamos un color verde neón (#ccff00) para diferenciarlo de los otros frames
            ax.plot(productos, precios, color='#ccff00', marker='o', 
                    markersize=6, linewidth=2, markerfacecolor='#ffffff')
            
            # Rellenar el área bajo la línea para un efecto más moderno
            ax.fill_between(productos, precios, color='#ccff00', alpha=0.1)

            # 4. Personalización de Ejes y Títulos
            ax.set_title("Metricas de pico ms", color='#00e5ff', fontsize=10, fontweight='bold')
            ax.tick_params(axis='x', colors='#00e5ff', labelsize=7, rotation=20)
            ax.tick_params(axis='y', colors='#00e5ff', labelsize=8)
            
            for spine in ax.spines.values():
                spine.set_edgecolor('#00e5ff')

            # 5. Integración en el frame_4
            if self.ui_content.frame_4.layout() is None:
                from PySide6.QtWidgets import QVBoxLayout
                self.ui_content.frame_4.setLayout(QVBoxLayout())

            for i in reversed(range(self.ui_content.frame_4.layout().count())): 
                widget = self.ui_content.frame_4.layout().itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            canvas = FigureCanvas(fig)
            self.ui_content.frame_4.layout().addWidget(canvas)
            
            print("✅ Buena información: Gráfico de análisis de mercado generado con éxito.")

        except Exception as e:
            print(f"❌ Error en frame_4: {e}")

    def graficar_operaciones_sistema(self):
        try:
            # 1. Conexión usando el nombre de TABLA y COLUMNAS exactos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Agrupamos por 'tipo_operacion' y sumamos el 'monto'
            query = """
                SELECT tipo_documento, COUNT(tipo_documento) 
                FROM reportes_sistema 
                GROUP BY tipo_documento
            """
            cursor.execute(query)
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                print("⚠️ No hay datos en operaciones_sistema.")
                return

            operaciones = [str(row[0]) for row in datos]
            montos = [float(row[1]) for row in datos]

            # 2. Configuración Dark Mode (Fondo Negro #121212)
            fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
            fig.patch.set_facecolor('#121212') 
            ax.set_facecolor('#121212')

            # 3. Gráfico de Barras Neón (Color Naranja Neón para esta sección)
            ax.bar(operaciones, montos, color='#ffaa00', edgecolor='#00e5ff', linewidth=1)

            # 4. Personalización de Ejes y Títulos (Legibilidad)
            ax.set_title("VOLUMEN ECONÓMICO POR OPERACIÓN", color='#00e5ff', fontsize=10, fontweight='bold')
            ax.tick_params(axis='x', colors='#00e5ff', labelsize=8)
            ax.tick_params(axis='y', colors='#00e5ff', labelsize=8)
            
            # Bordes en color Cian Neón
            for spine in ax.spines.values():
                spine.set_edgecolor('#00e5ff')

            # 5. Insertar en el objeto 'frame'
            if self.ui_content.frame.layout() is None:
                from PySide6.QtWidgets import QVBoxLayout
                self.ui_content.frame.setLayout(QVBoxLayout())

            # Limpieza absoluta de gráficos anteriores
            for i in reversed(range(self.ui_content.frame.layout().count())): 
                widget = self.ui_content.frame.layout().itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            canvas = FigureCanvas(fig)
            self.ui_content.frame.layout().addWidget(canvas)
            
            print("✅ Gráfico de operaciones_sistema generado con éxito.")

        except Exception as e:
            print(f"❌ Error en el gráfico: {e}")

    def comparar_rendimiento_mercado(self):
        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # 1. Obtener Capacidad Utilizada de operaciones_mercado
            # Columna: nodo_destino y capacidad_utilizada
            cursor.execute("SELECT nodo_destino, AVG(capacidad_utilizada) FROM operaciones_mercado GROUP BY nodo_destino")
            datos_capacidad = dict(cursor.fetchall())
            
            # 2. Obtener Métrica Pico de analisis_mercado
            # Columna: id_nodo_cluster y metrica_pico_ms
            cursor.execute("SELECT id_nodo_cluster, AVG(metrica_pico_ms) FROM analisis_mercado GROUP BY id_nodo_cluster")
            datos_pico = dict(cursor.fetchall())
            conn.close()

            # Sincronizar nodos comunes para la comparativa
            nodos = sorted(list(set(datos_capacidad.keys()) & set(datos_pico.keys())))
            if not nodos:
                print("⚠️ No hay nodos coincidentes para comparar.")
                return

            usos = [datos_capacidad[n] for n in nodos]
            picos = [datos_pico[n] for n in nodos]

            # 3. Configuración Visual Estilo Neón Dark (#121212)
            fig, ax1 = plt.subplots(figsize=(5, 3), dpi=100)
            fig.patch.set_facecolor('#121212')
            ax1.set_facecolor('#121212')

            # Eje Izquierdo: Capacidad (Barras Naranja Neón)
            ax1.bar(nodos, usos, color='#ffaa00', alpha=0.7, label='Carga (%)')
            ax1.set_ylabel('Uso de Capacidad %', color='#ffaa00', fontsize=8)
            ax1.tick_params(axis='y', labelcolor='#ffaa00', labelsize=8)

            # Eje Derecho: Latencia/Pico (Línea Cian Neón)
            ax2 = ax1.twinx() 
            ax2.plot(nodos, picos, color='#00e5ff', marker='s', linewidth=2, label='Latencia (ms)')
            ax2.set_ylabel('Pico de Respuesta (ms)', color='#00e5ff', fontsize=8)
            ax2.tick_params(axis='y', labelcolor='#00e5ff', labelsize=8)

            # 4. Estética de Ejes y Título
            ax1.set_title("COMPARATIVA: CARGA VS LATENCIA POR NODO", color='#00e5ff', fontsize=9, fontweight='bold')
            ax1.tick_params(axis='x', colors='#00e5ff', labelsize=7, rotation=30)
            
            for spine in ax1.spines.values():
                spine.set_edgecolor('#444444')

            # 5. Integración en el frame_5
            if self.ui_content.frame_5.layout() is None:
                from PySide6.QtWidgets import QVBoxLayout
                self.ui_content.frame_5.setLayout(QVBoxLayout())

            for i in reversed(range(self.ui_content.frame_5.layout().count())): 
                widget = self.ui_content.frame_5.layout().itemAt(i).widget()
                if widget: widget.setParent(None)

            canvas = FigureCanvas(fig)
            self.ui_content.frame_5.layout().addWidget(canvas)
            
            print("✅ Buena información: Rendimiento comparado entre operaciones y análisis.")

        except Exception as e:
            print(f"❌ Error en comparativa de frame_5: {e}")

    def graficar_estado_salud_sistema(self):
        try:
            # 1. Conexión y consulta exacta
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Agrupamos por prioridad para ver la salud general
            cursor.execute("SELECT prioridad_clasificacion, COUNT(*) FROM reportes_sistema GROUP BY prioridad_clasificacion")
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                print("⚠️ No hay datos de salud en reportes_sistema.")
                return

            etiquetas = [str(row[0]) for row in datos]
            cantidades = [row[1] for row in datos]

            # 2. Configuración Estética (Fondo Negro / Estilo Neón)
            fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
            fig.patch.set_facecolor('#121212')
            ax.set_facecolor('#121212')

            # Definir colores neón según la prioridad
            # Mapeamos: Crítico -> Rojo, Óptimo -> Cian, Degradado -> Naranja
            colores_map = {
                'Crítico': '#ff4444',
                'Óptimo': '#00e5ff',
                'Degradado': '#ffaa00'
            }
            colores = [colores_map.get(e, '#ffffff') for e in etiquetas]

            # 3. Crear Gráfico de Pastel
            wedges, texts, autotexts = ax.pie(
                cantidades, 
                labels=etiquetas, 
                autopct='%1.1f%%',
                startangle=140,
                colors=colores,
                textprops={'color': "#00e5ff", 'fontsize': 8},
                pctdistance=0.85,
                explode=[0.05] * len(etiquetas) # Separar un poco los gajos
            )

            # Hacer el centro hueco para que parezca un "Donut Chart" moderno
            centre_circle = plt.Circle((0,0), 0.70, fc='#121212')
            fig.gca().add_artist(centre_circle)

            # 4. Título
            ax.set_title("SALUD GENERAL DEL SISTEMA", color='#00e5ff', fontsize=10, fontweight='bold')

            # 5. Integración en el frame_6
            if self.ui_content.frame_6.layout() is None:
                from PySide6.QtWidgets import QVBoxLayout
                self.ui_content.frame_6.setLayout(QVBoxLayout())

            for i in reversed(range(self.ui_content.frame_6.layout().count())): 
                widget = self.ui_content.frame_6.layout().itemAt(i).widget()
                if widget: widget.setParent(None)

            canvas = FigureCanvas(fig)
            self.ui_content.frame_6.layout().addWidget(canvas)
            
            print("✅ Dashboard completo: Salud del sistema graficada en frame_6.")

        except Exception as e:
            print(f"❌ Error en salud frame_6: {e}")
                
    
                
class CanvasAnalisis(FigureCanvas):
    def __init__(self, parent=None):
        # Configuramos la figura con fondo oscuro
        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.fig.patch.set_facecolor('none') # Transparente para ver el frame_9
        super().__init__(self.fig)