

# Diccionario maestro de situaciones de brecha de seguridad
# Estructura: "Nombre de la situación": "Descripción detallada para el chat"
DICCIONARIO_BRECHAS = {
    "Acceso No Autorizado a Base de Datos": 
        "Se ha detectado un ingreso desde una IP externa a los servidores de producción.",
    
    "Fuga de Credenciales de Administrador": 
        "Las llaves de acceso del nivel gerencial han sido filtradas en un foro de seguridad.",
    
    "Infección por Ransomware en Terminales": 
        "Varios equipos de la oficina central presentan archivos encriptados y solicitud de rescate.",
    
    "Detección de Phishing Dirigido (Whaling)": 
        "Se han enviado correos fraudulentos suplantando la identidad del CEO para desviar fondos.",
    
    "Exfiltración de Datos de Clientes": 
        "Se detectó una descarga inusual de 50GB de información sensible hacia un servidor remoto.",
    
    "Vulnerabilidad en Pasarela de Pagos": 
        "El módulo de transacciones presenta un fallo que permite duplicar cobros sin autorización.",
    
    "Interrupción Crítica por Ataque DDoS": 
        "Nuestra plataforma web está fuera de servicio debido a una sobrecarga masiva de tráfico malintencionado."
}

# Opciones de manifestación (Tono del cliente)
MANIFESTACIONES = ["Agradable", "Normal", "Enojado", "Agresivo"]