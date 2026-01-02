import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def seleccionar_y_convertir():
    # 1. Configurar la ventana oculta de Tkinter para el explorador
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de Tkinter
    root.attributes("-topmost", True) # Pone el explorador al frente

    # 2. Abrir el explorador de archivos para seleccionar el CSV
    ruta_csv = filedialog.askopenfilename(
        title="Selecciona el archivo CSV de AutoMetrics",
        filetypes=[("Archivos CSV", "*.csv")]
    )

    # Si el usuario cierra la ventana sin seleccionar nada
    if not ruta_csv:
        print("Operación cancelada por el usuario.")
        return

    try:
        # 3. Leer el archivo CSV con Pandas para análisis de datos
        df = pd.read_csv(ruta_csv)

        # 4. Generar la ruta de salida (mismo nombre pero .xlsx)
        nombre_base = os.path.splitext(ruta_csv)[0]
        ruta_xlsx = f"{nombre_base}_Analisis.xlsx"

        # 5. Convertir a Excel (.xlsx)
        # Usamos el motor openpyxl para asegurar compatibilidad total
        df.to_excel(ruta_xlsx, index=False, engine='openpyxl')

        # 6. Notificar al usuario
        messagebox.showinfo("Éxito", f"Archivo convertido correctamente:\n{ruta_xlsx}")
        print(f"Conversión exitosa: {ruta_xlsx}")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo convertir el archivo:\n{str(e)}")
        print(f"Error: {e}")
    
    finally:
        root.destroy()
