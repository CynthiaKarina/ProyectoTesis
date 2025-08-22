from flask import Blueprint, render_template, redirect, url_for, flash, session, jsonify, request, current_app as app
from flask_login import current_user, login_required
from app.database.connection import get_db_connection
from app.models.proyecto import Proyecto
from app import db
from app.models.user import User
from app.models.institucion import Institucion
from app.models.area import Area
from app.models.laboratorio import Laboratorio

home_bp = Blueprint('home', __name__)

@home_bp.route('/home')
@login_required  # ✅ USAR FLASK-LOGIN CORRECTAMENTE
def index():
    # ✅ VERIFICAR ACCESO ADMINISTRATIVO USANDO EL SISTEMA DE PERMISOS
    from app.utils.permissions import has_admin_access
    admin_access = has_admin_access()
    
    # Obtener estadísticas reales de la base de datos
    stats = get_home_statistics()

    # Inyectar solicitudes pendientes para Super Admin (o quien tenga permiso gestionar_roles)
    role_requests = []
    role_requests_view = []
    try:
        from app.utils.permissions import has_permission
        if has_permission('gestionar_roles'):
            from app.models.role_request import RoleRequest
            role_requests = (db.session.query(RoleRequest)
                             .filter(RoleRequest.status == 'pendiente')
                             .order_by(RoleRequest.created_at.desc())
                             .limit(10)
                             .all())
            # Enriquecer con nombres de usuario y laboratorio
            try:
                user_ids = sorted({r.id_usuario for r in role_requests})
                lab_ids = sorted({r.id_laboratorio for r in role_requests if getattr(r, 'id_laboratorio', None)})
                users_map = {u.id_usuario: u for u in User.query.filter(User.id_usuario.in_(user_ids)).all()} if user_ids else {}
                labs_map = {l.id_laboratorio: l for l in Laboratorio.query.filter(Laboratorio.id_laboratorio.in_(lab_ids)).all()} if lab_ids else {}
                for r in role_requests:
                    u = users_map.get(r.id_usuario)
                    lab = labs_map.get(r.id_laboratorio) if getattr(r, 'id_laboratorio', None) else None
                    nombre_usuario = None
                    if u:
                        nombre_parts = [getattr(u, 'nombre', ''), getattr(u, 'apellido_paterno', ''), getattr(u, 'apellido_materno', '')]
                        nombre_usuario = ' '.join([p for p in nombre_parts if p]).strip() or u.username
                    role_requests_view.append({
                        'id_request': r.id_request,
                        'usuario_nombre': nombre_usuario or f"ID {r.id_usuario}",
                        'usuario_username': getattr(u, 'username', '') if u else '',
                        'rol': r.requested_role,
                        'laboratorio_nombre': getattr(lab, 'nombre_laboratorio', None) if lab else None,
                        'fecha': r.created_at.strftime('%Y-%m-%d %H:%M') if getattr(r, 'created_at', None) else ''
                    })
            except Exception as e_map:
                print(f"Error enriqueciendo solicitudes para home: {e_map}")
    except Exception as e:
        print(f"Error obteniendo solicitudes para home: {e}")
        role_requests = []
    
    # Inyectar respuestas de solicitudes para el usuario actual (aprobado/rechazado)
    my_role_responses = []
    try:
        from app.models.role_request import RoleRequest
        if getattr(current_user, 'id_usuario', None):
            my_role_responses = (
                db.session.query(RoleRequest)
                .filter(RoleRequest.id_usuario == current_user.id_usuario,
                        RoleRequest.status.in_(['aprobado', 'rechazado']))
                .order_by(RoleRequest.reviewed_at.desc().nullslast(), RoleRequest.created_at.desc())
                .limit(5)
                .all()
            )
    except Exception as e:
        print(f"Error obteniendo respuestas de solicitudes del usuario: {e}")
        my_role_responses = []
    
    # Contadores para el navbar
    pending_for_admin = len(role_requests_view)
    responses_for_user = len(my_role_responses)
    
    return render_template('home.html', usuario=current_user, admin_access=admin_access, stats=stats,
                           role_requests=role_requests, role_requests_view=role_requests_view,
                           my_role_responses=my_role_responses,
                           pending_for_admin=pending_for_admin,
                           responses_for_user=responses_for_user)

@home_bp.route('/pagina/<nombre>')
@login_required
def navegar_pagina(nombre):
    paginas_permitidas = {
        'proyectos': 'proyectos.html',
        'investigadores': 'investigadores.html', 
        'instituciones': 'instituciones.html',
        'insumos': 'materiales.html',
        'servicios': 'servicios.html',
        'productos': 'productos.html',
        'contacto': 'contacto.html',
        'acerca': 'acerca.html'
    }
    
    if nombre in paginas_permitidas:
        # Obtener datos específicos según la página
        page_data = get_page_data(nombre)
        return render_template(paginas_permitidas[nombre], 
                             usuario=current_user, 
                             page_data=page_data,
                             page_name=nombre)
    else:
        flash('Página no encontrada', 'error')
        return redirect(url_for('home.index'))

# Nueva ruta para ver la página de prueba con el diseño mejorado
@home_bp.route('/prueba-diseno')
def prueba_diseno():
    """Página de prueba para ver el nuevo sistema de diseño"""
    return render_template('ejemplo-pagina-mejorada.html', usuario=current_user)

@home_bp.route('/prueba-responsivo')
def prueba_responsivo():
    """Página de prueba para verificar la responsividad completa"""
    return render_template('prueba-responsivo.html')

@home_bp.route('/debug-template')
def debug_template():
    """Página de debug para verificar el template"""
    return render_template('debug_simple.html')

def get_home_statistics():
    """Obtener estadísticas reales de la base de datos para el home"""
    try:
        conn = get_db_connection()
        if not conn:
            return get_default_statistics()
            
        cursor = conn.cursor()
        stats = {}
        
        # Contar laboratorios
        cursor.execute("SELECT COUNT(*) FROM laboratorio WHERE disponibilidad = 'Disponible'")
        stats['laboratorios'] = cursor.fetchone()[0] or 0
        
        # Contar proyectos usando el modelo
        try:
            stats['proyectos'] = Proyecto.query.count()
        except Exception as e:
            print(f"Error contando proyectos: {e}")
            stats['proyectos'] = 0
        
        # Contar usuarios/investigadores
        cursor.execute("SELECT COUNT(*) FROM usuario WHERE activo = 1")
        stats['investigadores'] = cursor.fetchone()[0] or 0
        
        # Contar instituciones (ajustar campo según estructura real)
        try:
            cursor.execute("SELECT COUNT(*) FROM institucion WHERE activa = 1")
            stats['instituciones'] = cursor.fetchone()[0] or 0
        except:
            cursor.execute("SELECT COUNT(*) FROM institucion")
            stats['instituciones'] = cursor.fetchone()[0] or 0
        
        # Estadísticas por área
        cursor.execute("""
            SELECT a.nombre_area, COUNT(l.id_laboratorio) as total_labs
            FROM area a
            LEFT JOIN laboratorio l ON a.id_area = l.id_area
            WHERE l.disponibilidad = 'Disponible'
            GROUP BY a.id_area, a.nombre_area
            ORDER BY total_labs DESC
            LIMIT 4
        """)
        stats['areas_destacadas'] = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return stats
        
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return get_default_statistics()

def get_default_statistics():
    """Estadísticas por defecto si hay error con la base de datos"""
    return {
        'laboratorios': 18,
        'proyectos': 25,
        'investigadores': 45,
        'instituciones': 7,
        'areas_destacadas': [
            ('Biotecnología', 8),
            ('Ingeniería', 6),
            ('Informática', 4),
            ('Ciencias Básicas', 3)
        ]
    }

@home_bp.route('/api/search')
def api_search():
    """API mejorada para búsqueda global - Sin login requerido para testing"""
    query = request.args.get('q', '').strip()
    categories = request.args.getlist('categories')
    
    print(f"🔍 Búsqueda recibida: query='{query}', categories={categories}")
    
    # Validaciones mejoradas
    if not query:
        return jsonify({
            'success': False,
            'error': 'Por favor ingresa un término de búsqueda',
            'code': 'QUERY_REQUIRED'
        }), 400
    
    if len(query) < 2:
        return jsonify({
            'success': False,
            'error': 'El término de búsqueda debe tener al menos 2 caracteres',
            'code': 'QUERY_TOO_SHORT'
        }), 400
    
    if not categories:
        return jsonify({
            'success': False,
            'error': 'Selecciona al menos una categoría para buscar',
            'code': 'NO_CATEGORIES'
        }), 400
    
    # Validar categorías permitidas
    valid_categories = ['laboratorios', 'proyectos', 'investigadores', 'instituciones', 'convocatorias', 'publicaciones']
    categories = [cat for cat in categories if cat in valid_categories]
    
    if not categories:
        return jsonify({
            'success': False,
            'error': 'No se seleccionaron categorías válidas',
            'code': 'NO_VALID_CATEGORIES'
        }), 400
    
    try:
        # Realizar búsqueda
        print(f"📊 Realizando búsqueda en categorías: {categories}")
        results = perform_global_search_improved(query, categories)
        
        # Calcular estadísticas de resultados
        total_results = sum(len(results.get(cat, [])) for cat in results)
        print(f"📈 Resultados encontrados: {total_results}")
        
        return jsonify({
            'success': True,
            'results': results,
            'query': query,
            'categories': categories,
            'total_results': total_results,
            'message': f'Se encontraron {total_results} resultados para "{query}"' if total_results > 0 else f'No se encontraron resultados para "{query}"'
        })
        
    except Exception as e:
        print(f"❌ Error en búsqueda global: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor. Intenta nuevamente.',
            'code': 'INTERNAL_ERROR',
            'details': str(e) if app.debug else None
        }), 500

@home_bp.route('/api/search/suggestions')
def api_search_suggestions():
    """API para sugerencias de búsqueda - Sin login requerido"""
    query = request.args.get('q', '').strip()
    
    print(f"💡 Sugerencias solicitadas para: '{query}'")
    
    if len(query) < 2:
        return jsonify({'success': True, 'suggestions': []})
    
    try:
        suggestions = get_search_suggestions_improved(query)
        print(f"💡 Sugerencias encontradas: {len(suggestions)}")
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'query': query
        })
    except Exception as e:
        print(f"❌ Error obteniendo sugerencias: {e}")
        return jsonify({
            'success': False,
            'suggestions': [],
            'error': str(e)
        })

def perform_global_search(query, categories):
    """Realizar búsqueda global en la base de datos"""
    conn = get_db_connection()
    if not conn:
        return {}
        
    cursor = conn.cursor(dictionary=True)
    results = {}
    
    try:
        # Buscar en laboratorios
        if 'laboratorios' in categories:
            cursor.execute("""
                SELECT l.id_laboratorio as id, l.nombre_laboratorio as name, 
                       l.descripcion as description, i.nombre_institucion as institution,
                       'laboratorios' as type
                FROM laboratorio l
                LEFT JOIN institucion i ON l.id_institucion = i.id_institucion
                WHERE (l.nombre_laboratorio LIKE %s OR l.descripcion LIKE %s)
                AND l.disponibilidad = 'Disponible'
                LIMIT 10
            """, (f'%{query}%', f'%{query}%'))
            results['laboratorios'] = cursor.fetchall()
        
        # Buscar en usuarios/investigadores
        if 'investigadores' in categories:
            cursor.execute("""
                SELECT u.id_usuario as id, 
                       CONCAT(u.nombre, ' ', u.apellido_paterno, ' ', u.apellido_materno) as name,
                       a.nombre_area as specialty, i.nombre_institucion as institution,
                       'investigadores' as type
                FROM usuario u
                LEFT JOIN area a ON u.id_area = a.id_area
                LEFT JOIN institucion i ON u.id_institucion = i.id_institucion
                WHERE (u.nombre LIKE %s OR u.apellido_paterno LIKE %s OR u.apellido_materno LIKE %s)
                AND u.activo = 1
                LIMIT 10
            """, (f'%{query}%', f'%{query}%', f'%{query}%'))
            results['investigadores'] = cursor.fetchall()
        
        # Buscar en instituciones
        if 'instituciones' in categories:
            try:
                cursor.execute("""
                    SELECT i.id_institucion as id, i.nombre_institucion as name,
                           i.descripcion as description, i.ubicacion as location,
                           'instituciones' as type
                    FROM institucion i
                    WHERE (i.nombre_institucion LIKE %s OR i.descripcion LIKE %s)
                    AND i.activa = 1
                    LIMIT 10
                """, (f'%{query}%', f'%{query}%'))
                results['instituciones'] = cursor.fetchall()
            except:
                # Consulta alternativa sin campos que pueden no existir
                cursor.execute("""
                    SELECT i.id_institucion as id, i.nombre_institucion as name,
                           '' as description, i.ubicacion as location,
                           'instituciones' as type
                    FROM institucion i
                    WHERE i.nombre_institucion LIKE %s
                    LIMIT 10
                """, (f'%{query}%',))
                results['instituciones'] = cursor.fetchall()
        
        # Buscar proyectos usando el modelo
        if 'proyectos' in categories:
            try:
                proyectos_query = Proyecto.query.filter(
                    (Proyecto.nombre_proyecto.contains(query)) |
                    (Proyecto.resumen.contains(query))
                ).limit(10).all()
                
                results['proyectos'] = []
                for proyecto in proyectos_query:
                    results['proyectos'].append({
                        'id': proyecto.id_proyecto,
                        'name': proyecto.nombre_proyecto,
                        'description': proyecto.resumen_corto,
                        'type': 'proyectos',
                        'estatus': proyecto.estado_proyecto,
                        'tipo': proyecto.tipo_proyecto,
                        'fecha': proyecto.fecha_formateada
                    })
            except Exception as e:
                print(f"Error buscando proyectos: {e}")
                results['proyectos'] = []
        
    except Exception as e:
        print(f"Error en búsqueda específica: {e}")
    finally:
        cursor.close()
        conn.close()
    
    return results

def get_search_suggestions(query):
    """Obtener sugerencias de búsqueda basadas en el query"""
    conn = get_db_connection()
    suggestions = []
    
    if not conn:
        return suggestions
    
    try:
        cursor = conn.cursor()
        query_lower = query.lower()
        
        # Sugerencias de laboratorios
        try:
            cursor.execute("""
                SELECT DISTINCT nombre_laboratorio 
                FROM laboratorio 
                WHERE LOWER(nombre_laboratorio) LIKE %s 
                LIMIT 3
            """, (f'%{query_lower}%',))
            
            for (nombre,) in cursor.fetchall():
                suggestions.append({
                    'text': nombre,
                    'category': 'Laboratorio',
                    'icon': 'fas fa-flask',
                    'type': 'laboratorio'
                })
        except Exception as e:
            print(f"Error buscando sugerencias de laboratorios: {e}")
        
        # Sugerencias de proyectos
        try:
            from app.models.proyecto import Proyecto
            proyectos = Proyecto.query.filter(
                Proyecto.nombre_proyecto.contains(query)
            ).limit(3).all()
            
            for proyecto in proyectos:
                suggestions.append({
                    'text': proyecto.nombre_proyecto,
                    'category': 'Proyecto',
                    'icon': 'fas fa-project-diagram',
                    'type': 'proyecto'
                })
        except Exception as e:
            print(f"Error buscando sugerencias de proyectos: {e}")
        
        # Sugerencias de usuarios/investigadores
        try:
            cursor.execute("""
                SELECT DISTINCT CONCAT(nombre, ' ', apellido) as nombre_completo
                FROM usuario 
                WHERE LOWER(CONCAT(nombre, ' ', apellido)) LIKE %s 
                LIMIT 3
            """, (f'%{query_lower}%',))
            
            for (nombre_completo,) in cursor.fetchall():
                suggestions.append({
                    'text': nombre_completo,
                    'category': 'Investigador',
                    'icon': 'fas fa-user-tie',
                    'type': 'investigador'
                })
        except Exception as e:
            print(f"Error buscando sugerencias de investigadores: {e}")
        
        # Sugerencias de instituciones
        try:
            cursor.execute("""
                SELECT DISTINCT nombre_institucion 
                FROM institucion 
                WHERE LOWER(nombre_institucion) LIKE %s 
                LIMIT 3
            """, (f'%{query_lower}%',))
            
            for (nombre,) in cursor.fetchall():
                suggestions.append({
                    'text': nombre,
                    'category': 'Institución',
                    'icon': 'fas fa-university',
                    'type': 'institucion'
                })
        except Exception as e:
            print(f"Error buscando sugerencias de instituciones: {e}")
        
        # Sugerencias de áreas
        try:
            cursor.execute("""
                SELECT DISTINCT nombre_area 
                FROM area 
                WHERE LOWER(nombre_area) LIKE %s 
                LIMIT 2
            """, (f'%{query_lower}%',))
            
            for (nombre,) in cursor.fetchall():
                suggestions.append({
                    'text': nombre,
                    'category': 'Área de investigación',
                    'icon': 'fas fa-microscope',
                    'type': 'area'
                })
        except Exception as e:
            print(f"Error buscando sugerencias de áreas: {e}")
        
    except Exception as e:
        print(f"Error general obteniendo sugerencias: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
    
    return suggestions[:8]  # Limitar a 8 sugerencias máximo

def get_search_suggestions_improved(query):
    """Función mejorada para obtener sugerencias con mejor manejo de errores"""
    print(f"💡 Generando sugerencias mejoradas para: '{query}'")
    suggestions = []
    
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ No hay conexión a BD, usando sugerencias locales")
            return get_local_suggestions(query)
            
        cursor = conn.cursor()
        query_lower = query.lower()
        
        # Sugerencias de laboratorios (más seguras)
        try:
            cursor.execute("""
                SELECT DISTINCT nombre_laboratorio 
                FROM laboratorio 
                WHERE LOWER(nombre_laboratorio) LIKE %s 
                LIMIT 3
            """, (f'%{query_lower}%',))
            
            for (nombre,) in cursor.fetchall():
                suggestions.append({
                    'text': nombre,
                    'category': 'Laboratorio',
                    'icon': 'fas fa-flask',
                    'type': 'laboratorio'
                })
        except Exception as e:
            print(f"⚠️ Error en sugerencias de laboratorios: {e}")
        
        # Sugerencias de proyectos usando SQLAlchemy
        try:
            from app.models.proyecto import Proyecto
            proyectos = Proyecto.query.filter(
                Proyecto.nombre_proyecto.contains(query)
            ).limit(3).all()
            
            for proyecto in proyectos:
                suggestions.append({
                    'text': proyecto.nombre_proyecto,
                    'category': 'Proyecto',
                    'icon': 'fas fa-project-diagram',
                    'type': 'proyecto'
                })
        except Exception as e:
            print(f"⚠️ Error en sugerencias de proyectos: {e}")
        
        # Sugerencias de usuarios/investigadores
        try:
            cursor.execute("""
                SELECT DISTINCT CONCAT(nombre, ' ', COALESCE(apellido_paterno, '')) as nombre_completo
                FROM usuario 
                WHERE (LOWER(nombre) LIKE %s OR LOWER(apellido_paterno) LIKE %s)
                AND LENGTH(CONCAT(nombre, ' ', COALESCE(apellido_paterno, ''))) > 3
                LIMIT 3
            """, (f'%{query_lower}%', f'%{query_lower}%'))
            
            for (nombre_completo,) in cursor.fetchall():
                if nombre_completo and nombre_completo.strip():
                    suggestions.append({
                        'text': nombre_completo.strip(),
                        'category': 'Investigador',
                        'icon': 'fas fa-user-tie',
                        'type': 'investigador'
                    })
        except Exception as e:
            print(f"⚠️ Error en sugerencias de investigadores: {e}")
        
        # Sugerencias de instituciones
        try:
            cursor.execute("""
                SELECT DISTINCT nombre_institucion 
                FROM institucion 
                WHERE LOWER(nombre_institucion) LIKE %s 
                LIMIT 2
            """, (f'%{query_lower}%',))
            
            for (nombre,) in cursor.fetchall():
                suggestions.append({
                    'text': nombre,
                    'category': 'Institución',
                    'icon': 'fas fa-university',
                    'type': 'institucion'
                })
        except Exception as e:
            print(f"⚠️ Error en sugerencias de instituciones: {e}")
        
    except Exception as e:
        print(f"❌ Error general en sugerencias: {e}")
        return get_local_suggestions(query)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    # Si no hay sugerencias de BD, usar locales
    if not suggestions:
        suggestions = get_local_suggestions(query)
    
    print(f"💡 Sugerencias generadas: {len(suggestions)}")
    return suggestions[:8]

def get_local_suggestions(query):
    """Sugerencias locales como fallback"""
    predefined = [
        { 'text': 'laboratorio', 'category': 'Laboratorios', 'icon': 'fas fa-flask', 'type': 'laboratorio' },
        { 'text': 'proyecto', 'category': 'Proyectos', 'icon': 'fas fa-project-diagram', 'type': 'proyecto' },
        { 'text': 'investigador', 'category': 'Investigadores', 'icon': 'fas fa-user-tie', 'type': 'investigador' },
        { 'text': 'institución', 'category': 'Instituciones', 'icon': 'fas fa-university', 'type': 'institucion' },
        { 'text': 'biotecnología', 'category': 'Área de investigación', 'icon': 'fas fa-dna', 'type': 'area' },
        { 'text': 'informática', 'category': 'Área de investigación', 'icon': 'fas fa-laptop-code', 'type': 'area' },
        { 'text': 'ingeniería', 'category': 'Área de investigación', 'icon': 'fas fa-cogs', 'type': 'area' },
        { 'text': 'química', 'category': 'Área de investigación', 'icon': 'fas fa-atom', 'type': 'area' }
    ]
    
    return [item for item in predefined if query.lower() in item['text'].lower()][:5]

def perform_global_search_improved(query, categories):
    """Función de búsqueda mejorada con mejor manejo de errores"""
    print(f"🔍 Iniciando búsqueda mejorada: '{query}' en {categories}")
    
    results = {}
    
    # Inicializar todas las categorías
    for category in categories:
        results[category] = []
    
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ No se pudo conectar a la base de datos")
            return results
            
        cursor = conn.cursor(dictionary=True)
        
        # Buscar en laboratorios
        if 'laboratorios' in categories:
            try:
                print("🧪 Buscando en laboratorios...")
                cursor.execute("""
                    SELECT l.id_laboratorio as id, l.nombre_laboratorio as name, 
                           COALESCE(l.descripcion, 'Sin descripción') as description, 
                           COALESCE(i.nombre_institucion, 'Sin institución') as institution,
                           'laboratorios' as type
                    FROM laboratorio l
                    LEFT JOIN institucion i ON l.id_institucion = i.id_institucion
                    WHERE (l.nombre_laboratorio LIKE %s OR COALESCE(l.descripcion, '') LIKE %s)
                    LIMIT 10
                """, (f'%{query}%', f'%{query}%'))
                
                lab_results = cursor.fetchall()
                results['laboratorios'] = lab_results
                print(f"🧪 Laboratorios encontrados: {len(lab_results)}")
                
            except Exception as e:
                print(f"❌ Error buscando laboratorios: {e}")
                results['laboratorios'] = []
        
        # Buscar en investigadores/usuarios
        if 'investigadores' in categories:
            try:
                print("👥 Buscando en investigadores...")
                cursor.execute("""
                    SELECT u.id_usuario as id, 
                           CONCAT(COALESCE(u.nombre, ''), ' ', 
                                  COALESCE(u.apellido_paterno, ''), ' ', 
                                  COALESCE(u.apellido_materno, '')) as name,
                           COALESCE(a.nombre_area, 'Sin área') as specialty, 
                           COALESCE(i.nombre_institucion, 'Sin institución') as institution,
                           'investigadores' as type
                    FROM usuario u
                    LEFT JOIN area a ON u.id_area = a.id_area
                    LEFT JOIN institucion i ON u.id_institucion = i.id_institucion
                    WHERE (u.nombre LIKE %s OR u.apellido_paterno LIKE %s OR u.apellido_materno LIKE %s)
                    LIMIT 10
                """, (f'%{query}%', f'%{query}%', f'%{query}%'))
                
                user_results = cursor.fetchall()
                results['investigadores'] = user_results
                print(f"👥 Investigadores encontrados: {len(user_results)}")
                
            except Exception as e:
                print(f"❌ Error buscando investigadores: {e}")
                results['investigadores'] = []
        
        # Buscar en instituciones
        if 'instituciones' in categories:
            try:
                print("🏢 Buscando en instituciones...")
                cursor.execute("""
                    SELECT i.id_institucion as id, i.nombre_institucion as name,
                           COALESCE(i.descripcion, 'Sin descripción') as description, 
                           COALESCE(i.ubicacion, 'Sin ubicación') as location,
                           'instituciones' as type
                    FROM institucion i
                    WHERE (i.nombre_institucion LIKE %s OR COALESCE(i.descripcion, '') LIKE %s)
                    LIMIT 10
                """, (f'%{query}%', f'%{query}%'))
                
                inst_results = cursor.fetchall()
                results['instituciones'] = inst_results
                print(f"🏢 Instituciones encontradas: {len(inst_results)}")
                
            except Exception as e:
                print(f"❌ Error buscando instituciones: {e}")
                results['instituciones'] = []
        
        # Buscar en proyectos
        if 'proyectos' in categories:
            try:
                print("📋 Buscando en proyectos...")
                # Usar SQL directo para evitar problemas de contexto
                cursor.execute("""
                    SELECT id_proyecto as id, nombre_proyecto as name,
                           COALESCE(resumen, 'Sin descripción') as description,
                           COALESCE(estatus, 'Sin estado') as estatus,
                           COALESCE(tipo_proyecto, 'Sin tipo') as tipo,
                           'proyectos' as type
                    FROM proyecto
                    WHERE (nombre_proyecto LIKE %s OR COALESCE(resumen, '') LIKE %s)
                    LIMIT 10
                """, (f'%{query}%', f'%{query}%'))
                
                proyecto_results = cursor.fetchall()
                results['proyectos'] = proyecto_results
                print(f"📋 Proyectos encontrados: {len(proyecto_results)}")
                
            except Exception as e:
                print(f"❌ Error buscando proyectos: {e}")
                results['proyectos'] = []
        
        # Categorías no implementadas aún
        if 'convocatorias' in categories:
            print("📢 Convocatorias: No implementado aún")
            results['convocatorias'] = []
            
        if 'publicaciones' in categories:
            print("📚 Publicaciones: No implementado aún")
            results['publicaciones'] = []
        
    except Exception as e:
        print(f"❌ Error general en búsqueda: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    # Log final de resultados
    total = sum(len(results.get(cat, [])) for cat in results)
    print(f"📊 Búsqueda completada: {total} resultados totales")
    for cat, items in results.items():
        if items:
            print(f"   {cat}: {len(items)} elementos")
    
    return results

def get_page_data(page_name):
    """Obtener datos específicos para cada página"""
    try:
        conn = get_db_connection()
        if not conn:
            return {}
            
        cursor = conn.cursor(dictionary=True)
        data = {}
        
        if page_name == 'proyectos':
            try:
                # Obtener proyectos usando el modelo
                proyectos = Proyecto.query.order_by(Proyecto.fecha_creacion.desc()).limit(50).all()
                data['proyectos'] = [proyecto.to_dict() for proyecto in proyectos]
            except Exception as e:
                print(f"Error obteniendo proyectos: {e}")
                data['proyectos'] = []
        
        elif page_name == 'investigadores':
            cursor.execute("""
                SELECT u.id_usuario, u.nombre, u.apellido_paterno, u.apellido_materno,
                       u.email, a.nombre_area, i.nombre_institucion, u.ruta_imagen
                FROM usuario u
                LEFT JOIN area a ON u.id_area = a.id_area
                LEFT JOIN institucion i ON u.id_institucion = i.id_institucion
                WHERE u.activo = 1
                ORDER BY u.fecha_creacion DESC
                LIMIT 50
            """)
            data['investigadores'] = cursor.fetchall()
        
        elif page_name == 'instituciones':
            try:
                cursor.execute("""
                    SELECT i.*, COUNT(u.id_usuario) as total_usuarios
                    FROM institucion i
                    LEFT JOIN usuario u ON i.id_institucion = u.id_institucion AND u.activo = 1
                    WHERE i.activa = 1
                    GROUP BY i.id_institucion
                    ORDER BY total_usuarios DESC
                """)
                data['instituciones'] = cursor.fetchall()
            except:
                # Consulta alternativa sin campo activa
                cursor.execute("""
                    SELECT i.*, COUNT(u.id_usuario) as total_usuarios
                    FROM institucion i
                    LEFT JOIN usuario u ON i.id_institucion = u.id_institucion AND u.activo = 1
                    GROUP BY i.id_institucion
                    ORDER BY total_usuarios DESC
                """)
                data['instituciones'] = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return data
        
    except Exception as e:
        print(f"Error obteniendo datos de página {page_name}: {e}")
        return {}

@home_bp.route('/api/search/advanced')
def api_advanced_search():
    """API para búsqueda avanzada con filtros específicos"""
    print("🔍 BÚSQUEDA AVANZADA INICIADA")
    
    # Obtener parámetros de búsqueda
    query = request.args.get('q', '').strip()
    categories = request.args.getlist('categories')
    
    # Obtener filtros avanzados
    filters = {
        # Ubicación
        'estado': request.args.get('estado', '').strip(),
        'municipio': request.args.get('municipio', '').strip(),
        'ubicacion': request.args.get('ubicacion', '').strip(),
        
        # Área e institución
        'area': request.args.get('area', '').strip(),
        'institucion': request.args.get('institucion', '').strip(),
        'tipo_institucion': request.args.get('tipo_institucion', '').strip(),
        
        # Laboratorio específicos
        'capacidad_min': request.args.get('capacidad_min', '').strip(),
        'capacidad_max': request.args.get('capacidad_max', '').strip(),
        'superficie_min': request.args.get('superficie_min', '').strip(),
        'equipamiento': request.args.get('equipamiento', '').strip(),
        'disponibilidad': request.args.get('disponibilidad', '').strip(),
        'requiere_capacitacion': request.args.get('requiere_capacitacion') == 'true',
        
        # Proyecto específicos
        'tipo_proyecto': request.args.get('tipo_proyecto', '').strip(),
        'estatus_proyecto': request.args.get('estatus_proyecto', '').strip(),
        'con_adjuntos': request.args.get('con_adjuntos') == 'true',
        
        # Fechas
        'fecha_desde': request.args.get('fecha_desde', '').strip(),
        'fecha_hasta': request.args.get('fecha_hasta', '').strip(),
        'periodo': request.args.get('periodo', '').strip()
    }
    
    print(f"📊 Parámetros: query='{query}', categories={categories}")
    print(f"🔧 Filtros: {filters}")
    
    # Validaciones
    if not query and not any(filters.values()):
        return jsonify({
            'success': False,
            'error': 'Se requiere al menos un término de búsqueda o filtro',
            'code': 'NO_CRITERIA'
        }), 400
    
    if not categories:
        categories = ['laboratorios', 'proyectos', 'investigadores', 'instituciones']
    
    # Validar categorías
    valid_categories = ['laboratorios', 'proyectos', 'investigadores', 'instituciones']
    categories = [cat for cat in categories if cat in valid_categories]
    
    if not categories:
        return jsonify({
            'success': False,
            'error': 'No se seleccionaron categorías válidas',
            'code': 'NO_VALID_CATEGORIES'
        }), 400
    
    try:
        # Realizar búsqueda avanzada
        results = perform_advanced_search(query, categories, filters)
        
        # Calcular estadísticas
        total_results = sum(len(results.get(cat, [])) for cat in results)
        print(f"📈 Resultados avanzados: {total_results}")
        
        return jsonify({
            'success': True,
            'results': results,
            'query': query,
            'categories': categories,
            'filters': filters,
            'total_results': total_results,
            'message': f'Se encontraron {total_results} resultados con filtros avanzados' if total_results > 0 else 'No se encontraron resultados con los filtros aplicados'
        })
        
    except Exception as e:
        print(f"❌ Error en búsqueda avanzada: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor. Intenta nuevamente.',
            'code': 'INTERNAL_ERROR',
            'details': str(e) if app.debug else None
        }), 500

@home_bp.route('/api/filters/data')
def api_filters_data():
    """API para obtener datos para poblar los filtros (estados, municipios, áreas, etc.)"""
    try:
        filter_data = get_filter_options()
        
        return jsonify({
            'success': True,
            'data': filter_data
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo datos de filtros: {e}")
        return jsonify({
            'success': False,
            'error': 'Error obteniendo opciones de filtros',
            'details': str(e) if app.debug else None
        }), 500

def perform_advanced_search(query, categories, filters):
    """Realizar búsqueda avanzada con filtros específicos"""
    print(f"🔍 Búsqueda avanzada: '{query}' en {categories} con filtros")
    
    results = {}
    
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ No se pudo conectar a la base de datos")
            return results
            
        cursor = conn.cursor(dictionary=True)
        
        # Procesar período predefinido si está especificado
        if filters.get('periodo'):
            fecha_desde, fecha_hasta = get_date_range_from_period(filters['periodo'])
            if fecha_desde:
                filters['fecha_desde'] = fecha_desde
            if fecha_hasta:
                filters['fecha_hasta'] = fecha_hasta
        
        # Buscar en laboratorios con filtros avanzados
        if 'laboratorios' in categories:
            results['laboratorios'] = search_laboratories_advanced(cursor, query, filters)
        
        # Buscar en proyectos con filtros avanzados
        if 'proyectos' in categories:
            results['proyectos'] = search_projects_advanced(cursor, query, filters)
        
        # Buscar en usuarios/investigadores con filtros avanzados
        if 'investigadores' in categories:
            results['investigadores'] = search_users_advanced(cursor, query, filters)
        
        # Buscar en instituciones con filtros avanzados
        if 'instituciones' in categories:
            results['instituciones'] = search_institutions_advanced(cursor, query, filters)
        
        cursor.close()
        conn.close()
        
        # Log de resultados
        total_results = sum(len(results.get(cat, [])) for cat in results)
        print(f"📊 Búsqueda avanzada completada: {total_results} resultados totales")
        for cat in categories:
            if cat in results:
                print(f"   {cat}: {len(results[cat])} elementos")
        
    except Exception as e:
        print(f"❌ Error en búsqueda avanzada: {e}")
        import traceback
        traceback.print_exc()
    
    return results

def search_laboratories_advanced(cursor, query, filters):
    """Buscar laboratorios con filtros avanzados"""
    print("🧪 Buscando laboratorios con filtros avanzados...")
    
    # Construir consulta base
    base_query = """
        SELECT l.id_laboratorio as id, l.nombre_laboratorio as name,
               COALESCE(l.descripcion, 'Sin descripción') as description,
               COALESCE(l.ubicacion, 'Sin ubicación') as location,
               l.capacidad, l.superficie_m2, l.equipamiento, l.disponibilidad,
               l.requiere_capacitacion,
               COALESCE(i.nombre_institucion, 'Sin institución') as institution,
               COALESCE(a.nombre_area, 'Sin área') as area,
               'laboratorios' as type
        FROM laboratorio l
        LEFT JOIN institucion i ON l.id_institucion = i.id_institucion
        LEFT JOIN area a ON l.id_area = a.id_area
        WHERE 1=1
    """
    
    params = []
    conditions = []
    
    # Filtro de texto general
    if query:
        conditions.append("(l.nombre_laboratorio LIKE %s OR COALESCE(l.descripcion, '') LIKE %s OR COALESCE(l.equipamiento, '') LIKE %s)")
        params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])
    
    # Filtros de ubicación
    if filters.get('estado'):
        conditions.append("COALESCE(i.estado, '') LIKE %s")
        params.append(f"%{filters['estado']}%")
    
    if filters.get('municipio'):
        conditions.append("COALESCE(i.municipio, '') LIKE %s")
        params.append(f"%{filters['municipio']}%")
    
    if filters.get('ubicacion'):
        conditions.append("COALESCE(l.ubicacion, '') LIKE %s")
        params.append(f"%{filters['ubicacion']}%")
    
    # Filtros de área e institución
    if filters.get('area'):
        conditions.append("l.id_area = %s")
        params.append(filters['area'])
    
    if filters.get('institucion'):
        conditions.append("l.id_institucion = %s")
        params.append(filters['institucion'])
    
    # Filtros específicos de laboratorio
    if filters.get('capacidad_min'):
        try:
            conditions.append("l.capacidad >= %s")
            params.append(int(filters['capacidad_min']))
        except ValueError:
            pass
    
    if filters.get('capacidad_max'):
        try:
            conditions.append("l.capacidad <= %s")
            params.append(int(filters['capacidad_max']))
        except ValueError:
            pass
    
    if filters.get('superficie_min'):
        try:
            conditions.append("l.superficie_m2 >= %s")
            params.append(float(filters['superficie_min']))
        except ValueError:
            pass
    
    if filters.get('equipamiento'):
        conditions.append("COALESCE(l.equipamiento, '') LIKE %s")
        params.append(f"%{filters['equipamiento']}%")
    
    if filters.get('disponibilidad'):
        conditions.append("l.disponibilidad = %s")
        params.append(filters['disponibilidad'])
    
    if filters.get('requiere_capacitacion'):
        conditions.append("l.requiere_capacitacion = %s")
        params.append(1 if filters['requiere_capacitacion'] else 0)
    
    # Filtros de fecha
    if filters.get('fecha_desde'):
        conditions.append("l.fecha_creacion >= %s")
        params.append(filters['fecha_desde'])
    
    if filters.get('fecha_hasta'):
        conditions.append("l.fecha_creacion <= %s")
        params.append(filters['fecha_hasta'])
    
    # Construir consulta final
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    base_query += " ORDER BY l.nombre_laboratorio LIMIT 20"
    
    try:
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        print(f"🧪 Laboratorios encontrados: {len(results)}")
        return results
    except Exception as e:
        print(f"❌ Error buscando laboratorios: {e}")
        return []

def search_projects_advanced(cursor, query, filters):
    """Buscar proyectos con filtros avanzados"""
    print("📋 Buscando proyectos con filtros avanzados...")
    
    # Construir consulta base
    base_query = """
        SELECT p.id_proyecto as id, p.nombre_proyecto as name,
               COALESCE(p.resumen, 'Sin descripción') as description,
               COALESCE(p.estatus, 'Sin estado') as estatus,
               COALESCE(p.tipo_proyecto, 'Sin tipo') as tipo,
               p.adjunto, p.fecha, p.fecha_creacion,
               'proyectos' as type
        FROM proyecto p
        WHERE 1=1
    """
    
    params = []
    conditions = []
    
    # Filtro de texto general
    if query:
        conditions.append("(p.nombre_proyecto LIKE %s OR COALESCE(p.resumen, '') LIKE %s)")
        params.extend([f'%{query}%', f'%{query}%'])
    
    # Filtros específicos de proyecto
    if filters.get('tipo_proyecto'):
        conditions.append("p.tipo_proyecto = %s")
        params.append(filters['tipo_proyecto'])
    
    if filters.get('estatus_proyecto'):
        conditions.append("p.estatus = %s")
        params.append(filters['estatus_proyecto'])
    
    if filters.get('con_adjuntos'):
        conditions.append("p.adjunto = %s")
        params.append(1 if filters['con_adjuntos'] else 0)
    
    # Filtros de fecha
    if filters.get('fecha_desde'):
        conditions.append("p.fecha_creacion >= %s")
        params.append(filters['fecha_desde'])
    
    if filters.get('fecha_hasta'):
        conditions.append("p.fecha_creacion <= %s")
        params.append(filters['fecha_hasta'])
    
    # Construir consulta final
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    base_query += " ORDER BY p.fecha_creacion DESC LIMIT 20"
    
    try:
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        print(f"📋 Proyectos encontrados: {len(results)}")
        return results
    except Exception as e:
        print(f"❌ Error buscando proyectos: {e}")
        return []

def search_users_advanced(cursor, query, filters):
    """Buscar usuarios/investigadores con filtros avanzados"""
    print("👥 Buscando investigadores con filtros avanzados...")
    
    # Construir consulta base
    base_query = """
        SELECT u.id_usuario as id, 
               CONCAT(u.nombre, ' ', u.apellido_paterno, ' ', COALESCE(u.apellido_materno, '')) as name,
               COALESCE(u.email, 'Sin email') as description,
               COALESCE(i.nombre_institucion, 'Sin institución') as institution,
               COALESCE(a.nombre_area, 'Sin área') as specialty,
               u.activo, u.fecha_creacion,
               'investigadores' as type
        FROM usuario u
        LEFT JOIN institucion i ON u.id_institucion = i.id_institucion
        LEFT JOIN area a ON u.id_area = a.id_area
        WHERE u.activo = 1
    """
    
    params = []
    conditions = []
    
    # Filtro de texto general
    if query:
        conditions.append("(u.nombre LIKE %s OR u.apellido_paterno LIKE %s OR u.apellido_materno LIKE %s OR u.email LIKE %s)")
        params.extend([f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'])
    
    # Filtros de ubicación
    if filters.get('estado'):
        conditions.append("COALESCE(i.estado, '') LIKE %s")
        params.append(f"%{filters['estado']}%")
    
    if filters.get('municipio'):
        conditions.append("COALESCE(i.municipio, '') LIKE %s")
        params.append(f"%{filters['municipio']}%")
    
    # Filtros de área e institución
    if filters.get('area'):
        conditions.append("u.id_area = %s")
        params.append(filters['area'])
    
    if filters.get('institucion'):
        conditions.append("u.id_institucion = %s")
        params.append(filters['institucion'])
    
    # Filtros de fecha
    if filters.get('fecha_desde'):
        conditions.append("u.fecha_creacion >= %s")
        params.append(filters['fecha_desde'])
    
    if filters.get('fecha_hasta'):
        conditions.append("u.fecha_creacion <= %s")
        params.append(filters['fecha_hasta'])
    
    # Construir consulta final
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    base_query += " ORDER BY u.fecha_creacion DESC LIMIT 20"
    
    try:
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        print(f"👥 Investigadores encontrados: {len(results)}")
        return results
    except Exception as e:
        print(f"❌ Error buscando investigadores: {e}")
        return []

def search_institutions_advanced(cursor, query, filters):
    """Buscar instituciones con filtros avanzados"""
    print("🏛️ Buscando instituciones con filtros avanzados...")
    
    # Construir consulta base
    base_query = """
        SELECT i.id_institucion as id, i.nombre_institucion as name,
               CONCAT(COALESCE(i.calle, ''), ' ', COALESCE(i.colonia, ''), ' ', COALESCE(i.municipio, ''), ' ', COALESCE(i.estado, '')) as description,
               COALESCE(i.estado, 'Sin estado') as location,
               COALESCE(i.municipio, 'Sin municipio') as municipality,
               i.telefono, i.email, i.fecha_registro,
               'instituciones' as type
        FROM institucion i
        WHERE i.activo = 1
    """
    
    params = []
    conditions = []
    
    # Filtro de texto general
    if query:
        conditions.append("(i.nombre_institucion LIKE %s OR i.calle LIKE %s OR i.colonia LIKE %s)")
        params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])
    
    # Filtros de ubicación
    if filters.get('estado'):
        conditions.append("i.estado LIKE %s")
        params.append(f"%{filters['estado']}%")
    
    if filters.get('municipio'):
        conditions.append("i.municipio LIKE %s")
        params.append(f"%{filters['municipio']}%")
    
    # Filtros de fecha
    if filters.get('fecha_desde'):
        conditions.append("i.fecha_registro >= %s")
        params.append(filters['fecha_desde'])
    
    if filters.get('fecha_hasta'):
        conditions.append("i.fecha_registro <= %s")
        params.append(filters['fecha_hasta'])
    
    # Construir consulta final
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    base_query += " ORDER BY i.nombre_institucion LIMIT 20"
    
    try:
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        print(f"🏛️ Instituciones encontradas: {len(results)}")
        return results
    except Exception as e:
        print(f"❌ Error buscando instituciones: {e}")
        return []

def get_filter_options():
    """Obtener opciones para poblar los filtros (estados, municipios, áreas, etc.)"""
    print("📋 Obteniendo opciones para filtros...")
    
    filter_data = {
        'estados': [],
        'municipios': [],
        'areas': [],
        'instituciones': []
    }
    
    try:
        conn = get_db_connection()
        if not conn:
            return filter_data
            
        cursor = conn.cursor(dictionary=True)
        
        # Obtener estados únicos
        cursor.execute("""
            SELECT DISTINCT estado 
            FROM institucion 
            WHERE estado IS NOT NULL AND estado != '' 
            ORDER BY estado
        """)
        filter_data['estados'] = [row['estado'] for row in cursor.fetchall()]
        
        # Obtener municipios únicos
        cursor.execute("""
            SELECT DISTINCT municipio, estado
            FROM institucion 
            WHERE municipio IS NOT NULL AND municipio != '' 
            ORDER BY estado, municipio
        """)
        municipios = cursor.fetchall()
        filter_data['municipios'] = municipios
        
        # Obtener áreas
        cursor.execute("""
            SELECT id_area, nombre_area 
            FROM area 
            ORDER BY nombre_area
        """)
        filter_data['areas'] = cursor.fetchall()
        
        # Obtener instituciones
        cursor.execute("""
            SELECT id_institucion, nombre_institucion, estado, municipio
            FROM institucion 
            WHERE activo = 1
            ORDER BY nombre_institucion
        """)
        filter_data['instituciones'] = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        print(f"📋 Opciones obtenidas: {len(filter_data['estados'])} estados, {len(filter_data['areas'])} áreas, {len(filter_data['instituciones'])} instituciones")
        
    except Exception as e:
        print(f"❌ Error obteniendo opciones de filtros: {e}")
    
    return filter_data

def get_date_range_from_period(period):
    """Convertir período predefinido a rango de fechas"""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    fecha_desde = None
    fecha_hasta = now.strftime('%Y-%m-%d')
    
    if period == 'ultima_semana':
        fecha_desde = (now - timedelta(days=7)).strftime('%Y-%m-%d')
    elif period == 'ultimo_mes':
        fecha_desde = (now - timedelta(days=30)).strftime('%Y-%m-%d')
    elif period == 'ultimos_3_meses':
        fecha_desde = (now - timedelta(days=90)).strftime('%Y-%m-%d')
    elif period == 'ultimo_ano':
        fecha_desde = (now - timedelta(days=365)).strftime('%Y-%m-%d')
    
    return fecha_desde, fecha_hasta

