// Utilidades UX/UI para mejorar la experiencia del usuario

// ===========================
// LOADING STATES
// ===========================

class LoadingManager {
    constructor() {
        this.activeLoaders = new Set();
    }

    // Mostrar loading en un botón
    showButtonLoading(button, text = 'Cargando...') {
        if (!button) return null;
        
        button.disabled = true;
        const originalContent = button.innerHTML;
        button.setAttribute('data-original-content', originalContent);
        button.innerHTML = `
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            <span class="ms-2">${text}</span>
        `;
        
        return originalContent;
    }

    // Restaurar botón
    hideButtonLoading(button, content = null) {
        if (!button) return;
        
        const originalContent = content || button.getAttribute('data-original-content');
        button.disabled = false;
        button.innerHTML = originalContent;
        button.removeAttribute('data-original-content');
    }

    // Overlay de carga para toda la pantalla
    showPageLoading(message = 'Cargando...') {
        const overlay = document.createElement('div');
        overlay.id = 'page-loading-overlay';
        overlay.className = 'page-loading-overlay';
        overlay.innerHTML = `
            <div class="page-loading-content">
                <div class="spinner-large"></div>
                <p>${message}</p>
            </div>
        `;
        document.body.appendChild(overlay);
        this.activeLoaders.add('page');
        return overlay;
    }

    hidePageLoading() {
        const overlay = document.getElementById('page-loading-overlay');
        if (overlay) {
            overlay.classList.add('fade-out');
            setTimeout(() => overlay.remove(), 300);
            this.activeLoaders.delete('page');
        }
    }

    // Loading para secciones específicas
    showSectionLoading(element, message = '') {
        if (!element) return;
        
        const loader = document.createElement('div');
        loader.className = 'section-loading-overlay';
        loader.innerHTML = `
            <div class="section-loading-content">
                <div class="spinner-medium"></div>
                ${message ? `<p>${message}</p>` : ''}
            </div>
        `;
        
        element.style.position = 'relative';
        element.appendChild(loader);
    }

    hideSectionLoading(element) {
        if (!element) return;
        
        const loader = element.querySelector('.section-loading-overlay');
        if (loader) {
            loader.remove();
        }
    }
}

// ===========================
// VALIDACIÓN DE FORMULARIOS
// ===========================

class FormValidator {
    constructor(form) {
        this.form = form;
        this.init();
    }

    init() {
        const inputs = this.form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearError(input));
        });

        this.form.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
                showWarning('Por favor, corrige los errores en el formulario');
            }
        });
    }

    validateField(field) {
        this.clearError(field);

        // Campo requerido
        if (field.hasAttribute('required') && !field.value.trim()) {
            this.showError(field, 'Este campo es requerido');
            return false;
        }

        // Email
        if (field.type === 'email' && field.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(field.value)) {
                this.showError(field, 'Email inválido');
                return false;
            }
        }

        // Teléfono
        if (field.type === 'tel' && field.value) {
            const phoneRegex = /^[+]?[\d\s\-()]{8,}$/;
            if (!phoneRegex.test(field.value)) {
                this.showError(field, 'Teléfono inválido');
                return false;
            }
        }

        // Longitud mínima
        if (field.hasAttribute('minlength') && field.value) {
            const minLength = parseInt(field.getAttribute('minlength'));
            if (field.value.length < minLength) {
                this.showError(field, `Mínimo ${minLength} caracteres`);
                return false;
            }
        }

        // Longitud máxima
        if (field.hasAttribute('maxlength') && field.value) {
            const maxLength = parseInt(field.getAttribute('maxlength'));
            if (field.value.length > maxLength) {
                this.showError(field, `Máximo ${maxLength} caracteres`);
                return false;
            }
        }

        // Contraseñas coinciden
        if (field.hasAttribute('data-match')) {
            const matchField = document.getElementById(field.getAttribute('data-match'));
            if (matchField && field.value !== matchField.value) {
                this.showError(field, 'Las contraseñas no coinciden');
                return false;
            }
        }

        this.showSuccess(field);
        return true;
    }

    validateForm() {
        let isValid = true;
        const inputs = this.form.querySelectorAll('input[required], textarea[required], select[required]');
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    showError(field, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        
        let errorDiv = field.parentElement.querySelector('.invalid-feedback');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            field.parentElement.appendChild(errorDiv);
        }
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }

    showSuccess(field) {
        if (field.value.trim()) {
            field.classList.add('is-valid');
            field.classList.remove('is-invalid');
        }
    }

    clearError(field) {
        field.classList.remove('is-invalid', 'is-valid');
        const errorDiv = field.parentElement.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }
}

// ===========================
// UTILIDADES GENERALES
// ===========================

// Debounce para búsquedas
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Smooth scroll mejorado
function smoothScrollTo(element, offset = 0) {
    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;

    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
}

// Copiar al portapapeles con feedback
async function copyToClipboard(text, successMessage = 'Copiado al portapapeles') {
    try {
        await navigator.clipboard.writeText(text);
        showSuccess(successMessage);
        return true;
    } catch (err) {
        showError('Error al copiar');
        return false;
    }
}

// Confirmar acción
function confirmAction(message, onConfirm, onCancel = null) {
    const modal = document.createElement('div');
    modal.className = 'confirm-modal-overlay';
    modal.innerHTML = `
        <div class="confirm-modal">
            <div class="confirm-modal-icon">
                <i class="bi bi-question-circle"></i>
            </div>
            <h3>Confirmar Acción</h3>
            <p>${message}</p>
            <div class="confirm-modal-buttons">
                <button class="btn-cancel">Cancelar</button>
                <button class="btn-confirm">Confirmar</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    modal.querySelector('.btn-confirm').addEventListener('click', () => {
        modal.remove();
        if (onConfirm) onConfirm();
    });
    
    modal.querySelector('.btn-cancel').addEventListener('click', () => {
        modal.remove();
        if (onCancel) onCancel();
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
            if (onCancel) onCancel();
        }
    });
}

// Instancias globales
const loading = new LoadingManager();
window.loading = loading;

// Auto-inicializar validadores
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('form[data-validate]').forEach(form => {
        new FormValidator(form);
    });
});
