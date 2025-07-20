// ========================================================================== //
// ============= JAVASCRIPT MEJORAS PARA PANEL DE ADMINISTRACIÓN =========== //
// ========================================================================== //

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar todas las mejoras
    initPreloader();
    initCardAnimations();
    initParticleEffects();
    initButtonEffects();
    initTooltips();
    initScrollAnimations();
});

// Preloader animado
function initPreloader() {
    const preloader = document.createElement('div');
    preloader.className = 'admin-preloader';
    preloader.innerHTML = '<div class="admin-preloader-spinner"></div>';
    document.body.appendChild(preloader);
    
    // Remover preloader después de 2 segundos
    setTimeout(() => {
        preloader.remove();
    }, 2000);
}

// Animaciones de tarjetas mejoradas
function initCardAnimations() {
    const cards = document.querySelectorAll('.admin-card');
    
    cards.forEach((card, index) => {
        // Animación de entrada escalonada
        card.style.animationDelay = `${index * 0.1}s`;
        
        // Efectos de hover mejorados
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-15px) scale(1.02)';
            this.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.2)';
            
            // Animar ícono
            const icon = this.querySelector('.admin-card-header i');
            if (icon) {
                icon.style.transform = 'scale(1.2) rotate(10deg)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.1)';
            
            // Restaurar ícono
            const icon = this.querySelector('.admin-card-header i');
            if (icon) {
                icon.style.transform = 'scale(1) rotate(0deg)';
            }
        });
        
        // Efecto de clic
        card.addEventListener('click', function(e) {
            if (!e.target.closest('.admin-button')) {
                createRippleEffect(this, e);
            }
        });
    });
}

// Crear efecto ripple
function createRippleEffect(element, event) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
        position: absolute;
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s linear;
        background-color: rgba(255, 255, 255, 0.3);
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        pointer-events: none;
    `;
    
    element.style.position = 'relative';
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Efectos de partículas
function initParticleEffects() {
    const particleContainer = document.createElement('div');
    particleContainer.className = 'particle-container';
    particleContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
        overflow: hidden;
    `;
    
    document.body.appendChild(particleContainer);
    
    // Crear partículas
    for (let i = 0; i < 50; i++) {
        createParticle(particleContainer);
    }
}

function createParticle(container) {
    const particle = document.createElement('div');
    const size = Math.random() * 4 + 2;
    const duration = Math.random() * 10 + 5;
    const delay = Math.random() * 5;
    
    particle.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.3) 0%, transparent 70%);
        border-radius: 50%;
        left: ${Math.random() * 100}%;
        top: 100%;
        animation: particleFloat ${duration}s linear ${delay}s infinite;
    `;
    
    container.appendChild(particle);
    
    // Remover y recrear partícula después de la animación
    setTimeout(() => {
        particle.remove();
        createParticle(container);
    }, (duration + delay) * 1000);
}

// Efectos de botones mejorados
function initButtonEffects() {
    const buttons = document.querySelectorAll('.admin-button');
    
    buttons.forEach(button => {
        // Efecto de pulso en hover
        button.addEventListener('mouseenter', function() {
            this.style.animation = 'pulse 0.5s ease-in-out';
        });
        
        // Efecto de loading al hacer clic
        button.addEventListener('click', function(e) {
            if (!this.classList.contains('loading')) {
                this.classList.add('loading');
                
                // Simular carga por 2 segundos
                setTimeout(() => {
                    this.classList.remove('loading');
                }, 2000);
            }
        });
    });
}

// Tooltips mejorados
function initTooltips() {
    const cards = document.querySelectorAll('.admin-card');
    
    cards.forEach(card => {
        const title = card.querySelector('h2').textContent;
        const description = card.querySelector('p').textContent;
        
        card.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'admin-tooltip';
            tooltip.innerHTML = `
                <div class="tooltip-title">${title}</div>
                <div class="tooltip-description">${description}</div>
            `;
            
            tooltip.style.cssText = `
                position: fixed;
                background: rgba(0, 0, 0, 0.9);
                color: white;
                padding: 1rem;
                border-radius: 8px;
                font-size: 0.9rem;
                max-width: 300px;
                z-index: 1000;
                transform: translateY(-10px);
                opacity: 0;
                transition: all 0.3s ease;
                pointer-events: none;
            `;
            
            document.body.appendChild(tooltip);
            
            // Posicionar tooltip
            const rect = this.getBoundingClientRect();
            tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 10}px`;
            
            // Mostrar tooltip
            setTimeout(() => {
                tooltip.style.opacity = '1';
                tooltip.style.transform = 'translateY(0)';
            }, 100);
            
            // Remover tooltip al salir
            this.addEventListener('mouseleave', function() {
                tooltip.remove();
            });
        });
    });
}

// Animaciones al hacer scroll
function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.8s ease forwards';
            }
        });
    }, {
        threshold: 0.1
    });
    
    document.querySelectorAll('.admin-card').forEach(card => {
        observer.observe(card);
    });
}



// Función mejorada para "Próximamente"
function showComingSoon() {
    const toast = document.createElement('div');
    toast.className = 'toast enhanced';
    toast.innerHTML = `
        <div class="toast-content">
            <div class="toast-icon">🚀</div>
            <div class="toast-text">
                <div class="toast-title">¡Próximamente!</div>
                <div class="toast-subtitle">Esta funcionalidad estará disponible pronto</div>
            </div>
        </div>
    `;
    
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: var(--primary-gradient);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        border: 2px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        animation: toastSlideIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    `;
    
    document.body.appendChild(toast);
    
    // Agregar estilos para el contenido
    const style = document.createElement('style');
    style.textContent = `
        .toast-content {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .toast-icon {
            font-size: 1.5rem;
            animation: bounce 1s infinite;
        }
        .toast-title {
            font-weight: 600;
            margin-bottom: 0.25rem;
        }
        .toast-subtitle {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
    `;
    document.head.appendChild(style);
    
    // Remover toast después de 4 segundos
    setTimeout(() => {
        toast.style.animation = 'toastSlideOut 0.5s ease-in-out forwards';
        setTimeout(() => {
            toast.remove();
            style.remove();
        }, 500);
    }, 4000);
}

// Agregar animaciones CSS dinámicamente
const dynamicStyles = document.createElement('style');
dynamicStyles.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    @keyframes particleFloat {
        0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
        }
        100% {
            transform: translateY(-100vh) rotate(360deg);
            opacity: 0;
        }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes toastSlideOut {
        to {
            transform: translateX(100%) rotate(-10deg);
            opacity: 0;
        }
    }
    

`;

document.head.appendChild(dynamicStyles);

// Función para agregar efectos sonoros (opcional)
function playSound(type) {
    const audio = new Audio();
    switch(type) {
        case 'click':
            audio.src = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvGETBDaGy/fTiCs...';
            break;
        case 'hover':
            audio.src = 'data:audio/wav;base64,UklGRkoAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YSYAAAAkAAEAJAAEAFAABQBjAAcAaAAJAGAABgBbAAQAUAABAEAA...';
            break;
    }
    audio.volume = 0.1;
    audio.play().catch(() => {}); // Ignorar errores de autoplay
}

// Exportar funciones para uso global
window.showComingSoon = showComingSoon;
window.playSound = playSound; 