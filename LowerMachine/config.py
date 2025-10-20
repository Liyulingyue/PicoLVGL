"""
配置文件 - 包含主题颜色和布局配置
"""

# 配置主题颜色
THEME = {
    'bg_primary': 0x0a0e27,      # 主背景
    'bg_secondary': 0x0f1729,    # 次级背景
    'bg_header': 0x1a2847,       # 标题栏背景
    'bg_card': 0x1a2847,         # 卡片背景
    'border': 0x1a2847,          # 边框颜色
    'divider': 0x2a3850,         # 分隔线颜色
    'text_title': 0x00d4ff,      # 标题文字
    'text_time': 0x00d4ff,       # 时间文字
    'text_time_dim': 0x888888,   # 时间详情（暗）
    'text_cpu': 0xff6b6b,        # CPU文字（红）
    'text_memory': 0x51cf66,     # 内存文字（绿）
    'text_process': 0xa8e6cf,    # 进程文字（浅绿）
    'text_network': 0xffd89b,    # 网络文字（金）
    'text_stats': 0x666666,      # 统计文字（灰）
    'text_max': 0xffa500,        # 最高值文字（橙）
    'text_avg': 0x00cc88,        # 平均值文字（青绿）
    'text_score': 0x51cf66,      # 评分文字（绿）
    'indicator_on': 0x51cf66,    # 指示灯亮
    'indicator_off': 0x33aa55,   # 指示灯暗
}

# UI布局配置
LAYOUT = {
    'header_height': 40,
    'container_padding': 10,
    'card_padding': 8,           # 卡片内边距
    'card_spacing': 8,           # 卡片间距
    'label_spacing_y': 35,       # 标签垂直间距
    'bar_offset_y': 15,          # 进度条相对标签偏移
    'warn_offset_x': 400,        # 警告标记位置
}

# 屏幕尺寸
SCREEN = {
    'width': 480,
    'height': 320,
}
