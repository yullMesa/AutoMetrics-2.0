import sys
# Importamos los componentes necesarios directamente del módulo QtWidgets
from PySide6.QtWidgets import (QApplication, QDialog, QMainWindow, QVBoxLayout, 
                               QToolBar,QTableWidget,QTabWidget,QStackedWidget,QPushButton,QToolButton)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtGui import QAction
from PySide6 import QtWidgets
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
        if hasattr(self.ui, 'toolIngenieria'):
                self.ui.toolIngenieria.clicked.connect(self.accept)
        else:
            print("No se encontró el botón 'toolIngenieria' en Inicio.ui")
        
        # Conectamos el botón de ingeniería de tu inicio.ui
        self.btn_ingenieria = self.ui.findChild(QToolButton, "toolIngenieria") # Revisa el nombre en Designer
        if self.btn_ingenieria:
            self.btn_ingenieria.clicked.connect(self.abrir_ingenieria)
            
        
    def abrir_ingenieria(self):
        # Creamos la ventana de ingeniería
        from App import IngenieriaWindow 
        self.nueva_ventana = IngenieriaWindow()
        self.nueva_ventana.show()
        
        # Cerramos el inicio para que no estorben
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


    def regresar_al_inicio(self):
        print("Regresando al menú de selección...")
        
        # Importamos la clase de tu pantalla inicial
        from App import InicioDialog 
        
        # Creamos la ventana de inicio
        self.ventana_inicio = InicioDialog()
        
        # Le damos un tamaño manual si sale muy pequeña
        self.ventana_inicio.size()
        
        self.ventana_inicio.show()
        
        # Cerramos ingeniería SOLO después de mostrar inicio
        self.close()
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    dialogo = InicioDialog()
    
    # Si el ToolButton llama a self.accept(), exec() devolverá True
    if dialogo.exec():
        main_window = IngenieriaWindow()
        main_window.show()
        sys.exit(app.exec())