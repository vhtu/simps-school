/**
 * SIMPS - Notification Bell & Real-time Alert Component 2.0
 * Điều phối thông báo tức thì cho Quản trị viên (Admin) và Kỹ thuật viên (Staff).
 */

class NotificationManager {
  constructor(options = {}) {
    this.containerId = options.containerId || 'notification-bell-container';
    this.onIncidentClick = options.onIncidentClick || null;
    this.unreadCount = 0;
    this.notifications = [];
    this.isOpen = false;
    this.knownIds = new Set();
    this.pollInterval = null;
    this.init();
  }

  init() {
    this.renderBell();
    this.fetchNotifications(true); // initial fetch
    this.startPolling(6000);       // check every 6 seconds
  }

  renderBell() {
    const container = document.getElementById(this.containerId);
    if (!container) return;

    container.style.position = 'relative';
    container.innerHTML = `
      <button id="notif-bell-btn" class="notif-bell-btn" title="Thông báo sự cố mới">
        <span style="font-size: 1.25rem;">🔔</span>
        <span id="notif-badge" class="notif-badge" style="display: none;">0</span>
      </button>

      <!-- Dropdown Panel -->
      <div id="notif-dropdown" class="notif-dropdown" style="display: none;">
        <div class="notif-dropdown-header">
          <div>
            <div style="font-weight: 800; font-size: 0.95rem; color: #0f172a;">Thông Báo Sự Cố</div>
            <div style="font-size: 0.75rem; color: #64748b;">Cập nhật theo thời gian thực</div>
          </div>
          <button id="mark-all-read-btn" class="btn btn-xs btn-outline" style="font-size: 0.75rem;">
            Đã đọc tất cả
          </button>
        </div>

        <div id="notif-list" class="notif-list">
          <div style="padding: 2rem; text-align: center; color: #94a3b8; font-size: 0.85rem;">
            Đang tải thông báo...
          </div>
        </div>
      </div>
    `;

    // Events
    document.getElementById('notif-bell-btn').onclick = (e) => {
      e.stopPropagation();
      this.toggleDropdown();
    };

    document.getElementById('mark-all-read-btn').onclick = (e) => {
      e.stopPropagation();
      this.markAllRead();
    };

    document.addEventListener('click', (e) => {
      const dropdown = document.getElementById('notif-dropdown');
      if (dropdown && !dropdown.contains(e.target) && e.target.id !== 'notif-bell-btn') {
        this.closeDropdown();
      }
    });
  }

  toggleDropdown() {
    this.isOpen = !this.isOpen;
    const dropdown = document.getElementById('notif-dropdown');
    if (dropdown) {
      dropdown.style.display = this.isOpen ? 'block' : 'none';
      if (this.isOpen) {
        this.renderList();
      }
    }
  }

  closeDropdown() {
    this.isOpen = false;
    const dropdown = document.getElementById('notif-dropdown');
    if (dropdown) dropdown.style.display = 'none';
  }

  async fetchNotifications(isInitial = false) {
    try {
      const res = await ApiService.getNotifications({ limit: 15 });
      const data = res.data;
      const newItems = data.items || [];
      const newCount = data.unread_count || 0;

      // Kiểm tra có thông báo mới phát sinh không
      if (!isInitial) {
        const freshAlerts = newItems.filter(item => !this.knownIds.has(item.id) && !item.is_read);
        if (freshAlerts.length > 0) {
          freshAlerts.forEach(alert => {
            this.playNotificationSound(alert.priority_level);
            Toast.show(`${alert.title}`, alert.priority_level === 'emergency' ? 'error' : 'warning', 5000);
          });
          // Kích hoạt làm mới bảng sự cố nếu có hàm callback
          if (typeof window.loadIncidents === 'function') {
            window.loadIncidents();
          }
        }
      }

      // Lưu lại danh sách ID đã biết
      newItems.forEach(item => this.knownIds.add(item.id));

      this.notifications = newItems;
      this.unreadCount = newCount;
      this.updateBadge();

      if (this.isOpen) {
        this.renderList();
      }
    } catch (err) {
      // Bỏ qua lỗi polling im lặng khi chưa đăng nhập
    }
  }

  updateBadge() {
    const badge = document.getElementById('notif-badge');
    if (!badge) return;

    if (this.unreadCount > 0) {
      badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
      badge.style.display = 'flex';
    } else {
      badge.style.display = 'none';
    }
  }

  renderList() {
    const list = document.getElementById('notif-list');
    if (!list) return;

    if (this.notifications.length === 0) {
      list.innerHTML = `
        <div style="padding: 2.5rem 1.5rem; text-align: center; color: #94a3b8;">
          <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎉</div>
          <div style="font-weight: 600; font-size: 0.9rem; color: #475569;">Không có thông báo mới</div>
          <div style="font-size: 0.775rem;">Mọi sự cố học đường đều đã được xem xét.</div>
        </div>
      `;
      return;
    }

    list.innerHTML = this.notifications.map(n => {
      const isUnread = !n.is_read;
      const isEmergency = n.priority_level === 'emergency';
      const icon = isEmergency ? '🚨' : n.priority_level === 'urgent' ? '⚠️' : '📝';

      return `
        <div class="notif-item ${isUnread ? 'unread' : ''}" onclick="window.notifManager.handleItemClick(${n.id}, ${n.incident_id})">
          <div class="notif-icon-box ${n.priority_level}">${icon}</div>
          <div style="flex: 1; min-width: 0;">
            <div class="notif-title">${Utils.escapeHtml(n.title)}</div>
            <div class="notif-msg">${Utils.escapeHtml(n.message)}</div>
            <div class="notif-time">${Utils.formatDateTime(n.created_at)}</div>
          </div>
          ${isUnread ? '<span class="notif-dot"></span>' : ''}
        </div>
      `;
    }).join('');
  }

  async handleItemClick(notifId, incidentId) {
    try {
      await ApiService.markNotificationRead(notifId);
      const item = this.notifications.find(n => n.id === notifId);
      if (item) item.is_read = true;
      this.unreadCount = Math.max(0, this.unreadCount - 1);
      this.updateBadge();
      this.renderList();
    } catch (err) {}

    this.closeDropdown();

    if (incidentId) {
      if (typeof window.openAdminIncidentModal === 'function') {
        window.openAdminIncidentModal(incidentId);
      } else if (typeof window.openActionModal === 'function') {
        window.openActionModal(incidentId);
      } else if (typeof window.viewDetail === 'function') {
        window.viewDetail(incidentId);
      }
    }
  }

  async markAllRead() {
    try {
      await ApiService.markAllNotificationsRead();
      this.notifications.forEach(n => n.is_read = true);
      this.unreadCount = 0;
      this.updateBadge();
      this.renderList();
      Toast.success('Đã đánh dấu tất cả thông báo là đã đọc');
    } catch (err) {
      Toast.error('Không thể cập nhật thông báo');
    }
  }

  startPolling(intervalMs = 6000) {
    if (this.pollInterval) clearInterval(this.pollInterval);
    this.pollInterval = setInterval(() => {
      this.fetchNotifications(false);
    }, intervalMs);
  }

  /**
   * Phát âm thanh chuông thông báo nhẹ nhàng bằng Web Audio API thuần (Không cần file mp3)
   */
  playNotificationSound(priorityLevel) {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      const ctx = new AudioContext();

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = priorityLevel === 'emergency' ? 'sawtooth' : 'sine';
      osc.frequency.setValueAtTime(priorityLevel === 'emergency' ? 880 : 587.33, ctx.currentTime); // A5 or D5
      osc.frequency.exponentialRampToValueAtTime(priorityLevel === 'emergency' ? 440 : 880, ctx.currentTime + 0.3);

      gain.gain.setValueAtTime(0.15, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.35);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + 0.35);
    } catch (e) {
      // Silent fail if audio policy blocks autoplay
    }
  }
}

window.NotificationManager = NotificationManager;
