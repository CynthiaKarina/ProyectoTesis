from app.database.connection import get_db_connection

def verify_user(correo, contrasena):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM usuario WHERE username = %s AND password = %s"
        cursor.execute(query, (correo, contrasena))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user
    return None
