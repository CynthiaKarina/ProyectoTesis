import os

class Config:
    SECRET_KEY = 'tu_clave_secreta_aqui'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/proyectotesis'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración para subida de archivos
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads', 'profile_pics')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB límite máximo
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} 