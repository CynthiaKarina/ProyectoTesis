import os

def init_upload_directories():
    # Definir las rutas necesarias
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    upload_folder = os.path.join(base_dir, 'static', 'uploads', 'profile_pics')
    default_img_folder = os.path.join(base_dir, 'static', 'img')

    # Crear directorios si no existen
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(default_img_folder, exist_ok=True)

    print(f"Directorio para imágenes de perfil: {upload_folder}")
    return upload_folder 