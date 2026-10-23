/**
 * SIMPS - Hi-DPI Canvas Charts 2.0
 * Biểu đồ HTML5 Canvas thuần tối ưu độ nét Retina, bo góc mượt mà.
 */

class SimpleChart {
  /**
   * Thiết lập Canvas để không bị mờ trên màn hình độ phân giải cao (Retina/High-DPI)
   */
  static setupCanvas(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    const parent = canvas.parentElement;
    const dpr = window.devicePixelRatio || 1;
    const rect = parent.getBoundingClientRect();

    const width = rect.width || 400;
    const height = rect.height || 260;

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;

    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    return { ctx, width, height };
  }

  /**
   * Biểu đồ Cột đứng (Vertical Bar Chart) với Gradient & Bo góc
   */
  static drawBarChart(canvasId, labels, data, options = {}) {
    const setup = this.setupCanvas(canvasId);
    if (!setup) return;
    const { ctx, width, height } = setup;

    ctx.clearRect(0, 0, width, height);

    const padding = { top: 35, right: 25, bottom: 45, left: 45 };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    const maxVal = Math.max(...data, 5);
    const barWidth = Math.min(32, (chartW / (data.length || 1)) * 0.55);
    const gap = chartW / (data.length || 1);

    // Đường lưới ngang
    ctx.strokeStyle = '#f1f5f9';
    ctx.lineWidth = 1;
    const gridLines = 4;
    ctx.fillStyle = '#94a3b8';
    ctx.font = '500 11px var(--font-sans, sans-serif)';
    ctx.textAlign = 'right';

    for (let i = 0; i <= gridLines; i++) {
      const yVal = Math.round((maxVal / gridLines) * i);
      const yPos = padding.top + chartH - (i * (chartH / gridLines));
      ctx.beginPath();
      ctx.moveTo(padding.left, yPos);
      ctx.lineTo(width - padding.right, yPos);
      ctx.stroke();
      ctx.fillText(yVal, padding.left - 10, yPos + 4);
    }

    // Vẽ các cột
    data.forEach((val, i) => {
      const h = (val / maxVal) * chartH;
      const x = padding.left + (i * gap) + (gap - barWidth) / 2;
      const y = padding.top + chartH - h;

      // Gradient cột
      const grad = ctx.createLinearGradient(0, y, 0, y + h);
      const baseColor = options.color || '#4f46e5';
      grad.addColorStop(0, baseColor);
      grad.addColorStop(1, '#818cf8');

      ctx.fillStyle = grad;
      ctx.beginPath();
      // Bo góc trên
      const radius = 6;
      ctx.roundRect ? ctx.roundRect(x, y, barWidth, h, [radius, radius, 0, 0]) : ctx.rect(x, y, barWidth, h);
      ctx.fill();

      // Số liệu trên cột
      if (val > 0) {
        ctx.fillStyle = '#0f172a';
        ctx.font = '700 11px var(--font-sans, sans-serif)';
        ctx.textAlign = 'center';
        ctx.fillText(val, x + barWidth / 2, y - 8);
      }

      // Nhãn trục X
      ctx.fillStyle = '#64748b';
      ctx.font = '600 11px var(--font-sans, sans-serif)';
      ctx.textAlign = 'center';
      const label = labels[i] || '';
      ctx.fillText(label, x + barWidth / 2, height - padding.bottom + 22);
    });
  }

  /**
   * Biểu đồ Tròn Donut Chart với phần tâm tổng kết và chú thích sang trọng
   */
  static drawPieChart(canvasId, labels, data, colors = null) {
    const setup = this.setupCanvas(canvasId);
    if (!setup) return;
    const { ctx, width, height } = setup;

    ctx.clearRect(0, 0, width, height);

    const palette = colors || ['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#64748b'];
    const total = data.reduce((sum, v) => sum + v, 0);

    if (total === 0) {
      ctx.fillStyle = '#94a3b8';
      ctx.font = '600 14px var(--font-sans, sans-serif)';
      ctx.textAlign = 'center';
      ctx.fillText('Chưa có dữ liệu thống kê', width / 2, height / 2);
      return;
    }

    const centerX = width * 0.35;
    const centerY = height / 2;
    const radius = Math.min(centerX, centerY) - 25;

    let startAngle = -Math.PI / 2;

    data.forEach((val, i) => {
      const sliceAngle = (val / total) * 2 * Math.PI;
      ctx.fillStyle = palette[i % palette.length];
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
      ctx.closePath();
      ctx.fill();
      startAngle += sliceAngle;
    });

    // Donut hole
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius * 0.62, 0, 2 * Math.PI);
    ctx.fill();

    // Center summary text
    ctx.fillStyle = '#0f172a';
    ctx.font = '800 1.25rem var(--font-sans, sans-serif)';
    ctx.textAlign = 'center';
    ctx.fillText(total, centerX, centerY + 3);
    ctx.fillStyle = '#64748b';
    ctx.font = '600 10px var(--font-sans, sans-serif)';
    ctx.fillText('TỔNG SỰ CỐ', centerX, centerY + 18);

    // Chú thích (Legend)
    const legendX = width * 0.66;
    let legendY = Math.max(30, centerY - (labels.length * 14));
    ctx.textAlign = 'left';

    labels.forEach((label, i) => {
      const val = data[i];
      const percent = Math.round((val / total) * 100);

      // Dot color
      ctx.fillStyle = palette[i % palette.length];
      ctx.beginPath();
      ctx.arc(legendX + 6, legendY, 5, 0, 2 * Math.PI);
      ctx.fill();

      // Label text
      ctx.fillStyle = '#1e293b';
      ctx.font = '600 11px var(--font-sans, sans-serif)';
      const cleanLabel = label.length > 18 ? label.substring(0, 16) + '...' : label;
      ctx.fillText(cleanLabel, legendX + 18, legendY + 4);

      // Percent
      ctx.fillStyle = '#64748b';
      ctx.font = '700 11px var(--font-mono, monospace)';
      ctx.fillText(`${percent}%`, legendX + 130, legendY + 4);

      legendY += 26;
    });
  }
  /**
   * Biểu đồ Cột ngang (Horizontal Bar Chart)
   * Thích hợp cho danh sách có nhãn dài hoặc so sánh thời gian giải quyết
   */
  static drawHorizontalBarChart(canvasId, labels, data, options = {}) {
    const setup = this.setupCanvas(canvasId);
    if (!setup) return;
    const { ctx, width, height } = setup;

    ctx.clearRect(0, 0, width, height);

    const padding = { top: 25, right: 55, bottom: 25, left: options.labelWidth || 110 };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    const maxVal = Math.max(...data.map(v => Number(v) || 0), 5);
    const n = labels.length || 1;
    const rowHeight = chartH / n;
    const barHeight = Math.min(22, rowHeight * 0.55);

    // Đường lưới dọc mờ
    ctx.strokeStyle = '#f1f5f9';
    ctx.lineWidth = 1;
    const gridCols = 4;
    for (let i = 0; i <= gridCols; i++) {
      const x = padding.left + (chartW / gridCols) * i;
      ctx.beginPath();
      ctx.moveTo(x, padding.top);
      ctx.lineTo(x, height - padding.bottom);
      ctx.stroke();
    }

    labels.forEach((label, i) => {
      const val = Number(data[i]) || 0;
      const barW = maxVal > 0 ? (val / maxVal) * chartW : 0;
      const y = padding.top + i * rowHeight + (rowHeight - barHeight) / 2;

      // Nhãn bên trái
      ctx.fillStyle = '#475569';
      ctx.font = '600 12px var(--font-sans, sans-serif)';
      ctx.textAlign = 'right';
      const cleanLabel = label.length > 16 ? label.substring(0, 15) + '..' : label;
      ctx.fillText(cleanLabel, padding.left - 12, y + barHeight / 2 + 4);

      // Thanh nền mờ
      ctx.fillStyle = '#f8fafc';
      if (ctx.roundRect) {
        ctx.beginPath();
        ctx.roundRect(padding.left, y, chartW, barHeight, 6);
        ctx.fill();
      }

      // Màu cột (hỗ trợ mảng màu hoặc hàm hoặc màu mặc định)
      let barColor = options.color || '#4f46e5';
      if (options.colors && options.colors[i]) {
        barColor = options.colors[i];
      }

      // Vẽ thanh giá trị
      if (barW > 0) {
        const grad = ctx.createLinearGradient(padding.left, 0, padding.left + barW, 0);
        grad.addColorStop(0, barColor);
        grad.addColorStop(1, options.gradientEnd || barColor);

        ctx.fillStyle = grad;
        ctx.beginPath();
        if (ctx.roundRect) {
          ctx.roundRect(padding.left, y, barW, barHeight, 6);
        } else {
          ctx.rect(padding.left, y, barW, barHeight);
        }
        ctx.fill();
      }

      // Số liệu nhãn phía sau thanh
      ctx.fillStyle = '#0f172a';
      ctx.font = '700 12px var(--font-mono, monospace)';
      ctx.textAlign = 'left';
      const unit = options.unit || '';
      ctx.fillText(`${val}${unit}`, padding.left + barW + 8, y + barHeight / 2 + 4);
    });
  }

  /**
   * Biểu đồ Cột ghép nhóm (Grouped Bar Chart)
   * Dùng so sánh 2 hoặc nhiều chỉ số cùng lúc (VD: Sự cố Đang xử lý vs Đã hoàn thành theo Nhân viên)
   */
  static drawGroupedBarChart(canvasId, labels, series, options = {}) {
    const setup = this.setupCanvas(canvasId);
    if (!setup) return;
    const { ctx, width, height } = setup;

    ctx.clearRect(0, 0, width, height);

    const padding = { top: 40, right: 25, bottom: 45, left: 45 };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    // Tìm max value trong toàn bộ series
    let allVals = [];
    series.forEach(s => allVals.push(...s.data.map(v => Number(v) || 0)));
    const maxVal = Math.max(...allVals, 5);

    // Chú thích (Legend) ở góc trên
    let legendX = width - padding.right;
    ctx.textAlign = 'right';
    for (let sIdx = series.length - 1; sIdx >= 0; sIdx--) {
      const s = series[sIdx];
      ctx.fillStyle = '#475569';
      ctx.font = '600 11px var(--font-sans, sans-serif)';
      ctx.fillText(s.name, legendX, 22);
      const textW = ctx.measureText(s.name).width;

      ctx.fillStyle = s.color;
      ctx.beginPath();
      ctx.arc(legendX - textW - 8, 18, 5, 0, 2 * Math.PI);
      ctx.fill();

      legendX -= (textW + 28);
    }

    // Lưới ngang
    ctx.strokeStyle = '#f1f5f9';
    ctx.lineWidth = 1;
    const gridLines = 4;
    ctx.fillStyle = '#94a3b8';
    ctx.font = '500 11px var(--font-sans, sans-serif)';
    ctx.textAlign = 'right';

    for (let i = 0; i <= gridLines; i++) {
      const yVal = Math.round((maxVal / gridLines) * i);
      const yPos = padding.top + chartH - (i * (chartH / gridLines));
      ctx.beginPath();
      ctx.moveTo(padding.left, yPos);
      ctx.lineTo(width - padding.right, yPos);
      ctx.stroke();
      ctx.fillText(yVal, padding.left - 8, yPos + 4);
    }

    const groupCount = labels.length || 1;
    const groupW = chartW / groupCount;
    const seriesCount = series.length;
    const barW = Math.min(18, (groupW * 0.7) / seriesCount);
    const groupPadding = (groupW - (barW * seriesCount + (seriesCount - 1) * 3)) / 2;

    labels.forEach((label, gIdx) => {
      const groupStartX = padding.left + gIdx * groupW + groupPadding;

      series.forEach((s, sIdx) => {
        const val = Number(s.data[gIdx]) || 0;
        const h = (val / maxVal) * chartH;
        const x = groupStartX + sIdx * (barW + 3);
        const y = padding.top + chartH - h;

        // Vẽ cột
        ctx.fillStyle = s.color;
        ctx.beginPath();
        if (ctx.roundRect) {
          ctx.roundRect(x, y, barW, h, [4, 4, 0, 0]);
        } else {
          ctx.rect(x, y, barW, h);
        }
        ctx.fill();

        // Số liệu trên cột
        if (val > 0) {
          ctx.fillStyle = '#1e293b';
          ctx.font = '700 10px var(--font-mono, monospace)';
          ctx.textAlign = 'center';
          ctx.fillText(val, x + barW / 2, y - 4);
        }
      });

      // Nhãn trục X
      ctx.fillStyle = '#64748b';
      ctx.font = '600 11px var(--font-sans, sans-serif)';
      ctx.textAlign = 'center';
      const cleanLabel = label.length > 12 ? label.substring(0, 10) + '..' : label;
      ctx.fillText(cleanLabel, groupStartX + (barW * seriesCount) / 2, height - padding.bottom + 22);
    });
  }
}

window.SimpleChart = SimpleChart;
