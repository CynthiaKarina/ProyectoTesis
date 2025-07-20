# 🗃️ Guía de Migraciones con Flask-Migrate

## 📋 ¿Qué son las migraciones?

Las migraciones son scripts que permiten versionar y aplicar cambios a la estructura de la base de datos de forma controlada y reproducible. Flask-Migrate utiliza Alembic (de SQLAlchemy) para generar y aplicar estos cambios automáticamente.

## 🚀 Configuración

Flask-Migrate ya está configurado en este proyecto:

- ✅ **Instalado**: Flask-Migrate 4.1.0
- ✅ **Configurado**: En `app/__init__.py`
- ✅ **Inicializado**: Carpeta `migrations/` creada
- ✅ **Sincronizado**: Base de datos actual marcada como migrada

## 🛠️ Comandos Básicos

### Opción 1: Usando Flask CLI (Recomendado)
```bash
# Ver estado actual
flask db current

# Crear nueva migración
flask db migrate -m "Descripción del cambio"

# Aplicar migraciones pendientes
flask db upgrade

# Revertir última migración
flask db downgrade

# Ver historial
flask db history
```

### Opción 2: Usando el script de utilidad
```bash
# Ver ayuda
python migrate_db.py help

# Crear nueva migración
python migrate_db.py migrate -m "Agregar tabla usuarios"

# Aplicar migraciones
python migrate_db.py upgrade

# Ver estado actual
python migrate_db.py current
```

## 📝 Flujo de Trabajo Típico

### 1. **Modificar un modelo**
```python
# En app/models/user.py
class User(db.Model):
    # ... campos existentes ...
    nueva_columna = db.Column(db.String(100), nullable=True)  # ← Nuevo campo
```

### 2. **Crear migración**
```bash
flask db migrate -m "Agregar nueva_columna a User"
```

### 3. **Revisar la migración generada**
- Archivo creado en: `migrations/versions/xxxxx_agregar_nueva_columna_a_user.py`
- **¡IMPORTANTE!** Revisar el contenido antes de aplicar

### 4. **Aplicar la migración**
```bash
flask db upgrade
```

### 5. **Verificar en base de datos**
- La nueva columna debe aparecer en la tabla `usuario`

## ⚠️ Casos Especiales

### **Cambios que requieren datos**
Si tu migración necesita poblar datos:

```python
# En el archivo de migración generado
def upgrade():
    # Operaciones de esquema (automáticas)
    op.add_column('usuario', sa.Column('nuevo_campo', sa.String(50)))
    
    # Operaciones de datos (manuales)
    connection = op.get_bind()
    connection.execute("UPDATE usuario SET nuevo_campo = 'valor_por_defecto'")

def downgrade():
    op.drop_column('usuario', 'nuevo_campo')
```

### **Renombrar columnas/tablas**
Flask-Migrate puede no detectar renombramientos automáticamente:

```python
# En lugar de renombrar, crear nueva y migrar datos
def upgrade():
    # Crear nueva columna
    op.add_column('usuario', sa.Column('email_nuevo', sa.String(120)))
    
    # Copiar datos
    connection = op.get_bind()
    connection.execute("UPDATE usuario SET email_nuevo = email_viejo")
    
    # Eliminar columna vieja
    op.drop_column('usuario', 'email_viejo')
```

## 🔧 Comandos de Diagnóstico

```bash
# Ver estado actual de la base de datos
flask db current

# Ver todas las migraciones disponibles
flask db history

# Ver migraciones pendientes
flask db heads

# Ver diferencias sin crear migración
flask db show [revision]
```

## 🚨 Solución de Problemas

### **Error: "Target database is not up to date"**
```bash
flask db stamp head  # Marca como actual sin aplicar cambios
```

### **Error: "Can't locate revision identified by"**
```bash
# Limpiar y reinicializar (¡CUIDADO! Solo en desarrollo)
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### **Conflictos en migraciones**
1. Resolver conflictos manualmente en el archivo de migración
2. O crear nueva migración que solucione el conflicto

## 📚 Buenas Prácticas

### ✅ **Hacer**
- Siempre revisar las migraciones antes de aplicar
- Usar mensajes descriptivos en las migraciones
- Hacer backup de la base de datos antes de migraciones importantes
- Probar migraciones en desarrollo antes de producción
- Incluir tanto `upgrade()` como `downgrade()` cuando sea posible

### ❌ **No hacer**
- Editar migraciones ya aplicadas en producción
- Aplicar migraciones directamente en producción sin probar
- Ignorar errores en las migraciones
- Hacer cambios manuales en la base de datos sin migración correspondiente

## 🔄 Workflow para Equipos

1. **Desarrollador A** crea migración:
   ```bash
   git pull origin main
   flask db migrate -m "Agregar tabla productos"
   git add migrations/
   git commit -m "Migración: Agregar tabla productos"
   git push origin feature/productos
   ```

2. **Desarrollador B** aplica migración:
   ```bash
   git pull origin main
   flask db upgrade  # Aplica nuevas migraciones
   ```

## 📞 Ayuda y Recursos

- [Documentación oficial Flask-Migrate](https://flask-migrate.readthedocs.io/)
- [Documentación Alembic](https://alembic.sqlalchemy.org/)
- Script de utilidad: `python migrate_db.py help`

---

> **💡 Tip**: Siempre hacer backup de la base de datos antes de aplicar migraciones en producción. 