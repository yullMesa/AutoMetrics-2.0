import sys
import os
# Importamos los componentes necesarios directamente del módulo QtWidgets
from PySide6.QtWidgets import (QApplication, QDialog, QMainWindow, QVBoxLayout, 
                               QToolBar,QTableWidget,QTabWidget,QStackedWidget,QPushButton,
                               QToolButton,QFileDialog,QMessageBox)

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtGui import QAction,QPixmap
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
        
        self.conectar_botonesD()
        self.actualizar_grafica_estados()
        self.conectar_botonesM()
        # Agrégalo justo debajo de donde cargas la UI
        self.tableWidget_3 = self.findChild(QtWidgets.QTableWidget, "tableWidget_3")
        self.consultar_materiales()
        # En lugar de la línea 112 que falla
        # 1. Buscamos el botón del menú superior
        self.btn_materiales = self.findChild(QtWidgets.QPushButton, "pushButton_3")

        if self.btn_materiales:
            # Conectamos el botón para que ejecute la consulta al hacer clic
            self.btn_materiales.clicked.connect(self.consultar_materiales)
            print("DEBUG: Conexión establecida con el botón de materiales.")
        

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

        tabla = self.findChild(QtWidgets.QTableWidget, "TablaWire")
        label_foto = self.findChild(QtWidgets.QLabel, "image") # El nuevo nombre
        fila = tabla.currentRow()
        
        if fila != -1:
            # 1. Extraer datos (Columnas: 0=Tabla, 1=ID, 2=Componente...)
            t_val = tabla.item(fila, 0).text()
            i_val = tabla.item(fila, 1).text()
            c_val = tabla.item(fila, 2).text()
            e_val = tabla.item(fila, 3).text()
            v_val = tabla.item(fila, 4).text()

            # 2. Rellenar los campos de texto
            self.findChild(QtWidgets.QLineEdit, "lineEdit_TABLA").setText(t_val)
            self.findChild(QtWidgets.QLineEdit, "lineEdit_ID_DISENO").setText(i_val)
            self.findChild(QtWidgets.QLineEdit, "lineEdit_COMPONENTE").setText(c_val)
            self.findChild(QtWidgets.QLineEdit, "lineEdit_ESTADO").setText(e_val)
            self.findChild(QtWidgets.QLineEdit, "lineEdit_VERSION").setText(v_val)

            # 3. Lógica de Imagen
            ruta_foto = os.path.join("WireFrame", f"{c_val}.png")
            
            if label_foto:
                if os.path.exists(ruta_foto):
                    pixmap = QtGui.QPixmap(ruta_foto)
                    # Ajustar imagen al tamaño del label
                    label_foto.setPixmap(pixmap.scaled(
                        label_foto.size(), 
                        QtCore.Qt.KeepAspectRatio, 
                        QtCore.Qt.SmoothTransformation
                    ))
                else:
                    label_foto.clear()
                    label_foto.setText(f"No existe imagen para: {c_val}")

    def actualizar_registro(self):
       
        # 1. Capturar TODOS los campos (excepto ID que solo lo usamos para buscar)
        # Forzamos a string para evitar el error de tipo de dato que descubriste
        id_val = str(self.findChild(QtWidgets.QLineEdit, "lineEdit_ID_DISENO").text()).strip()
        tabla_val = str(self.findChild(QtWidgets.QLineEdit, "lineEdit_TABLA").text()).strip()
        comp_val = str(self.findChild(QtWidgets.QLineEdit, "lineEdit_COMPONENTE").text()).strip()
        est_val = str(self.findChild(QtWidgets.QLineEdit, "lineEdit_ESTADO").text()).strip()
        ver_val = str(self.findChild(QtWidgets.QLineEdit, "lineEdit_VERSION").text()).strip()

        if not id_val:
            print("Error: Selecciona un registro de la tabla para obtener su ID.")
            return

        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # 2. SQL ampliado: Ahora actualizamos 4 columnas
            # El ID se queda en el WHERE porque es lo que NO cambia.
            query = """UPDATE diseno 
                    SET tabla = ?, componente = ?, estado = ?, version = ? 
                    WHERE id = ?"""
            
            # El orden de los datos debe coincidir exactamente con los '?'
            cursor.execute(query, (tabla_val, comp_val, est_val, ver_val, id_val))
            
            if cursor.rowcount > 0:
                conn.commit()
                print(f"ÉXITO: Se actualizó el diseño {id_val}. (Componente ahora es: {comp_val})")
            else:
                print(f"AVISO: No se encontró el ID '{id_val}' para actualizar.")
                
            conn.close()
            
            # 3. Refrescar tabla y datos visuales
            self.consultar_disenos()
            
        except Exception as e:
            print(f"Error al actualizar: {e}")



    def conectar_botonesD(self):
        # Localizar botones por su nombre de objeto
        btn_guardar = self.findChild(QtWidgets.QPushButton, "pushButton_7") # Nuevo Diseño
        btn_actualizar = self.findChild(QtWidgets.QPushButton, "pushButton_6") # Actualizar/Refrescar
        btn_eliminar = self.findChild(QtWidgets.QPushButton, "btn_eliminar_2") # Eliminar
        btn_exportar = self.findChild(QtWidgets.QPushButton, "pushButton_2") # Exportar (ajusta el nombre si varía)
        tabla = self.findChild(QtWidgets.QTableWidget, "TablaWire")
        self.consultar_disenos()
        # Conectar las funciones

        if btn_guardar:
            btn_guardar.clicked.connect(self.guardar_nuevo_wireframe)
        if btn_eliminar:
            btn_eliminar.clicked.connect(self.eliminar_registro)
        if tabla:
            tabla.itemClicked.connect(self.seleccionar_diseno)
        if btn_actualizar:
            btn_actualizar.clicked.connect(self.actualizar_registro)
        # CONEXIÓN DEL BOTÓN EXPORTAR
        if btn_exportar:
            btn_exportar.clicked.connect(self.ejecutar_exportacion)



    def eliminar_registro(self):
        # Obtener el ID del campo de texto
        id_val = self.findChild(QtWidgets.QLineEdit, "lineEdit_ID_DISENO").text()
        
        if not id_val:
            print("Error: Selecciona un diseño de la tabla para eliminar.")
            return

        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            # USAR 'id' EN LUGAR DE 'id_diseno'
            cursor.execute("DELETE FROM diseno WHERE id = ?", (id_val,))
            conn.commit()
            conn.close()
            
            self.consultar_disenos() # Refresca la tabla visual
            print(f"ÉXITO: Registro {id_val} eliminado.")
            
            # Limpiar la imagen y los campos
            self.findChild(QtWidgets.QLabel, "image").clear()
        except Exception as e:
            print(f"Error al eliminar: {e}")

    
    def nuevo_diseno(self):
        # 1. Localizar y limpiar los LineEdits
        campos = [
            "lineEdit_TABLA", 
            "lineEdit_ID_DISENO", 
            "lineEdit_COMPONENTE", 
            "lineEdit_ESTADO", 
            "lineEdit_VERSION"
        ]
        
        for nombre in campos:
            widget = self.findChild(QtWidgets.QLineEdit, nombre)
            if widget:
                widget.clear() # Borra el texto actual

        # 2. Limpiar la imagen del Label
        label_foto = self.findChild(QtWidgets.QLabel, "image")
        if label_foto:
            label_foto.clear()
            label_foto.setText("Esperando nuevo diseño...")
        
        # 3. Poner el foco en el primer campo para empezar a escribir
        le_tabla = self.findChild(QtWidgets.QLineEdit, "lineEdit_TABLA")
        if le_tabla:
            le_tabla.setFocus()
        
        print("Formulario listo para un nuevo registro.")

    
    def guardar_nuevo_registro(self):
        # 1. Obtener los valores de los lineEdit
        t_val = self.findChild(QtWidgets.QLineEdit, "lineEdit_TABLA").text()
        i_val = self.findChild(QtWidgets.QLineEdit, "lineEdit_ID_DISENO").text()
        c_val = self.findChild(QtWidgets.QLineEdit, "lineEdit_COMPONENTE").text()
        e_val = self.findChild(QtWidgets.QLineEdit, "lineEdit_ESTADO").text()
        v_val = self.findChild(QtWidgets.QLineEdit, "lineEdit_VERSION").text()

        if not i_val: # El ID es obligatorio
            print("Error: El campo ID es necesario para guardar.")
            return

        try:
            # 2. Conectar e Insertar en la DB
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Ajusta los nombres de las columnas según tu tabla 'diseno'
            query = """INSERT INTO diseno (tabla, id_diseno, componente, estado, version) 
                    VALUES (?, ?, ?, ?, ?)"""
            cursor.execute(query, (t_val, i_val, c_val, e_val, v_val))
            
            conn.commit()
            conn.close()
            
            # 3. Refrescar la tabla visual para ver el nuevo dato
            self.consultar_disenos()
            print(f"ÉXITO: Registro {i_val} guardado correctamente.")
            
        except Exception as e:
            print(f"Error al guardar: {e}")

    
    def guardar_nuevo_wireframe(self):
        # 1. Obtener datos de los campos de texto
        t_val = self.findChild(QtWidgets.QLineEdit, "lineEdit_TABLA").text()
        i_val = self.findChild(QtWidgets.QLineEdit, "lineEdit_ID_DISENO").text()
        c_val = self.findChild(QtWidgets.QLineEdit, "lineEdit_COMPONENTE").text()
        e_val = self.findChild(QtWidgets.QLineEdit, "lineEdit_ESTADO").text()
        v_val = self.findChild(QtWidgets.QLineEdit, "lineEdit_VERSION").text()

        if not i_val:
            print("Error: El ID es obligatorio para guardar.")
            return

        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            query = "INSERT INTO diseno (tabla, id, componente, estado, version) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(query, (t_val, i_val, c_val, e_val, v_val))
            conn.commit()
            conn.close()
            
            self.consultar_disenos()
            print("ÉXITO: Registro guardado.")
        except sqlite3.IntegrityError:
            # Esto captura específicamente el error de ID repetido
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "ID Duplicado", f"El ID '{i_val}' ya existe. Si quieres modificarlo, usa el botón 'Actualizar'.")
        except Exception as e:
            print(f"Error: {e}")
    
    
    def actualizar_grafica_estados(self):

        self.Fdiseno = self.findChild(QtWidgets.QFrame, "Fdiseno")
    
        if self.Fdiseno is None:
            print("Error: No se encontró el QFrame llamado 'Fdiseno' en la interfaz.")
            return
        try:
            # 1. Obtener datos de la base de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("SELECT estado, COUNT(*) FROM diseno GROUP BY estado")
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                return

            estados = [row[0] for row in datos]
            cantidades = [row[1] for row in datos]

            # 2. Configurar la gráfica de Matplotlib
            fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
            fig.patch.set_facecolor('#1e1e1e') # Color de fondo oscuro para combinar
            
            colores = ['#005599', '#00aaff', '#00cccc', '#0088cc'] # Paleta azul
            
            ax.pie(cantidades, labels=estados, autopct='%1.1f%%', startangle=90, 
                textprops={'color':"w"}, colors=colores)
            ax.set_title("Distribución de Estados", color='cyan', fontweight='bold')

            # 3. Insertar la gráfica en el QFrame 'Fdiseno'
            # Limpiamos el layout anterior si existe
            if self.Fdiseno.layout() is not None:
                # Eliminar widgets antiguos para que no se encimen
                while self.Fdiseno.layout().count():
                    item = self.Fdiseno.layout().takeAt(0)
                    widget = item.widget()
                    if widget: widget.deleteLater()
            else:
                layout = QtWidgets.QVBoxLayout(self.Fdiseno)
                self.Fdiseno.setLayout(layout)

            canvas = FigureCanvas(fig)
            self.Fdiseno.layout().addWidget(canvas)
            
        except Exception as e:
            print(f"Error al generar gráfica: {e}")


    def consultar_materiales(self):
        
        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # 1. Consulta SQL
            cursor.execute("SELECT id_material, descripcion, cantidad, proveedor, unidad, costo_unidad FROM materiales")
            datos = cursor.fetchall()
            # Justo después de: datos = cursor.fetchall()
            print(f"DEBUG: Se encontraron {len(datos)} materiales en la base de datos.")
            
            # 2. Configuración de la tabla
            self.tableWidget_3.setColumnCount(6) 
            self.tableWidget_3.setHorizontalHeaderLabels([
                "ID", "DESCRIPCIÓN", "CANTIDAD", "PROVEEDOR", "UNIDAD", "COSTO UNITARIO"
            ])
            self.tableWidget_3.setColumnCount(6)
            self.tableWidget_3.setRowCount(0)
            
            # 3. Llenado de datos
            for row_number, row_data in enumerate(datos):
                self.tableWidget_3.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    # Convertimos a string por seguridad para evitar errores de tipo
                    item = QtWidgets.QTableWidgetItem(str(data))
                    self.tableWidget_3.setItem(row_number, column_number, item)
            
            # 4. Ajuste visual (Para que ocupe todo el ancho)
            header = self.tableWidget_3.horizontalHeader()
            header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            
            conn.close()
            # Al final de consultar_materiales, después de conn.close()
            self.tableWidget_3.viewport().update()
            print("ÉXITO: Lista de materiales cargada en tableWidget_3.")
            
        except Exception as e:
            print(f"Error al cargar materiales: {e}")
        self.graficar_materiales_proveedor()

    def conectar_materiales(self):
        # Localizamos los botones por los nombres de tu lista
        btn_guardar = self.findChild(QtWidgets.QPushButton, "pushButton_15")
        btn_actualizar = self.findChild(QtWidgets.QPushButton, "pushButton_5")
        btn_eliminar = self.findChild(QtWidgets.QPushButton, "btn_eliminar_3")
        
        # Conexión a las funciones CRUD
        if btn_guardar:
            btn_guardar.clicked.connect(self.guardar_material)
        if btn_actualizar:
            btn_actualizar.clicked.connect(self.actualizar_material)
        if btn_eliminar:
            btn_eliminar.clicked.connect(self.eliminar_material)
            
        # Conectar la tabla para que al tocar un material se llenen los campos
        self.tableWidget_3 = self.findChild(QtWidgets.QTableWidget, "tableWidget_3")
        if self.tableWidget_3:
            self.tableWidget_3.itemClicked.connect(self.seleccionar_material)

    def seleccionar_material(self):
        fila = self.tableWidget_3.currentRow()
        # Usamos los nombres de tu lista de objetos
        self.findChild(QtWidgets.QLineEdit, "lineEdit_6").setText(self.tableWidget_3.item(fila, 0).text()) # ID
        self.findChild(QtWidgets.QLineEdit, "lineEdit_8").setText(self.tableWidget_3.item(fila, 1).text()) # Desc
        self.findChild(QtWidgets.QLineEdit, "lineEdit_9").setText(self.tableWidget_3.item(fila, 2).text()) # Cant
        self.findChild(QtWidgets.QLineEdit, "lineEdit_10").setText(self.tableWidget_3.item(fila, 3).text())  # Prov
        self.findChild(QtWidgets.QLineEdit, "lineEdit_11").setText(self.tableWidget_3.item(fila, 4).text())  # Unid
        self.findChild(QtWidgets.QLineEdit, "lineEdit_12").setText(self.tableWidget_3.item(fila, 5).text())  # Costo
    
            
    def guardar_nuevo_material(self):
        print("DEBUG: El botón Añadir fue presionado")
        # 1. Recoger datos de los lineEdits según tu árbol de objetos
        id_m = self.findChild(QtWidgets.QLineEdit, "lineEdit_10").text()
        desc = self.findChild(QtWidgets.QLineEdit, "lineEdit_8").text()
        cant = self.findChild(QtWidgets.QLineEdit, "lineEdit_9").text()
        prov = self.findChild(QtWidgets.QLineEdit, "lineEdit_10").text()
        unid = self.findChild(QtWidgets.QLineEdit, "lineEdit_11").text()
        cost = self.findChild(QtWidgets.QLineEdit, "lineEdit_12").text()

        # Validación básica
        if not id_m or not desc:
            print("Error: El ID y la Descripción son obligatorios.")
            return

        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Insertar en la tabla 'materiales' que creamos en SQL
            query = """INSERT INTO materiales (id_material, descripcion, cantidad, proveedor, unidad, costo_unidad) 
                    VALUES (?, ?, ?, ?, ?, ?)"""
            cursor.execute(query, (id_m, desc, cant, prov, unid, cost))
            
            conn.commit()
            conn.close()
            
            print(f"ÉXITO: Material {id_m} guardado correctamente.")
            
            # Limpiar campos y refrescar la tabla
            self.consultar_materiales() 
            self.limpiar_campos_materiales()
            
        except Exception as e:
            print(f"Error al guardar material: {e}")


    def limpiar_campos_materiales(self):
        nombres = ["lineEdit_10", "lineEdit_11", "lineEdit_12", "lineEdit_6", "lineEdit_8", "lineEdit_9"]
        for nombre in nombres:
            widget = self.findChild(QtWidgets.QLineEdit, nombre)
            if widget:
                widget.clear()

    def eliminar_material(self):
        # 1. Obtener el ID del material a eliminar
        id_m = self.txt_id_mat.text()

        if not id_m:
            print("Error: Debes seleccionar un material o ingresar su ID para eliminarlo.")
            return

        # 2. Confirmación de seguridad
        mensaje = QtWidgets.QMessageBox.question(self, "Confirmar", 
            f"¿Estás seguro de que deseas eliminar el material {id_m}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if mensaje == QtWidgets.QMessageBox.Yes:
            try:
                conn = sqlite3.connect("ingenieria.db")
                cursor = conn.cursor()
                
                # Ejecutamos la eliminación en la tabla SQL
                cursor.execute("DELETE FROM materiales WHERE id_material = ?", (id_m,))
                
                conn.commit()
                conn.close()
                
                print(f"ÉXITO: Material {id_m} eliminado.")
                
                # Limpiar la interfaz y actualizar la tabla
                self.consultar_materiales()
                self.limpiar_campos_materiales()
                
            except Exception as e:
                print(f"Error al eliminar material: {e}")

    def actualizar_material(self):
        # 1. Recoger los datos actuales de los cuadros de texto
        id_m = self.txt_id_mat.text()
        desc = self.txt_desc_mat.text()
        cant = self.txt_cant_mat.text()
        prov = self.txt_prov_mat.text()
        unid = self.txt_unid_mat.text()
        cost = self.txt_cost_mat.text()

        if not id_m:
            print("Error: Selecciona un material de la tabla para actualizar.")
            return

        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # 2. Sentencia SQL UPDATE
            query = """UPDATE materiales 
                    SET descripcion = ?, cantidad = ?, proveedor = ?, unidad = ?, costo_unidad = ? 
                    WHERE id_material = ?"""
            
            cursor.execute(query, (desc, cant, prov, unid, cost, id_m))
            
            conn.commit()
            conn.close()
            
            print(f"ÉXITO: Material {id_m} actualizado correctamente.")
            
            # 3. Refrescar la tabla para ver los cambios
            self.consultar_materiales()
            
        except Exception as e:
            print(f"Error al actualizar: {e}")

    def conectar_botonesM(self):
        # 1. Vincular los LineEdits (Entradas de texto)
        self.txt_id_mat = self.findChild(QtWidgets.QLineEdit, "lineEdit_6")
        self.txt_desc_mat = self.findChild(QtWidgets.QLineEdit, "lineEdit_8")
        self.txt_cant_mat = self.findChild(QtWidgets.QLineEdit, "lineEdit_9")
        self.txt_prov_mat = self.findChild(QtWidgets.QLineEdit, "lineEdit_10")
        self.txt_unid_mat = self.findChild(QtWidgets.QLineEdit, "lineEdit_11")
        self.txt_cost_mat = self.findChild(QtWidgets.QLineEdit, "lineEdit_12")
        self.btn_exportar = self.findChild(QtWidgets.QPushButton, "pushButton_5")

        # 2. Vincular y conectar los Botones
        btn_anadir = self.findChild(QtWidgets.QPushButton, "pushButton_9")
        btn_actualizar = self.findChild(QtWidgets.QPushButton, "pushButton_15")
        btn_eliminar = self.findChild(QtWidgets.QPushButton, "btn_eliminar_3")

        if btn_anadir:
            btn_anadir.clicked.connect(self.guardar_nuevo_material)
        if btn_actualizar:
            btn_actualizar.clicked.connect(self.consultar_materiales)
        if btn_eliminar:
            btn_eliminar.clicked.connect(self.eliminar_material)
        if self.btn_exportar:
            self.btn_exportar.clicked.connect(self.ejecutar_exportacion)

        # 3. Vincular y conectar la Tabla
        self.tableWidget_3 = self.findChild(QtWidgets.QTableWidget, "tableWidget_3")
        if self.tableWidget_3:
            self.tableWidget_3.itemClicked.connect(self.seleccionar_material)

        btn_actualizar = self.findChild(QtWidgets.QPushButton, "pushButton_15")
        if btn_actualizar:
            # Limpiamos conexiones previas para evitar que se ejecute doble
            try: btn_actualizar.clicked.disconnect()
            except: pass
            
            btn_actualizar.clicked.connect(self.actualizar_material)

    def seleccionar_material(self):
        fila = self.tableWidget_3.currentRow()
        if fila != -1:
            # Llenamos los lineEdits con lo que hay en la tabla
            self.txt_id_mat.setText(self.tableWidget_3.item(fila, 0).text())
            self.txt_desc_mat.setText(self.tableWidget_3.item(fila, 1).text())
            self.txt_cant_mat.setText(self.tableWidget_3.item(fila, 2).text())
            self.txt_prov_mat.setText(self.tableWidget_3.item(fila, 3).text())
            self.txt_unid_mat.setText(self.tableWidget_3.item(fila, 4).text())
            self.txt_cost_mat.setText(self.tableWidget_3.item(fila, 5).text())

            # 1. Obtener el ID de la primera columna
            id_m = self.tableWidget_3.item(fila, 0).text()
            
            # 2. Llenar los campos de texto
            self.findChild(QtWidgets.QLineEdit, "lineEdit_6").setText(id_m)
            self.findChild(QtWidgets.QLineEdit, "lineEdit_8").setText(self.tableWidget_3.item(fila, 1).text())
            self.findChild(QtWidgets.QLineEdit, "lineEdit_9").setText(self.tableWidget_3.item(fila, 2).text())
            self.findChild(QtWidgets.QLineEdit, "lineEdit_10").setText(self.tableWidget_3.item(fila, 3).text())
            self.findChild(QtWidgets.QLineEdit, "lineEdit_11").setText(self.tableWidget_3.item(fila, 4).text())
            self.findChild(QtWidgets.QLineEdit, "lineEdit_12").setText(self.tableWidget_3.item(fila, 5).text())

            # 3. Lógica para cargar la imagen en label_7
            self.mostrar_imagen_material(id_m)


    def mostrar_imagen_material(self, id_material):
        # 1. Definimos las posibles rutas (Prioridad PNG según tus archivos)
        ruta_png = f"Materiales/{id_material}.png"
        ruta_jpg = f"Materiales/{id_material}.jpg"
        
        # Seleccionamos la que exista físicamente
        ruta_final = None
        if os.path.exists(ruta_png):
            ruta_final = ruta_png
        elif os.path.exists(ruta_jpg):
            ruta_final = ruta_jpg

        # 2. Buscamos el label_7
        label_foto = self.findChild(QtWidgets.QLabel, "label_7")
        
        if label_foto:
            if ruta_final:
                pixmap = QPixmap(ruta_final)
                if not pixmap.isNull():
                    # Escalado de alta calidad para mecatrónica
                    label_foto.setPixmap(pixmap.scaled(
                        label_foto.size(), 
                        QtCore.Qt.KeepAspectRatio, 
                        QtCore.Qt.SmoothTransformation
                    ))
                    label_foto.setText("") 
                else:
                    label_foto.setText("Error al leer archivo")
            else:
                # Si no existe ni PNG ni JPG
                label_foto.setText(f"Sin foto: {id_material}")
                label_foto.setStyleSheet("color: yellow; font-weight: bold; background-color: #333;")

    def graficar_materiales_proveedor(self):
        try:
            # 1. Conexión a la base de datos y extracción de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            # Agrupamos por proveedor para sumar sus cantidades totales
            cursor.execute("SELECT proveedor, SUM(cantidad) FROM materiales GROUP BY proveedor")
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                return

            proveedores = [row[0] for row in datos]
            cantidades = [row[1] for row in datos]

            # 2. Configuración del gráfico de barras
            fig, ax = plt.subplots(figsize=(5, 4), tight_layout=True)
            # Aplicamos un estilo oscuro para que combine con tu interfaz
            fig.patch.set_facecolor('#1e1e1e')
            ax.set_facecolor('#2d2d2d')
            
            ax.bar(proveedores, cantidades, color='#00d2ff') # Color cyan como tu interfaz
            ax.set_xlabel('Proveedores', color='white', fontweight='bold')
            ax.set_ylabel('Cantidad Total', color='white', fontweight='bold')
            ax.set_title('Stock por Proveedor', color='white', pad=10)
            ax.tick_params(axis='x', colors='white', rotation=45)
            ax.tick_params(axis='y', colors='white')

            # 3. Limpiar el QFrame 'Flista' e insertar el gráfico
            # Buscamos el frame por su objectName definido en Qt Designer
            frame_grafico = self.findChild(QtWidgets.QFrame, "Flista")
            
            if frame_grafico:
                # Si el frame ya tiene un layout, eliminamos lo anterior
                if frame_grafico.layout() is None:
                    layout = QtWidgets.QVBoxLayout(frame_grafico)
                else:
                    layout = frame_grafico.layout()
                    while layout.count():
                        child = layout.takeAt(0)
                        if child.widget():
                            child.widget().deleteLater()

                canvas = FigureCanvas(fig)
                layout.addWidget(canvas)
                canvas.draw()

        except Exception as e:
            print(f"Error al generar gráfico de barras: {e}")

    
    










if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Solo iniciamos la primera ventana
    inicio = InicioDialog()
    inicio.show()
    
    # El loop de la app (exec()) mantiene todo vivo mientras haya ventanas abiertas
    sys.exit(app.exec())