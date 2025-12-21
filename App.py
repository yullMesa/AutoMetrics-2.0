import sys
# Importamos los componentes necesarios directamente del módulo QtWidgets
from PySide6.QtWidgets import (QApplication, QDialog, QMainWindow, QVBoxLayout, 
                               QToolBar,QTableWidget,QTabWidget,QStackedWidget,QPushButton,
                               QToolButton,QFileDialog,QMessageBox)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtGui import QAction
from PySide6 import QtWidgets
import sqlite3
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

    from PySide6.QtWidgets import QFileDialog, QMessageBox

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
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Solo iniciamos la primera ventana
    inicio = InicioDialog()
    inicio.show()
    
    # El loop de la app (exec()) mantiene todo vivo mientras haya ventanas abiertas
    sys.exit(app.exec())