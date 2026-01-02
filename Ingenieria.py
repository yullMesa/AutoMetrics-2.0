import os
from PySide6.QtWidgets import QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import recursos_rc

class VentanaIngenieria(QMainWindow):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        ruta_ui = os.path.join(os.path.dirname(__file__), "Ingenieria.ui")
        ui_file = QFile(ruta_ui)
        
        if ui_file.open(QFile.ReadOnly):
            self.ui = loader.load(ui_file)
            ui_file.close()
            self.setCentralWidget(self.ui)
            self.resize(self.ui.size())

            # 1. Conectar las 7 páginas del menú
            self.conectar_menu()

            # 2. Conectar botón VOLVER (para regresar a Inicio.ui)
            # Asegúrate que el objectName en Designer sea 'actionInicio'
            if hasattr(self.ui, 'actionInicio'):
                self.ui.actionInicio.triggered.connect(self.regresar)

    def conectar_menu(self):
        conexiones = {
            "actionDashboard": 0, "actionCrud": 1, "actionCRUD2": 2,
            "actionCRUD_5": 3, "actionCRUD_C": 4, "actionCRUD_4": 5
        }
        for nombre, indice in conexiones.items():
            accion = self.ui.findChild(object, nombre)
            if accion:
                accion.triggered.connect(lambda chk=False, i=indice: self.cambiar_pagina(i))

    def cambiar_pagina(self, indice):
        stack = self.ui.findChild(object, "stackedWidget")
        if stack:
            stack.setCurrentIndex(indice)

    def regresar(self):
        # Importamos aquí dentro para evitar errores de importación circular
        from App import VentanaInicio
        self.nueva = VentanaInicio()
        self.nueva.show()
        self.close() # Cierra la ventana de Ingeniería