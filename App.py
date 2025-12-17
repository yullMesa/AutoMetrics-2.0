import sys
import os
from PySide6.QtWidgets import (QApplication, QDialog, QMainWindow, QVBoxLayout, QWidget,
                               QMenuBar,QStatusBar,QStackedWidget,QSizePolicy,QTableWidget,
                               QTableWidgetItem,QLayout,QFrame)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile,Qt
import pandas as pd
import plotly.express as px
from PySide6.QtWebEngineWidgets import QWebEngineView
import recursos_rc 

class IngenieriaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        ui_file = QFile("Ingenieria.ui")
        if not ui_file.open(QFile.ReadOnly): return
        self.ui_content = loader.load(ui_file)
        ui_file.close()

        # Configuración básica
        self.setFixedSize(1300, 1000)
        self.setCentralWidget(self.ui_content.findChild(QWidget, "centralwidget"))
        
        # Elementos de la UI
        self.stack = self.ui_content.findChild(QStackedWidget, "stackedWidget")
        self.menu_bar = self.ui_content.findChild(QMenuBar)
        
        if self.menu_bar:
            self.setMenuBar(self.menu_bar)
            # Conectar la acción del Menú "Dashboard"
            # Asegúrate que en Designer la acción se llame 'actionDashboard'
            self.action_dash = self.ui_content.findChild(object, "actionDashboard")
            if self.action_dash:
                self.action_dash.triggered.connect(self.cargar_dashboard)
            
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

    def cargar_dashboard(self):
        # 1. Crear la gráfica (usa 'include' para asegurar que cargue sin internet)
        df = pd.DataFrame({'x': [1, 2, 3], 'y': [10, 20, 15]})
        fig = px.line(df, x='x', y='y', template="plotly_dark")
        
        # IMPORTANTE: usa include_plotlyjs='include'
        html_content = fig.to_html(include_plotlyjs='include', full_html=True)

        # 2. Buscar el widget y cargar el contenido
        web_widget = self.ui_content.findChild(QWebEngineView, "web_dashboard")
        
        if web_widget:
            web_widget.setHtml(html_content)
            # Forzar que el stackedWidget muestre la página correcta
            # page_3 suele ser el índice 0 si es la primera
            self.stack.setCurrentIndex(0) 
            web_widget.show() # Asegurar que sea visible
       

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

    