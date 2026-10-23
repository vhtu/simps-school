/**
 * SIMPS - Utilities & Helpers
 * Các hàm hỗ trợ định dạng, hiển thị badge và xử lý thời gian.
 */

const Utils = {
  /**
   * Định dạng thời gian thân thiện (vd: 10 phút trước, hôm qua, hoặc DD/MM/YYYY HH:mm)
   */
  formatDateTime(isoString) {
    if (!isoString) return '--';
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return '--';

    const now = new Date();
    const diffSeconds = Math.floor((now - date) / 1000);

    if (diffSeconds < 60) return 'Vừa xong';
    if (diffSeconds < 3600) return `${Math.floor(diffSeconds / 60)} phút trước`;
    if (diffSeconds < 86400) return `${Math.floor(diffSeconds / 3600)} giờ trước`;
    if (diffSeconds < 259200) return `${Math.floor(diffSeconds / 86400)} ngày trước`;

    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${day}/${month}/${year} ${hours}:${minutes}`;
  },

  /**
   * Render HTML cho Badge trạng thái sự cố
   */
  renderStatusBadge(status) {
    const config = {
      reported: { label: 'Mới báo cáo', class: 'status-reported', icon: '📝' },
      received: { label: 'Đã tiếp nhận', class: 'status-received', icon: '📥' },
      assigned: { label: 'Đã phân công', class: 'status-assigned', icon: '👤' },
      in_progress: { label: 'Đang xử lý', class: 'status-in-progress', icon: '⚙️' },
      resolved: { label: 'Đã khắc phục', class: 'status-resolved', icon: '🔧' },
      confirmed: { label: 'Đã xác nhận', class: 'status-confirmed', icon: '✅' },
      closed: { label: 'Đã đóng', class: 'status-closed', icon: '🔒' },
    };

    const item = config[status] || { label: status, class: '', icon: '' };
    return `<span class="badge ${item.class}">${item.icon} ${item.label}</span>`;
  },

  /**
   * Render HTML cho Badge mức độ ưu tiên (P)
   */
  renderPriorityBadge(level, score = null) {
    const config = {
      emergency: { label: 'Khẩn cấp', class: 'priority-emergency', icon: '🚨' },
      urgent: { label: 'Cấp bách', class: 'priority-urgent', icon: '⚠️' },
      high: { label: 'Ưu tiên cao', class: 'priority-high', icon: '⚡' },
      normal: { label: 'Bình thường', class: 'priority-normal', icon: 'ℹ️' },
    };

    const item = config[level] || { label: level, class: '', icon: '' };
    const scoreText = score !== null ? ` (P: ${score >= 900 ? 'MAX' : score})` : '';
    return `<span class="badge ${item.class}">${item.icon} ${item.label}${scoreText}</span>`;
  },

  /**
   * Render nhãn số sao / mức độ nghiêm trọng
   */
  renderSeverity(value) {
    const stars = '★'.repeat(value) + '☆'.repeat(5 - value);
    return `<span style="color: #f59e0b; font-size: 1.1rem;">${stars}</span> (${value}/5)`;
  },

  /**
   * Escape HTML để tránh lỗi bảo mật XSS
   */
  escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
};

window.Utils = Utils;
