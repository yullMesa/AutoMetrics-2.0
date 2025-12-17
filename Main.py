import sys
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QToolButton, QStackedWidget, QWidget, QVBoxLayout, QSizePolicy, QFrame, QMessageBox
from PySide6.QtUiTools import QUiLoader 
from PySide6.QtCore import QUrl, QTimer
import recursos_rc
import sqlite3
from PySide6.QtWebEngineWidgets import QWebEngineView 
from PySide6.QtCore import QUrl
import threading
import dash
import os
# Asegúrate de que esto esté en la parte superior del archivo (o en tu módulo dash_app.py):

from dash import html # <- ¡Esta línea es la clave para resolver el error!
from dash import dcc  # dcc (Dash Core Components) también se necesita para gráficos
import plotly.express as px
import pandas as pd
from dash_app import iniciar_servidor_en_hilo

# Si True, las ventanas tomarán exactamente el tamaño definido en sus .ui (coincidir con Designer)
MATCH_UI_SIZE_EXACT = True



# Función de conexión
def conectar_db(nombre_archivo_db="autometrics_ingenieria.db"):
    try:
        # Si el archivo no existe, SQLite lo crea automáticamente.
        conexion = sqlite3.connect(nombre_archivo_db)
        print("Conexión a SQLite exitosa.")
        return conexion
    except sqlite3.Error as e:
        print(f"Error al conectar a SQLite: {e}")
        return None

# Ejemplo de uso:
db_conn = conectar_db()
if db_conn:
    # Asegúrate de cerrar la conexión cuando termines
    db_conn.close()



class VentanaPrincipal(QDialog):
    def __init__(self):
        super().__init__()
        
        # Usando QUiLoader para cargar el archivo .ui directamente
        loader = QUiLoader()
        self.ui = loader.load("inicio.ui", self)
        
        # Aseguramos que la ventana principal de la UI sea la que se muestra
        if self.ui:
            self.setWindowTitle("AutoMetrics 2.0")
            # Aplicar tamaño desde el archivo .ui para que coincida con Designer si está definido
            try:
                geom = self.ui.geometry()
                w = geom.width()
                h = geom.height()
                if w > 0 and h > 0:
                    self.resize(w, h)
                    print(f"Ventana Inicio: aplicando tamaño desde 'inicio.ui': {w}x{h}")
            except Exception:
                pass


        # 📌 CONEXIÓN CLAVE
        self.ui.btn_Ingenieria.clicked.connect(self.abrir_ingenieria)

    def abrir_ingenieria(self):
        self.ventana_ingenieria = VentanaIngenieria() 
        self.ventana_ingenieria.show()
        self.ui.close()

        
        
        # ... (resto de las conexiones) ...

class VentanaIngenieria(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        loader = QUiLoader()
        
        # 1. Cargar el diseño en un objeto temporal, sin parent
        # Esto crea una instancia completa de QMainWindow con el diseño de Ingenieria.ui
        self.loaded_ui = loader.load("Ingenieria.ui") 
        
        # 2. 📌 CÓDIGO CLAVE: Establecer el widget central y la barra de menú 
        # del diseño cargado en la ventana de Python (self)
        
        # A. Asignamos el centralwidget (que contiene tu barra lateral y QStackedWidget)
        self.setCentralWidget(self.loaded_ui.centralWidget()) 
        
        # B. Asignamos la barra de menú si existe
        self.setMenuBar(self.loaded_ui.menuBar()) 
        
        # 3. Propiedades y Dimensiones (usar tamaño definido en el .ui para coincidir con Designer)
        self.setWindowTitle("AutoMetrics - Ingeniería de Producto")

        # Manual mapping overrides (useful for forcing a button to open a specific page)
        # Example: {'btn_diseno_cad': 'page'} will make the Diseño button open the page whose objectName == 'page'
        self.manual_mapping = {
            'btn_diseno_cad': 'page'
        }
        # Aplicar tamaño desde el archivo .ui (si está definido en el diseñador)
        try:
            ui_geom = self.loaded_ui.geometry()
            ui_w = ui_geom.width()
            ui_h = ui_geom.height()
            if ui_w > 0 and ui_h > 0:
                self.resize(ui_w, ui_h)
                self._designed_size = (ui_w, ui_h)
                print(f"Aplicando tamaño de 'Ingenieria.ui': {ui_w}x{ui_h}")
            else:
                # fallback al tamaño mínimo del central widget
                central = self.loaded_ui.centralWidget()
                if central:
                    sh = central.sizeHint()
                    if sh.width() > 0 and sh.height() > 0:
                        self.resize(sh.width(), sh.height())
                        self._designed_size = (sh.width(), sh.height())
        except Exception as e:
            print(f"Aviso: no se pudo aplicar tamaño desde UI ({e}), usando tamaño por defecto.")
            self.resize(1070, 870)


        # 4. Inicialización y Conexiones (Acceso a widgets usando self.loaded_ui)
        # Los widgets viven en el objeto cargado, así que usamos findChild en él.
        
        self.stacked_widget = self.loaded_ui.findChild(QStackedWidget, 'stacked_widget_ingenieria')
        # Fallback para stacked_widget si no se encuentra directamente
        if not self.stacked_widget:
            central = self.loaded_ui.centralWidget() if hasattr(self.loaded_ui, 'centralWidget') else None
            if central:
                self.stacked_widget = central.findChild(QStackedWidget, 'stacked_widget_ingenieria')
            if not self.stacked_widget:
                self.stacked_widget = self.findChild(QStackedWidget, 'stacked_widget_ingenieria')

        
        # Inicializar todos los botones para las conexiones
        self.btn_dashboard = self.loaded_ui.findChild(QToolButton, 'btn_dashboard')
        self.btn_requisitos = self.loaded_ui.findChild(QToolButton, 'btn_requisitos')
        self.btn_diseno_cad = self.loaded_ui.findChild(QToolButton, 'btn_diseno_cad')
        self.btn_gestion_bom = self.loaded_ui.findChild(QToolButton, 'btn_gestion_bom')
        self.btn_control_cambios = self.loaded_ui.findChild(QToolButton, 'btn_control_cambios')
        self.btn_calidad = self.loaded_ui.findChild(QToolButton, 'btn_calidad')
        self.btn_reportes = self.loaded_ui.findChild(QToolButton, 'btn_reportes')

        # DEBUG: mostrar qué botones se encontraron


        # Fallback: si algunos botones no se encontraron en 'loaded_ui', intentar buscarlos en centralWidget o en self
        central = self.loaded_ui.centralWidget() if hasattr(self.loaded_ui, 'centralWidget') else None
        if central:
            if not self.btn_dashboard:
                self.btn_dashboard = central.findChild(QToolButton, 'btn_dashboard')
            if not self.btn_requisitos:
                self.btn_requisitos = central.findChild(QToolButton, 'btn_requisitos')
            if not self.btn_diseno_cad:
                self.btn_diseno_cad = central.findChild(QToolButton, 'btn_diseno_cad')
            if not self.btn_gestion_bom:
                self.btn_gestion_bom = central.findChild(QToolButton, 'btn_gestion_bom')
            if not self.btn_control_cambios:
                self.btn_control_cambios = central.findChild(QToolButton, 'btn_control_cambios')
            if not self.btn_calidad:
                self.btn_calidad = central.findChild(QToolButton, 'btn_calidad')
            if not self.btn_reportes:
                self.btn_reportes = central.findChild(QToolButton, 'btn_reportes')

        # También intentar buscarlos en la propia ventana (self)
        if not self.btn_dashboard:
            self.btn_dashboard = self.findChild(QToolButton, 'btn_dashboard')
        if not self.btn_requisitos:
            self.btn_requisitos = self.findChild(QToolButton, 'btn_requisitos')
        if not self.btn_diseno_cad:
            self.btn_diseno_cad = self.findChild(QToolButton, 'btn_diseno_cad')
        if not self.btn_gestion_bom:
            self.btn_gestion_bom = self.findChild(QToolButton, 'btn_gestion_bom')
        if not self.btn_control_cambios:
            self.btn_control_cambios = self.findChild(QToolButton, 'btn_control_cambios')
        if not self.btn_calidad:
            self.btn_calidad = self.findChild(QToolButton, 'btn_calidad')
        if not self.btn_reportes:
            self.btn_reportes = self.findChild(QToolButton, 'btn_reportes')

        # DEBUG: mostrar qué botones se encontraron después de fallback


        # Conexiones (usando las variables locales sin "ui")
        # Las conexiones a los botones de la barra lateral se gestionan de forma unificada más abajo
        # (señales conectadas a `handle_sidebar_click` para mantener lógica centralizada)

        # En Main.py, dentro de VentanaIngenieria

# ... (Dentro de __init__, después de buscar todos los botones)

        self.sidebar_buttons = [
            self.btn_dashboard,
            self.btn_requisitos,
            self.btn_diseno_cad,
            self.btn_gestion_bom,
            self.btn_control_cambios,
            self.btn_calidad,
            self.btn_reportes,
        ]

        # Construir lista simple de textos por página para diagnóstico
        self.page_titles = {}
        if self.stacked_widget:
            try:
                from PySide6.QtWidgets import QLabel
                for i in range(self.stacked_widget.count()):
                    w = self.stacked_widget.widget(i)
                    texts = []
                    for lbl in w.findChildren(QLabel):
                        try:
                            txt = lbl.text().strip()
                            if txt:
                                texts.append(txt)
                        except Exception:
                            pass
                    self.page_titles[i] = texts
            except Exception as e:
                print(f"Aviso al construir page_titles: {e}")

        # Construir mapeo dinámico de botones -> índices (mejor heurística)
        print(f"DEBUG: page_titles = {self.page_titles}")
        self.button_to_index = {}
        try:
            count = self.stacked_widget.count() if self.stacked_widget else 0
            used = set()
            from PySide6.QtWidgets import QLabel, QFrame, QWidget

            # 1) Detectar página del dashboard por nombre de child
            for i in range(count):
                try:
                    pg = self.stacked_widget.widget(i)
                    if pg.findChild(QFrame, 'dashboard_container') is not None:
                        self.button_to_index['btn_dashboard'] = i
                        used.add(i)
                        break
                except Exception:
                    pass

            # 2) Detectar página de Requisitos por objectName o por textos detectados
            for i in range(count):
                if i in used:
                    continue
                try:
                    pg = self.stacked_widget.widget(i)
                    lbl = pg.findChild(QLabel, 'label_requisitos_titulo')
                    if lbl is not None or any('requisit' in t.lower() for t in self.page_titles.get(i, [])):
                        self.button_to_index['btn_requisitos'] = i
                        used.add(i)
                        break
                except Exception:
                    pass

            # 3) Detectar página de Diseño/Modelado buscando textos u objectNames relacionados
            for i in range(count):
                if i in used:
                    continue
                try:
                    texts = self.page_titles.get(i, [])
                    if any(('dise' in t.lower() or 'model' in t.lower() or 'cad' in t.lower()) for t in texts):
                        self.button_to_index['btn_diseno_cad'] = i
                        used.add(i)
                        break
                    # buscar en nombres de objetos hijos
                    pg = self.stacked_widget.widget(i)
                    for child in pg.findChildren(QWidget):
                        try:
                            name = child.objectName()
                            if not name:
                                continue
                            ln = name.lower()
                            if 'disen' in ln or 'diseno' in ln or 'cad' in ln or 'model' in ln:
                                self.button_to_index['btn_diseno_cad'] = i
                                used.add(i)
                                raise StopIteration
                        except StopIteration:
                            break
                        except Exception:
                            pass
                except Exception:
                    pass

            # 4) Asignar el resto por orden de aparición para mantener lógica del diseñador
            remaining_pages = [i for i in range(count) if i not in used]
            btn_order = ['btn_gestion_bom', 'btn_control_cambios', 'btn_calidad', 'btn_reportes']
            for btn_name, page_idx in zip(btn_order, remaining_pages):
                self.button_to_index[btn_name] = page_idx

            # Fallbacks razonables si aún falta alguno
            if 'btn_dashboard' not in self.button_to_index and count > 0:
                self.button_to_index['btn_dashboard'] = 0
            if 'btn_requisitos' not in self.button_to_index and count > 1:
                self.button_to_index['btn_requisitos'] = count - 1

            print(f"Mapeo dinámico detectado: {self.button_to_index}")
            # Aplicar overrides manuales si el autor del UI lo requiere (p. ej. diseño en índice 1)
            try:
                # Preferir la detección directa de una página con objectName 'page_diseno' si existe.
                for i in range(count):
                    try:
                        pg = self.stacked_widget.widget(i)
                        if pg is not None and (pg.objectName() == 'page_diseno' or pg.findChild(QFrame, 'frame_diseno') is not None):
                            self.button_to_index['btn_diseno_cad'] = i
                            used.add(i)
                            print(f"Detected 'page_diseno' at index {i}; asignado btn_diseno_cad -> {i}")
                            break
                    except Exception:
                        pass

                manual_mapping = {'btn_diseno_cad': 1}  # <- Si quieres otro índice, cámbialo aquí
                for k,v in manual_mapping.items():
                    if k not in self.button_to_index:
                        if 0 <= v < count:
                            self.button_to_index[k] = v
                            print(f"Manual override: asignado {k} -> {v}")
                        else:
                            print(f"Manual override ignorado: índice {v} fuera de rango para {k}")

                # Mostrar mapping final tras aplicar overrides para ayudar al diagnóstico
                print(f"Mapeo final tras overrides: {self.button_to_index}")
            except Exception as e:
                print(f"Error aplicando manual overrides: {e}")

            # Dump detallado por página para ayudar al diagnóstico
            try:
                print("DEBUG: Page summaries:")
                for i in range(count):
                    try:
                        pg = self.stacked_widget.widget(i)
                        name = pg.objectName() if pg is not None else '<none>'
                        labels = self.page_titles.get(i, [])
                        child_names = []
                        for child in pg.findChildren(QWidget)[:10]:
                            try:
                                cn = child.objectName() or '<no-name>'
                                child_names.append(f"{child.__class__.__name__}:{cn}")
                            except Exception:
                                pass
                        print(f" - idx {i}: name={name}, labels={labels}, children={child_names[:10]}")
                    except Exception as e:
                        print(f"  - idx {i}: error leyendo página: {e}")

                if 'btn_diseno_cad' not in self.button_to_index:
                    print("AVISO: 'btn_diseno_cad' no detectado en mapping. Buscando candidatos...")
                    candidates = []
                    for i in range(count):
                        try:
                            texts = self.page_titles.get(i, [])
                            pg = self.stacked_widget.widget(i)
                            hit_text = any(('dise' in t.lower() or 'model' in t.lower() or 'cad' in t.lower()) for t in texts)
                            hit_child = False
                            for child in pg.findChildren(QWidget):
                                try:
                                    name = child.objectName() or ''
                                    ln = name.lower()
                                    if any(k in ln for k in ('disen', 'diseno', 'model', 'cad')):
                                        hit_child = True
                                        break
                                except Exception:
                                    pass
                            if hit_text or hit_child:
                                candidates.append(i)
                        except Exception:
                            pass
                    print(f"Candidates for 'diseno' pages: {candidates}")
            except Exception as e:
                print(f"Error al hacer dump de páginas: {e}")
        except Exception as e:
            print(f"Aviso al construir mapping dinámico: {e}")


        # Recalcular/refinar mapeo justo antes de conectar señales (garantizar overrides aplicados)
        try:
            self._compute_button_to_index()
        except Exception as e:
            print(f"Aviso: _compute_button_to_index falló justo antes de conectar: {e}")

        # 📌 Conectar todos los botones a la nueva función de manejo
        for button in self.sidebar_buttons:
            if button:
                button.setCheckable(True) # Establecer como "chequeable"
                try:
                    button.clicked.connect(self.handle_sidebar_click)

                except Exception as e:
                    print(f"Error conectando botón {getattr(button, 'objectName', lambda: 'unknown')()}: {e}")
            else:
                print("Aviso: se encontró un botón None en sidebar_buttons")

        # 📌 Asegurar que el dashboard inicie marcado
        if self.btn_dashboard:
            self.btn_dashboard.setChecked(True)

            
        # ... (Tu función __init__ termina aquí) ...



     

        self.dash_url = "http://127.0.0.1:8050"
        self.web_view = QWebEngineView()

        # Localizar el contenedor del dashboard en la UI (no sobrescribir si ya está definido)
        if not hasattr(self, 'stacked_widget') or not self.stacked_widget:
            self.stacked_widget = self.loaded_ui.findChild(QStackedWidget, 'stacked_widget_ingenieria')
        # Intentar encontrar el contenedor como QFrame; si falla, intentar como QWidget (fallback)
        self.dashboard_container = self.loaded_ui.findChild(QFrame, 'dashboard_container')  # Debe coincidir el objectName en Ingenieria.ui
        if self.dashboard_container is None:
            self.dashboard_container = self.loaded_ui.findChild(QWidget, 'dashboard_container')
            if self.dashboard_container is not None:
                print("Se encontró 'dashboard_container' usando fallback a QWidget en loaded_ui.")

        # Si sigue sin encontrarse, intentar buscar en 'self' (QMainWindow) después de setCentralWidget
        if self.dashboard_container is None:
            self.dashboard_container = self.findChild(QFrame, 'dashboard_container')
            if self.dashboard_container is None:
                self.dashboard_container = self.findChild(QWidget, 'dashboard_container')
            if self.dashboard_container is not None:
                print("Se encontró 'dashboard_container' usando búsqueda en la ventana principal (self).")

        # Comprobar la existencia del contenedor y preparar el layout
        if self.dashboard_container is None:
            print("Aviso: 'dashboard_container' no encontrado en 'Ingenieria.ui'. Verifica el objectName del QFrame.")
            print(f"El servidor Dash se iniciará igualmente en {self.dash_url}. Abre esa URL en un navegador si no ves el dashboard en la app.")
            iniciar_servidor_en_hilo()
        else:
            layout = self.dashboard_container.layout()
            if layout is None:
                layout = QVBoxLayout()
                self.dashboard_container.setLayout(layout)

            # Añadir el QWebEngineView si aún no existe
            if layout.count() == 0:
                layout.addWidget(self.web_view)
                layout.setContentsMargins(0, 0, 0, 0)
                from PySide6.QtWidgets import QSizePolicy
                # Hacer que el webview y el contenedor puedan expandir y encogerse correctamente
                self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.web_view.setMinimumSize(0, 0)
                self.dashboard_container.setMinimumSize(0, 0)
                self.dashboard_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                # Iniciar el servidor Dash y programar la carga del dashboard en el WebView
                try:
                    iniciar_servidor_en_hilo()
                except Exception as e:
                    print(f"Aviso: no se pudo iniciar el servidor Dash: {e}")

                # Intentar cargar la URL cuando el servidor esté arriba; hacemos varios reintentos si es necesario
                QTimer.singleShot(500, lambda: self._try_load_dash())

                # Si está activado el autotest por variable de entorno, programar la prueba automática de botones
                try:
                    if os.environ.get('AUTOTEST', '0') == '1':
                        QTimer.singleShot(1500, lambda: self._auto_test_sidebar())
                except Exception:
                    pass

                # Ajustar tamaño inicial de la ventana para que coincida con el diseño del .ui
                try:
                    from PySide6.QtGui import QGuiApplication
                    screen = QGuiApplication.primaryScreen()
                    avail = screen.availableGeometry()

                    # Si el usuario quiere coincidencia exacta, usar la dimensión almacenada desde el UI
                    if MATCH_UI_SIZE_EXACT and hasattr(self, '_designed_size') and self._designed_size:
                        desired_w, desired_h = self._designed_size
                        print(f"MATCH_UI_SIZE_EXACT activo: ajustando ventana exactamente a {desired_w}x{desired_h}")
                        try:
                            self.resize(desired_w, desired_h)
                        except Exception:
                            # Si no es posible, maximizar como fallback
                            self.showMaximized()
                    else:
                        # Intentar obtener tamaño diseñado del central widget o usar un fallback razonable
                        central = self.loaded_ui.centralWidget()
                        desired_w = None
                        desired_h = None
                        if central:
                            geom = central.geometry()
                            desired_w = geom.width()
                            desired_h = geom.height()
                            if desired_w == 0 or desired_h == 0:
                                sh = central.sizeHint()
                                desired_w, desired_h = sh.width(), sh.height()

                        if not desired_w or not desired_h:
                            desired_w = min(1280, avail.width() - 50)
                            desired_h = min(900, avail.height() - 50)

                        if desired_w > avail.width() - 50 or desired_h > avail.height() - 50:
                            print(f"Maximizando ventana porque el diseño ({desired_w}x{desired_h}) excede pantalla {avail.width()}x{avail.height()}")
                            self.showMaximized()
                        else:
                            print(f"Ajustando ventana al tamaño del diseño: {desired_w}x{desired_h}")
                except Exception as e:
                    print(f"Aviso: no se pudo ajustar el tamaño desde la pantalla ({e}), usando tamaño por defecto.")
                    try:
                        self.resize(1070, 870)
                    except Exception:
                        # Si no se puede redimensionar, maximizar como último recurso
                        try:
                            self.showMaximized()
                        except Exception:
                            pass
        # Si no hay mapping dinámico (fallo de detección), usar un mapeo estático flexible como fallback
        if not hasattr(self, 'button_to_index') or not self.button_to_index:
            total_pages = self.stacked_widget.count() if self.stacked_widget else 0
            self.button_to_index = {
                'btn_dashboard': 0,
                'btn_diseno_cad': 1 if total_pages > 1 else 0,
                'btn_gestion_bom': 2 if total_pages > 2 else max(0, total_pages - 1),
                'btn_control_cambios': 3 if total_pages > 3 else max(0, total_pages - 1),
                'btn_calidad': 4 if total_pages > 4 else max(0, total_pages - 1),
                # Requisitos y reportes por defecto apuntan a la última página (más seguro si se han añadido páginas)
                'btn_requisitos': max(0, total_pages - 1),
                'btn_reportes': max(0, total_pages - 1),
            }
        else:
            # Si ya teníamos mapping dinámico, intentar refinarlo (por si el UI cambió tras la carga)
            try:
                self._compute_button_to_index()
            except Exception as e:
                print(f"Aviso: no se pudo refinar mapping dinámico: {e}")

        # Imprimir detalles del mapping para diagnóstico (botón -> índice -> page objectName y labels)
        try:
            for k, idx in self.button_to_index.items():
                pg = None
                try:
                    if self.stacked_widget and 0 <= idx < self.stacked_widget.count():
                        pg = self.stacked_widget.widget(idx)
                except Exception:
                    pg = None
                pn = pg.objectName() if pg is not None else '<none>'
                print(f"Mapping detalle: {k} -> index {idx}, page {pn}, labels={self.page_titles.get(idx)}")
        except Exception as e:
            print(f"Error mostrando detalles del mapping: {e}")
        # Intentar fijar la página inicial acorde al botón dashboard detectado
        try:
            if self.btn_dashboard and self.stacked_widget:
                init_idx = self.button_to_index.get('btn_dashboard', 0)
                if init_idx < self.stacked_widget.count():
                    self.stacked_widget.setCurrentIndex(init_idx)
                    print(f"Índice inicial fijado a {init_idx} (dashboard).")
        except Exception as e:
            print(f"Aviso: no se pudo fijar índice inicial: {e}")

        # Sidebar click handling moved to `handle_sidebar_click` method (defined below).

        # ... (Resto de findChild y conexiones de botones) ...

    def handle_sidebar_click(self):
        """Maneja clicks de la barra lateral y cambia la página correspondiente en el QStackedWidget."""
        sender = self.sender()
        if sender is None:
            return

        # Desmarcar otros botones de forma segura
        for button in self.sidebar_buttons:
            if button and button != sender:
                try:
                    button.blockSignals(True)
                    button.setChecked(False)
                    button.blockSignals(False)
                except Exception:
                    pass
        try:
            sender.setChecked(True)
        except Exception:
            pass

        try:
            sender_name = sender.objectName()
        except Exception:
            sender_name = None

        # Usar mapping dinámico si existe (con fallback seguro)
        mapping = getattr(self, 'button_to_index', None) or {}
        idx = mapping.get(sender_name)
        if idx is None:
            # intentar heurística rápida: buscar índice por widgets conocidos en cada página
            idx = None
            try:
                from PySide6.QtWidgets import QLabel, QFrame
                for i in range(self.stacked_widget.count()):
                    pg = self.stacked_widget.widget(i)
                    if pg is None:
                        continue
                    if sender_name == 'btn_requisitos' and pg.findChild(QLabel, 'label_requisitos_titulo'):
                        idx = i
                        break
                    if sender_name == 'btn_dashboard' and pg.findChild(QFrame, 'dashboard_container'):
                        idx = i
                        break
                    # Heurística explícita para Diseño/Modelado
                    if sender_name == 'btn_diseno_cad' and (pg.findChild(QLabel, 'label_Diseno') or pg.findChild(QFrame, 'frame_diseno') or pg.objectName() == 'page_diseno'):
                        idx = i
                        break
            except Exception:
                pass

        if idx is None:
            print(f"Sidebar: botón {sender_name} no mapeado. No se cambiará la página.")
            try:
                sender.setChecked(False)
            except Exception:
                pass
            return

        # Asegurar índice válido
        try:
            count = self.stacked_widget.count()
            if idx >= count:
                idx = max(0, count-1)
        except Exception:
            pass

        # Cambiar página
        try:
            print(f"Cambiando a página {idx} (botón {sender_name})")
            self.stacked_widget.setCurrentIndex(idx)
            # Mostrar info de la página tras cambiar para diagnóstico
            try:
                pg = self.stacked_widget.widget(idx)
                pn = pg.objectName() if pg is not None else '<none>'
                print(f"Página actual tras click: index={idx}, objectName={pn}, labels={self.page_titles.get(idx)}")
            except Exception as e:
                print(f"Error mostrando info de página tras click: {e}")
        except Exception as e:
            print(f"Error cambiando página: {e}")
            try:
                sender.setChecked(False)
            except Exception:
                pass
            return

    def _compute_button_to_index(self):
        """Reconstruye el mapeo botones -> índices usando heurísticas más completas
        (objectName, textos de QLabel, nombres de hijos) para adaptarse a páginas nuevas.
        """
        try:
            count = self.stacked_widget.count() if self.stacked_widget else 0
            page_info = {}
            from PySide6.QtWidgets import QLabel, QWidget
            for i in range(count):
                pg = self.stacked_widget.widget(i)
                names = set()
                texts = []
                try:
                    if pg is not None:
                        on = getattr(pg, 'objectName', lambda: '')()
                        if on:
                            names.add(on.lower())
                        for child in pg.findChildren(QWidget):
                            try:
                                nm = child.objectName() or ''
                                if nm:
                                    names.add(nm.lower())
                            except Exception:
                                pass
                        for lbl in pg.findChildren(QLabel):
                            try:
                                t = lbl.text().strip().lower()
                                if t:
                                    texts.append(t)
                            except Exception:
                                pass
                except Exception:
                    pass
                page_info[i] = {'names': names, 'texts': texts}

            new_map = {}
            for btn in self.sidebar_buttons:
                if not btn:
                    continue
                try:
                    bname = btn.objectName()
                    btext = (btn.text() or '').strip().lower()
                except Exception:
                    bname = None
                    btext = ''
                token = ''
                if bname and bname.startswith('btn_'):
                    token = bname[4:]
                # Score pages
                best = None
                best_score = 0
                for i, info in page_info.items():
                    score = 0
                    # match by names
                    if token and any(token in nm for nm in info['names']):
                        score += 4
                    # match by text content
                    for tk in btext.split():
                        if any(tk in nm for nm in info['names']):
                            score += 2
                        if any(tk in text for text in info['texts']):
                            score += 3
                    # explicit boosts
                    if token == 'dashboard' and any('dashboard_container' in nm for nm in info['names']):
                        score += 8
                    if token == 'requisitos' and (any('label_requisitos_titulo' in nm for nm in info['names']) or any('requisit' in text for text in info['texts'])):
                        score += 8
                    if score > best_score:
                        best_score = score
                        best = i
                if best is not None and best_score > 0:
                    new_map[bname] = best
            # Merge preserving existing mapping and preferring new_map where it has higher confidence
            final = getattr(self, 'button_to_index', {}).copy()
            final.update(new_map)

            # Apply manual overrides first (allow forcing buttons to open specific pages)
            try:
                mm = getattr(self, 'manual_mapping', {}) or {}
                for bk, bv in mm.items():
                    try:
                        if isinstance(bv, str):
                            # find page with objectName == bv
                            for i in range(self.stacked_widget.count()):
                                try:
                                    pg = self.stacked_widget.widget(i)
                                    if pg is not None and getattr(pg, 'objectName', lambda: '')() == bv:
                                        final[bk] = i
                                        print(f"Manual override: {bk} -> index {i} (page objectName='{bv}')")
                                        break
                                except Exception:
                                    pass
                        elif isinstance(bv, int):
                            final[bk] = bv
                            print(f"Manual override: {bk} -> index {bv} (int override)")
                    except Exception:
                        pass
            except Exception:
                pass

            # Backwards-compat: also ensure btn_diseno_cad maps to 'page' if present (legacy-safe)
            try:
                if self.stacked_widget and 'btn_diseno_cad' not in final:
                    for i in range(self.stacked_widget.count()):
                        try:
                            pg = self.stacked_widget.widget(i)
                            if pg is not None and getattr(pg, 'objectName', lambda: '')() == 'page':
                                final['btn_diseno_cad'] = i
                                print(f"Fallback override: btn_diseno_cad -> index {i} (page objectName='page')")
                                break
                        except Exception:
                            pass
            except Exception:
                pass

            self.button_to_index = final
            print(f"Refined mapping (compute): {self.button_to_index}")
        except Exception as e:
            print(f"Error en _compute_button_to_index: {e}")

    def _auto_test_sidebar(self):
        """Auto-test: simula clicks en los botones de la barra lateral y escribe resultados en consola."""
        try:
            print('\n--- Auto Test Start ---')
            for b in self.sidebar_buttons:
                if not b:
                    print('Button None in sidebar_buttons')
                    continue
                try:
                    name = b.objectName()
                    txt = b.text() if hasattr(b, 'text') else ''
                    print(f"Clicking {name} -> '{txt}'")
                    b.click()
                    QTimer.singleShot(200, lambda: None)  # dejar tiempo a que la UI responda
                    from PySide6.QtCore import QCoreApplication
                    QCoreApplication.processEvents()
                    idx = self.stacked_widget.currentIndex() if self.stacked_widget else -1
                    pg = self.stacked_widget.widget(idx) if (self.stacked_widget and idx >= 0) else None
                    pn = pg.objectName() if pg is not None else '<none>'
                    print(f" -> index={idx}, page={pn}, labels={self.page_titles.get(idx)})")
                except Exception as e:
                    print(' -> Error during click:', e)
            print('--- Auto Test End ---\n')
        except Exception as e:
            print('Auto test failed:', e)

    def _try_load_dash(self, retries=8):
        """Intentar cargar la URL del dashboard en el QWebEngineView con varios reintentos.
        Si el servidor no responde tras varios intentos, muestra un mensaje de advertencia.
        """
        from urllib.request import urlopen
        try:
            # Intentar una petición rápida para comprobar si el servidor responde
            urlopen(self.dash_url, timeout=1)
            try:
                self.web_view.setUrl(QUrl(self.dash_url))
                print("Dash cargado en QWebEngineView.")
            except Exception as e:
                print(f"Error al establecer URL en QWebEngineView: {e}")
        except Exception as e:
            if retries > 0:
                print(f"Dash aún no disponible, reintentando en 1s (intentos restantes: {retries})")
                QTimer.singleShot(1000, lambda: self._try_load_dash(retries-1))
            else:
                print(f"No fue posible conectar con {self.dash_url}: {e}")
                QMessageBox.warning(self, "Dash no disponible", f"No se pudo cargar el dashboard en {self.dash_url}.\nAbre la URL en tu navegador: {self.dash_url}")
# ---------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Crea una instancia de la ventana
    ventana = VentanaPrincipal()
    
    # ** CÓDIGO CLAVE PARA TERMINAR AL CERRAR **
    # Conecta la señal 'finished' de la ventana (Dialog) a la función 'quit' de la aplicación.
    app.aboutToQuit.connect(app.deleteLater) 
    
    # Si la ventana principal es un QDialog o QWidget, este paso ayuda a una terminación limpia.
    # Conecta la acción de cierre a la terminación de la aplicación
    app.lastWindowClosed.connect(app.quit)
    
    # Muestra la ventana
    if ventana.ui:
        ventana.ui.show()

    # Si estamos en modo de test automático, abrir la ventana de Ingeniería directamente
    try:
        import os
        if os.environ.get('AUTOTEST', '0') == '1':
            print('AUTOTEST detected: abriendo VentanaIngenieria automáticamente...')
            ventana.abrir_ingenieria()
    except Exception:
        pass

    # Ejecuta el bucle principal de la aplicación
    sys.exit(app.exec())

# Nota: la aplicación Dash y el servidor están definidos en `dash_app.py`.
# Se utiliza `iniciar_servidor_en_hilo()` desde ahí para arrancar el servidor en segundo plano.