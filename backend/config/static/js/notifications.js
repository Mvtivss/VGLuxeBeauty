// Sistema de Notificaciones Toast
class NotificationManager {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Crear contenedor de notificaciones si no existe
        if (!document.getElementById('notification-container')) {
            this.container = document.createElement('div');
            this.container.id = 'notification-container';
            this.container.className = 'notification-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('notification-container');
        }
    }

    show(message, type = 'info', duration = 4000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type} notification-enter`;
        
        // Iconos según tipo
        const icons = {
            success: '<i class="bi bi-check-circle-fill"></i>',
            error: '<i class="bi bi-x-circle-fill"></i>',
            warning: '<i class="bi bi-exclamation-triangle-fill"></i>',
            info: '<i class="bi bi-info-circle-fill"></i>'
        };

        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">
                    ${icons[type] || icons.info}
                </div>
                <div class="notification-message">${message}</div>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="bi bi-x"></i>
                </button>
            </div>
        `;

        this.container.appendChild(notification);

        // Animación de entrada
        setTimeout(() => {
            notification.classList.remove('notification-enter');
        }, 10);

        // Auto-cerrar
        if (duration > 0) {
            setTimeout(() => {
                this.close(notification);
            }, duration);
        }

        return notification;
    }

    close(notification) {
        notification.classList.add('notification-exit');
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Instancia global
const notify = new NotificationManager();

// Funciones de conveniencia globales
window.showNotification = (message, type, duration) => notify.show(message, type, duration);
window.showSuccess = (message, duration) => notify.success(message, duration);
window.showError = (message, duration) => notify.error(message, duration);
window.showWarning = (message, duration) => notify.warning(message, duration);
window.showInfo = (message, duration) => notify.info(message, duration);
