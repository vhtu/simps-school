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

// Modal chung cho việc Đổi mật khẩu cá nhân
function openSelfPasswordModal() {
  const content = `
    <form id="self-pass-form">
      <div class="form-group">
        <label class="form-label">Mật khẩu hiện tại</label>
        <input type="password" id="self-old-pass" class="form-control" required placeholder="Nhập mật khẩu hiện tại">
      </div>
      <div class="form-group">
        <label class="form-label">Mật khẩu mới</label>
        <input type="password" id="self-new-pass" class="form-control" required placeholder="Nhập ít nhất 4 ký tự">
      </div>
      <div class="form-group">
        <label class="form-label">Xác nhận mật khẩu mới</label>
        <input type="password" id="self-confirm-pass" class="form-control" required placeholder="Nhập lại mật khẩu mới">
      </div>
    </form>
  `;

  if (window.Modal) {
    Modal.open({
      title: '🔑 Đổi Mật Khẩu Cá Nhân',
      content,
      confirmText: 'Xác Nhận Đổi',
      onConfirm: async (close) => {
        const oldP = document.getElementById('self-old-pass').value;
        const newP = document.getElementById('self-new-pass').value;
        const confP = document.getElementById('self-confirm-pass').value;

        if (!oldP || !newP) {
          Toast.warning('Vui lòng điền đủ các trường');
          return;
        }
        if (newP !== confP) {
          Toast.warning('Mật khẩu xác nhận không khớp');
          return;
        }
        if (newP.length < 4) {
          Toast.warning('Mật khẩu mới phải từ 4 ký tự trở lên');
          return;
        }

        try {
          await ApiService.changePassword(oldP, newP);
          Toast.success('Đổi mật khẩu thành công!');
          close();
        } catch (err) {
          Toast.error(err.message || 'Lỗi đổi mật khẩu');
        }
      }
    });
  }
}

window.openSelfPasswordModal = openSelfPasswordModal;
window.AuthService = AuthService;
