import sys
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout,QMainWindow
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
        loader = QUiLoader()
        ui_file = QFile("Ingenieria.ui")
        
        if ui_file.open(QFile.ReadOnly):
            self.ui = loader.load(ui_file, self)
            ui_file.close()
            self.setCentralWidget(self.ui)
            self.setWindowTitle("AutoMetrics 2.0 - Ingeniería")
            self.resize(self.ui.size())
        else:
            print("Error al abrir Ingenieria.ui")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    dialogo = InicioDialog()
    
    # Si el ToolButton llama a self.accept(), exec() devolverá True
    if dialogo.exec():
        main_window = IngenieriaWindow()
        main_window.show()
        sys.exit(app.exec())