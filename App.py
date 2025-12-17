import sys
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import recursos_rc

class InicioDialog(QDialog):
    def __init__(self):
        super().__init__()
        
        # 1. Cargar el archivo .ui
        loader = QUiLoader()
        ui_file = QFile("Inicio.ui")
        
        if not ui_file.open(QFile.ReadOnly):
            print(f"Error: No se pudo abrir el archivo: {ui_file.errorString()}")
            return
            
        # 2. Cargar la interfaz
        self.ui = loader.load(ui_file) # Cargamos sin pasar 'self' aquí primero
        ui_file.close()

        # 3. ¡ESTO ES LO QUE FALTA! 
        # Creamos un layout para el diálogo y metemos la interfaz cargada dentro
        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)
        layout.setContentsMargins(0, 0, 0, 0) # Quitar bordes blancos extra

        # 4. Ajustes visuales finales
        self.setWindowTitle("AutoMetrics 2.0")
        self.resize(self.ui.size()) # Forzar el tamaño del diseño original

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Opcional: Forzar fondo negro si el .ui no lo tiene aplicado globalmente
    app.setStyleSheet("QDialog { background-color: #0b0b0b; }")
    
    dialogo = InicioDialog()
    dialogo.show()
    
    sys.exit(app.exec())