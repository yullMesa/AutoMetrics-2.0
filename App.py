import sys
# Importamos los componentes necesarios directamente del módulo QtWidgets
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QVBoxLayout, QToolBar
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
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
            
        
    def abrir_ingenieria(self):
        # Cerramos el diálogo y abrimos la ventana principal
        self.accept()

# 1. Clase para la ventana de Ingeniería (QMainWindow)
class IngenieriaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 1. Cargar el archivo .ui de forma segura
        loader = QUiLoader()
        ui_file = QFile("Ingenieria.ui")
        
        if not ui_file.open(QFile.ReadOnly):
            print("Error: No se encontró Ingenieria.ui")
            return
            
        # IMPORTANTE: Cargamos el contenido pasándole 'self' para que NO se borre de memoria
        self.ui_content = loader.load(ui_file) # Cargamos el widget raíz del .ui
        ui_file.close()

        # 2. Configuración de la Ventana Principal
        if self.ui_content:
            # Transferimos el widget central (TabWidget, LCDs, etc.)
            self.setCentralWidget(self.ui_content.centralWidget())
            
            # Transferimos el Menú que diseñaste
            if self.ui_content.menuBar():
                self.setMenuBar(self.ui_content.menuBar())
                
            # Transferimos las Barras de Herramientas
            for toolbar in self.ui_content.findChildren(QToolBar):
                self.addToolBar(toolbar)
                
            # 3. Ajustes de visualización para evitar el error de resize
            self.setWindowTitle("AutoMetrics 2.0 - Ingeniería")
            
            # Usamos el tamaño del contenido para definir la ventana
            self.resize(self.ui_content.size())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    dialogo = InicioDialog()
    
    # Si el ToolButton llama a self.accept(), exec() devolverá True
    if dialogo.exec():
        main_window = IngenieriaWindow()
        main_window.show()
        sys.exit(app.exec())