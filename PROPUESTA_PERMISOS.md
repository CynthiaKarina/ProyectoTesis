# 🔐 PROPUESTA DE ASIGNACIÓN MEJORADA DE PERMISOS

## 📊 **Situación Actual vs Propuesta**

### ❌ **PROBLEMAS IDENTIFICADOS:**
1. **Rol "Administrador"** - Le faltan permisos importantes
2. **Permisos no asignados** - Algunos permisos no están en ningún rol
3. **Roles genéricos** - Falta especialización por área funcional
4. **Inconsistencias** - Permisos relacionados separados entre roles

---

## 🎯 **PROPUESTA DE ROLES MEJORADOS**

### **1. 👑 Super Administrador**
- **Descripción**: Acceso completo y total al sistema
- **Permisos**: `acceso_total` (automáticamente incluye todos los permisos)
- **Usuarios recomendados**: Desarrolladores, administradores de sistema

### **2. 🛡️ Administrador**
- **Descripción**: Administrador del sistema con permisos completos de gestión
- **Permisos**: **TODOS** los permisos excepto `acceso_total`
- **Funcionalidades**:
  - ✅ Administración general (`admin_access`, `ver_dashboard`)
  - ✅ Gestión de usuarios (crear, editar, eliminar, gestionar)
  - ✅ Gestión de roles y permisos (completa)
  - ✅ Gestión de laboratorios (completa)
  - ✅ Gestión de áreas (completa)
  - ✅ Gestión de instituciones (completa)
  - ✅ Gestión de solicitudes (completa)
  - ✅ Perfil personal (completo)
  - ✅ Reportes (ver y generar)

### **3. 🧪 Gestor de Laboratorios**
- **Descripción**: Gestión completa de laboratorios y solicitudes relacionadas
- **Permisos específicos**:
  - `ver_dashboard`
  - **Laboratorios**: `gestionar_laboratorios`, `crear_laboratorio`, `editar_laboratorio`, `eliminar_laboratorio`
  - **Áreas**: `gestionar_areas` (para gestionar áreas de laboratorios)
  - **Solicitudes**: `ver_solicitudes`, `crear_solicitud`, `editar_solicitud`, `eliminar_solicitud`, `aprobar_solicitud`, `rechazar_solicitud`, `ver_todas_solicitudes`
  - **Perfil**: `ver_perfil`, `editar_perfil`, `cambiar_password`
  - **Reportes**: `ver_reportes`

### **4. 👥 Gestor de Usuarios** *(NUEVO ROL)*
- **Descripción**: Gestión de usuarios e instituciones
- **Permisos específicos**:
  - `ver_dashboard`
  - **Usuarios**: `gestionar_usuarios`, `crear_usuario`, `editar_usuario`, `eliminar_usuario`
  - **Instituciones**: `gestionar_instituciones`, `crear_institucion`, `editar_institucion`, `eliminar_institucion`
  - **Áreas**: `gestionar_areas` (para asignar áreas a usuarios)
  - **Perfil**: `ver_perfil`, `editar_perfil`, `cambiar_password`
  - **Reportes**: `ver_reportes`

### **5. 🎓 Coordinador Académico** *(NUEVO ROL)*
- **Descripción**: Gestión de áreas, instituciones y supervisión de solicitudes
- **Permisos específicos**:
  - `ver_dashboard`
  - **Áreas**: `gestionar_areas`, `crear_area`, `editar_area`, `eliminar_area`
  - **Instituciones**: `gestionar_instituciones`, `crear_institucion`, `editar_institucion`, `eliminar_institucion`
  - **Solicitudes**: `ver_todas_solicitudes`, `aprobar_solicitud`, `rechazar_solicitud`
  - **Perfil**: `ver_perfil`, `editar_perfil`, `cambiar_password`
  - **Reportes**: `ver_reportes`

### **6. 👤 Usuario Regular**
- **Descripción**: Usuario estándar con permisos básicos de uso
- **Permisos específicos**:
  - `ver_dashboard`
  - **Solicitudes**: `crear_solicitud`, `editar_solicitud`, `ver_solicitudes`
  - **Perfil**: `ver_perfil`, `editar_perfil`, `cambiar_password`

### **7. 👁️ Usuario Invitado**
- **Descripción**: Acceso básico de solo lectura
- **Permisos específicos**:
  - `ver_dashboard`
  - `ver_perfil`

---

## 📋 **MATRIZ DE PERMISOS POR ROL**

| Permiso | Super Admin | Admin | Gestor Lab | Gestor User | Coord Acad | Usuario | Invitado |
|---------|-------------|-------|------------|-------------|------------|---------|----------|
| `acceso_total` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `admin_access` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `ver_dashboard` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **USUARIOS** |
| `gestionar_usuarios` | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `crear_usuario` | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `editar_usuario` | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `eliminar_usuario` | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **ROLES Y PERMISOS** |
| `gestionar_roles` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `crear_rol` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `editar_rol` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `eliminar_rol` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `gestionar_permisos` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `asignar_permisos` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **LABORATORIOS** |
| `gestionar_laboratorios` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `crear_laboratorio` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `editar_laboratorio` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `eliminar_laboratorio` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **ÁREAS** |
| `gestionar_areas` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| `crear_area` | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| `editar_area` | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| `eliminar_area` | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **INSTITUCIONES** |
| `gestionar_instituciones` | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| `crear_institucion` | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| `editar_institucion` | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| `eliminar_institucion` | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| **SOLICITUDES** |
| `ver_solicitudes` | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| `crear_solicitud` | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| `editar_solicitud` | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| `eliminar_solicitud` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `aprobar_solicitud` | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| `rechazar_solicitud` | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| `ver_todas_solicitudes` | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| **PERFIL** |
| `ver_perfil` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `editar_perfil` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `cambiar_password` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **REPORTES** |
| `ver_reportes` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| `generar_reportes` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 🎯 **BENEFICIOS DE LA PROPUESTA**

### **1. 🔐 Seguridad Mejorada**
- ✅ **Principio de menor privilegio**: Cada rol tiene solo los permisos necesarios
- ✅ **Segregación de funciones**: Responsabilidades separadas por área
- ✅ **Roles especializados**: Permisos específicos para funciones específicas

### **2. 📚 Organización Funcional**
- ✅ **Roles por área**: Gestor de Laboratorios, Gestor de Usuarios, etc.
- ✅ **Permisos agrupados**: Permisos relacionados van juntos
- ✅ **Escalabilidad**: Fácil agregar nuevos roles especializados

### **3. 🛠️ Mantenibilidad**
- ✅ **Configuración clara**: Fácil entender qué hace cada rol
- ✅ **Modificación sencilla**: Cambios por área funcional
- ✅ **Trazabilidad**: Permisos asignados de forma lógica

### **4. 👥 Experiencia de Usuario**
- ✅ **Interfaces personalizadas**: Cada rol ve solo lo que necesita
- ✅ **Flujos optimizados**: Permisos alineados con tareas reales
- ✅ **Menos errores**: Usuarios no acceden a funciones incorrectas

---

## 🚀 **IMPLEMENTACIÓN**

### **Para aplicar la propuesta:**

```bash
# 1. Ejecutar el script de configuración
python asignar_permisos_mejorados.py

# 2. Verificar los cambios
python test_permissions.py

# 3. Asignar usuarios a roles apropiados
# (Usar la interfaz de administración o scripts adicionales)
```

### **Usuarios recomendados por rol:**

- **👑 Super Administrador**: Desarrolladores, administradores técnicos
- **🛡️ Administrador**: Administradores de sistema, directores
- **🧪 Gestor de Laboratorios**: Jefes de laboratorio, técnicos senior
- **👥 Gestor de Usuarios**: Personal de recursos humanos, coordinadores
- **🎓 Coordinador Académico**: Coordinadores académicos, supervisores
- **👤 Usuario Regular**: Estudiantes, investigadores, personal general
- **👁️ Usuario Invitado**: Visitantes, consultores externos

---

## ✅ **PRÓXIMOS PASOS**

1. **Revisar la propuesta** y ajustar según necesidades específicas
2. **Ejecutar el script** `asignar_permisos_mejorados.py`
3. **Probar el sistema** con diferentes usuarios
4. **Asignar usuarios** a los roles apropiados
5. **Documentar** los cambios para el equipo
6. **Capacitar** a los usuarios en las nuevas funcionalidades

---

## 📞 **¿Necesitas Ayuda?**

Si tienes dudas sobre:
- 🔄 Cómo aplicar los cambios
- 👥 Qué rol asignar a qué usuario
- 🔧 Cómo personalizar la configuración
- 🧪 Cómo probar el sistema

¡Pregúntame y te ayudo paso a paso! 🚀 