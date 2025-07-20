import os

class Config:
    SECRET_KEY = 'tu_clave_secreta_aqui'
    # Configuración actualizada para Google Cloud SQL
    # Instancia: seismic-sentry-466506-j0-northamerica-south1-proyecto-tesis
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://proyecto-tesis:K7re^bY0q":Rf*|R@34.51.57.50:3306/proyectotesis'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración para subida de archivos
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads', 'profile_pics')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB límite máximo
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} 