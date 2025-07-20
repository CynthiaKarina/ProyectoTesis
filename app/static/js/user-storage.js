/**
 * Manejo de datos del usuario en localStorage
 * Este archivo proporciona funciones para guardar, obtener y gestionar
 * los datos del usuario en localStorage de forma consistente
 */

// Namespace para las funciones de almacenamiento del usuario
window.UserStorage = {
    
    // Claves utilizadas en localStorage
    KEYS: {
        USER_DATA: 'user_data',
        USER_LOGGED_IN: 'user_logged_in',
        LOGIN_TIMESTAMP: 'login_timestamp',
        USER_ID: 'user_id',
        USERNAME: 'username',
        USER_NAME: 'user_name',
        USER_ROLE: 'user_role',
        USER_EMAIL: 'user_email'
    },

    /**
     * Guarda los datos del usuario en localStorage
     * @param {Object} userData - Datos del usuario a guardar
     */
    save: function(userData) {
        try {
            // Validar datos mínimos requeridos
            if (!userData || !userData.id_usuario || !userData.username) {
                console.error('❌ UserStorage.save: Datos de usuario incompletos');
                return false;
            }

            // Datos principales del usuario
            const userInfo = {
                id_usuario: userData.id_usuario,
                username: userData.username,
                email: userData.email || '',
                nombre: userData.nombre || '',
                apellido_paterno: userData.apellido_paterno || '',
                apellido_materno: userData.apellido_materno || '',
                nombre_completo: userData.nombre_completo || '',
                telefono: userData.telefono || '',
                ruta_imagen: userData.ruta_imagen || '',
                id_rol: userData.id_rol || null,
                role_name: userData.role_name || '',
                id_institucion: userData.id_institucion || null,
                institucion_nombre: userData.institucion_nombre || '',
                id_area: userData.id_area || null,
                area_nombre: userData.area_nombre || '',
                activo: userData.activo !== undefined ? userData.activo : true,
                fecha_registro: userData.fecha_registro || null,
                iniciales: userData.iniciales || '',
                ultimo_acceso: new Date().toISOString(),
                session_timestamp: new Date().toISOString()
            };

            // Guardar en localStorage
            localStorage.setItem(this.KEYS.USER_DATA, JSON.stringify(userInfo));
            localStorage.setItem(this.KEYS.USER_LOGGED_IN, 'true');
            localStorage.setItem(this.KEYS.LOGIN_TIMESTAMP, new Date().toISOString());

            // Guardar también datos específicos para acceso rápido
            localStorage.setItem(this.KEYS.USER_ID, userInfo.id_usuario);
            localStorage.setItem(this.KEYS.USERNAME, userInfo.username);
            localStorage.setItem(this.KEYS.USER_NAME, userInfo.nombre_completo);
            localStorage.setItem(this.KEYS.USER_ROLE, userInfo.role_name);
            localStorage.setItem(this.KEYS.USER_EMAIL, userInfo.email);

            console.log('✅ UserStorage.save: Datos guardados exitosamente:', userInfo);
            
            // Disparar evento personalizado
            this._dispatchEvent('userDataSaved', userInfo);
            
            return true;
            
        } catch (error) {
            console.error('❌ UserStorage.save: Error al guardar datos:', error);
            return false;
        }
    },

    /**
     * Obtiene los datos del usuario desde localStorage
     * @returns {Object|null} - Datos del usuario o null si no existen
     */
    get: function() {
        try {
            const userData = localStorage.getItem(this.KEYS.USER_DATA);
            if (userData) {
                return JSON.parse(userData);
            }
            return null;
        } catch (error) {
            console.error('❌ UserStorage.get: Error al obtener datos:', error);
            return null;
        }
    },

    /**
     * Obtiene un dato específico del usuario
     * @param {string} key - Clave del dato a obtener
     * @returns {any} - Valor del dato o null si no existe
     */
    getValue: function(key) {
        const userData = this.get();
        return userData ? userData[key] : null;
    },

    /**
     * Actualiza un dato específico del usuario
     * @param {string} key - Clave del dato a actualizar
     * @param {any} value - Nuevo valor
     * @returns {boolean} - true si se actualizó exitosamente
     */
    updateValue: function(key, value) {
        try {
            const userData = this.get();
            if (userData) {
                userData[key] = value;
                userData.ultimo_acceso = new Date().toISOString();
                
                localStorage.setItem(this.KEYS.USER_DATA, JSON.stringify(userData));
                
                // Actualizar también claves específicas si corresponde
                if (key === 'nombre_completo') {
                    localStorage.setItem(this.KEYS.USER_NAME, value);
                } else if (key === 'role_name') {
                    localStorage.setItem(this.KEYS.USER_ROLE, value);
                } else if (key === 'email') {
                    localStorage.setItem(this.KEYS.USER_EMAIL, value);
                }
                
                console.log(`✅ UserStorage.updateValue: ${key} actualizado`);
                this._dispatchEvent('userDataUpdated', { key, value });
                
                return true;
            }
            return false;
        } catch (error) {
            console.error('❌ UserStorage.updateValue: Error al actualizar:', error);
            return false;
        }
    },

    /**
     * Verifica si el usuario está logueado
     * @returns {boolean} - true si está logueado
     */
    isLoggedIn: function() {
        const loggedIn = localStorage.getItem(this.KEYS.USER_LOGGED_IN) === 'true';
        const userData = this.get();
        return loggedIn && userData !== null;
    },

    /**
     * Obtiene información básica del usuario para mostrar en la UI
     * @returns {Object} - Información básica del usuario
     */
    getBasicInfo: function() {
        const userData = this.get();
        if (!userData) return null;

        return {
            id: userData.id_usuario,
            username: userData.username,
            name: userData.nombre_completo,
            email: userData.email,
            role: userData.role_name,
            avatar: userData.ruta_imagen,
            initials: userData.iniciales,
            institution: userData.institucion_nombre,
            area: userData.area_nombre
        };
    },

    /**
     * Limpia todos los datos del usuario del localStorage
     */
    clear: function() {
        try {
            console.log('🧹 UserStorage.clear: Limpiando datos del usuario...');
            
            // Obtener datos antes de limpiar para el evento
            const userData = this.get();
            
            // Limpiar todas las claves relacionadas con el usuario
            Object.values(this.KEYS).forEach(key => {
                if (localStorage.getItem(key)) {
                    localStorage.removeItem(key);
                    console.log(`🗑️ UserStorage.clear: Eliminado ${key}`);
                }
            });
            
            // Disparar evento de limpieza
            this._dispatchEvent('userDataCleared', userData);
            
            console.log('✅ UserStorage.clear: Datos eliminados exitosamente');
            return true;
            
        } catch (error) {
            console.error('❌ UserStorage.clear: Error al limpiar datos:', error);
            return false;
        }
    },

    /**
     * Limpia también sessionStorage y cookies
     */
    clearAll: function() {
        try {
            // Limpiar localStorage
            this.clear();
            
            // Limpiar sessionStorage
            this._clearSessionStorage();
            
            // Limpiar cookies de sesión
            this._clearSessionCookies();
            
            console.log('✅ UserStorage.clearAll: Todos los datos eliminados');
            return true;
            
        } catch (error) {
            console.error('❌ UserStorage.clearAll: Error al limpiar:', error);
            return false;
        }
    },

    /**
     * Obtiene el tiempo transcurrido desde el login
     * @returns {number} - Minutos transcurridos desde el login
     */
    getSessionDuration: function() {
        try {
            const loginTime = localStorage.getItem(this.KEYS.LOGIN_TIMESTAMP);
            if (loginTime) {
                const now = new Date();
                const login = new Date(loginTime);
                return Math.floor((now - login) / (1000 * 60)); // Minutos
            }
            return 0;
        } catch (error) {
            console.error('❌ UserStorage.getSessionDuration: Error:', error);
            return 0;
        }
    },

    /**
     * Verifica si la sesión ha expirado
     * @param {number} maxMinutes - Máximo de minutos permitidos (default: 480 = 8 horas)
     * @returns {boolean} - true si ha expirado
     */
    isSessionExpired: function(maxMinutes = 480) {
        const duration = this.getSessionDuration();
        return duration > maxMinutes;
    },

    /**
     * Actualiza el timestamp de último acceso
     */
    updateLastAccess: function() {
        const userData = this.get();
        if (userData) {
            userData.ultimo_acceso = new Date().toISOString();
            localStorage.setItem(this.KEYS.USER_DATA, JSON.stringify(userData));
        }
    },

    /**
     * Obtiene estadísticas de uso del localStorage
     * @returns {Object} - Estadísticas de uso
     */
    getStorageStats: function() {
        try {
            const stats = {
                isLoggedIn: this.isLoggedIn(),
                sessionDuration: this.getSessionDuration(),
                lastAccess: this.getValue('ultimo_acceso'),
                loginTime: localStorage.getItem(this.KEYS.LOGIN_TIMESTAMP),
                dataSize: 0,
                keysCount: 0
            };
            
            // Calcular tamaño de datos
            Object.values(this.KEYS).forEach(key => {
                const value = localStorage.getItem(key);
                if (value) {
                    stats.dataSize += value.length;
                    stats.keysCount++;
                }
            });
            
            return stats;
        } catch (error) {
            console.error('❌ UserStorage.getStorageStats: Error:', error);
            return null;
        }
    },

    // Métodos privados
    _clearSessionStorage: function() {
        try {
            Object.values(this.KEYS).forEach(key => {
                if (sessionStorage.getItem(key)) {
                    sessionStorage.removeItem(key);
                    console.log(`🗑️ SessionStorage eliminado: ${key}`);
                }
            });
        } catch (error) {
            console.error('❌ Error al limpiar sessionStorage:', error);
        }
    },

    _clearSessionCookies: function() {
        try {
            const cookiesToClear = [
                'remembered_user', 'session_token', 'user_token',
                'auth_token', 'remember_token'
            ];
            
            cookiesToClear.forEach(cookieName => {
                document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
                console.log(`🗑️ Cookie eliminada: ${cookieName}`);
            });
        } catch (error) {
            console.error('❌ Error al limpiar cookies:', error);
        }
    },

    _dispatchEvent: function(eventName, data) {
        try {
            const event = new CustomEvent(eventName, {
                detail: data
            });
            window.dispatchEvent(event);
        } catch (error) {
            console.error(`❌ Error al disparar evento ${eventName}:`, error);
        }
    }
};

// Alias para compatibilidad con versiones anteriores
window.userStorage = window.UserStorage;

// Inicialización automática
document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 UserStorage inicializado');
    
    // Actualizar último acceso si el usuario está logueado
    if (window.UserStorage.isLoggedIn()) {
        window.UserStorage.updateLastAccess();
        console.log('🔄 Último acceso actualizado');
    }
});

// Eventos para detectar cambios en localStorage desde otras pestañas
window.addEventListener('storage', function(e) {
    if (Object.values(window.UserStorage.KEYS).includes(e.key)) {
        console.log('🔄 Datos de usuario actualizados desde otra pestaña');
        window.UserStorage._dispatchEvent('userDataChangedFromOtherTab', {
            key: e.key,
            oldValue: e.oldValue,
            newValue: e.newValue
        });
    }
});

// Manejo de visibilidad de la página para actualizar último acceso
document.addEventListener('visibilitychange', function() {
    if (!document.hidden && window.UserStorage.isLoggedIn()) {
        window.UserStorage.updateLastAccess();
    }
});

console.log('✅ UserStorage cargado correctamente'); 