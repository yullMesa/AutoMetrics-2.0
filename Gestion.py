import sqlite3
import os
from PySide6 import QtWidgets, QtCore, QtUiTools,QtGui
from PySide6.QtUiTools import QUiLoader
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas # Nota el cambio a qtagg



class VentanaGestion(QtWidgets.QMainWindow):
    def __init__(self, inicio=None):
        super().__init__()
        self.inicio = inicio # Guardamos la referencia para el botón volver
        
        # 1. CARGA CORRECTA DEL UI
        loader = QtUiTools.QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "GestionDeLaCadenaDeValor.ui")
        ui_file = QtCore.QFile(path)
        
        if ui_file.open(QtCore.QFile.ReadOnly):
            # Cargamos el archivo UI. IMPORTANTE: No pasar 'self' aquí todavía
            self.ui = loader.load(ui_file) 
            ui_file.close()
            
            # 2. VINCULACIÓN VISUAL: Esto quita el fondo blanco
            self.setCentralWidget(self.ui)
            
            # 3. REDIMENSIONAR: Para que no salga pequeña
            self.resize(self.ui.size())
            self.setWindowTitle("Gestión de la Cadena de Valor")
            
            # 4. ACTIVAR NAVEGACIÓN
            self.configurar_navegacion()

            #Datos planificacion
            self.mostrar_y_cargar_planificacion()
            self.mostrar_y_cargar_materiales()
            self.actualizar_dashboard()
        
        
        else:
            print("No se pudo cargar el archivo .ui")
        
        

    def configurar_navegacion(self):
        """Mapeo universal para el stackedWidget"""
        # Conectamos las acciones de tu menubar
        self.ui.actionGrafico.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.actionCrud.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.actionCrud_2.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.actionCrud_3.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(3))
        self.ui.actionCrud_4.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(4))
        self.ui.actionCrud_5.triggered.connect(lambda: self.ui.stackedWidget.setCurrentIndex(5))
        
        # Acción Volver
        self.ui.actionInicio.triggered.connect(self.regresar_al_inicio)

    def regresar_al_inicio(self):
        """Reabre Inicio.ui y cierra esta ventana"""
        if self.inicio:
            self.inicio.show()
        self.close()
        
        

    def cambiar_pagina(self, indice):
        """Método único para controlar las 6 páginas del stackedWidget"""
        # Suponiendo que tu widget se llama 'stackedWidget' en el Designer
        if hasattr(self.ui, 'stackedWidget'):
            self.ui.stackedWidget.setCurrentIndex(indice)
        else:
            print("Error: No se encontró el objeto 'stackedWidget' en el .ui")

    
    
    #-----------planificación suministros-----------------------------

    def cargar_tabla_planificacion(self):
        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # 1. Seleccionamos las columnas en el orden exacto de tu interfaz
            query = """
                SELECT id, cantidad_requerida, proveedor, fecha_estimada, descripcion, costo_unitario 
                FROM planificacion_suministros
            """
            cursor.execute(query)
            datos = cursor.fetchall()

            # 2. Configuración estética y de limpieza
            self.ui.tableWidget.setRowCount(len(datos))
            self.ui.tableWidget.setColumnCount(6)
            self.ui.tableWidget.verticalHeader().setVisible(False) # Quita índices de fila

            # 3. LLENAR TODA LA TABLA (Ajuste de estiramiento)
            header = self.ui.tableWidget.horizontalHeader()
            # Esto hace que todas las columnas se repartan el ancho total proporcionalmente
            for i in range(6):
                header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

            # 4. Inserción de datos
            for row_index, row_data in enumerate(datos):
                for col_index, value in enumerate(row_data):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    # Centramos el texto para mejor estética
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.ui.tableWidget.setItem(row_index, col_index, item)
            
            conn.close()
        except Exception as e:
            print(f"Error al ajustar tabla: {e}")
            
       

    def mostrar_y_cargar_planificacion(self):
        # Cambia a la página 1 del stackedWidget
        #self.ui.stackedWidget.setCurrentIndex(1)
        # Carga los datos frescos de la DB
        self.cargar_tabla_planificacion()

    #treewidget
    def cargar_tree_materiales(self):
        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            # Seleccionamos todos los campos necesarios
            query = "SELECT id_material, descripcion, cantidad, proveedor, unidad, costo_unidad FROM materiales"
            cursor.execute(query)
            datos = cursor.fetchall()

            self.ui.treeWidget.clear()
            # Solo necesitamos una columna principal para el ID
            self.ui.treeWidget.setHeaderLabels(["Explorador de Materiales (ID)"]) 

            for fila in datos:
                # 1. Crear el ítem PADRE (Solo muestra el ID)
                padre = QtWidgets.QTreeWidgetItem(self.ui.treeWidget)
                padre.setText(0, f"📦 MATERIAL: {fila[0]}")
                padre.setForeground(0, QtGui.QColor("#00d4ff")) # Color celeste neón
                
                # 2. Crear los ítems HIJOS (Detalles desplegables)
                hijo_desc = QtWidgets.QTreeWidgetItem(padre)
                hijo_desc.setText(0, f"📝 Descripción: {fila[1]}")
                
                hijo_stock = QtWidgets.QTreeWidgetItem(padre)
                hijo_stock.setText(0, f"📊 Stock: {fila[2]} {fila[4]}")
                
                hijo_prov = QtWidgets.QTreeWidgetItem(padre)
                hijo_prov.setText(0, f"🏭 Proveedor: {fila[3]}")
                
                hijo_costo = QtWidgets.QTreeWidgetItem(padre)
                hijo_costo.setText(0, f"💰 Costo Unitario: ${fila[5]:,.2f}")

            # Configuración estética final
            self.ui.treeWidget.setIndentation(20) # Espacio de la "carpeta"
            conn.close()
        except Exception as e:
            print(f"Error en estructura de carpetas: {e}")


    def mostrar_y_cargar_materiales(self):
        # Cambia a la página del stackedWidget (ajusta el índice si es necesario)
        #self.ui.stackedWidget.setCurrentIndex(2) 
        # Carga los materiales desde la DB
        self.cargar_tree_materiales()

    #visual
    
    def graficar_costos_proveedores(self):
        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            query = """
                SELECT proveedor, SUM(cantidad_requerida * costo_unitario) 
                FROM planificacion_suministros 
                GROUP BY proveedor
            """
            cursor.execute(query)
            datos = cursor.fetchall()
            conn.close()

            if not datos: return

            proveedores = [fila[0] for fila in datos]
            totales = [fila[1] for fila in datos]

            # Aumentamos un poco el tamaño de la figura para dar aire
            fig, ax = plt.subplots(figsize=(7, 5)) 
            fig.patch.set_facecolor('#000000')
            ax.set_facecolor('#000000')
            
            ax.bar(proveedores, totales, color='#00d4ff')
            
            # --- EL TRUCO PARA LOS NOMBRES ---
            # Rotamos los nombres 45 grados y los alineamos a la derecha
            ax.set_xticklabels(proveedores, rotation=45, ha='right', fontsize=9)
            
            # Damos espacio extra en la parte inferior para que no se corten los nombres
            plt.subplots_adjust(bottom=0.30) 

            # Estética de colores
            ax.set_title("Inversión Total por Proveedor", color='#00d4ff', fontweight='bold', pad=20)
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            for spine in ax.spines.values():
                spine.set_color('white')

            # Limpieza e inserción en el frame_11
            layout = self.ui.frame_11.layout()
            if layout is not None:
                while layout.count():
                    layout.takeAt(0).widget().deleteLater()
            else:
                from PySide6.QtWidgets import QVBoxLayout
                layout = QVBoxLayout(self.ui.frame_11)

            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)
            canvas.draw()

        except Exception as e:
            print(f"Error al mejorar la gráfica: {e}")


    def actualizar_dashboard(self):
        #self.ui.stackedWidget.setCurrentIndex(0) # Va al dashboard
        self.graficar_costos_proveedores()
    