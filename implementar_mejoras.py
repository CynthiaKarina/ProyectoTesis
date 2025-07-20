#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para implementar automáticamente las mejoras del panel de administración
"""

import os
import shutil
from datetime import datetime

def implementar_mejoras():
    """Implementa las mejoras del panel de administración"""
    
    print("🎨 IMPLEMENTANDO MEJORAS DEL PANEL DE ADMINISTRACIÓN")
    print("=" * 60)
    
    # Verificar archivos necesarios
    archivos_necesarios = [
        "app/static/admin-mejoras.css",
        "app/static/js/admin-mejoras.js",
        "app/templates/admin_options_mejorado.html"
    ]
    
    print("📋 Verificando archivos necesarios...")
    for archivo in archivos_necesarios:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - NO ENCONTRADO")
            return False
    
    # Crear backup del archivo original
    print("\n💾 Creando backup del archivo original...")
    original_file = "app/templates/admin_options.html"
    backup_file = f"app/templates/admin_options_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    if os.path.exists(original_file):
        shutil.copy2(original_file, backup_file)
        print(f"✅ Backup creado: {backup_file}")
    else:
        print("⚠️  Archivo original no encontrado")
    
    # Crear directorio js si no existe
    js_dir = "app/static/js"
    if not os.path.exists(js_dir):
        os.makedirs(js_dir)
        print(f"📁 Directorio creado: {js_dir}")
    
    # Implementar mejoras
    print("\n🚀 Implementando mejoras...")
    
    # Opción 1: Reemplazar archivo existente
    print("\n¿Cómo deseas implementar las mejoras?")
    print("1. Reemplazar archivo existente (recomendado)")
    print("2. Crear nueva ruta /admin-mejorado")
    print("3. Solo mostrar instrucciones")
    
    try:
        opcion = input("\nSelecciona una opción (1-3): ").strip()
        
        if opcion == "1":
            # Reemplazar archivo existente
            if os.path.exists(original_file):
                shutil.copy2("app/templates/admin_options_mejorado.html", original_file)
                print("✅ Archivo admin_options.html reemplazado")
            else:
                shutil.copy2("app/templates/admin_options_mejorado.html", original_file)
                print("✅ Archivo admin_options.html creado")
            
            print("\n🎉 ¡Mejoras implementadas exitosamente!")
            print("📝 Accede a: /admin-options para ver las mejoras")
            
        elif opcion == "2":
            # Crear nueva ruta
            print("\n📝 Para crear una nueva ruta, agrega este código en:")
            print("   app/controllers/admin_options_controller.py")
            print("\n" + "="*50)
            print("""
@admin_options_bp.route('/admin-mejorado')
def admin_options_mejorado():
    return render_template('admin_options_mejorado.html')
""")
            print("="*50)
            print("📝 Luego accede a: /admin-mejorado")
            
        elif opcion == "3":
            # Solo mostrar instrucciones
            print("\n📖 Consulta el archivo: INSTRUCCIONES_MEJORAS_ADMIN.md")
            print("   para ver todas las instrucciones detalladas")
            
        else:
            print("❌ Opción inválida")
            return False
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("✅ PROCESO COMPLETADO")
        print("="*60)
        
        print("\n📋 ARCHIVOS CREADOS:")
        print("   ✅ app/static/admin-mejoras.css")
        print("   ✅ app/static/js/admin-mejoras.js")
        print("   ✅ app/templates/admin_options_mejorado.html")
        print("   ✅ INSTRUCCIONES_MEJORAS_ADMIN.md")
        
        if opcion == "1":
            print(f"   ✅ {backup_file} (backup)")
        
        print("\n🎨 CARACTERÍSTICAS IMPLEMENTADAS:")
        print("   ✨ Animaciones 3D y efectos visuales")
        print("   🎭 Gradientes únicos por categoría")
        print("   🎪 Partículas flotantes de fondo")
        print("   🔘 Efectos ripple al hacer clic")
        print("   💫 Preloader animado")
        print("   🎯 Tooltips informativos")
        print("   🚀 Botón FAB para acceso rápido")
        print("   📱 Diseño responsive optimizado")
        
        print("\n🔧 PERSONALIZACIÓN:")
        print("   • Edita variables CSS en admin-mejoras.css")
        print("   • Ajusta animaciones en admin-mejoras.js")
        print("   • Modifica colores y efectos según tu preferencia")
        
        print("\n🎉 ¡Disfruta de tu panel de administración mejorado!")
        
        return True
        
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    implementar_mejoras() 