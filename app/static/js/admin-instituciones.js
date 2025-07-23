// ===================== ADMINISTRACIÓN DE INSTITUCIONES =====================
// Variables globales
let editandoInstitucion = false;
let institucionIdActual = null;
let allInstitutions = [];
let filteredInstitutions = [];

// Función para alternar el menú FAB
function toggleFabMenu() {
    const fabOptions = document.querySelector('.fab-options');
    const fabMain = document.querySelector('.fab-main');
    
    if (fabOptions.classList.contains('open')) {
        fabOptions.classList.remove('open');
        fabMain.classList.remove('open');
    } else {
        fabOptions.classList.add('open');
        fabMain.classList.add('open');
    }
}

// Funciones del Modal
function openModal() {
    document.getElementById('modalOverlay').classList.add('show');
    clearForm();
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    document.getElementById('modalOverlay').classList.remove('show');
    document.body.style.overflow = 'auto';
    clearForm();
}

function clearForm() {
    document.getElementById('institucion-form').reset();
    document.getElementById('institucion-id').value = '';
    document.getElementById('modalTitle').innerHTML = '<i class="fas fa-plus"></i> Nueva Institución';
    document.getElementById('submitBtn').innerHTML = '<i class="fas fa-save"></i> Crear Institución';
    document.getElementById('activo').checked = true;
    editandoInstitucion = false;
    institucionIdActual = null;
    
    // Cerrar FAB menu
    const fabOptions = document.querySelector('.fab-options');
    const fabMain = document.querySelector('.fab-main');
    if (fabOptions && fabMain) {
        fabOptions.classList.remove('open');
        fabMain.classList.remove('open');
    }
}

// Función para editar institución
async function editarInstitucion(id) {
    let btn = null;
    let originalHTML = '';
    
    try {
        // Mostrar loading en el botón
        btn = event.target.closest('.btn-edit');
        originalHTML = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cargando...';
        btn.disabled = true;
        
        const response = await fetch(`/admin/instituciones/${id}`);
        const data = await response.json();
        
        if (response.ok) {
            // Abrir modal
            openModal();
            
            // Llenar el formulario con los datos
            document.getElementById('institucion-id').value = data.id_institucion;
            document.getElementById('nombre_institucion').value = data.nombre_institucion || '';
            document.getElementById('id_tipo_institucion').value = data.id_tipo_institucion || '';
            document.getElementById('email').value = data.email || '';
            document.getElementById('telefono').value = data.telefono || '';
            document.getElementById('calle').value = data.calle || '';
            document.getElementById('colonia').value = data.colonia || '';
            document.getElementById('municipio').value = data.municipio || '';
            document.getElementById('estado').value = data.estado || '';
            document.getElementById('codigo_postal').value = data.codigo_postal || '';
            document.getElementById('activo').checked = data.activo;
            
            // Cambiar el título y botón
            document.getElementById('modalTitle').innerHTML = '<i class="fas fa-edit"></i> Editar Institución';
            document.getElementById('submitBtn').innerHTML = '<i class="fas fa-save"></i> Actualizar Institución';
            
            editandoInstitucion = true;
            institucionIdActual = id;
        } else {
            throw new Error(data.error || 'Error al cargar la institución');
        }
    } catch (error) {
        console.error('Error al cargar institución:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message || 'No se pudo cargar la información de la institución',
            confirmButtonColor: '#667eea'
        });
    } finally {
        // Restaurar botón
        if (btn) {
            btn.innerHTML = originalHTML;
            btn.disabled = false;
        }
    }
}

// Función para cambiar estado
async function toggleStatus(id) {
    try {
        const result = await Swal.fire({
            title: '¿Cambiar estado?',
            text: "Se cambiará el estado de la institución",
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#667eea',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Sí, cambiar',
            cancelButtonText: 'Cancelar'
        });
        
        if (result.isConfirmed) {
            const response = await fetch(`/admin/instituciones/toggle-status/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                Swal.fire({
                    icon: 'success',
                    title: '¡Éxito!',
                    text: data.mensaje,
                    confirmButtonColor: '#667eea',
                    timer: 2000,
                    showConfirmButton: false
                });
                
                // Actualizar la tabla sin recargar
                setTimeout(() => location.reload(), 1000);
            } else {
                throw new Error(data.error);
            }
        }
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message || 'Error de conexión',
            confirmButtonColor: '#dc3545'
        });
    }
}

// Función para eliminar institución
function eliminarInstitucion(id) {
    Swal.fire({
        title: '¿Estás seguro?',
        text: "Esta acción eliminará la institución permanentemente",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        reverseButtons: true
    }).then(async (result) => {
        if (result.isConfirmed) {
            try {
                // Mostrar loading
                Swal.fire({
                    title: 'Eliminando...',
                    allowOutsideClick: false,
                    didOpen: () => {
                        Swal.showLoading();
                    }
                });
                
                const response = await fetch(`/admin/instituciones/eliminar/${id}`, {
                    method: 'DELETE'
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    Swal.fire({
                        icon: 'success',
                        title: '¡Eliminada!',
                        text: data.mensaje,
                        confirmButtonColor: '#28a745',
                        timer: 2000,
                        showConfirmButton: false
                    });
                    
                    // Animar eliminación de la fila
                    const row = document.querySelector(`tr[data-institucion-id="${id}"]`);
                    if (row) {
                        row.style.transition = 'all 0.5s ease';
                        row.style.transform = 'translateX(-100%)';
                        row.style.opacity = '0';
                        setTimeout(() => location.reload(), 500);
                    } else {
                        setTimeout(() => location.reload(), 1000);
                    }
                } else {
                    throw new Error(data.error);
                }
            } catch (error) {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: error.message || 'No se pudo eliminar la institución',
                    confirmButtonColor: '#dc3545'
                });
            }
        }
    });
}

// Función para exportar instituciones
function exportarInstituciones() {
    Swal.fire({
        title: 'Exportar Instituciones',
        text: '¿En qué formato deseas exportar la lista de instituciones?',
        icon: 'question',
        showCancelButton: true,
        showDenyButton: true,
        confirmButtonText: '<i class="fas fa-file-excel"></i> Excel',
        denyButtonText: '<i class="fas fa-file-csv"></i> CSV',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#28a745',
        denyButtonColor: '#17a2b8',
        cancelButtonColor: '#6c757d'
    }).then((result) => {
        if (result.isConfirmed) {
            exportToExcel();
        } else if (result.isDenied) {
            exportToCSV();
        }
    });
}

// Función para exportar a Excel
async function exportToExcel() {
    try {
        Swal.fire({
            title: 'Generando archivo Excel...',
            html: 'Por favor espera mientras se genera el archivo',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        const response = await fetch('/admin/instituciones/exportar', {
            method: 'GET'
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `instituciones_${new Date().toISOString().slice(0,10)}.xlsx`;
            
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            Swal.fire({
                icon: 'success',
                title: '¡Descarga exitosa!',
                text: 'El archivo Excel se ha descargado correctamente',
                confirmButtonColor: '#28a745',
                timer: 3000,
                showConfirmButton: false
            });
        } else {
            throw new Error('Error en la respuesta del servidor');
        }
    } catch (error) {
        console.error('Error al exportar a Excel:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error al exportar',
            text: 'No se pudo generar el archivo Excel. Intenta de nuevo.',
            confirmButtonColor: '#dc3545'
        });
    }
}

// Función para exportar a CSV
async function exportToCSV() {
    try {
        Swal.fire({
            title: 'Generando archivo CSV...',
            html: 'Por favor espera mientras se genera el archivo',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        const response = await fetch('/admin/instituciones/exportar-csv', {
            method: 'GET'
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `instituciones_${new Date().toISOString().slice(0,10)}.csv`;
            
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            Swal.fire({
                icon: 'success',
                title: '¡Descarga exitosa!',
                text: 'El archivo CSV se ha descargado correctamente',
                confirmButtonColor: '#28a745',
                timer: 3000,
                showConfirmButton: false
            });
        } else {
            throw new Error('Error en la respuesta del servidor');
        }
    } catch (error) {
        console.error('Error al exportar a CSV:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error al exportar',
            text: 'No se pudo generar el archivo CSV. Intenta de nuevo.',
            confirmButtonColor: '#dc3545'
        });
    }
}

// ===================== FUNCIONALIDAD DE BÚSQUEDA =====================
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    const clearBtn = document.getElementById('clearSearchBtn');
    
    allInstitutions = Array.from(document.querySelectorAll('.institution-row'));
    filteredInstitutions = [...allInstitutions];
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        
        if (searchTerm.length === 0) {
            clearSearch();
            return;
        }
        
        clearBtn.style.display = searchTerm.length > 0 ? 'block' : 'none';
        filterInstitutions(searchTerm);
    });
    
    searchInput.addEventListener('keyup', function(e) {
        if (e.key === 'Escape') {
            clearSearch();
        }
    });
}

function filterInstitutions(searchTerm) {
    const resultsInfo = document.getElementById('searchResultsInfo');
    const noResults = document.getElementById('noResults');
    const tableTitle = document.getElementById('tableTitle');
    const totalCount = document.getElementById('totalCount');
    
    filteredInstitutions = allInstitutions.filter(row => {
        const institutionName = row.querySelector('.institution-name').textContent.toLowerCase();
        const institutionEmail = row.querySelector('.institution-email')?.textContent.toLowerCase() || '';
        const institutionLocation = row.querySelector('.institution-location')?.textContent.toLowerCase() || '';
        const institutionType = row.querySelector('.institution-type')?.textContent.toLowerCase() || '';
        
        return institutionName.includes(searchTerm) ||
               institutionEmail.includes(searchTerm) ||
               institutionLocation.includes(searchTerm) ||
               institutionType.includes(searchTerm);
    });
    
    allInstitutions.forEach(row => {
        if (filteredInstitutions.includes(row)) {
            row.classList.remove('hidden');
        } else {
            row.classList.add('hidden');
        }
    });
    
    const totalResults = filteredInstitutions.length;
    const totalInstitutions = allInstitutions.length;
    
    if (totalResults === 0) {
        noResults.style.display = 'block';
        resultsInfo.style.display = 'none';
    } else {
        noResults.style.display = 'none';
        resultsInfo.style.display = 'block';
        resultsInfo.innerHTML = `
            <i class="fas fa-info-circle"></i>
            Mostrando <strong>${totalResults}</strong> de <strong>${totalInstitutions}</strong> instituciones
        `;
    }
    
    tableTitle.textContent = totalResults === totalInstitutions ? 
        'Instituciones Registradas' : 
        'Resultados de Búsqueda';
    totalCount.textContent = totalResults;
}

function clearSearch() {
    const searchInput = document.getElementById('searchInput');
    const clearBtn = document.getElementById('clearSearchBtn');
    const resultsInfo = document.getElementById('searchResultsInfo');
    const noResults = document.getElementById('noResults');
    const tableTitle = document.getElementById('tableTitle');
    const totalCount = document.getElementById('totalCount');
    
    searchInput.value = '';
    clearBtn.style.display = 'none';
    resultsInfo.style.display = 'none';
    noResults.style.display = 'none';
    
    allInstitutions.forEach(row => {
        row.classList.remove('hidden');
    });
    
    tableTitle.textContent = 'Instituciones Registradas';
    totalCount.textContent = allInstitutions.length;
    
    filteredInstitutions = [...allInstitutions];
}

// ===================== INICIALIZACIÓN =====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🏢 Admin Instituciones JS cargado');
    
    // Inicializar búsqueda
    initializeSearch();
    
    // Manejo del formulario
    const form = document.getElementById('institucion-form');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData.entries());
            data.activo = document.getElementById('activo').checked;
            
            try {
                const submitBtn = document.getElementById('submitBtn');
                const originalHTML = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
                submitBtn.disabled = true;
                
                let url, method;
                
                if (editandoInstitucion && institucionIdActual) {
                    url = `/admin/instituciones/editar/${institucionIdActual}`;
                    method = 'PUT';
                } else {
                    url = '/admin/instituciones/agregar';
                    method = 'POST';
                }
                
                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    Swal.fire({
                        icon: 'success',
                        title: '¡Éxito!',
                        text: result.mensaje,
                        confirmButtonColor: '#28a745',
                        timer: 2000,
                        showConfirmButton: false
                    });
                    
                    closeModal();
                    setTimeout(() => location.reload(), 1500);
                } else {
                    throw new Error(result.error);
                }
            } catch (error) {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: error.message || 'Error al procesar la solicitud',
                    confirmButtonColor: '#dc3545'
                });
            } finally {
                const submitBtn = document.getElementById('submitBtn');
                submitBtn.innerHTML = editandoInstitucion ? '<i class="fas fa-save"></i> Actualizar Institución' : '<i class="fas fa-save"></i> Crear Institución';
                submitBtn.disabled = false;
            }
        });
    }

    // Cerrar modal al hacer clic fuera
    const modalOverlay = document.getElementById('modalOverlay');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
    }

    // Cerrar FAB menu al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.fab-menu')) {
            const fabOptions = document.querySelector('.fab-options');
            const fabMain = document.querySelector('.fab-main');
            if (fabOptions && fabMain) {
                fabOptions.classList.remove('open');
                fabMain.classList.remove('open');
            }
        }
    });

    // Cerrar modal con tecla ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });

    // Animaciones de entrada
    const statCards = document.querySelectorAll('.stat-card-enhanced');
    if (statCards.length > 0) {
        statCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 150);
        });
    }

    // Efectos hover en filas de tabla
    const tableRows = document.querySelectorAll('.instituciones-table tbody tr');
    if (tableRows.length > 0) {
        tableRows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                if (!this.classList.contains('hidden')) {
                    this.style.transform = 'translateX(5px)';
                }
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.transform = 'translateX(0)';
            });
        });
    }
}); 