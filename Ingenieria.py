import sqlite3
import os
import Exportar
import pandas as pd
from PySide6.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView, QFrame,QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt
from PySide6.QtGui import QColor ,QPixmap# Importación necesaria para el color de letra
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

            # Limpieza estética inicial
            self.configurar_tabla_estetica()
            # Carga de datos
            self.cargar_datos_requisitos()
            if hasattr(self.ui, 'pushButton_4'):
                self.ui.pushButton_4.clicked.connect(self.añadir_requisito)
        
            # Cargamos los datos iniciales
            self.cargar_datos_requisitos()
            # Cargar datos por primera vez al abrir
            self.cargar_datos_tabla()
            

            # ... dentro de cargar_datos_requisitos o en el __init__ ...
        
            tabla = self.ui.findChild(object, "tableWidget")
            if tabla:
                # Conectamos el clic en la tabla con la función de transferencia
                tabla.itemClicked.connect(self.transferir_datos_a_campos)

            # Dentro del __init__
            if hasattr(self.ui, 'pushButton_3'):
                self.ui.pushButton_3.clicked.connect(self.actualizar_requisito)

            # Dentro del método __init__
            if hasattr(self.ui, 'btn_eliminar'):
                self.ui.btn_eliminar.clicked.connect(self.eliminar_requisito)

            if hasattr(self.ui, 'pushButton'): 
                self.ui.pushButton.clicked.connect(self.accion_exportar)

            # cargar datos de diseño wireframe

            self.ir_a_diseno()
            
            if hasattr(self.ui, 'pushButton_7'):
                self.ui.pushButton_7.clicked.connect(self.añadir_diseno)
            
            if hasattr(self.ui, 'pushButton_6'):
                self.ui.pushButton_6.clicked.connect(self.actualizar_diseno)
            # Dentro del __init__
            if hasattr(self.ui, 'btn_eliminar_2'):
                self.ui.btn_eliminar_2.clicked.connect(self.eliminar_diseno)

            if hasattr(self.ui, 'pushButton_2'): 
                self.ui.pushButton_2.clicked.connect(self.accion_exportar)

            # cargar datos de materiales
            
            self.cargar_datos_materiales()
           




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
            
            # Si el índice es 1 (Gestión), cargamos los datos
            if indice == 1:
                self.cargar_datos_requisitos()


    def regresar(self):
        # Importamos aquí dentro para evitar errores de importación circular
        from App import VentanaInicio
        self.nueva = VentanaInicio()
        self.nueva.show()
        self.close() # Cierra la ventana de Ingeniería


    def configurar_tabla_estetica(self):
        tabla = self.ui.findChild(object, "tableWidget")
        if tabla:
            # Eliminar números de fila
            tabla.verticalHeader().setVisible(False)
            # Quitar bordes blancos de Windows (Viewport)
            tabla.viewport().setAutoFillBackground(False)
            # Hacer que las columnas llenen el ancho
            tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # Evitar que Windows pinte encima de tu QSS
            tabla.horizontalHeader().setHighlightSections(False)


    def cargar_datos_requisitos(self):
        tabla = self.ui.findChild(object, "tableWidget")
        if not tabla:
            print("No se encontró el tableWidget")
            return

        # --- LIMPIEZA TOTAL DE ESTILOS DE WINDOWS ---
        tabla.setAlternatingRowColors(False)      # Todas las filas del mismo color
        tabla.verticalHeader().setVisible(False)   # Quita los números laterales
        tabla.setFrameShape(QFrame.NoFrame)        # Quita el borde blanco exterior
        tabla.viewport().setAutoFillBackground(False) # Usa el fondo del QSS (#12151c)
        tabla.setShowGrid(True)                    # Muestra tu gridline-color neón

        try:
            ruta_db = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            conn = sqlite3.connect(ruta_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM requisitos")
            datos = cursor.fetchall()
            
            # Obtener nombres de columnas
            nombres_columnas = [desc[0] for desc in cursor.description]
            
            tabla.setRowCount(len(datos))
            tabla.setColumnCount(len(nombres_columnas))
            tabla.setHorizontalHeaderLabels(nombres_columnas)

            # Llenar la tabla
            for f_idx, fila in enumerate(datos):
                for c_idx, valor in enumerate(fila):
                    item = QTableWidgetItem(str(valor))
                    
                    # FORZAR TEXTO BLANCO (Para que se vea sobre el fondo negro)
                    item.setForeground(QColor("white"))
                    
                    # Centrar el texto (opcional, mejora la estética)
                    item.setTextAlignment(Qt.AlignCenter)
                    
                    tabla.setItem(f_idx, c_idx, item)
            
            conn.close()
            
            # Ajustar columnas al final para que no se corten
            tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        except sqlite3.Error as e:
            print(f"Error de base de datos: {e}")


    # --- NUEVA FUNCIÓN ---
    def transferir_datos_a_campos(self, item):
        # Obtenemos la fila donde se hizo clic
        fila = item.row()
        tabla = self.ui.findChild(object, "tableWidget")

        # Extraemos los datos de cada columna (ID, Nombre, Petición, Prioridad)
        # Columna 0 = ID, 1 = Nombre, 2 = Petición, 3 = Prioridad
        id_val = tabla.item(fila, 0).text()
        nombre_val = tabla.item(fila, 1).text()
        peticion_val = tabla.item(fila, 2).text()
        prioridad_val = tabla.item(fila, 3).text()

        # Buscamos los lineEdits según tus capturas de Designer
        txt_id = self.ui.findChild(object, "lineEdit")      # ID
        txt_nombre = self.ui.findChild(object, "lineEdit_2") # Nombre del requisito
        txt_peticion = self.ui.findChild(object, "lineEdit_5") # Petición
        cmb_prioridad = self.ui.findChild(object, "comboBox") # Prioridad

        # Asignamos los valores a los campos
        if txt_id: txt_id.setText(id_val)
        if txt_nombre: txt_nombre.setText(nombre_val)
        if txt_peticion: txt_peticion.setText(peticion_val)
        
        # Para el ComboBox, buscamos el texto que coincida (Crítica, Alta, etc.)
        if cmb_prioridad:
            index = cmb_prioridad.findText(prioridad_val)
            if index >= 0:
                cmb_prioridad.setCurrentIndex(index)


    # ... Añadir...

    def añadir_requisito(self):
        # 1. Obtener datos de los widgets
        id_val = self.ui.lineEdit.text().strip()
        nombre_val = self.ui.lineEdit_2.text().strip()
        peticion_val = self.ui.lineEdit_5.text().strip()
        prioridad_val = self.ui.comboBox.currentText()

        if not id_val or not nombre_val:
            QMessageBox.warning(self, "Error", "El ID y el Nombre son obligatorios.")
            return

        try:
            ruta_db = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            conn = sqlite3.connect(ruta_db)
            cursor = conn.cursor()
            
            # 2. Insertar en las columnas correctas
            # Cambia esta línea en tu función añadir_requisito:
            query = "INSERT OR REPLACE INTO requisitos (id, nombre, peticion, prioridad) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (id_val, nombre_val, peticion_val, prioridad_val))
            
            conn.commit()
            conn.close()

            # 3. Limpiar los campos
            self.ui.lineEdit.clear()
            self.ui.lineEdit_2.clear()
            self.ui.lineEdit_5.clear()

            # 4. ACTUALIZACIÓN CRUCIAL: Se vuelve a llamar a la función de carga
            self.cargar_datos_requisitos()
            
            print("Datos añadidos y tabla actualizada.")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

        

    
    def cargar_datos_requisitos(self):
        # Buscamos tu tableWidget
        tabla = self.ui.findChild(object, "tableWidget")
        if not tabla: return

        # --- APLICAR ESTÉTICA NEÓN (Fuerza el QSS y quita el blanco) ---
        tabla.verticalHeader().setVisible(False)      # Quita números de fila
        tabla.setAlternatingRowColors(False)          # Quita filas blancas alternadas
        tabla.viewport().setAutoFillBackground(False)  # Usa el fondo negro del QSS
        tabla.setFrameShape(QFrame.NoFrame)            # Quita bordes de Windows
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.configurar_tabla_estetica()

        try:
            ruta_db = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            conn = sqlite3.connect(ruta_db)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM requisitos")
            datos = cursor.fetchall()
            
            tabla.setRowCount(len(datos))
            tabla.setColumnCount(4)
            tabla.setHorizontalHeaderLabels(["ID", "NOMBRE", "PETICION", "PRIORIDAD"])

            # Llenado de celdas
            for f_idx, fila in enumerate(datos):
                for c_idx, valor in enumerate(fila):
                    item = QTableWidgetItem(str(valor))
                    item.setForeground(QColor("white")) # Letras blancas sobre fondo negro
                    item.setTextAlignment(Qt.AlignCenter)
                    tabla.setItem(f_idx, c_idx, item)
            
            conn.close()
        except sqlite3.Error as e:
            print(f"Error al cargar: {e}")


    
    def cargar_datos_tabla(self):
        """Función para refrescar el QTableWidget con los datos actuales"""
        try:
            conexion = sqlite3.connect("Ingenieria.db")
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM requisitos")
            datos = cursor.fetchall()

            # Configurar filas del tableWidget
            self.ui.tableWidget.setRowCount(len(datos))
            
            for i, fila in enumerate(datos):
                for j, valor in enumerate(fila):
                    self.ui.tableWidget.setItem(i, j, QTableWidgetItem(str(valor)))
            
            conexion.close()
        except Exception as e:
            print(f"Error al cargar tabla: {e}")

    #------------------Actualizar-------------------

    def actualizar_requisito(self):
        # 1. Obtener los valores de los campos
        id_val = self.ui.lineEdit.text().strip()      # El ID es la llave para buscar
        nombre_val = self.ui.lineEdit_2.text().strip()
        peticion_val = self.ui.lineEdit_5.text().strip()
        prioridad_val = self.ui.comboBox.currentText()

        # 2. Validación básica
        if not id_val:
            QMessageBox.warning(self, "Error", "Debe seleccionar un requisito (ID) para actualizar.")
            return

        try:
            ruta_db = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            conn = sqlite3.connect(ruta_db)
            cursor = conn.cursor()

            # 3. Sentencia SQL UPDATE
            # Actualizamos nombre, peticion y prioridad donde el id coincida
            query = """
                UPDATE requisitos 
                SET nombre = ?, peticion = ?, prioridad = ? 
                WHERE id = ?
            """
            cursor.execute(query, (nombre_val, peticion_val, prioridad_val, id_val))
            
            conn.commit()
            
            # Verificamos si realmente se actualizó algo
            if cursor.rowcount > 0:
                QMessageBox.information(self, "Éxito", f"Requisito {id_val} actualizado correctamente.")
                # 4. Refrescar la tabla para ver los cambios
                self.cargar_datos_requisitos()
            else:
                QMessageBox.warning(self, "Error", "No se encontró ningún requisito con ese ID.")

            conn.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"No se pudo actualizar: {e}")

    #-----------------Eliminar--------------------

    def eliminar_requisito(self):
        # 1. Obtener el ID del campo de texto (donde se carga al hacer clic en la tabla)
        id_val = self.ui.lineEdit.text().strip()

        # 2. Validación: Si no hay ID, no sabemos qué borrar
        if not id_val:
            QMessageBox.warning(self, "Atención", "Por favor, seleccione un requisito de la tabla para eliminar.")
            return

        # 3. Confirmación de seguridad
        respuesta = QMessageBox.question(self, "Confirmar Eliminación", 
                                        f"¿Está seguro de que desea eliminar el requisito con ID: {id_val}?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                ruta_db = os.path.join(os.path.dirname(__file__), "ingenieria.db")
                conn = sqlite3.connect(ruta_db)
                cursor = conn.cursor()

                # 4. Sentencia SQL DELETE
                query = "DELETE FROM requisitos WHERE id = ?"
                cursor.execute(query, (id_val,))
                
                conn.commit()

                if cursor.rowcount > 0:
                    QMessageBox.information(self, "Éxito", "Requisito eliminado correctamente.")
                    
                    # 5. Limpiar los campos después de eliminar
                    self.ui.lineEdit.clear()
                    self.ui.lineEdit_2.clear()
                    self.ui.lineEdit_5.clear()
                    
                    # 6. Refrescar la tabla para actualizar la vista neón
                    self.cargar_datos_requisitos()
                else:
                    QMessageBox.warning(self, "Error", "No se encontró el registro en la base de datos.")

                conn.close()

            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el registro: {e}")

    #--------------------------------Exportar a Excel--------------------

    def accion_exportar(self):
        # Llamamos a la función que está dentro de Exportar.py
        exito = Exportar.seleccionar_y_convertir()
        
        if exito:
            QMessageBox.information(self, "Exportación", "Los datos se han exportado correctamente.")
        else:
            QMessageBox.critical(self, "Error", "No se pudo completar la exportación.")



   #----------Wireframe---------------

    def cargar_datos_diseno(self):
        # Buscamos el tableWidget específico de esta página
        tabla = self.ui.findChild(object, "TablaWire")
        if not tabla:
            return

        # --- CONFIGURACIÓN ESTÉTICA (Igual que la anterior) ---
        tabla.verticalHeader().setVisible(False)      # Quita números de fila
        tabla.setAlternatingRowColors(False)          # Evita filas blancas
        tabla.viewport().setAutoFillBackground(False)  # Fondo negro del QSS
        tabla.setFrameShape(QFrame.NoFrame)            # Quita bordes de Windows
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        try:
            ruta_db = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            conn = sqlite3.connect(ruta_db)
            cursor = conn.cursor()
            
            # Consultamos la tabla 'diseno'
            cursor.execute("SELECT * FROM diseno")
            datos = cursor.fetchall()
            
            # Obtener nombres de columnas dinámicamente
            columnas = [desc[0] for desc in cursor.description]
            
            tabla.setRowCount(len(datos))
            tabla.setColumnCount(len(columnas))
            tabla.setHorizontalHeaderLabels([c.upper() for c in columnas])

            # Llenar celdas con texto blanco
            for f_idx, fila in enumerate(datos):
                for c_idx, valor in enumerate(fila):
                    item = QTableWidgetItem(str(valor))
                    item.setForeground(QColor("white")) # Letras blancas
                    item.setTextAlignment(Qt.AlignCenter)
                    tabla.setItem(f_idx, c_idx, item)
            
            conn.close()
        except sqlite3.Error as e:
            print(f"Error al cargar tabla diseño: {e}")

    
    # cargar imagen
    
    def actualizar_vista_previa(self, nombre_archivo):
        # 1. Ruta a la carpeta WireFrame
        ruta_base = os.path.dirname(__file__)
        ruta_imagen = os.path.join(ruta_base, "WireFrame", nombre_archivo)
        
        label_foto = self.ui.findChild(object, "image") # Tu label de imagen
        
        if label_foto:
            if os.path.exists(ruta_imagen) and nombre_archivo != "":
                pixmap = QPixmap(ruta_imagen)
                # Ajustamos la imagen al tamaño del label sin deformarla demasiado
                label_foto.setPixmap(pixmap.scaled(
                    label_foto.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                ))
                label_foto.setScaledContents(True) 
            else:
                # Si no hay imagen o no existe, ponemos un fondo oscuro o texto
                label_foto.clear()
                label_foto.setText("S/N Wireframe")
                label_foto.setStyleSheet("color: #00ffff; border: 1px solid #00ffff;")


    def cargar_datos_diseno(self):
        tabla = self.ui.TablaWire
        if not tabla: return

        # Estética segura
        tabla.setFrameShape(QFrame.NoFrame) # Esto es lo que PySide6 espera 
        tabla.verticalHeader().setVisible(False)
        # Localizamos la tabla de la página 2
        tabla = self.ui.findChild(object, "TablaWire")
        if not tabla: return

        # Estética segura: evita el TypeError
        tabla.setFrameShape(QFrame.NoFrame) 
        tabla.verticalHeader().setVisible(False)
        tabla.setAlternatingRowColors(False)
        tabla.viewport().setAutoFillBackground(False)

        try:
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            # Asegúrate de que la tabla en la DB sea 'diseno'
            cursor.execute("SELECT * FROM diseno") 
            datos = cursor.fetchall()
            
            tabla.setRowCount(len(datos))
            tabla.setColumnCount(5) # Ajusta según tus columnas (ID, COMPONENTE, etc)

            for f_idx, fila in enumerate(datos):
                for c_idx, valor in enumerate(fila):
                    item = QTableWidgetItem(str(valor))
                    item.setForeground(QColor("white"))
                    item.setTextAlignment(Qt.AlignCenter)
                    tabla.setItem(f_idx, c_idx, item)
            conn.close()
            
            # Conectar el clic UNA SOLA VEZ para evitar cierres inesperados
            try: tabla.itemClicked.disconnect() 
            except: pass
            tabla.itemClicked.connect(self.al_seleccionar_diseno)

        except Exception as e:
            print(f"Error al cargar diseño: {e}")


    def al_seleccionar_diseno(self, item):
        fila = item.row()
        tabla = self.ui.TablaWire # Tu tabla de la página 2
        # 1. Obtenemos el nombre del componente (Columna 2: COMPONENTE)
        nombre_componente = self.ui.TablaWire.item(fila, 2).text() 
        
        # 2. Le sumamos la extensión .png para que coincida con la carpeta
        nombre_archivo_final = f"{nombre_componente}.png"
        
        print(f"Buscando imagen: {nombre_archivo_final}") # Para depurar en terminal
        
        # 3. Llamamos a la función que ya tienes para mostrarla
        self.actualizar_vista_previa(nombre_archivo_final)
        try:
            # 1. Extraer datos de todas las columnas (0 a 4)
            val_tabla = tabla.item(fila, 0).text()
            val_id = tabla.item(fila, 1).text()
            val_componente = tabla.item(fila, 2).text()
            val_estado = tabla.item(fila, 3).text()
            val_version = tabla.item(fila, 4).text() # La columna VERSIÓN

            # 2. Subir datos a los LineEdits correspondientes
            self.ui.lineEdit_TABLA.setText(val_tabla)
            self.ui.lineEdit_ID_DISENO.setText(val_id)
            self.ui.lineEdit_COMPONENTE.setText(val_componente)
            self.ui.lineEdit_ESTADO.setText(val_estado)
            
            # Verificamos que el nombre coincida con el de tu Designer para VERSIÓN
            if hasattr(self.ui, 'lineEdit_VERSION'):
                self.ui.lineEdit_VERSION.setText(val_version) #

            # 3. Actualizar la imagen Wireframe
            # Recuerda que usamos el nombre del componente + la extensión
            self.actualizar_vista_previa(f"{val_componente}.png")

        except Exception as e:
            print(f"Error al transferir datos de diseño: {e}")


    def ir_a_diseno(self):
        self.ui.stackedWidget.setCurrentIndex(2) 
        # Solo conectamos la señal una vez para evitar errores
        try:
            self.ui.TablaWire.itemClicked.disconnect() # Limpiamos conexiones previas
        except:
            pass
        self.ui.TablaWire.itemClicked.connect(self.al_seleccionar_diseno)
        self.cargar_datos_diseno()

    
    
    #------Botones wireframe ---------
    def añadir_diseno(self):
        # 1. Capturar datos de tus LineEdits específicos
        val_tabla = self.ui.lineEdit_TABLA.text().strip()
        val_id = self.ui.lineEdit_ID_DISENO.text().strip()
        val_comp = self.ui.lineEdit_COMPONENTE.text().strip()
        val_est = self.ui.lineEdit_ESTADO.text().strip()
        val_ver = self.ui.lineEdit_VERSION.text().strip()

        # 2. Validación: ID y Componente son esenciales
        if not val_id or not val_comp:
            QMessageBox.warning(self, "Campos Vacíos", "El ID y el Componente son obligatorios.")
            return

        try:
            # 3. Conexión a la base de datos
            ruta_db = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            conn = sqlite3.connect(ruta_db)
            cursor = conn.cursor()
            
            # 4. Sentencia SQL para la tabla 'diseno'
            query = """
                INSERT INTO diseno (tabla, id, componente, estado, version) 
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (val_tabla, val_id, val_comp, val_est, val_ver))
            
            conn.commit()
            conn.close()

            # 5. Limpiar los campos para el siguiente ingreso
            self.ui.lineEdit_TABLA.clear()
            self.ui.lineEdit_ID_DISENO.clear()
            self.ui.lineEdit_COMPONENTE.clear()
            self.ui.lineEdit_ESTADO.clear()
            self.ui.lineEdit_VERSION.clear()

            # 6. Actualizar la tabla visualmente
            self.cargar_datos_diseno()
            
            # Opcional: Intentar cargar la imagen del nuevo componente
            self.actualizar_vista_previa(f"{val_comp}.png")

            QMessageBox.information(self, "Éxito", f"Diseño '{val_comp}' añadido correctamente.")

        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Error", f"El ID '{val_id}' ya existe en la base de datos.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de DB", f"Ocurrió un error: {e}")

    
    def actualizar_diseno(self):
        # 1. Obtener valores de los campos de la página de diseño
        val_tabla = self.ui.lineEdit_TABLA.text().strip()
        val_id = self.ui.lineEdit_ID_DISENO.text().strip() # Usado como llave en WHERE
        val_comp = self.ui.lineEdit_COMPONENTE.text().strip()
        val_est = self.ui.lineEdit_ESTADO.text().strip()
        val_ver = self.ui.lineEdit_VERSION.text().strip()

        # 2. Validación: Necesitamos el ID para saber qué actualizar
        if not val_id:
            QMessageBox.warning(self, "Atención", "Seleccione un diseño de la tabla para actualizar.")
            return

        try:
            ruta_db = os.path.join(os.path.dirname(__file__), "ingenieria.db")
            conn = sqlite3.connect(ruta_db)
            cursor = conn.cursor()

            # 3. Sentencia SQL UPDATE para la tabla diseno
            # Actualizamos las otras columnas basándonos en el ID
            query = """
                UPDATE diseno 
                SET tabla = ?, componente = ?, estado = ?, version = ? 
                WHERE id = ?
            """
            cursor.execute(query, (val_tabla, val_comp, val_est, val_ver, val_id))
            
            conn.commit()
            
            # 4. Verificar si se realizó el cambio
            if cursor.rowcount > 0:
                QMessageBox.information(self, "Éxito", f"El componente '{val_comp}' ha sido actualizado.")
                # Refrescar la tabla y la imagen
                self.cargar_datos_diseno()
                self.actualizar_vista_previa(f"{val_comp}.png")
            else:
                QMessageBox.warning(self, "Error", "No se encontró el registro para actualizar.")

            conn.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de DB", f"No se pudo actualizar: {e}")


    def eliminar_diseno(self):
        # 1. Tomamos los datos de los LineEdits
        # SEGÚN TU DB: El ID es el código corto (ENG-01) y TABLA es el nombre (Motor)
        codigo_id = self.ui.lineEdit_TABLA.text().strip() 
        nombre_diseno = self.ui.lineEdit_ID_DISENO.text().strip()

        if not codigo_id:
            QMessageBox.warning(self, "Atención", "No hay un código seleccionado para borrar.")
            return

        # 2. Confirmación
        if QMessageBox.question(self, "Confirmar", f"¿Borrar registro {codigo_id}?") == QMessageBox.Yes:
            try:
                conn = sqlite3.connect("ingenieria.db")
                cursor = conn.cursor()

                # 3. EJECUCIÓN: Usamos los nombres exactos de tu imagen image_e1a08c.png
                # Borramos donde la columna 'id' sea igual al código corto
                cursor.execute("DELETE FROM diseno WHERE id = ?", (codigo_id,))
                conn.commit()

                # 4. Verificación de éxito real
                if cursor.rowcount > 0:
                    QMessageBox.information(self, "Éxito", f"Registro {codigo_id} eliminado de la base de datos.")
                    
                    # 5. Limpiar interfaz
                    self.ui.lineEdit_TABLA.clear()
                    self.ui.lineEdit_ID_DISENO.clear()
                    self.ui.lineEdit_COMPONENTE.clear()
                    self.ui.lineEdit_ESTADO.clear()
                    self.ui.lineEdit_VERSION.clear()
                    self.ui.image.clear()
                    self.ui.image.setText("S/N Wireframe") #

                    # 6. REFRESCAR TABLA: Vital para ver el cambio
                    self.cargar_datos_diseno()
                else:
                    # Si entra aquí es porque buscó el código y no estaba
                    QMessageBox.warning(self, "Error", f"No se encontró el código '{codigo_id}' en la base de datos.")

                conn.close()
            except Exception as e:
                QMessageBox.critical(self, "Error de Sistema", f"Error: {e}")



   #----------------------Materiales-----------------------------------------
    def cargar_datos_materiales(self):
        try:
            # 1. Conexión a la base de datos
            conn = sqlite3.connect("ingenieria.db")
            cursor = conn.cursor()
            
            # 2. Consultar todos los datos de la tabla materiales
            cursor.execute("SELECT id_material, descripcion, cantidad, proveedor, unidad, costo_unidad FROM materiales")
            datos = cursor.fetchall()
            
            # 3. Preparar el TableWidget
            # Importante: Limpiar filas existentes para refrescar correctamente
            self.ui.tableWidget_3.setRowCount(0)
            
            # 4. Insertar los datos fila por fila
            for fila_numero, fila_datos in enumerate(datos):
                self.ui.tableWidget_3.insertRow(fila_numero)
                for columna_numero, dato in enumerate(fila_datos):
                    # Creamos el ítem y lo insertamos en la celda correspondiente
                    item = QTableWidgetItem(str(dato))
                    # Opcional: Centrar el texto para que se vea mejor
                    item.setTextAlignment(Qt.AlignCenter)
                    self.ui.tableWidget_3.setItem(fila_numero, columna_numero, item)
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los materiales: {e}")
   