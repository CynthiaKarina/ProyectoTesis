import os

def init_upload_folders():
    # Definir las rutas base
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    upload_folder = os.path.join(base_dir, 'static', 'uploads', 'profile_pics')
    
    # Crear el directorio si no existe
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        print(f"Directorio creado: {upload_folder}")
    
    return upload_folder 