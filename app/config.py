import os

# Configuración de Base de Datos (lee variables de entorno si existen)
DB_HOST = os.environ.get("DB_HOST", "34.51.57.50")
DB_USER = os.environ.get("DB_USER", "proyecto-tesis")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "proyectotesis")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))

# Configuraciones adicionales para la conexión
DB_CHARSET = os.environ.get("DB_CHARSET", "utf8mb4")
DB_AUTOCOMMIT = os.environ.get("DB_AUTOCOMMIT", "True").lower() in ["true", "1", "yes"]
