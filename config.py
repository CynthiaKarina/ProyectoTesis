import os

class Config:
    SECRET_KEY = 'tu_clave_secreta_aqui'
    # Configuración actualizada para Google Cloud SQL
    # Instancia: seismic-sentry-466506-j0-northamerica-south1-proyecto-tesis
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://proyecto-tesis:K7re^bY0q":Rf*|R@34.51.57.50:3306/proyectotesis'
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/proyectotesis'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración para subida de archivos
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads', 'profile_pics')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB límite máximo
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} 

    # -------------------------------
    # Configuración de Email (SMTP)
    # -------------------------------
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.environ.get('notificaciones.sigral@gmail.com')  # ej. notificaciones.sigral@gmail.com
    MAIL_PASSWORD = os.environ.get('gyzz yjnp glxz qzab')  # Usa contraseña de aplicación de Gmail
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    # Salt para tokens de email (restablecer contraseña, etc.)
    SECURITY_EMAIL_SALT = os.environ.get('SECURITY_EMAIL_SALT', 'sigral-email-salt')
    SECURITY_APPROVAL_SALT = os.environ.get('SECURITY_APPROVAL_SALT', 'sigral-approval-salt')