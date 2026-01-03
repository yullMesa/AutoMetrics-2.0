import sqlite3
import os
from PySide6 import QtWidgets, QtCore, QtUiTools,QtGui
from PySide6.QtUiTools import QUiLoader
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas # Nota el cambio a qtagg
from datetime import datetime
import Exportar
from PySide6.QtWidgets import QMainWindow, QMessageBox, QApplication,QVBoxLayout
# O si ya importas el módulo completo:
from PySide6 import QtWidgets # En este caso usarías QtWidgets.QMessageBox
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtWidgets import QTreeWidgetItem, QFileIconProvider #


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
            self.ui.tableWidget.itemClicked.connect(self.recuperar_datos_tabla)
            self.ui.pushButton_4.clicked.connect(self.agregar_suministro)
            self.ui.pushButton_3.clicked.connect(self.eliminar_suministro)
            self.ui.pushButton_5.clicked.connect(self.actualizar_suministro)
            self.ui.pushButton.clicked.connect(self.accion_exportar)

            #Datos gestión proveedores
            self.cargar_tabla_proveedores()
            self.cargar_arbol_gestion()
            self.ui.treeWidget_2.itemClicked.connect(self.controlar_navegacion_arbol)
            self.ui.treeWidget_2.setColumnCount(2)
            self.ui.treeWidget_2.setHeaderLabels(["Módulos del Sistema", "Información Extra"])
            if self.ui.frame_28.layout() is None:
                layout = QVBoxLayout(self.ui.frame_28)
                self.ui.frame_28.setLayout(layout)
            self.graficar_tiempos_proveedores()
            self.ui.tableWidget_2.itemClicked.connect(self.recuperar_datos_gestion_tabla)
            self.ui.pushButton_6.clicked.connect(self.agregar_proveedor)
            # Conectar el botón Eliminar (pushButton_7)
            self.ui.pushButton_7.clicked.connect(self.eliminar_proveedor)
            # Conectar el botón Actualizar (pushButton_8)
            self.ui.pushButton_8.clicked.connect(self.actualizar_proveedor)
            self.ui.pushButton_2.clicked.connect(self.accion_exportar)
        
        
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

    
    #recuperar datos
    
    def recuperar_datos_tabla(self):
        # 1. Obtener la fila seleccionada actualmente
        fila_seleccionada = self.ui.tableWidget.currentRow()
        
        if fila_seleccionada != -1:
            # 2. Extraer el texto de cada celda de esa fila
            # El orden debe coincidir con las columnas de tu tabla
            id_material = self.ui.tableWidget.item(fila_seleccionada, 0).text()
            cantidad    = self.ui.tableWidget.item(fila_seleccionada, 1).text()
            proveedor   = self.ui.tableWidget.item(fila_seleccionada, 2).text()
            fecha       = self.ui.tableWidget.item(fila_seleccionada, 3).text()
            descripcion = self.ui.tableWidget.item(fila_seleccionada, 4).text()
            costo       = self.ui.tableWidget.item(fila_seleccionada, 5).text()

            # 3. Mandar los datos a los QLineEdit
            self.ui.txt_id_material.setText(id_material)
            self.ui.txt_cantidad.setText(cantidad)
            self.ui.txtproveedor.setText(proveedor)
            self.ui.txtFecha.setText(fecha)
            self.ui.txt_descripcion.setText(descripcion)
            self.ui.txtCosto.setText(costo)

    
    #Botones

    def agregar_suministro(self):
        try:
            # 1. Capturar datos y convertir tipos
            id_val = int(self.ui.txt_id_material.text())
            cant   = int(self.ui.txt_cantidad.text())
            prov   = self.ui.txtproveedor.text()
            desc   = self.ui.txt_descripcion.text()
            costo  = float(self.ui.txtCosto.text())

            # 2. GENERAR FECHA AUTOMÁTICA (Formato: Año-Mes-Día)
            fecha_auto = datetime.now().strftime("%Y-%m-%d")

            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # 3. Query con el orden de tu tabla visual
            # (id, cantidad_requerida, proveedor, fecha_estimada, descripcion, costo_unitario)
            query = """
                INSERT INTO planificacion_suministros 
                (id, cantidad_requerida, proveedor, fecha_estimada, descripcion, costo_unitario) 
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (id_val, cant, prov, fecha_auto, desc, costo))
            
            conn.commit()
            conn.close()

            # 4. Actualizar todo
            self.cargar_tabla_planificacion() 
            self.graficar_costos_proveedores()
            self.limpiar_campos()
            print(f"Agregado con fecha: {fecha_auto}")

        except ValueError:
            print("Error: Revisa que ID, Cantidad y Costo sean números.")
        except Exception as e:
            print(f"Error: {e}")

    def limpiar_campos(self):
        self.ui.txt_id_material.clear()
        self.ui.txt_descripcion.clear()
        self.ui.txt_cantidad.clear()
        self.ui.txtproveedor.clear()
        self.ui.txtCosto.clear()
        self.ui.txtFecha.clear()
    
    def eliminar_suministro(self):
        # 1. Obtener el ID del LineEdit
        id_para_eliminar = self.ui.txt_id_material.text()

        if not id_para_eliminar:
            print("Error: Selecciona una fila de la tabla para eliminar")
            return

        try:
            # 2. Conexión y ejecución del borrado
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # SQL para eliminar por ID único
            query = "DELETE FROM planificacion_suministros WHERE id = ?"
            cursor.execute(query, (id_para_eliminar,))
            
            conn.commit()
            conn.close()

            # 3. Actualizar la interfaz
            print(f"Registro con ID {id_para_eliminar} eliminado")
            
            # Usamos tu método de actualización que me mostraste
            self.cargar_tabla_planificacion() 
            
            # También actualizamos la gráfica y limpiamos campos
            self.graficar_costos_proveedores()
            self.limpiar_campos()

        except Exception as e:
            print(f"Error al eliminar: {e}")


    def actualizar_suministro(self):
        try:
            # 1. Capturar los datos actualizados de la interfaz
            # Convertimos a los tipos correctos para evitar el error de 'datatype mismatch'
            id_val = int(self.ui.txt_id_material.text())
            cant   = int(self.ui.txt_cantidad.text())
            prov   = self.ui.txtproveedor.text()
            desc   = self.ui.txt_descripcion.text()
            costo  = float(self.ui.txtCosto.text())
            # La fecha suele mantenerse o actualizarse automáticamente con datetime
            from datetime import datetime
            fecha_act = datetime.now().strftime("%Y-%m-%d")

            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # 2. Query SQL para actualizar
            # Usamos SET para los nuevos valores y WHERE para localizar el ID original
            query = """
                UPDATE planificacion_suministros 
                SET cantidad_requerida = ?, proveedor = ?, fecha_estimada = ?, 
                    descripcion = ?, costo_unitario = ?
                WHERE id = ?
            """
            cursor.execute(query, (cant, prov, fecha_act, desc, costo, id_val))
            
            conn.commit()
            conn.close()

            # 3. Refrescar la interfaz
            print(f"Registro {id_val} actualizado correctamente.")
            self.cargar_tabla_planificacion() # Tu método de la imagen
            self.graficar_costos_proveedores()
            self.limpiar_campos()

        except ValueError:
            print("Error: Asegúrate de que los campos numéricos sean correctos antes de actualizar.")
        except Exception as e:
            print(f"Error al actualizar: {e}")

    def accion_exportar(self):
        # Llamamos a la función que está dentro de Exportar.py
        exito = Exportar.seleccionar_y_convertir()
        
        if exito:
            QMessageBox.information(self, "Exportación", "Los datos se han exportado correctamente.")

    
    
    #---------------Datos gestión proveedores---------------------

    def cargar_tabla_proveedores(self):
        try:
            # 1. Conexión a la base de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # 2. Seleccionar los datos en el orden de tu interfaz
            query = """
                SELECT id_proveedor, nombre_empresa, calificacion, 
                    proveedor_contacto, tiempo_entrega, estado 
                FROM gestion_proveedores
            """
            cursor.execute(query)
            datos = cursor.fetchall()

            # 3. Configuración de la tabla
            self.ui.tableWidget_2.setRowCount(len(datos))
            self.ui.tableWidget_2.setColumnCount(6)
            self.ui.tableWidget_2.verticalHeader().setVisible(False)

            # 4. Ajuste de columnas para que llenen el espacio
            header = self.ui.tableWidget_2.horizontalHeader()
            for i in range(6):
                header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

            # 5. Llenado de datos con alineación centrada
            for row_index, row_data in enumerate(datos):
                for col_index, value in enumerate(row_data):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    
                    # TRUCO PRO: Cambiar color según el estado
                    if col_index == 5: # Columna de "Estado"
                        if value == "Activo":
                            item.setForeground(QtGui.QColor("#00ff00")) # Verde
                        elif value == "Suspendido":
                            item.setForeground(QtGui.QColor("#ff0000")) # Rojo
                    
                    self.ui.tableWidget_2.setItem(row_index, col_index, item)
            
            conn.close()
        except Exception as e:
            print(f"Error al cargar tabla proveedores: {e}")

    
    # treewidget

    def cargar_arbol_gestion(self):
        try:
            self.ui.treeWidget_2.clear()
            
            # --- AJUSTE DE ESPACIO (Para que no se vea apretado) ---
            # Hacemos que la primera columna sea mucho más ancha que la segunda
            header = self.ui.treeWidget_2.header()
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
            header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            
            # Proveedor de iconos del sistema
            iconos = QFileIconProvider()
            icono_carpeta = iconos.icon(QFileIconProvider.Folder)
            icono_archivo = iconos.icon(QFileIconProvider.File)

            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()

            # --- CARPETA: SUMINISTROS ---
            rama_sum = QTreeWidgetItem(self.ui.treeWidget_2, ["Suministros y Compras", ""])
            rama_sum.setIcon(0, icono_carpeta) # Agrega la carpeta visual
            
            tablas_sum = [
                ("Inventario de Materiales", "materiales"),
                ("Planificación de Suministros", "planificacion_suministros"),
                ("Gestión de Proveedores", "gestion_proveedores")
            ]

            for nombre_v, tabla in tablas_sum:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                cant = cursor.fetchone()[0]
                item = QTreeWidgetItem(rama_sum, [nombre_v, f"{cant} registros"])
                item.setIcon(0, icono_archivo) # Icono de archivo para los hijos

            # --- CARPETA: INGENIERÍA ---
            rama_ing = QTreeWidgetItem(self.ui.treeWidget_2, ["Proyectos de Ingeniería", ""])
            rama_ing.setIcon(0, icono_carpeta)
            
            tablas_ing = [
                ("Diseño de Planos", "diseno"),
                ("Control de Cambios", "control_cambios"),
                ("Aseguramiento de Calidad", "aseguramiento_calidad")
            ]

            for nombre_v, tabla in tablas_ing:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                    cant = cursor.fetchone()[0]
                    item = QTreeWidgetItem(rama_ing, [nombre_v, f"{cant} items"])
                    item.setIcon(0, icono_archivo)
                except:
                    item = QTreeWidgetItem(rama_ing, [nombre_v, "Tabla vacía"])
                    item.setIcon(0, icono_archivo)

            # 4. Expandir todo y cerrar conexión
            self.ui.treeWidget_2.expandAll()
            conn.close()

        except Exception as e:
            print(f"Error al organizar el árbol: {e}")


    def controlar_navegacion_arbol(self, item, column):
        nombre = item.text(0)
        if nombre == "Gestión de Proveedores":
            self.cargar_tabla_proveedores() # El método que hicimos antes
        elif nombre == "Planificación de Suministros":
            self.cargar_tabla_planificacion() 

    
    #grafica

    def graficar_tiempos_proveedores(self):
        try:
            # 1. Obtener datos de la base de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            cursor.execute("SELECT nombre_empresa, tiempo_entrega FROM gestion_proveedores")
            datos = cursor.fetchall()
            conn.close()

            empresas = []
            tiempos = []

            for nombre, tiempo_str in datos:
                # Extraemos solo el número del texto "X días"
                try:
                    num_dias = int(tiempo_str.split()[0])
                    empresas.append(nombre)
                    tiempos.append(num_dias)
                except:
                    continue

            # 2. Limpiar el frame antes de dibujar para evitar el error 'NoneType'
            for i in reversed(range(self.ui.frame_28.layout().count())):
                self.ui.frame_28.layout().itemAt(i).widget().setParent(None)

            # 3. Crear la gráfica de barras
            fig, ax = plt.subplots(figsize=(5, 4), tight_layout=True)
            fig.patch.set_facecolor('#121212') # Color oscuro como tu interfaz
            ax.set_facecolor('#121212')

            colores = ['#00e5ff', '#00b8d4', '#0097a7'] # Tonos celestes de tu diseño
            bars = ax.bar(empresas, tiempos, color=colores)

            # Configuración de ejes
            ax.set_title("Días de Entrega por Proveedor", color='white', fontsize=12)
            ax.set_ylabel("Días", color='white')
            ax.tick_params(axis='both', colors='white')
            
            # Corrección del Warning de ticks
            ax.set_xticks(range(len(empresas)))
            ax.set_xticklabels(empresas, rotation=45, ha='right', fontsize=8)

            # 4. Mostrar en el frame
            canvas = FigureCanvas(fig)
            self.ui.frame_28.layout().addWidget(canvas)

        except Exception as e:
            print(f"Error en gráfica de proveedores: {e}")

    #botones

    def recuperar_datos_gestion_tabla(self):
        # 1. Obtener la fila seleccionada en la tabla de proveedores
        fila_seleccionada = self.ui.tableWidget_2.currentRow()

        if fila_seleccionada != -1:
            # 2. Extraer el texto respetando el orden de GESTIÓN DE PROVEEDORES
            id_prov   = self.ui.tableWidget_2.item(fila_seleccionada, 0).text()
            empresa   = self.ui.tableWidget_2.item(fila_seleccionada, 1).text()
            calif     = self.ui.tableWidget_2.item(fila_seleccionada, 2).text()
            contacto  = self.ui.tableWidget_2.item(fila_seleccionada, 3).text()
            tiempo    = self.ui.tableWidget_2.item(fila_seleccionada, 4).text()
            estado    = self.ui.tableWidget_2.item(fila_seleccionada, 5).text()

            # 3. Mandar los datos a los QLineEdit correctos
            self.ui.txt_id_poveedor.setText(id_prov)
            self.ui.txt_nombre_empresa.setText(empresa)
            self.ui.txt_calificacion.setText(calif)
            self.ui.txt_contacto_proveedor.setText(contacto)
            self.ui.txt_tiempo_entrega.setText(tiempo)
            self.ui.txt_estado_proveedor.setText(estado)

    def agregar_proveedor(self):
        # 1. Capturar los datos de los QLineEdit
        # Usamos los nombres exactos de tus objetos
        id_p      = self.ui.txt_id_poveedor.text()
        empresa   = self.ui.txt_nombre_empresa.text()
        calif     = self.ui.txt_calificacion.text()
        contacto  = self.ui.txt_contacto_proveedor.text()
        tiempo    = self.ui.txt_tiempo_entrega.text()
        estado    = self.ui.txt_estado_proveedor.text()

        # Validación básica: No dejar el ID o la Empresa vacíos
        if not id_p or not empresa:
            QMessageBox.warning(self, "Campos Vacíos", "El ID y el Nombre de Empresa son obligatorios.")
            return

        try:
            # 2. Conectar e insertar en SQL
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            query = """
                INSERT INTO gestion_proveedores 
                (id_proveedor, nombre_empresa, calificacion, proveedor_contacto, tiempo_entrega, estado) 
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            # Ejecutamos la inserción
            cursor.execute(query, (id_p, empresa, calif, contacto, tiempo, estado))
            
            conn.commit()
            conn.close()

            # 3. Éxito y Actualización
            QMessageBox.information(self, "Éxito", f"Proveedor '{empresa}' añadido correctamente.")
            
            # Limpiamos los campos y refrescamos la tabla y el árbol
            self.limpiar_campos_proveedores()
            self.cargar_tabla_proveedores()
            self.cargar_arbol_gestion() # Para que se actualice el conteo de registros
            self.graficar_tiempos_proveedores()

        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Error", "El ID del proveedor ya existe.")
        except Exception as e:
            QMessageBox.critical(self, "Error Crítico", f"No se pudo guardar: {e}")


    def limpiar_campos_proveedores(self):
        self.ui.txt_id_poveedor.clear()
        self.ui.txt_nombre_empresa.clear()
        self.ui.txt_calificacion.clear()
        self.ui.txt_contacto_proveedor.clear()
        self.ui.txt_tiempo_entrega.clear()
        self.ui.txt_estado_proveedor.clear()


    def eliminar_proveedor(self):
        # 1. Obtener la fila seleccionada y el ID del proveedor
        fila_seleccionada = self.ui.tableWidget_2.currentRow()
        
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Selección", "Por favor, selecciona un proveedor de la tabla para eliminar.")
            return

        id_proveedor = self.ui.tableWidget_2.item(fila_seleccionada, 0).text()
        nombre_empresa = self.ui.tableWidget_2.item(fila_seleccionada, 1).text()

        # 2. Confirmación de seguridad
        respuesta = QMessageBox.question(
            self, 
            "Confirmar Eliminación", 
            f"¿Estás seguro de que deseas eliminar a '{nombre_empresa}' permanentemente?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            try:
                # 3. Ejecutar la eliminación en SQL
                conn = sqlite3.connect("ingenieria.db")
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM gestion_proveedores WHERE id_proveedor = ?", (id_proveedor,))
                
                conn.commit()
                conn.close()

                # 4. Actualizar la interfaz
                QMessageBox.information(self, "Éxito", "Proveedor eliminado correctamente.")
                self.cargar_tabla_proveedores()
                self.cargar_arbol_gestion() # Para actualizar el conteo en el TreeWidget_2
                self.limpiar_campos_proveedores() # Limpia los QLineEdit
                self.graficar_tiempos_proveedores()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el registro: {e}")

    def actualizar_proveedor(self):
        try:
            # 1. Capturar los datos desde los QLineEdit
            id_p      = self.ui.txt_id_poveedor.text()
            empresa   = self.ui.txt_nombre_empresa.text()
            calif     = self.ui.txt_calificacion.text()
            contacto  = self.ui.txt_contacto_proveedor.text()
            tiempo    = self.ui.txt_tiempo_entrega.text()
            estado    = self.ui.txt_estado_proveedor.text()

            # Validación: El ID es necesario para saber qué registro actualizar
            if not id_p:
                QMessageBox.warning(self, "Error", "No hay un ID seleccionado para actualizar.")
                return

            # 2. Ejecutar la actualización en la base de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            query = """
                UPDATE gestion_proveedores 
                SET nombre_empresa = ?, calificacion = ?, proveedor_contacto = ?, 
                    tiempo_entrega = ?, estado = ?
                WHERE id_proveedor = ?
            """
            
            cursor.execute(query, (empresa, calif, contacto, tiempo, estado, id_p))
            
            conn.commit()
            conn.close()

            # 3. Notificar y refrescar
            QMessageBox.information(self, "Actualización", f"Datos de '{empresa}' actualizados con éxito.")
            
            self.cargar_tabla_proveedores()     # Refresca la tabla visual
            self.graficar_tiempos_proveedores() # Actualiza la gráfica con los nuevos tiempos
            self.limpiar_campos_proveedores()   # Limpia los campos de texto
            self.graficar_tiempos_proveedores()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al actualizar el proveedor: {e}")

    