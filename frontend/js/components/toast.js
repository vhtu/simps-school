/**
 * SIMPS - Toast Notification Component
 * Hiển thị thông báo nhỏ ở góc màn hình.
 */

class Toast {
  static init() {
    if (!document.getElementById('toast-container')) {
      const container = document.createElement('div');
      container.id = 'toast-container';
      container.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 10px;
        max-width: 360px;
      `;
      document.body.appendChild(container);
    }
  }

  static show(message, type = 'info', duration = 3500) {
    this.init();
    const container = document.getElementById('toast-container');

    const toast = document.createElement('div');
    const colors = {
      success: { bg: '#10b981', icon: '✅' },
      error: { bg: '#ef4444', icon: '❌' },
      warning: { bg: '#f59e0b', icon: '⚠️' },
      info: { bg: '#3b82f6', icon: 'ℹ️' },
    };
    const c = colors[type] || colors.info;

    toast.style.cssText = `
      background: white;
      color: #1e293b;
      padding: 12px 18px;
      border-radius: 8px;
      box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1);
      border-left: 5px solid ${c.bg};
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 0.95rem;
      animation: slideIn 0.3s ease-out forwards;
      transition: all 0.3s ease;
    `;

    toast.innerHTML = `
      <span style="font-size: 1.2rem;">${c.icon}</span>
      <div style="flex: 1;">${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  static success(msg) { this.show(msg, 'success'); }
  static error(msg) { this.show(msg, 'error'); }
  static warning(msg) { this.show(msg, 'warning'); }
  static info(msg) { this.show(msg, 'info'); }
}

window.Toast = Toast;
