/**
 * SIMPS - API Service
 * Giao tiếp với FastAPI Backend (http://localhost:8000/api)
 */

// Tự động nhận diện môi trường: Cloud (Vercel) dùng '/api', Local Dev nếu chạy cổng khác thì gọi port 8000
const API_BASE_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') && window.location.port !== '8000' && window.location.port !== ''
  ? 'http://localhost:8000/api'
  : '/api';

class ApiService {
  /**
   * Lấy token JWT từ LocalStorage
   */
  static getToken() {
    return localStorage.getItem('simps_token');
  }

  /**
   * Lưu token JWT vào LocalStorage
   */
  static setToken(token) {
    localStorage.setItem('simps_token', token);
  }

  /**
   * Xóa token (đăng xuất)
   */
  static removeToken() {
    localStorage.removeItem('simps_token');
    localStorage.removeItem('simps_user');
  }

  /**
   * Gửi request chung đến backend
   */
  static async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Nếu hết hạn token hoặc không có quyền
      if (response.status === 401) {
        this.removeToken();
        if (!window.location.pathname.endsWith('index.html') && window.location.pathname !== '/') {
          window.location.href = '../index.html';
        }
        throw new Error('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
      }

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Đã có lỗi xảy ra');
      }

      return data;
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // === AUTH ===
  static login(username, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  static getMe() {
    return this.request('/auth/me');
  }

  // === INCIDENTS ===
  static getIncidents(params = {}) {
    const query = new URLSearchParams();
    Object.keys(params).forEach(key => {
      if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
        query.append(key, params[key]);
      }
    });
    return this.request(`/incidents?${query.toString()}`);
  }

  static getIncidentById(id) {
    return this.request(`/incidents/${id}`);
  }

  static createIncident(incidentData) {
    return this.request('/incidents', {
      method: 'POST',
      body: JSON.stringify(incidentData),
    });
  }

  static updateIncidentStatus(id, statusData) {
    return this.request(`/incidents/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify(statusData),
    });
  }

  static assignIncident(id, staffId) {
    return this.request(`/incidents/${id}/assign`, {
      method: 'PATCH',
      body: JSON.stringify({ assigned_to: staffId }),
    });
  }

  static confirmResolution(id) {
    return this.request(`/incidents/${id}/confirm`, {
      method: 'POST',
    });
  }

  static getIncidentHistory(id) {
    return this.request(`/incidents/${id}/history`);
  }

  // === UPLOAD IMAGE ===
  static async uploadImage(file) {
    const url = `${API_BASE_URL}/incidents/upload-image`;
    const formData = new FormData();
    formData.append('file', file);

    const token = this.getToken();
    const headers = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Không thể upload ảnh');
    }
    return data;
  }

  // === CONFIG & CATEGORIES ===
  static getLocations() {
    return this.request('/config/locations');
  }

  static createLocation(locData) {
    return this.request('/config/locations', {
      method: 'POST',
      body: JSON.stringify(locData),
    });
  }

  static updateLocation(id, locData) {
    return this.request(`/config/locations/${id}`, {
      method: 'PUT',
      body: JSON.stringify(locData),
    });
  }

  static deleteLocation(id) {
    return this.request(`/config/locations/${id}`, {
      method: 'DELETE',
    });
  }

  static getIncidentTypes() {
    return this.request('/config/incident-types');
  }

  static createIncidentType(typeData) {
    return this.request('/config/incident-types', {
      method: 'POST',
      body: JSON.stringify(typeData),
    });
  }

  static updateIncidentType(id, typeData) {
    return this.request(`/config/incident-types/${id}`, {
      method: 'PUT',
      body: JSON.stringify(typeData),
    });
  }

  static deleteIncidentType(id) {
    return this.request(`/config/incident-types/${id}`, {
      method: 'DELETE',
    });
  }

  static getWeights() {
    return this.request('/config/weights');
  }

  static updateWeights(weightsData) {
    return this.request('/config/weights', {
      method: 'PUT',
      body: JSON.stringify(weightsData),
    });
  }

  // === STATS ===
  static getStatsOverview() {
    return this.request('/stats/overview');
  }

  static getStatsByLocation() {
    return this.request('/stats/by-location');
  }

  static getStatsByType() {
    return this.request('/stats/by-type');
  }

  static getStatsByMonth() {
    return this.request('/stats/by-month');
  }

  static getAvgResolutionTime() {
    return this.request('/stats/avg-resolution-time');
  }

  static getStatsByStaff() {
    return this.request('/stats/by-staff');
  }

  static getMaintenanceRecommendations() {
    return this.request('/stats/maintenance-recommendations');
  }

  // === USERS ===
  static getUsers(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/users?${query}`);
  }

  static createUser(userData) {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  static updateUser(id, userData) {
    return this.request(`/users/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(userData),
    });
  }

  static deleteUser(id) {
    return this.request(`/users/${id}`, {
      method: 'DELETE',
    });
  }

  // === AUTH & PASSWORD ===
  static changePassword(oldPassword, newPassword) {
    return this.request('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({
        old_password: oldPassword,
        new_password: newPassword
      })
    });
  }

  // === INCIDENT UPDATE & DELETE ===
  static updateIncident(id, data) {
    return this.request(`/incidents/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  static deleteIncident(id) {
    return this.request(`/incidents/${id}`, {
      method: 'DELETE'
    });
  }

  // === NOTIFICATIONS ===
  static getNotifications(params = {}) {
    const query = new URLSearchParams();
    Object.keys(params).forEach(k => {
      if (params[k] !== undefined && params[k] !== null && params[k] !== '') {
        query.append(k, params[k]);
      }
    });
    return this.request(`/notifications?${query.toString()}`);
  }

  static markNotificationRead(id) {
    return this.request(`/notifications/${id}/read`, {
      method: 'PATCH',
    });
  }

  static markAllNotificationsRead() {
    return this.request('/notifications/read-all', {
      method: 'POST',
    });
  }
}

window.ApiService = ApiService;
