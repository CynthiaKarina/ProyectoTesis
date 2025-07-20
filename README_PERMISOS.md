# 🔐 SISTEMA DE PERMISOS MEJORADO

## 📋 **Resumen**

Este sistema de permisos mejorado organiza los roles y permisos de forma eficiente, siguiendo el principio de menor privilegio y separación de responsabilidades.

---

## 📁 **Archivos Creados**

### **1. 📖 Documentación**
- **`PROPUESTA_PERMISOS.md`** - Propuesta detallada con matriz de permisos
- **`README_PERMISOS.md`** - Este archivo con instrucciones completas

### **2. 🛠️ Scripts de Configuración**
- **`asignar_permisos_mejorados.py`** - Script completo con nuevos roles especializados
- **`actualizar_permisos_existentes.py`** - Script simple para actualizar roles existentes
- **`asignar_usuarios_roles.py`** - Script interactivo para asignar usuarios a roles

### **3. 🧪 Scripts de Prueba**
- **`test_permissions.py`** - Script mejorado para verificar el sistema

---

## 🚀 **PLAN DE IMPLEMENTACIÓN**

### **OPCIÓN A: Implementación Gradual (Recomendada)**

#### **Paso 1: Actualizar Roles Existentes**
```bash
# Actualizar permisos de roles existentes
python actualizar_permisos_existentes.py
```

**¿Qué hace?**
- ✅ Actualiza el rol "Administrador" con TODOS los permisos necesarios
- ✅ Mejora el rol "Gestor de Laboratorios" con permisos específicos
- ✅ Optimiza "Usuario Regular" con permisos básicos
- ✅ Configura "Invitado" con acceso mínimo

#### **Paso 2: Verificar Funcionamiento**
```bash
# Probar el sistema actualizado
python test_permissions.py
```

#### **Paso 3: Asignar Usuarios a Roles**
```bash
# Asignar usuarios usando interfaz interactiva
python asignar_usuarios_roles.py
```

#### **Paso 4: Probar en Aplicación**
```bash
# Ejecutar aplicación y probar con diferentes usuarios
python run.py
```

### **OPCIÓN B: Implementación Completa**

#### **Paso 1: Implementar Sistema Completo**
```bash
# Crear roles especializados adicionales
python asignar_permisos_mejorados.py
```

**¿Qué hace?**
- ✅ Crea nuevos roles especializados:
  - 👥 **Gestor de Usuarios**
  - 🎓 **Coordinador Académico**
- ✅ Actualiza todos los roles existentes
- ✅ Organiza permisos por área funcional

#### **Paso 2: Verificar y Asignar**
```bash
# Verificar sistema completo
python test_permissions.py

# Asignar usuarios a roles
python asignar_usuarios_roles.py
```

---

## 🎭 **ROLES DISPONIBLES**

### **Roles Existentes (Mejorados)**
1. **👑 Super Administrador** - Acceso total (`acceso_total`)
2. **🛡️ Administrador** - Gestión completa del sistema
3. **🧪 Gestor de Laboratorios** - Gestión de laboratorios y solicitudes
4. **👤 Usuario Regular** - Permisos básicos de uso
5. **👁️ Invitado** - Solo lectura básica

### **Roles Nuevos (Opcionales)**
6. **👥 Gestor de Usuarios** - Gestión de usuarios e instituciones
7. **🎓 Coordinador Académico** - Gestión de áreas y supervisión académica

---

## 📊 **FUNCIONALIDADES POR ROL**

### **🛡️ Administrador (Rol Principal)**
- ✅ **Panel de administración** completo
- ✅ **Gestión de usuarios** (crear, editar, eliminar)
- ✅ **Gestión de roles y permisos** (completa)
- ✅ **Gestión de laboratorios** (completa)
- ✅ **Gestión de áreas** (completa)
- ✅ **Gestión de instituciones** (completa)
- ✅ **Gestión de solicitudes** (completa)
- ✅ **Reportes** (ver y generar)

### **🧪 Gestor de Laboratorios**
- ✅ **Laboratorios** (gestión completa)
- ✅ **Solicitudes** (aprobar, rechazar, gestionar)
- ✅ **Áreas** (consultar para laboratorios)
- ✅ **Reportes** (ver reportes de laboratorios)

### **👤 Usuario Regular**
- ✅ **Solicitudes** (crear, editar, ver propias)
- ✅ **Perfil** (ver y editar propio)
- ✅ **Dashboard** (acceso básico)

---

## 🔧 **CONFIGURACIÓN AVANZADA**

### **Personalizar Permisos**
1. **Editar** `actualizar_permisos_existentes.py`
2. **Modificar** la configuración de roles:
```python
'Mi Rol Personalizado': {
    'permisos': [
        'ver_dashboard',
        'mi_permiso_especifico',
        # ... más permisos
    ]
}
```

### **Agregar Nuevos Permisos**
1. **Agregar** al array `basic_permissions` en `setup_permissions.py`
2. **Ejecutar** `python setup_permissions.py`
3. **Asignar** a roles usando los scripts

### **Crear Nuevos Roles**
1. **Usar** `asignar_permisos_mejorados.py` como plantilla
2. **Agregar** configuración de nuevo rol
3. **Ejecutar** script para crear el rol

---

## 🧪 **PRUEBAS**

### **Verificar Sistema**
```bash
# Prueba completa del sistema
python test_permissions.py
```

### **Probar Funcionalidades**
1. **Iniciar sesión** con diferentes usuarios
2. **Verificar** que cada rol ve solo sus funcionalidades
3. **Comprobar** que los permisos se aplican correctamente

### **Solución de Problemas**
```bash
# Si hay problemas, reinicializar permisos
python setup_permissions.py

# Verificar modelos de base de datos
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); print('Tablas:', db.engine.table_names())"
```

---

## 📚 **ESTRUCTURA DE PERMISOS**

### **Categorías de Permisos**
- **🔐 Administración**: `admin_access`, `acceso_total`
- **👥 Usuarios**: `gestionar_usuarios`, `crear_usuario`, etc.
- **🎭 Roles**: `gestionar_roles`, `crear_rol`, etc.
- **🧪 Laboratorios**: `gestionar_laboratorios`, `crear_laboratorio`, etc.
- **📍 Áreas**: `gestionar_areas`, `crear_area`, etc.
- **🏢 Instituciones**: `gestionar_instituciones`, `crear_institucion`, etc.
- **📋 Solicitudes**: `ver_solicitudes`, `crear_solicitud`, etc.
- **👤 Perfil**: `ver_perfil`, `editar_perfil`, etc.
- **📊 Reportes**: `ver_reportes`, `generar_reportes`

### **Principios de Asignación**
- **🔒 Menor privilegio**: Solo permisos necesarios
- **🔄 Separación de funciones**: Responsabilidades divididas
- **📊 Escalabilidad**: Fácil agregar nuevos permisos
- **🎯 Funcionalidad**: Permisos alineados con tareas reales

---

## 🚨 **IMPORTANTE**

### **Antes de Implementar**
1. **📋 Hacer backup** de la base de datos
2. **🧪 Probar** en entorno de desarrollo
3. **📝 Documentar** usuarios y roles actuales
4. **🔍 Verificar** que tienes acceso de administrador

### **Después de Implementar**
1. **🧪 Probar** todas las funcionalidades
2. **👥 Asignar** usuarios a roles apropiados
3. **📚 Capacitar** a los usuarios en cambios
4. **📊 Monitorear** el sistema por problemas

---

## 🆘 **SOLUCIÓN DE PROBLEMAS**

### **Error: "Permiso no encontrado"**
```bash
# Reinicializar permisos
python setup_permissions.py
```

### **Error: "Rol no encontrado"**
```bash
# Verificar roles existentes
python -c "from app import create_app, db; from app.models.roles import Roles; app = create_app(); app.app_context().push(); print([r.nombre_rol for r in Roles.query.all()])"
```

### **Error: "Usuario sin permisos"**
```bash
# Asignar rol al usuario
python asignar_usuarios_roles.py
```

### **Error: "Template no carga"**
- Verificar que `current_user` esté disponible
- Verificar que las funciones de permisos estén registradas en `app/__init__.py`

---

## 💡 **CONSEJOS**

### **Para Administradores**
- 🛡️ **Usa** el rol "Administrador" para gestión diaria
- 👑 **Reserva** "Super Administrador" para tareas críticas
- 🔍 **Monitorea** regularmente las asignaciones de roles

### **Para Desarrollo**
- 📝 **Documenta** nuevos permisos que agregues
- 🧪 **Prueba** siempre con diferentes roles
- 🔄 **Actualiza** este README con cambios

### **Para Usuarios**
- 👤 **Solicita** el rol apropiado a tu función
- 📞 **Contacta** al administrador si no tienes acceso
- 📚 **Familiarízate** con las funcionalidades de tu rol

---

## 📞 **SOPORTE**

Si tienes problemas:
1. **🔍 Consulta** este README
2. **🧪 Ejecuta** `python test_permissions.py`
3. **📞 Contacta** al administrador del sistema
4. **💬 Documenta** el problema para futuras referencias

---

## 🎉 **¡LISTO!**

Con este sistema de permisos mejorado tendrás:
- 🔐 **Seguridad** robusta y escalable
- 👥 **Roles** organizados por función
- 🛠️ **Herramientas** para gestión fácil
- 📊 **Visibilidad** completa del sistema

¡Disfruta de tu sistema de permisos mejorado! 🚀 