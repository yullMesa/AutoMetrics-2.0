import os
import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QTreeWidgetItem,QTableWidgetItem, QAbstractItemView,QHeaderView,QVBoxLayout
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
    