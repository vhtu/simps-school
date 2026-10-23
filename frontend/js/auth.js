/**
 * SIMPS - Auth Service
 * Quản lý trạng thái đăng nhập, phiên người dùng và điều hướng theo vai trò.
 */

class AuthService {
  /**
   * Lưu thông tin người dùng vào LocalStorage
   */
  static setUser(user) {
    localStorage.setItem('simps_user', JSON.stringify(user));
  }

  /**
   * Lấy thông tin người dùng hiện tại
   */
  static getUser() {
    const userStr = localStorage.getItem('simps_user');
    try {
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      return null;
    }
  }

  /**
   * Đăng nhập và điều hướng đến trang tương ứng với vai trò
   */
  static async login(username, password) {
    const response = await ApiService.login(username, password);
    if (response.success && response.data) {
      ApiService.setToken(response.data.access_token);
      this.setUser(response.data.user);
      this.redirectByRole(response.data.user.role);
      return response.data.user;
    }
    throw new Error(response.message || 'Đăng nhập không thành công');
  }

  /**
   * Đăng xuất và trở về trang đăng nhập
   */
  static logout() {
    ApiService.removeToken();
    const isInsidePages = window.location.pathname.includes('/pages/');
    window.location.href = isInsidePages ? '../index.html' : 'index.html';
  }

  /**
   * Điều hướng theo vai trò người dùng
   */
  static redirectByRole(role) {
    const isInsidePages = window.location.pathname.includes('/pages/');
    const prefix = isInsidePages ? '' : 'pages/';

    switch (role) {
      case 'student':
        window.location.href = `${prefix}student.html`;
        break;
      case 'staff':
        window.location.href = `${prefix}staff.html`;
        break;
      case 'admin':
        window.location.href = `${prefix}admin.html`;
        break;
      default:
        window.location.href = `${prefix}student.html`;
    }
  }

  /**
   * Kiểm tra quyền truy cập của trang hiện tại
   */
  static checkAuth(allowedRoles = []) {
    const token = ApiService.getToken();
    const user = this.getUser();

    if (!token || !user) {
      this.logout();
      return null;
    }

    if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
      alert('Bạn không có quyền truy cập vào phân hệ này.');
      this.redirectByRole(user.role);
      return null;
    }

    return user;
  }
}

window.AuthService = AuthService;
