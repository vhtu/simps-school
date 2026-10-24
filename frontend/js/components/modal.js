/**
 * SIMPS - Modal Component
 * Quản lý popup dialog đơn giản, linh hoạt.
 */

class Modal {
  static open({ title, content, onConfirm, confirmText = 'Xác nhận', cancelText = 'Đóng' }) {
    this.close(); // Đóng modal cũ nếu có

    const backdrop = document.createElement('div');
    backdrop.id = 'simps-modal-backdrop';
    backdrop.className = 'modal-backdrop';
    backdrop.style.cssText = `
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(4px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 1rem;
    `;

    const dialog = document.createElement('div');
    dialog.className = 'modal-dialog';
    dialog.style.cssText = `
      background: white;
      border-radius: 12px;
      width: 100%;
      max-width: 540px;
      box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1);
      overflow: hidden;
      animation: modalFadeIn 0.2s ease-out;
      margin: auto;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
    `;

    dialog.innerHTML = `
      <div style="padding: 1.25rem 1.5rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;">
        <h3 style="margin: 0; font-size: 1.2rem; font-weight: 600; color: #1e293b;">${title}</h3>
        <button id="modal-close-btn" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #94a3b8;">&times;</button>
      </div>
      <div style="padding: 1.25rem 1.5rem; max-height: 70vh; overflow-y: auto; flex: 1;">
        ${content}
      </div>
      <div style="padding: 1rem 1.5rem; background: #f8fafc; border-top: 1px solid #e2e8f0; display: flex; justify-content: flex-end; gap: 0.75rem;">
        <button id="modal-cancel-btn" class="btn btn-secondary">${cancelText}</button>
        ${onConfirm ? `<button id="modal-confirm-btn" class="btn btn-primary">${confirmText}</button>` : ''}
      </div>
    `;

    backdrop.appendChild(dialog);
    document.body.appendChild(backdrop);

    // Sự kiện đóng
    document.getElementById('modal-close-btn').onclick = () => this.close();
    document.getElementById('modal-cancel-btn').onclick = () => this.close();
    backdrop.onclick = (e) => {
      if (e.target === backdrop) this.close();
    };

    if (onConfirm) {
      document.getElementById('modal-confirm-btn').onclick = () => {
        onConfirm(this.close);
      };
    }
  }

  static close() {
    const existing = document.getElementById('simps-modal-backdrop');
    if (existing) existing.remove();
  }
}

window.Modal = Modal;
