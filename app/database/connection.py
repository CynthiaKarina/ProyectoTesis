import mysql.connector
from mysql.connector import Error
from app.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT, DB_CHARSET, DB_AUTOCOMMIT

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            charset=DB_CHARSET,
            autocommit=DB_AUTOCOMMIT,
            connect_timeout=10,  # Timeout de conexión de 10 segundos
            raise_on_warnings=True
        )
        if connection.is_connected():
            print(f"Conectado exitosamente a la base de datos '{DB_NAME}' en {DB_HOST}")
            return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None