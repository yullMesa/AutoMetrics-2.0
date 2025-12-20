from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

# Supongamos que tu label se llama 'label_titulo'
titulo = self.ui_content.findChild(QLabel, "label_titulo")

if titulo:
    # Crear el efecto de resplandor azul
    glow = QGraphicsDropShadowEffect()
    glow.setBlurRadius(15) # Qué tan "borroso" es el brillo
    glow.setColor(QColor(0, 242, 255, 150)) # Color azul con transparencia
    glow.setOffset(0, 0) # Centrado detrás del texto
    titulo.setGraphicsEffect(glow)

from PySide6.QtGui import QColor

# ... dentro de tu función para llenar la tabla ...
item_prioridad = QTableWidgetItem("Crítica")
# Aplicar el color cyan solo a esta celda
item_prioridad.setForeground(QColor("#00f2ff")) 
tabla.setItem(fila, 2, item_prioridad)

header = tabla.horizontalHeader()
header.setSectionResizeMode(QHeaderView.Stretch) # Todas las columnas iguales

from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

# Efecto para el botón eliminar
shadow = QGraphicsDropShadowEffect()
shadow.setBlurRadius(15)
shadow.setColor(QColor(255, 0, 85, 150)) # Sombra roja neón
shadow.setOffset(0, 0)
self.ui_content.findChild(QPushButton, "btn_eliminar").setGraphicsEffect(shadow)

# Busca el widget en tu archivo .ui
guia_browser = self.ui_content.findChild(QTextBrowser, "nombre_de_tu_widget")

if guia_browser:
    html_guia = """
    <div style="color: #ffffff;">
        <h3 style="color: #00f2ff; margin-bottom: 5px;">GUÍA DE REGISTRO</h3>
        <p>Para añadir un nuevo requisito, complete los siguientes campos en el formulario:</p>
        
        <ul style="margin-left: -20px;">
            <li><b style="color: #00f2ff;">Nombre del Requisito:</b> Título corto y descriptivo (ej. <i>Sistema de Frenado</i>).</li>
            <li><b style="color: #00f2ff;">Petición:</b> Descripción detallada de la necesidad técnica o funcional.</li>
            <li><b style="color: #00f2ff;">Nivel de Prioridad:</b> Clasifique según la importancia: 
                <span style="color: #ff0055;">Crítica</span>, 
                <span style="color: #ffaa00;">Alta</span> o 
                <span style="color: #00ffaa;">Media</span>.
            </li>
        </ul>
        <hr style="border: 0.5px solid #1f2530;">
        <p style="font-size: 11px; color: #8a95a5;"><i>Nota: Todos los campos son obligatorios para el control de calidad.</i></p>
    </div>
    """
    guia_browser.setHtml(html_guia)