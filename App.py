import sys
import os
# Importamos los componentes necesarios directamente del módulo QtWidgets
from PySide6.QtWidgets import (QApplication, QDialog, QMainWindow, QVBoxLayout, 
                               QToolBar,QTableWidget,QTabWidget,QStackedWidget,QPushButton,
                               QToolButton,QFileDialog,QMessageBox,QTreeWidgetItem)

from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtGui import QAction,QPixmap,QIcon, QColor
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
        
        
        self.btn_logistica = self.ui.findChild(QToolButton, "toolGestion") # Asegúrate que el nombre en QtDesigner coincida
        if self.btn_logistica:
            self.btn_logistica.clicked.connect(self.abrir_logistica)

        else:
            print("No se encontró el botón 'toolGestion' en Inicio.ui")
       
        
    def abrir_ingenieria(self):
        # Creamos la ventana y la guardamos en una variable para que no muera
        self.nueva_ventana = IngenieriaWindow()
        self.nueva_ventana.show()
        
        # IMPORTANTE: Usamos close() en lugar de accept() para no disparar el main
        self.close()
        # Cerramos el diálogo y abrimos la ventana principal
        self.accept()



    # Nuevo método en InicioDialog
    def abrir_logistica(self):
        self.nueva_ventana = ModuloCadenaValor()
        self.nueva_ventana.show()
        self.close() # Cierra el menú de inicio
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
        self.conectar_botones_cambios()
        # Agrégalo justo debajo de donde cargas la UI
        self.tableWidget_3 = self.findChild(QtWidgets.QTableWidget, "tableWidget_3")
        self.consultar_materiales()
        self.conectar_aseguramiento_calidad()
        self.graficar_estadisticas_calidad()
        self.configurar_resumen_ingenieria()
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


    def consultar_cambios(self):
        try:
            # 1. Conexión a la base de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Seleccionamos todos los cambios, ordenados por el más reciente
            cursor.execute("SELECT id, persona, fecha, cargo, descripcion FROM control_cambios ORDER BY id DESC")
            datos = cursor.fetchall()
            conn.close()

            # 2. Configurar el tableWidget_4
            self.tableWidget_4.setRowCount(0) # Limpiamos la tabla antes de cargar
            
            for fila_numero, fila_datos in enumerate(datos):
                self.tableWidget_4.insertRow(fila_numero)
                for columna_numero, data in enumerate(fila_datos):
                    # Convertimos todo a string para evitar errores de visualización
                    item = QtWidgets.QTableWidgetItem(str(data))
                    
                    # Opcional: Centrar el texto en las primeras columnas
                    if columna_numero < 4:
                        item.setTextAlignment(QtCore.Qt.AlignCenter)
                    
                    self.tableWidget_4.setItem(fila_numero, columna_numero, item)
            
            # Ajustar el tamaño de las columnas al contenido
            self.tableWidget_4.resizeColumnsToContents()
            # Hacer que la columna de descripción ocupe el espacio restante
            self.tableWidget_4.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)

        except Exception as e:
            print(f"Error al cargar el control de cambios: {e}")

    def conectar_botones_cambios(self):
        # 1. Vincular Entradas (Usa los nombres que pusiste en Qt Designer)
        # 1. ¡ESTA ES LA LÍNEA QUE FALTA! Vincular la tabla
        self.tableWidget_4 = self.findChild(QtWidgets.QTableWidget, "tableWidget_4")
        # Conecta el clic de la tabla con la función que carga los datos
        self.tableWidget_4.itemClicked.connect(self.seleccionar_cambio_tabla)
        # Revisa en Qt Designer si se llaman exactamente así:
        self.txt_persona_cambio = self.findChild(QtWidgets.QLineEdit, "lineEdit_3") # Ejemplo: verifica el nombre real
        self.txt_cargo_cambio = self.findChild(QtWidgets.QLineEdit, "lineEdit_4")   # Ejemplo: verifica el nombre real
        self.txt_desc_cambio = self.findChild(QtWidgets.QTextEdit, "textEdit")       # Tu captura muestra 'textEdit'

        # 2. Vincular Botones
        btn_anadir = self.findChild(QtWidgets.QPushButton, "pushButton_11") # El botón 'Añadir'
        btn_eliminar = self.findChild(QtWidgets.QPushButton, "btn_eliminar_4") # Eliminar (Verifica el nombre en Qt)
        btn_actualizar = self.findChild(QtWidgets.QPushButton, "pushButton_8")
        
        if btn_anadir:
            try: btn_anadir.clicked.disconnect()
            except: pass
            btn_anadir.clicked.connect(self.guardar_nuevo_cambio)
            print("DEBUG: Botón Añadir Cambios conectado")

        # Conectar botón Eliminar
        if btn_eliminar:
            try: btn_eliminar.clicked.disconnect()
            except: pass
            btn_eliminar.clicked.connect(self.eliminar_cambio)

        # Conectar botón Actualizar (Refrescar tabla)
        if btn_actualizar:
            try: btn_actualizar.clicked.disconnect()
            except: pass
            btn_actualizar.clicked.connect(self.actualizar_cambio)

        # 3. Cargar datos iniciales
        self.consultar_cambios()
        self.graficar_control_cambios()



    def guardar_nuevo_cambio(self):
        persona = self.txt_persona_cambio.text()
        cargo = self.txt_cargo_cambio.text()
        descripcion = self.txt_desc_cambio.toPlainText() # .toPlainText() porque es un QTextEdit

        if not persona or not descripcion:
            print("Error: Persona y Descripción son campos obligatorios.")
            return

        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO control_cambios (persona, cargo, descripcion) VALUES (?, ?, ?)",
                        (persona, cargo, descripcion))
            conn.commit()
            conn.close()
            
            print("Cambio registrado exitosamente.")
            self.consultar_cambios() # Refresca la tabla automáticamente
            self.limpiar_campos_cambios()
            
        except Exception as e:
            print(f"Error al guardar cambio: {e}")


    def eliminar_cambio(self):
        fila_seleccionada = self.tableWidget_4.currentRow()
        
        if fila_seleccionada == -1:
            print("Error: Por favor selecciona un cambio de la tabla para eliminar.")
            return

        # Obtener el ID del cambio (asumiendo que está en la columna 0)
        id_cambio = self.tableWidget_4.item(fila_seleccionada, 0).text()

        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM control_cambios WHERE id = ?", (id_cambio,))
            conn.commit()
            conn.close()
            
            print(f"ÉXITO: Cambio ID {id_cambio} eliminado.")
            self.consultar_cambios() # Refrescar la tabla automáticamente
        except Exception as e:
            print(f"Error al eliminar: {e}") 

    def cargar_datos_cambio_a_campos(self):
        self.tableWidget_4.itemClicked.connect(self.cargar_datos_cambio_a_campos)   
        fila = self.tableWidget_4.currentRow()
        if fila != -1:
            # Extraemos datos de la tabla (IDs de columnas según tu captura)
            self.txt_persona_cambio.setText(self.tableWidget_4.item(fila, 1).text())
            self.txt_cargo_cambio.setText(self.tableWidget_4.item(fila, 3).text())
            self.txt_desc_cambio.setPlainText(self.tableWidget_4.item(fila, 4).text())


    def cargar_datos_cambio_a_campos(self):
        fila = self.tableWidget_4.currentRow()
        if fila != -1:
            # Extraemos datos de la tabla (IDs de columnas según tu captura)
            self.txt_persona_cambio.setText(self.tableWidget_4.item(fila, 1).text())
            self.txt_cargo_cambio.setText(self.tableWidget_4.item(fila, 3).text())
            self.txt_desc_cambio.setPlainText(self.tableWidget_4.item(fila, 4).text())


    def actualizar_cambio(self):
        fila_seleccionada = self.tableWidget_4.currentRow()
        
        if fila_seleccionada == -1:
            print("Error: Selecciona un registro de la tabla para actualizar.")
            return

        # 1. Obtener el ID único del registro
        id_registro = self.tableWidget_4.item(fila_seleccionada, 0).text()
        
        # 2. Capturar los nuevos datos de los campos
        nueva_persona = self.txt_persona_cambio.text()
        nuevo_cargo = self.txt_cargo_cambio.text()
        nueva_desc = self.txt_desc_cambio.toPlainText()

        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # SQL para actualizar basado en el ID
            query = """UPDATE control_cambios 
                    SET persona = ?, cargo = ?, descripcion = ? 
                    WHERE id = ?"""
            
            cursor.execute(query, (nueva_persona, nuevo_cargo, nueva_desc, id_registro))
            conn.commit()
            conn.close()
            
            print(f"ÉXITO: Registro {id_registro} actualizado correctamente.")
            self.consultar_cambios() # Refrescar tabla visual
            
        except Exception as e:
            print(f"Error al actualizar el cambio: {e}")

    
    def seleccionar_cambio_tabla(self):
        # 1. Identificamos qué fila se seleccionó
        fila = self.tableWidget_4.currentRow()
        
        if fila != -1:
            # 2. Extraemos los datos según el orden de tus columnas
            # Columna 0: ID (opcional, si quieres guardarlo en una variable oculta)
            # Columna 1: Persona que lo realiza
            # Columna 2: Fecha (normalmente no se edita manualmente)
            # Columna 3: Cargo
            # Columna 4: Descripción del cambio
            
            persona = self.tableWidget_4.item(fila, 1).text()
            cargo = self.tableWidget_4.item(fila, 3).text()
            descripcion = self.tableWidget_4.item(fila, 4).text()

            # 3. "Agarramos" los datos y los ponemos en los campos de la interfaz
            self.txt_persona_cambio.setText(persona)
            self.txt_cargo_cambio.setText(cargo)
            self.txt_desc_cambio.setPlainText(descripcion) # Usamos setPlainText por ser QTextEdit
            
            print(f"DEBUG: Datos cargados del registro ID {self.tableWidget_4.item(fila, 0).text()}")

    def graficar_control_cambios(self):
        try:
            # 1. Conexión y extracción de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            # Agrupamos por cargo para contar la frecuencia de cambios
            cursor.execute("SELECT cargo, COUNT(id) FROM control_cambios GROUP BY cargo")
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                return

            cargos = [row[0] if row[0] else "N/A" for row in datos]
            frecuencias = [row[1] for row in datos]

            # 2. Configuración Estética (Cyan Dashboard Style)
            fig, ax = plt.subplots(figsize=(5, 4), tight_layout=True)
            fig.patch.set_facecolor('#1e1e1e') # Fondo oscuro igual que tu UI
            ax.set_facecolor('#2d2d2d')        # Fondo interno de la gráfica
            
            # Usamos el color Azul Cyan exacto de tu tabla de materiales
            color_cyan = '#00d2ff'
            
            ax.bar(cargos, frecuencias, color=color_cyan, edgecolor='white', linewidth=0.5)
            
            # Configuración de textos y ejes
            ax.set_xlabel('Cargo del Responsable', color='white', fontweight='bold', fontsize=9)
            ax.set_ylabel('Frecuencia de Cambios', color='white', fontweight='bold', fontsize=9)
            ax.set_title('DISTRIBUCIÓN POR CARGO', color=color_cyan, pad=15, fontweight='bold')
            
            # Ajuste de etiquetas para que no se corten
            ax.tick_params(axis='x', colors='white', rotation=25, labelsize=8)
            ax.tick_params(axis='y', colors='white', labelsize=8)

            # 3. Integración en el QFrame 'Fcontrol'
            frame_grafico = self.findChild(QtWidgets.QFrame, "Fcontrol")
            
            if frame_grafico:
                if frame_grafico.layout() is None:
                    layout = QtWidgets.QVBoxLayout(frame_grafico)
                else:
                    layout = frame_grafico.layout()
                    # Limpiar gráficos anteriores para evitar superposición
                    while layout.count():
                        child = layout.takeAt(0)
                        if child.widget():
                            child.widget().deleteLater()

                canvas = FigureCanvas(fig)
                layout.addWidget(canvas)
                canvas.draw()

        except Exception as e:
            print(f"Error al generar gráfico de control: {e}")

    def guardar_inspeccion_calidad(self):
        # 1. Capturar datos de la interfaz
        id_prueba = self.txt_id_prueba.text() # Asumiendo este nombre para el QLineEdit
        persona = self.txt_persona_calidad.text()
        descripcion = self.txt_desc_calidad.toPlainText()
        
        # El criterio se obtiene del botón presionado (OK, RETRY, NO)
        criterio = self.criterio_seleccionado 

        if not id_prueba or not persona:
            print("Error: ID de Prueba y Persona son campos obligatorios.")
            return

        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            query = """INSERT INTO aseguramiento_calidad (id_prueba, criterio, persona, descripcion) 
                    VALUES (?, ?, ?, ?)"""
            
            cursor.execute(query, (id_prueba, criterio, persona, descripcion))
            conn.commit()
            conn.close()
            
            print(f"ÉXITO: Inspección {id_prueba} registrada correctamente.")
            self.consultar_calidad() # Función para refrescar la tabla inferior
            
        except Exception as e:
            print(f"Error al guardar en Aseguramiento de Calidad: {e}")


    def consultar_calidad(self):
        try:
            # 1. Conexión y extracción de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # Seleccionamos los campos: ID Prueba, Persona, Criterio, Descripción
            cursor.execute("SELECT id_prueba, persona, criterio, descripcion FROM aseguramiento_calidad ORDER BY id DESC")
            datos = cursor.fetchall()
            conn.close()

            # 2. Configurar el tableWidget_5
            # Asegúrate de que el objectName en Qt Designer sea tableWidget_5
            self.tableWidget_5 = self.findChild(QtWidgets.QTableWidget, "tableWidget_5")
            
            if self.tableWidget_5:
                self.tableWidget_5.setRowCount(0) # Limpiar tabla antes de cargar
                
                for fila_idx, fila_datos in enumerate(datos):
                    self.tableWidget_5.insertRow(fila_idx)
                    for col_idx, valor in enumerate(fila_datos):
                        item = QtWidgets.QTableWidgetItem(str(valor))
                        
                        # Centrar el texto en las primeras 3 columnas
                        if col_idx < 3:
                            item.setTextAlignment(QtCore.Qt.AlignCenter)
                        
                        # Aplicar color a la celda del CRITERIO para armonía visual
                        if col_idx == 2: # Columna de Criterio
                            if valor == "OK": item.setForeground(QtGui.QColor("#2ecc71")) # Verde
                            elif valor == "RETRY": item.setForeground(QtGui.QColor("#00d2ff")) # Cyan
                            elif valor == "NO": item.setForeground(QtGui.QColor("#e74c3c")) # Rojo
                        
                        self.tableWidget_5.setItem(fila_idx, col_idx, item)
                
                # Ajustes de diseño para que se vea profesional
                self.tableWidget_5.resizeColumnsToContents()
                self.tableWidget_5.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch) # Estirar descripción
                
        except Exception as e:
            print(f"Error al cargar la tabla de calidad: {e}")

    # Dentro de tu función principal de carga o en conectar_botones_cambios
    def conectar_aseguramiento_calidad(self):
        # Cargar datos iniciales en la tabla
        self.consultar_calidad()
        self.actualizar_indicadores_calidad()
        self.tableWidget_5.itemClicked.connect(self.cargar_datos_calidad_a_campos)
        self.tableWidget_5.itemClicked.connect(self.cargar_imagen_inspeccion)
         # 1. Vincular campos de entrada
        self.txt_id_prueba = self.findChild(QtWidgets.QLineEdit, "lineEdit_14")
        self.txt_persona_calidad = self.findChild(QtWidgets.QLineEdit, "lineEdit_13")
        self.txt_desc_calidad = self.findChild(QtWidgets.QTextEdit, "textEdit_2")
        
        # 2. El ButtonBox para los criterios (OK, RETRY, NO)
        # En tu UI estos funcionan como botones independientes, vamos a capturar el clic:
        self.btn_confirmar = self.findChild(QtWidgets.QPushButton, "pushButton_13") # Botón 'Confirmar'

        if self.btn_confirmar:
            try: self.btn_confirmar.clicked.disconnect()
            except: pass
            self.btn_confirmar.clicked.connect(self.guardar_inspeccion_calidad)
        
        # Vincular botones de acción (Confirmar, Actualizar, etc.)
        btn_confirmar = self.findChild(QtWidgets.QPushButton, "pushButton_confirmar") # Ajusta el nombre real
        if btn_confirmar:
            btn_confirmar.clicked.connect(self.guardar_inspeccion_calidad)

        # Vincular los LCD Numbers del árbol de objetos
        self.lcd_aprobados = self.findChild(QtWidgets.QLCDNumber, "lcdNumber_2")
        self.lcd_revision = self.findChild(QtWidgets.QLCDNumber, "lcdNumber_3")
        self.lcd_rechazados = self.findChild(QtWidgets.QLCDNumber, "lcdNumber_4")

        # 1. Buscar el buttonBox en el árbol de objetos
        self.caja_botones = self.findChild(QtWidgets.QDialogButtonBox, "buttonBox")

        if self.caja_botones:
            # Buscamos los botones específicos por su rol o texto
            # Nota: Asegúrate de que en Qt Designer los botones tengan estos nombres/textos
            btn_ok = self.caja_botones.button(QtWidgets.QDialogButtonBox.Ok)
            btn_retry = self.caja_botones.button(QtWidgets.QDialogButtonBox.Retry)
            btn_no = self.caja_botones.button(QtWidgets.QDialogButtonBox.No)

            # Conectar a tus métodos de selección
            if btn_ok: btn_ok.clicked.connect(self.seleccionar_ok)
            if btn_retry: btn_retry.clicked.connect(self.seleccionar_retry)
            if btn_no: btn_no.clicked.connect(self.seleccionar_no)

        # Vincular botones según sus IDs en el árbol
        self.btn_actualizar_q = self.findChild(QtWidgets.QPushButton, "pushButton_14")
        self.btn_eliminar_q = self.findChild(QtWidgets.QPushButton, "pushButton_10") # El botón rojo
        self.btn_exportar_q = self.findChild(QtWidgets.QPushButton, "pushButton_12")

        if self.btn_actualizar_q:
            self.btn_actualizar_q.clicked.connect(self.actualizar_calidad)

        if self.btn_eliminar_q:
            self.btn_eliminar_q.clicked.connect(self.eliminar_calidad)

        if self.btn_exportar_q:
            self.btn_exportar_q.clicked.connect(self.ejecutar_exportacion)

        

    def establecer_criterio(self, valor):
        self.criterio_actual = valor
        print(f"Criterio seleccionado: {valor}")


    def actualizar_indicadores_calidad(self):
        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()

            # Conteo preciso por cada estado
            cursor.execute("SELECT (SELECT COUNT(*) FROM aseguramiento_calidad WHERE criterio='OK'), "
                        "(SELECT COUNT(*) FROM aseguramiento_calidad WHERE criterio='RETRY'), "
                        "(SELECT COUNT(*) FROM aseguramiento_calidad WHERE criterio='NO')")
            
            ok, retry, no = cursor.fetchone()
            conn.close()

            # Actualizar la visualización digital
            if self.lcd_aprobados: self.lcd_aprobados.display(ok)
            if self.lcd_revision: self.lcd_revision.display(retry)
            if self.lcd_rechazados: self.lcd_rechazados.display(no)

        except Exception as e:
            print(f"Error en diagnóstico de indicadores: {e}")
       

    def guardar_inspeccion_calidad(self):
        # Recoger los datos de los LineEdits y TextEdit
        id_prueba = self.txt_id_prueba.text()
        persona = self.txt_persona_calidad.text()
        descripcion = self.txt_desc_calidad.toPlainText() # .toPlainText() para QTextEdit
        
        # Captura del criterio seleccionado (debes definir esta lógica al presionar OK/RETRY/NO)
        # Por defecto usaremos una variable que guarde el último botón presionado
        criterio = getattr(self, "criterio_actual", "PENDIENTE")

        if not id_prueba or not persona:
            print("ALERTA: El ID de Prueba y la Persona son obligatorios.")
            return

        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            query = """INSERT INTO aseguramiento_calidad (id_prueba, criterio, persona, descripcion) 
                    VALUES (?, ?, ?, ?)"""
            cursor.execute(query, (id_prueba, criterio, persona, descripcion))
            conn.commit()
            conn.close()
            
            print(f"ÉXITO: Inspección {id_prueba} registrada.")
            self.consultar_calidad() # Refresca el tableWidget_5
            self.limpiar_campos_calidad()
            
        except Exception as e:
            print(f"Error al guardar calidad: {e}")

        try:
            # Tras el commit exitoso:
            self.consultar_calidad()            # Refresca la tabla inferior
            self.actualizar_indicadores_calidad() # Refresca los números LCD
            print("Dashboard de calidad actualizado.")
        except Exception as e:
            print(f"Error en actualización de dashboard: {e}")

    # Ejemplo de conexión de botones de estado
    def seleccionar_ok(self):
        self.criterio_actual = "OK"
        print("Criterio: Aprobado")

    def seleccionar_retry(self):
        self.criterio_actual = "RETRY"
        print("Criterio: En Revisión")

    def seleccionar_no(self):
        self.criterio_actual = "NO"
        print("Criterio: Rechazado")


    def actualizar_indicadores_calidad(self):
        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()

            # Consultar conteos por criterio
            cursor.execute("SELECT COUNT(*) FROM aseguramiento_calidad WHERE criterio = 'OK'")
            aprobados = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM aseguramiento_calidad WHERE criterio = 'RETRY'")
            revision = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM aseguramiento_calidad WHERE criterio = 'NO'")
            rechazados = cursor.fetchone()[0]

            conn.close()

            # Asignar valores a los LCD Numbers
            self.lcd_aprobados = self.findChild(QtWidgets.QLCDNumber, "lcdNumber_2")
            self.lcd_revision = self.findChild(QtWidgets.QLCDNumber, "lcdNumber_3")
            self.lcd_rechazados = self.findChild(QtWidgets.QLCDNumber, "lcdNumber_4")

            if self.lcd_aprobados: self.lcd_aprobados.display(aprobados)
            if self.lcd_revision: self.lcd_revision.display(revision)
            if self.lcd_rechazados: self.lcd_rechazados.display(rechazados)

        except Exception as e:
            print(f"Error al actualizar indicadores LCD: {e}")

    def actualizar_calidad(self):
        fila = self.tableWidget_5.currentRow()
        if fila == -1: return

        # El ID real de la DB suele estar en una columna oculta o ser el primero
        id_prueba_ui = self.txt_id_prueba.text()
        persona = self.txt_persona_calidad.text()
        desc = self.txt_desc_calidad.toPlainText()
        criterio = getattr(self, "criterio_actual", "OK")

        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            # Actualizamos por el ID de prueba
            cursor.execute("""UPDATE aseguramiento_calidad 
                            SET persona=?, criterio=?, descripcion=? 
                            WHERE id_prueba=?""", (persona, criterio, desc, id_prueba_ui))
            conn.commit()
            conn.close()
            self.consultar_calidad()
            self.actualizar_indicadores_calidad() # Refresca los LCD
        except Exception as e:
            print(f"Error al actualizar: {e}")

    def eliminar_calidad(self):
        fila = self.tableWidget_5.currentRow()
        if fila == -1: return

        # Obtenemos el ID de la prueba de la primera columna
        id_prueba = self.tableWidget_5.item(fila, 0).text()

        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM aseguramiento_calidad WHERE id_prueba=?", (id_prueba,))
            conn.commit()
            conn.close()
            self.consultar_calidad()
            self.actualizar_indicadores_calidad() # Los números bajan automáticamente
        except Exception as e:
            print(f"Error al eliminar: {e}")

    def cargar_datos_calidad_a_campos(self):
        fila = self.tableWidget_5.currentRow()
        
        if fila != -1:
            # Extraemos los datos con los índices correctos
            id_prueba = self.tableWidget_5.item(fila, 0).text()   # Columna 0 -> ID PRUEBA
            persona = self.tableWidget_5.item(fila, 1).text()     # Columna 1 -> PERSONA
            criterio = self.tableWidget_5.item(fila, 2).text()    # Columna 2 -> CRITERIO
            descripcion = self.tableWidget_5.item(fila, 3).text() # Columna 3 -> DESCRIPCIÓN

            # Asignamos a los LineEdits correctos según tu árbol de objetos
            # lineEdit_13 es ID PRUEBA, lineEdit_14 es PERSONA
            self.txt_id_prueba.setText(id_prueba)     # Ahora recibirá "PR-008" correctamente
            self.txt_persona_calidad.setText(persona) # Ahora recibirá "Jorge Hincapié"
            self.txt_desc_calidad.setPlainText(descripcion)
            
            self.criterio_actual = criterio
            print(f"Sincronización corregida para: {id_prueba}")

    def cargar_imagen_inspeccion(self):
        fila = self.tableWidget_5.currentRow()
        if fila == -1: return

        # 1. Obtener el ID de la prueba (Columna 0)
        id_prueba = self.tableWidget_5.item(fila, 0).text()
        
        # 2. Definir la ruta de la imagen (asumiendo formato .png o .jpg)
        ruta_imagen = f"calidad/{id_prueba}.png" 
        
        # 3. Buscar el label_8 en el árbol de objetos
        self.visor_imagen = self.findChild(QtWidgets.QLabel, "label_8")
        
        if self.visor_imagen:
            if os.path.exists(ruta_imagen):
                pixmap = QPixmap(ruta_imagen)
                # Escalar imagen al tamaño del label manteniendo la proporción
                self.visor_imagen.setPixmap(pixmap.scaled(
                    self.visor_imagen.width(), 
                    self.visor_imagen.height(), 
                    QtCore.Qt.KeepAspectRatio, 
                    QtCore.Qt.SmoothTransformation
                ))
            else:
                # Si no hay imagen, mostrar un mensaje o limpiar el label
                self.visor_imagen.setText("SIN IMAGEN DE EVIDENCIA")
                self.visor_imagen.setStyleSheet("color: gray; font-weight: bold;")


    def graficar_estadisticas_calidad(self):
        try:
            # 1. Consultar sumatorias por criterio
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            criterios = ['OK', 'RETRY', 'NO']
            conteos = []
            
            for c in criterios:
                cursor.execute("SELECT COUNT(*) FROM aseguramiento_calidad WHERE criterio = ?", (c,))
                conteos.append(cursor.fetchone()[0])
            conn.close()

            # 2. Configuración Estética de la Gráfica
            fig, ax = plt.subplots(figsize=(4, 3), tight_layout=True)
            fig.patch.set_facecolor('#1e1e1e') # Fondo oscuro del dashboard
            ax.set_facecolor('#2d2d2d')
            
            # Colores institucionales: Verde (OK), Cyan (RETRY), Rojo (NO)
            colores = ['#2ecc71', '#00d2ff', '#e74c3c']
            
            barras = ax.bar(criterios, conteos, color=colores)
            
            # Etiquetas y Estilo
            ax.set_title('ESTADO DE CALIDAD', color='white', fontweight='bold', fontsize=10)
            ax.tick_params(axis='both', colors='white', labelsize=8)
            
            # Añadir el número exacto sobre cada barra para precisión técnica
            for barra in barras:
                height = barra.get_height()
                ax.annotate(f'{int(height)}',
                            xy=(barra.get_x() + barra.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha='center', va='bottom', color='white', fontweight='bold')

            # 3. Insertar en el QFrame 'Faseguramiento'
            # Nota: Asegúrate de que el frame se llame Faseguramiento en Qt Designer
            frame_grafico = self.findChild(QtWidgets.QFrame, "Faseguramiento")
            
            if frame_grafico:
                if frame_grafico.layout() is None:
                    layout = QtWidgets.QVBoxLayout(frame_grafico)
                else:
                    layout = frame_grafico.layout()
                    # Limpiar gráfico anterior para refrescar
                    while layout.count():
                        child = layout.takeAt(0)
                        if child.widget(): child.widget().deleteLater()

                canvas = FigureCanvas(fig)
                layout.addWidget(canvas)
                canvas.draw()

        except Exception as e:
            print(f"Error al generar gráfica de aseguramiento: {e}")

    def configurar_resumen_ingenieria(self):
        try:
            # 1. Consultar datos actuales para el KPI
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM aseguramiento_calidad WHERE criterio = 'OK'")
            ok = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM aseguramiento_calidad")
            total = cursor.fetchone()[0]
            conn.close()

            # Calcular porcentaje de efectividad
            yield_rate = (ok / total * 100) if total > 0 else 0

            # 2. Configurar el Frame (Asumiendo que se llama frame_resumen)
            frame = self.findChild(QtWidgets.QFrame, "frame_10") # Ajusta al nombre real
            
            if frame:
                if frame.layout() is None:
                    layout = QtWidgets.QVBoxLayout(frame)
                else:
                    layout = frame.layout()
                    while layout.count(): layout.takeAt(0).widget().deleteLater()

                # Crear un Label con estilo de alta ingeniería
                label_kpi = QtWidgets.QLabel(f"EFECTIVIDAD DE PLANTA\n{yield_rate:.1f}%")
                label_kpi.setAlignment(QtCore.Qt.AlignCenter)
                label_kpi.setStyleSheet("""
                    font-size: 24px; 
                    font-weight: bold; 
                    color: #00d2ff; 
                    border: 2px solid #00d2ff; 
                    border-radius: 10px;
                    padding: 10px;
                    background-color: #1e1e1e;
                """)
                layout.addWidget(label_kpi)
                # 3. Actualización de la Interfaz
        except Exception as e:
            print(f"Error en KPI: {e}")


class ModuloCadenaValor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        loader = QUiLoader()
        ui_file = QFile("GestionDeLaCadenaDeValor.ui")
        
        if ui_file.open(QFile.ReadOnly):
            # IMPORTANTE: Cargamos el UI y lo guardamos en self.ui
            self.ui = loader.load(ui_file) 
            ui_file.close()
            
            # Esto es lo que falta: poner el diseño dentro de la ventana
            self.setCentralWidget(self.ui)
            
            # Ajustar el tamaño de la ventana al tamaño del diseño original
            self.resize(self.ui.size())
            self.setWindowTitle("Gestión de la Cadena de Valor - Logística")
        else:
            print("No se pudo encontrar el archivo .ui")

        self.configurar_navegacion_menu()
        self.cargar_datos_planificacion()
        self.actualizar_treewidget_logistica()
        self.cargar_datos_diferentes()

    def configurar_navegacion_menu(self):
        # La lógica de índices de izquierda a derecha según tu imagen de la barra:
        # 0: Dashboard, 1: Planificación, 2: Gestión Proveedores, 
        # 3: Logística, 4: Análisis Costos, 5: Inventario Crítico

        # 1. Dashboard (Índice 0)
        self.ui.actionGrafico.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))

        # 2. Planificación de Suministros (Índice 1)
        self.ui.actionCrud.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))

        # 3. Gestión de Proveedores (Índice 2)
        self.ui.actionCrud_2.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))

        # 4. Logística y Transporte (Índice 3)
        self.ui.actionCrud_3.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(3))

        # 5. Análisis de Costos (Índice 4)
        self.ui.actionCrud_4.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(4))

        # 6. Inventario Crítico (Índice 5)
        self.ui.actionCrud_5.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(5))

         # BOTÓN VOLVER (actionInicio)
        self.ui.actionInicio.triggered.connect(self.regresar_al_inicio)
        

       

    def regresar_al_inicio(self):
        print("Regresando al menú de selección...")
        
        # Creamos la ventana de inicio
        self.ventana_inicio = InicioDialog()
        
        # Le damos un tamaño manual si sale muy pequeña
        self.ventana_inicio.size()
        
        self.ventana_inicio.show()
        
        # Cerramos ingeniería SOLO después de mostrar inicio
        self.close()

    def cargar_datos_planificacion(self):
        # 1. Configuración visual
        self.ui.tableWidget.verticalHeader().setVisible(False)
        
        # 2. CONEXIÓN CORREGIDA: Apuntamos a la DB de Gestión, no a Ingeniería
        # Asegúrate de que el nombre del archivo sea exacto al que ves en tu VS Code
        conn = sqlite3.connect("GestionDelValor.db") 
        cursor = conn.cursor()
        
        try:
            # Seleccionamos los datos
            cursor.execute("SELECT id_material, cantidad_requerida, proveedor, fecha_estimada, descripcion FROM planificacion_suministros")
            datos = cursor.fetchall()
            
            # 3. Limpiar y llenar tabla
            self.ui.tableWidget.setRowCount(0)
            for row_number, row_data in enumerate(datos):
                self.ui.tableWidget.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    item = QtWidgets.QTableWidgetItem(str(data))
                    self.ui.tableWidget.setItem(row_number, column_number, item)
                    
        except sqlite3.OperationalError as e:
            print(f"Error: La tabla no existe en GestionDelValor.db. Detalles: {e}")
        finally:
            conn.close()

    def actualizar_treewidget_logistica(self):
        self.ui.treeWidget.clear()
        # Encabezados según tu diseño
        self.ui.treeWidget.setHeaderLabels(["ID ENVÍO", "TRANSPORTISTA", "RUTA", "CARGA", "FECHA", "ESTADO"])

        conn = sqlite3.connect("GestionDelValor.db")
        cursor = conn.cursor()
        
        try:
            # Traemos los datos de la tabla de logística
            cursor.execute("SELECT * FROM logistica_transporte")
            envios = cursor.fetchall()
            
            for e in envios:
                # Creamos el PADRE (El Envío)
                padre = QTreeWidgetItem(self.ui.treeWidget)
                padre.setText(0, e[0]) # ID Envío
                padre.setText(1, e[1]) # Transportista
                padre.setText(2, e[2]) # Ruta
                padre.setText(5, e[5]) # Estado

                # Creamos un HIJO de ejemplo (El detalle de la carga)
                # Esto es lo que hace que NO se vea igual a una tabla plana
                detalle = QTreeWidgetItem(padre)
                detalle.setText(0, "Detalle:")
                detalle.setText(1, f"Peso: {e[3]}")
                detalle.setText(2, f"Salida: {e[4]}")
                
        except sqlite3.OperationalError as e:
            print(f"Error de base de datos: {e}")
        finally:
            conn.close()

    def cargar_datos_diferentes(self):
        self.ui.treeWidget.clear()
        # Habilitamos que se vea la estructura de árbol
        self.ui.treeWidget.setRootIsDecorated(True) 
        
        # 1. Creamos un "Envío Padre" (El Camión o Ruta)
        envio_padre = QTreeWidgetItem(self.ui.treeWidget)
        envio_padre.setText(0, "RUTA-NACIONAL-001")
        envio_padre.setText(1, "Transportes Transandina")
        envio_padre.setText(5, "EN CAMINO")
        # Ponemos un color de fondo diferente al padre para resaltarlo
        envio_padre.setBackground(0, QColor("#004d4d")) 

        # 2. Creamos "Hijos" (Los productos dentro de esa ruta)
        # Al pasar 'envio_padre' como argumento, se vuelve un sub-elemento
        producto1 = QTreeWidgetItem(envio_padre)
        producto1.setText(0, "MAT-001")
        producto1.setText(2, "Sensores Laser")
        producto1.setText(3, "50 unidades")
        
        producto2 = QTreeWidgetItem(envio_padre)
        producto2.setText(0, "MAT-005")
        producto2.setText(2, "Fuentes de Poder")
        producto2.setText(3, "30 unidades")

        self.ui.treeWidget.expandAll()

        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Solo iniciamos la primera ventana
    inicio = InicioDialog()
    inicio.show()
    
    # El loop de la app (exec()) mantiene todo vivo mientras haya ventanas abiertas
    sys.exit(app.exec())