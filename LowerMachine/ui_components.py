"""
UI组件辅助函数
"""
import lvgl as lv
from config import THEME, LAYOUT

def create_label(parent, x, y, text, color_key, font=None):
    """创建并配置标签的辅助函数"""
    label = lv.label(parent)
    label.set_pos(x, y)
    label.set_text(text)
    label.set_style_text_color(lv.color_hex(THEME[color_key]), 0)
    if font:
        label.set_style_text_font(font, 0)
    return label

def create_card(parent, x, y, w, h):
    """创建卡片式容器"""
    card = lv.obj(parent)
    card.set_pos(x, y)
    card.set_size(w, h)
    card.set_style_bg_color(lv.color_hex(THEME['bg_card']), 0)
    card.set_style_border_width(1, 0)
    card.set_style_border_color(lv.color_hex(THEME['divider']), 0)
    card.set_style_pad_all(LAYOUT['card_padding'], 0)
    card.set_style_radius(4, 0)  # 圆角
    return card

def make_bar(percent):
    """生成文本进度条，percent为0-100"""
    if percent < 0:
        percent = 0
    elif percent > 100:
        percent = 100
    filled = int(percent / 10)  # 10个格子
    empty = 10 - filled
    return "[" + "+" * filled + "=" * empty + "]"

def format_bytes(bytes_val):
    """将字节转换为可读的单位"""
    if bytes_val < 1024:
        return f"{bytes_val}B"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val // 1024}KB"
    else:
        return f"{bytes_val // (1024 * 1024)}MB"

def get_warn_indicator(percent):
    """根据百分比返回警告标记"""
    if percent >= 80:
        return "!"  # 严重警告
    elif percent >= 60:
        return "*"  # 轻微警告
    else:
        return ""   # 无警告

def get_performance_score(avg_cpu, avg_mem):
    """根据平均CPU和内存计算性能评分"""
    avg_usage = (avg_cpu + avg_mem) / 2
    if avg_usage < 30:
        return "A"  # 优秀
    elif avg_usage < 50:
        return "B"  # 良好
    elif avg_usage < 70:
        return "C"  # 正常
    elif avg_usage < 85:
        return "D"  # 较差
    else:
        return "F"  # 极差
