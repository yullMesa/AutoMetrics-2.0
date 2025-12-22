import sys
import os
# Importamos los componentes necesarios directamente del módulo QtWidgets
from PySide6.QtWidgets import (QApplication, QDialog, QMainWindow, QVBoxLayout, 
                               QToolBar,QTableWidget,QTabWidget,QStackedWidget,QPushButton,
                               QToolButton,QFileDialog,QMessageBox)

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtGui import QAction
from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui
import sqlite3
import pandas as pd
from matplotlib import pyplot as plt 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import recursos_rc

class InicioDialog(QDialog):
    """Clase para el menú de selección (QDialog)"""
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        ui_file = QFile("Inicio.ui")
        
        if not ui_file.open(QFile.ReadOnly):
            print(f"Error al abrir Inicio.ui")
            return
            
        self.ui = loader.load(ui_file)
        ui_file.close()

        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)
        layout.setContentsMargins(0, 0, 0, 0)
        self.resize(self.ui.size())
        # CONEXIÓN: Al presionar el botón OK del ButtonBox, abrimos Ingeniería
        # Suponiendo que usas el standard button box
        self.btn_ingenieria = self.ui.findChild(QToolButton, "toolIngenieria")
        if self.btn_ingenieria:
            self.btn_ingenieria.clicked.connect(self.abrir_ingenieria)
        else:
            print("No se encontró el botón 'toolIngenieria' en Inicio.ui")

       
        
    def abrir_ingenieria(self):
        # Creamos la ventana y la guardamos en una variable para que no muera
        self.nueva_ventana = IngenieriaWindow()
        self.nueva_ventana.show()
        
        # IMPORTANTE: Usamos close() en lugar de accept() para no disparar el main
        self.close()
        # Cerramos el diálogo y abrimos la ventana principal
        self.accept()

        

class IngenieriaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 1. CARGA DEL UI
        loader = QUiLoader()
        ui_file = QFile("Ingenieria.ui")
        
        if ui_file.open(QFile.ReadOnly):
            # CARGAMOS SIN 'self' para evitar el error de "already deleted"
            self.ui_content = loader.load(ui_file) 
            ui_file.close()
        else:
            print("Error al abrir Ingenieria.ui")
            return

        # 2. CONFIGURACIÓN DE LA INTERFAZ
        # Establecemos el widget principal del archivo UI como el centro de esta ventana
        self.setCentralWidget(self.ui_content)
        # 1. Tomamos el tamaño que definiste en Qt Designer
        diseno_size = self.ui_content.size() 

        # 2. Aplicamos ese tamaño a la ventana principal
        self.setFixedSize(diseno_size) 

        # O si quieres que se pueda estirar un poco pero empiece con ese tamaño:
        # self.resize(diseno_size)

        self.setWindowTitle("AutoMetrics 2.0 - Ingeniería")
        
        # Copiamos el estilo y la barra de menú
        self.setStyleSheet(self.ui_content.styleSheet())
        if self.ui_content.menuBar():
            self.setMenuBar(self.ui_content.menuBar())
            self.ui_content.menuBar().setVisible(True)

        # 3. NAVEGACIÓN (stackedWidget)
        # Buscamos el stackedWidget dentro del contenido cargado
        self.stack = self.ui_content.findChild(QStackedWidget, "stackedWidget")
        
        if self.stack:
            self.conectar_botones()
        
        if self.stack:
            print("DEBUG: StackedWidget listo para navegar.")
            self.conectar_botones()
        else:
            print("ERROR: No se encontró 'stackedWidget' en el árbol de objetos.")

    def conectar_botones(self):
        # Conexiones basadas en tu Object Inspector

        # Dashboard (Pestaña 0)
        btn_dash = self.ui_content.findChild(QAction, "actionDashboard")
        if btn_dash:
            btn_dash.triggered.connect(lambda: self.stack.setCurrentIndex(0))
        
        # Gestión de Requisito (Página 1)
        btn_req = self.ui_content.findChild(QAction, "actionCrud")
        if btn_req:
            btn_req.triggered.connect(lambda: self.stack.setCurrentIndex(1))
        
        # Dashboard (Pestaña 0)
        btn_dash = self.ui_content.findChild(QAction, "actionCRUD2")
        if btn_dash:
            btn_dash.triggered.connect(lambda: self.stack.setCurrentIndex(2))

        # Dashboard (Pestaña 0)
        btn_dash = self.ui_content.findChild(QAction, "actionCRUD_5")
        if btn_dash:
            btn_dash.triggered.connect(lambda: self.stack.setCurrentIndex(3))
        
        # Dashboard (Pestaña 0)
        btn_dash = self.ui_content.findChild(QAction, "actionCRUD_C")
        if btn_dash:
            btn_dash.triggered.connect(lambda: self.stack.setCurrentIndex(4))

        # Aseguramiento de Calidad (Página 5)
        btn_cal = self.ui_content.findChild(QAction, "actionCRUD_4")
        if btn_cal:
            btn_cal.triggered.connect(lambda: self.stack.setCurrentIndex(5))

        # BOTÓN VOLVER (actionInicio)
        btn_volver = self.ui_content.findChild(QAction, "actionInicio")
        if btn_volver:
            # Aquí podrías cerrar esta ventana y abrir InicioDialog
            btn_volver.triggered.connect(self.regresar_al_inicio)

        # ... (código de carga de UI anterior)
        
        # Referencias a los campos del formulario
        self.txt_id = self.ui_content.findChild(QtWidgets.QLineEdit, "lineEdit") # El ID
        self.txt_nombre = self.ui_content.findChild(QtWidgets.QLineEdit, "lineEdit_2") 
        self.txt_peticion = self.ui_content.findChild(QtWidgets.QLineEdit, "lineEdit_5")
        self.cbx_prioridad = self.ui_content.findChild(QtWidgets.QComboBox, "comboBox")
        self.tabla_requisitos = self.ui_content.findChild(QtWidgets.QTableWidget, "tableWidget")
        
        # Configurar opciones del ComboBox según tu guía
        self.cbx_prioridad.clear()
        self.cbx_prioridad.addItems(["Crítica", "Alta", "Media", "Baja"])
        
        # Conectar botón "Nuevo Requisito"
        self.btn_guardar = self.ui_content.findChild(QtWidgets.QPushButton, "pushButton_4")
        self.btn_guardar.clicked.connect(self.guardar_requisito)
        # Referencias a botones
        self.btn_editar = self.ui_content.findChild(QtWidgets.QPushButton, "pushButton_3")
        self.btn_eliminar = self.ui_content.findChild(QtWidgets.QPushButton, "btn_eliminar")
        self.btn_exportar = self.ui_content.findChild(QtWidgets.QPushButton, "pushButton")

        # Conexiones
        if self.btn_editar: self.btn_editar.clicked.connect(self.editar_requisito)
        if self.btn_eliminar: self.btn_eliminar.clicked.connect(self.eliminar_requisito)
        if self.btn_exportar: self.btn_exportar.clicked.connect(self.ejecutar_exportacion)

        self.tabla_requisitos.itemClicked.connect(self.rellenar_campos_desde_tabla)
        self.cargar_datos_tabla()
        # ... después de cargar la UI ...
        self.Fgestion = self.ui_content.findChild(QtWidgets.QFrame, "Fgestion")
        
        # IMPORTANTE: Fgestion debe tener un layout para contener el gráfico
        if self.Fgestion.layout() is None:
            layout = QtWidgets.QVBoxLayout(self.Fgestion)
            self.Fgestion.setLayout(layout)

        # Cargar el gráfico inicial
        self.graficar_prioridades()
        self.consultar_disenos()
        # Busca el widget por su nombre de objeto en el Designer
        self.TablaWire = self.findChild(QtWidgets.QTableWidget, "TablaWire")
        self.TablaWire.itemClicked.connect(self.seleccionar_diseno)

    def guardar_requisito(self):
        id_req = self.txt_id.text()
        nombre = self.txt_nombre.text()
        peticion = self.txt_peticion.text()
        prioridad = self.cbx_prioridad.currentText()

        # Validación de campo obligatorio
        if not id_req or not nombre:
            print("Error: El ID y el Nombre son obligatorios.")
            return

        # Guardar en SQLite
        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO requisitos (id, nombre, peticion, prioridad) 
                VALUES (?, ?, ?, ?)""", (id_req, nombre, peticion, prioridad))
            conn.commit()
            conn.close()
            print("Requisito guardado con éxito.")
            #self.limpiar_campos()
            # Limpiar los campos después de guardar
            self.txt_id.clear()
            self.txt_nombre.clear()
            self.txt_peticion.clear()
            # Aquí deberías llamar a una función para refrescar la QTableWidget

        except sqlite3.IntegrityError:
            print("Error: El ID ya existe.")

    def editar_requisito(self):
        id_val = self.txt_id.text()
        nom_val = self.txt_nombre.text()
        pet_val = self.txt_peticion.text()
        pri_val = self.cbx_prioridad.currentText()

        if not id_val:
            print("Error: Debes ingresar el ID para editar.")
            return

        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            # Actualizamos basándonos en el ID obligatorio
            cursor.execute("""
                UPDATE requisitos 
                SET nombre = ?, peticion = ?, prioridad = ? 
                WHERE id = ?""", (nom_val, pet_val, pri_val, id_val))
            
            if cursor.rowcount > 0:
                conn.commit()
                print(f"ID {id_val} actualizado correctamente.")
                self.cargar_datos_tabla() # Función para refrescar la QTableWidget
            else:
                print("Error: El ID no existe en la base de datos.")
            conn.close()
        except Exception as e:
            print(f"Error al editar: {e}")   

    def eliminar_requisito(self):
        id_val = self.txt_id.text()

        if not id_val:
            print("Error: Ingresa el ID del requisito a eliminar.")
            return

        # Mensaje de confirmación
        confirmar = QtWidgets.QMessageBox.question(self, "Eliminar", 
                    f"¿Seguro que deseas eliminar el ID {id_val}?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if confirmar == QtWidgets.QMessageBox.Yes:
            try:
                conn = sqlite3.connect("ingenieria.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM requisitos WHERE id = ?", (id_val,))
                conn.commit()
                conn.close()
                self.cargar_datos_tabla()
                self.limpiar_campos()
                print("Registro eliminado.")
            except Exception as e:
                print(f"Error al eliminar: {e}")
    


    def cargar_datos_tabla(self):
        try:
            # 1. Conexión a la base de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # 2. Seleccionamos los datos según las columnas de tu diseño
            cursor.execute("SELECT id, nombre, peticion, prioridad FROM requisitos")
            datos = cursor.fetchall()
            conn.close()

            # 3. Limpiar la tabla antes de cargar para no duplicar datos
            self.tabla_requisitos.setRowCount(0)
            
            # 4. Llenar la tabla fila por fila
            for fila_idx, fila_datos in enumerate(datos):
                self.tabla_requisitos.insertRow(fila_idx)
                for col_idx, valor in enumerate(fila_datos):
                    # Creamos el ítem para la celda
                    item = QtWidgets.QTableWidgetItem(str(valor))
                    # Insertamos el dato en la posición correspondiente
                    self.tabla_requisitos.setItem(fila_idx, col_idx, item)
                    
            print("Datos cargados en la tabla con éxito.")
            
        except Exception as e:
            print(f"Error al cargar los datos en el QTableWidget: {e}")
    

    def rellenar_campos_desde_tabla(self):
        fila = self.tabla_requisitos.currentRow()
        self.txt_id.setText(self.tabla_requisitos.item(fila, 0).text())
        self.txt_nombre.setText(self.tabla_requisitos.item(fila, 1).text())
        self.txt_peticion.setText(self.tabla_requisitos.item(fila, 2).text())
        # Para el combo, buscamos el índice del texto
        index = self.cbx_prioridad.findText(self.tabla_requisitos.item(fila, 3).text())
        self.cbx_prioridad.setCurrentIndex(index)


    def abrir_conversor_exportar(self):
        # Abrimos el buscador para seleccionar el archivo CSV
        archivo_csv, _ = QFileDialog.getOpenFileName(
            self, 
            "Seleccionar archivo CSV para convertir", 
            "", 
            "Archivos CSV (*.csv)"
        )
        
        if archivo_csv:
            try:
                # Importamos la lógica de tu otro archivo
                from Exportar import transformar_a_excel
                
                # Ejecutamos la transformación
                ruta_final = transformar_a_excel(archivo_csv)
                
                QMessageBox.information(self, "Éxito", f"Archivo convertido y guardado en:\n{ruta_final}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo convertir el archivo: {e}")

        # La función que llama al script externo:
    def ejecutar_exportacion(self):
        try:
            import Exportar
            # Llama a la función que abre el explorador de archivos
            Exportar.seleccionar_y_convertir() 
        except Exception as e:
            print(f"Error al llamar al modulo de exportación: {e}")

    def regresar_al_inicio(self):
        print("Regresando al menú de selección...")
        
        # Creamos la ventana de inicio
        self.ventana_inicio = InicioDialog()
        
        # Le damos un tamaño manual si sale muy pequeña
        self.ventana_inicio.size()
        
        self.ventana_inicio.show()
        
        # Cerramos ingeniería SOLO después de mostrar inicio
        self.close()

    def graficar_prioridades(self):
        try:
            # 1. Obtener los datos para el análisis
            conn = sqlite3.connect("ingenieria.db")
            df = pd.read_sql_query("SELECT prioridad FROM requisitos", conn)
            conn.close()

            if df.empty:
                print("No hay datos para graficar.")
                return

            # 2. Procesar los datos (Conteo de cada prioridad)
            conteo = df['prioridad'].value_counts()
            etiquetas = conteo.index
            valores = conteo.values

            # 3. Crear la figura de Matplotlib con estética Dark
            fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
            fig.patch.set_facecolor('#1e1e1e') # Fondo oscuro como tu App
            ax.set_facecolor('#1e1e1e')
            
            # Colores cian y variantes para tu diseño
            colores = ['#00e5ff', '#00b8d4', '#0091ea', '#01579b']
            
            # Crear gráfico de pastel (Pie Chart)
            wedges, texts, autotexts = ax.pie(
                valores, labels=etiquetas, autopct='%1.1f%%', 
                startangle=90, colors=colores, textprops={'color':"w"}
            )
            ax.set_title("Distribución de Prioridades", color='#00e5ff', fontsize=12, fontweight='bold')

            # 4. Insertar el gráfico en el frame Fgestion
            # Limpiamos el frame por si ya hay un gráfico anterior
            for i in reversed(range(self.Fgestion.layout().count())): 
                self.Fgestion.layout().itemAt(i).widget().setParent(None)

            canvas = FigureCanvas(fig)
            self.Fgestion.layout().addWidget(canvas)
            canvas.draw()

        except Exception as e:
            print(f"Error al generar gráfico: {e}")

    def guardar_diseno(self):
        # 1. Recoger datos de los lineEdit específicos de Diseño
        # Ajusta los nombres 'lineEdit_X' según tu Object Inspector
        tabla_val = self.ui.lineEdit_TABLA.text() 
        id_val = self.ui.lineEdit_ID_DISENO.text()
        componente_val = self.ui.lineEdit_COMPONENTE.text()
        estado_val = self.ui.lineEdit_ESTADO.text()
        version_val = self.ui.lineEdit_VERSION.text()

        # Validación básica de campos obligatorios
        if not id_val or not componente_val:
            QtWidgets.QMessageBox.warning(self, "Error", "El ID y Componente son obligatorios.")
            return

        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # 2. Insertar en la tabla 'diseno'
            query = """INSERT INTO diseno (id, tabla, componente, estado, version) 
                    VALUES (?, ?, ?, ?, ?)"""
            cursor.execute(query, (id_val, tabla_val, componente_val, estado_val, version_val))
            
            conn.commit()
            conn.close()
            
            # 3. Actualizar la vista y limpiar
            self.consultar_disenos() 
            self.limpiar_campos_diseno()
            QtWidgets.QMessageBox.information(self, "Éxito", "Diseño guardado correctamente.")
            
        except sqlite3.IntegrityError:
            QtWidgets.QMessageBox.critical(self, "Error", "El ID ya existe en la base de datos.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error crítico: {e}")

    def consultar_disenos(self):
        try:
            # Usamos el nombre exacto que aparece en tu Object Inspector
            # Si usas un cargador de UI (ui_content o self.ui), agrégalo antes:
            # tabla = self.ui_content.findChild(QtWidgets.QTableWidget, "TablaWire")
            
            # PRUEBA ESTA LÍNEA (la más segura para tu error):
            tabla = self.findChild(QtWidgets.QTableWidget, "TablaWire") 
            
            if tabla is None:
                print("ERROR: El sistema aún no reconoce 'TablaWire'. ¿Recompilaste el .ui?")
                return

            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("SELECT tabla, id, componente, estado, version FROM diseno")
            datos = cursor.fetchall()
            conn.close()

            tabla.setRowCount(0)
            for row_number, row_data in enumerate(datos):
                tabla.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    item = QtWidgets.QTableWidgetItem(str(data))
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    tabla.setItem(row_number, column_number, item)
            
            print("ÉXITO: Datos cargados en TablaWire.")

        except Exception as e:
            print(f"Error fatal: {e}")


    def seleccionar_diseno(self):
        # 1. Localizar la tabla y el frame_4
        tabla = self.findChild(QtWidgets.QTableWidget, "TablaWire")
        frame_destino = self.findChild(QtWidgets.QFrame, "frame_4")
        fila = tabla.currentRow()
        
        if fila != -1:
            # Extraer el nombre del componente (Columna 2)
            c_val = tabla.item(fila, 2).text()
            
            # --- LÓGICA DE IMAGEN EN FRAME ---
            # 2. Verificar si ya existe un label de imagen dentro del frame
            # Si no existe, lo creamos dinámicamente
            self.label_imagen = frame_destino.findChild(QtWidgets.QLabel, "label_dinamico")
            if not self.label_imagen:
                self.label_imagen = QtWidgets.QLabel(frame_destino)
                self.label_imagen.setObjectName("label_dinamico")
                # Hacemos que el label use todo el espacio del frame
                self.label_imagen.setGeometry(0, 0, frame_destino.width(), frame_destino.height())
                self.label_imagen.setAlignment(QtCore.Qt.AlignCenter)

            # 3. Cargar la imagen desde la carpeta WireFrame
            ruta_foto = os.path.join("WireFrame", f"{c_val}.png")
            
            if os.path.exists(ruta_foto):
                pixmap = QtGui.QPixmap(ruta_foto)
                # Escalamos la imagen para que quepa en el frame sin deformarse
                self.label_imagen.setPixmap(pixmap.scaled(
                    frame_destino.size(), 
                    QtCore.Qt.KeepAspectRatio, 
                    QtCore.Qt.SmoothTransformation
                ))
                self.label_imagen.show()
            else:
                self.label_imagen.setText(f"No se encontró:\n{c_val}.png")
                print(f"Error: El archivo {ruta_foto} no existe.")

            


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Solo iniciamos la primera ventana
    inicio = InicioDialog()
    inicio.show()
    
    # El loop de la app (exec()) mantiene todo vivo mientras haya ventanas abiertas
    sys.exit(app.exec())