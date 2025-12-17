import sys
import os
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QVBoxLayout, QWidget,QMenuBar,QStatusBar,QStackedWidget,QSizePolicy
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile,Qt

import recursos_rc 

class IngenieriaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        ui_file = QFile("Ingenieria.ui")
        
        if not ui_file.open(QFile.ReadOnly):
            print("No se pudo abrir Ingenieria.ui")
            return
            
        # 1. Cargamos el contenido SIN pasar 'self' para evitar el RuntimeError
        self.ui_content = loader.load(ui_file)
        ui_file.close()

        # 2. Extraemos y asignamos el Widget Central (el cuerpo de tu app)
        # Buscamos el objeto que contiene todo tu diseño de ingeniería
        central = self.ui_content.findChild(QWidget, "centralwidget")
        if central:
            self.setCentralWidget(central)

        # 3. Extraemos y configuramos la Barra de Menú
        menu_bar = self.ui_content.findChild(QMenuBar)
        if menu_bar:
            self.setMenuBar(menu_bar)
            # Aplicamos estilo para que las letras sean blancas y visibles
            menu_bar.setStyleSheet("""
                QMenuBar {
                    background-color: #1a1a1a;
                    color: white;
                    padding: 5px;
                }
                QMenuBar::item:selected {
                    background-color: #00ccff;
                    color: black;
                }
            """)
        self.stack = self.ui_content.findChild(QStackedWidget, "stackedWidget")

        if self.stack:
            # 1. Hacer que el stackedWidget sea elástico
            self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            # 2. Si no pusiste layout en Designer, lo ponemos por código
            if self.centralWidget().layout() is None:
                from PySide6.QtWidgets import QVBoxLayout
                layout = QVBoxLayout(self.centralWidget())
                layout.addWidget(self.stack)
                layout.setContentsMargins(0, 0, 0, 0) # Cero bordes

        # 4. PANTALLA COMPLETA
        self.showMaximized()


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

        # Conexión al botón de Ingeniería
        if hasattr(self.ui, 'toolIngenieria'):
            self.ui.toolIngenieria.clicked.connect(self.abrir_ingenieria)
        else:
            print("Error: El botón se llama diferente en Designer")

    def abrir_ingenieria(self):
        # Crear la instancia de la ventana principal
        self.ventana_ing = IngenieriaWindow()
        self.ventana_ing.show()
        # Cerrar el diálogo actual
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Estilo oscuro global
    app.setStyleSheet("""
        QMainWindow, QDialog { background-color: #0b0b0b; }
        QLabel { color: white; }
    """)
    
    inicio = InicioDialog()
    inicio.show()
    
    sys.exit(app.exec())

    