#!/usr/bin/env python
"""
Script de utilidad para manejar migraciones de base de datos
Uso: python migrate_db.py [comando]

Comandos disponibles:
- init: Inicializa las migraciones
- migrate: Crea nueva migración
- upgrade: Aplica migraciones pendientes
- downgrade: Revierte última migración
- current: Muestra versión actual
- history: Muestra historial de migraciones
- stamp: Marca base de datos como migrada (solo primera vez)
"""

import os
import sys
from flask.cli import FlaskGroup
from app import create_app, db

def create_cli_app():
    """Crea la aplicación Flask para CLI"""
    return create_app()

cli = FlaskGroup(create_app=create_cli_app)

def show_help():
    """Muestra la ayuda del script"""
    print(__doc__)
    print("\nEjemplos de uso:")
    print("  python migrate_db.py migrate -m 'Agregar nueva tabla'")
    print("  python migrate_db.py upgrade")
    print("  python migrate_db.py current")
    print("  python migrate_db.py history")

def run_migration_command(command, message=None):
    """Ejecuta un comando de migración"""
    try:
        if command == 'init':
            os.system('flask db init')
        elif command == 'migrate':
            if message:
                os.system(f'flask db migrate -m "{message}"')
            else:
                os.system('flask db migrate')
        elif command == 'upgrade':
            os.system('flask db upgrade')
        elif command == 'downgrade':
            os.system('flask db downgrade')
        elif command == 'current':
            os.system('flask db current')
        elif command == 'history':
            os.system('flask db history')
        elif command == 'stamp':
            os.system('flask db stamp head')
        else:
            print(f"Comando desconocido: {command}")
            show_help()
            return False
        return True
    except Exception as e:
        print(f"Error ejecutando comando: {e}")
        return False

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command in ['-h', '--help', 'help']:
        show_help()
        return
    
    # Obtener mensaje para migrate
    message = None
    if command == 'migrate' and len(sys.argv) > 2:
        if sys.argv[2] == '-m' and len(sys.argv) > 3:
            message = sys.argv[3]
        else:
            message = ' '.join(sys.argv[2:])
    
    print(f"🚀 Ejecutando comando de migración: {command}")
    if message:
        print(f"📝 Mensaje: {message}")
    
    success = run_migration_command(command, message)
    
    if success:
        print("✅ Comando ejecutado exitosamente")
        
        # Mostrar información adicional según el comando
        if command == 'migrate':
            print("\n💡 Siguiente paso: Ejecuta 'python migrate_db.py upgrade' para aplicar la migración")
        elif command == 'upgrade':
            print("\n💡 Base de datos actualizada. Reinicia tu aplicación si es necesario.")
        elif command == 'init':
            print("\n💡 Migraciones inicializadas. Ahora puedes crear tu primera migración con:")
            print("   python migrate_db.py migrate -m 'Initial migration'")
    else:
        print("❌ Error ejecutando el comando")

if __name__ == '__main__':
    main() 