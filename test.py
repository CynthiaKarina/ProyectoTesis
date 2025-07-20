import mysql.connector
from mysql.connector import Error
from app.models.area import Area

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="proyectotesis"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def verificar_tabla_areas():
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM area")
            count = cursor.fetchone()[0]
            cursor.close()
            connection.close()
            return count > 0
    except Exception as e:
        print(f"Error al verificar tabla areas: {str(e)}")
        return False
    return False

if __name__ == "__main__":
    resultado = verificar_tabla_areas()
    if resultado:
        print("La tabla 'area' existe y contiene registros.")
    else:
        print("La tabla 'area' no existe o está vacía.")

    areas = Area.obtener_areas()
    print("Áreas:", areas)