import machine
import usys as sys
sys.path.append('') # See: https://github.com/micropython/micropython/issues/6419

import lvgl as lv
import lv_utils
import ujson
import time

class driver:
    def __init__(self):
        machine.freq(240000000)  # set the CPU frequency to 240 MHz
        print("CPU freq : ", machine.freq() / 1000000, "MHz")

    def init_gui(self):
        import ili9488 as tft
        import ft6236 as tp

        hres = 480
        vres = 320

        # Register display driver
        event_loop = lv_utils.event_loop()
        tft.deinit()
        tft.init()
        tp.init()

        disp_buf1 = lv.disp_draw_buf_t()
        buf1_1 = tft.framebuffer(1)
        buf1_2 = tft.framebuffer(2)
        disp_buf1.init(buf1_1, buf1_2, len(buf1_1) // lv.color_t.__SIZE__)
        disp_drv = lv.disp_drv_t()
        disp_drv.init()
        disp_drv.draw_buf = disp_buf1
        disp_drv.flush_cb = tft.flush
        disp_drv.hor_res = hres
        disp_drv.ver_res = vres
        disp_drv.register()

        # Register touch sensor
        indev_drv = lv.indev_drv_t()
        indev_drv.init()
        indev_drv.type = lv.INDEV_TYPE.POINTER
        indev_drv.read_cb = tp.ts_read
        indev_drv.register()

if not lv_utils.event_loop.is_running():
    drv = driver()
    drv.init_gui()

############################################################################################
# 配置主题颜色
THEME = {
    'bg_primary': 0x0a0e27,      # 主背景
    'bg_secondary': 0x0f1729,    # 次级背景
    'bg_header': 0x1a2847,       # 标题栏背景
    'bg_card': 0x1a2847,         # 卡片背景（新增）
    'border': 0x1a2847,          # 边框颜色
    'divider': 0x2a3850,         # 分隔线颜色（新增）
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
    'card_padding': 8,           # 卡片内边距（新增）
    'card_spacing': 8,           # 卡片间距（新增）
    'label_spacing_y': 35,       # 标签垂直间距
    'bar_offset_y': 15,          # 进度条相对标签偏移
    'warn_offset_x': 400,        # 警告标记位置
}

scr = lv.obj()
scr.set_style_bg_color(lv.color_hex(THEME['bg_primary']), 0)

# 辅助函数：创建标签
def create_label(parent, x, y, text, color_key, font=None):
    """创建并配置标签的辅助函数"""
    label = lv.label(parent)
    label.set_pos(x, y)
    label.set_text(text)
    label.set_style_text_color(lv.color_hex(THEME[color_key]), 0)
    if font:
        label.set_style_text_font(font, 0)
    return label

# 辅助函数：创建卡片容器
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

# 标题和状态指示灯（直接在主屏幕上，不用容器）
title_label = create_label(scr, 10, 8, "SYSTEM MONITOR", 'text_title')
status_indicator = create_label(scr, 460, 8, "●", 'indicator_on')

# 主容器（内容区域）
main_container = lv.obj(scr)
main_container.set_size(480, 295)
main_container.set_pos(0, 25)
main_container.set_style_bg_color(lv.color_hex(THEME['bg_primary']), 0)
main_container.set_style_border_width(0, 0)
main_container.set_style_pad_all(LAYOUT['container_padding'], 0)

# 卡片1：性能监控区域 (CPU + Memory)
card_performance = create_card(main_container, 10, 0, 220, 140)

# 卡片2：系统信息区域 (Time + Process)
card_system = create_card(main_container, 240, 0, 220, 140)

# 卡片3：网络和统计区域
card_network = create_card(main_container, 10, 150, 450, 110)

# === 卡片1内容：性能监控 ===
# CPU 信息
cpu_icon = create_label(card_performance, 5, 5, "[C]", 'text_cpu')  # CPU图标
cpu_label = create_label(card_performance, 30, 5, "CPU", 'text_cpu')
cpu_value = create_label(card_performance, 145, 5, "0.0%", 'text_cpu')
cpu_warn = create_label(card_performance, 195, 5, "", 'text_cpu')
cpu_bar_label = create_label(card_performance, 30, 22, "[==========]", 'text_cpu')

# 内存信息
mem_icon = create_label(card_performance, 5, 70, "[M]", 'text_memory')  # 内存图标
memory_label = create_label(card_performance, 30, 70, "Memory", 'text_memory')
memory_value = create_label(card_performance, 145, 70, "0.0%", 'text_memory')
mem_warn = create_label(card_performance, 195, 70, "", 'text_memory')
mem_bar_label = create_label(card_performance, 30, 87, "[==========]", 'text_memory')

# === 卡片2内容：系统信息 ===
# 时间信息
time_icon = create_label(card_system, 5, 5, "[T]", 'text_time')  # 时间图标
time_label = create_label(card_system, 30, 5, "Time", 'text_time')
time_value = create_label(card_system, 30, 22, "Loading...", 'text_time_dim')
time_detail = create_label(card_system, 30, 37, "", 'text_time')

# 进程信息
proc_icon = create_label(card_system, 5, 70, "[P]", 'text_process')  # 进程图标
process_label = create_label(card_system, 30, 70, "Processes", 'text_process')
process_value = create_label(card_system, 30, 87, "0", 'text_process')

# === 卡片3内容：网络和统计 ===
# 网络信息
net_icon = create_label(card_network, 5, 5, "[N]", 'text_network')  # 网络图标
net_label = create_label(card_network, 30, 5, "Network", 'text_network')
net_sent_label = create_label(card_network, 30, 22, "^ 0B", 'text_network')
net_recv_label = create_label(card_network, 160, 22, "v 0B", 'text_network')

# 统计信息 - 左列
stats_icon = create_label(card_network, 5, 50, "[#]", 'text_stats')  # 统计图标
stats_label = create_label(card_network, 30, 50, "00000", 'text_stats')
avg_label = create_label(card_network, 30, 67, "C-0% M-0%", 'text_avg')

# 统计信息 - 右列
max_icon = create_label(card_network, 240, 50, "MAX", 'text_max')  # 最高值图标
max_label = create_label(card_network, 270, 50, "C-0% M-0%", 'text_max')
perf_icon = create_label(card_network, 240, 67, "Score", 'text_score')  # 评分图标
performance_label = create_label(card_network, 280, 67, "A", 'text_score')

lv.scr_load(scr)

# 生成进度条显示函数
def make_bar(percent):
    """生成文本进度条，percent为0-100"""
    if percent < 0:
        percent = 0
    elif percent > 100:
        percent = 100
    filled = int(percent / 10)  # 10个格子
    empty = 10 - filled
    return "[" + "+" * filled + "=" * empty + "]"

# 格式化网络数据
def format_bytes(bytes_val):
    """将字节转换为可读的单位"""
    if bytes_val < 1024:
        return f"{bytes_val}B"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val // 1024}KB"
    else:
        return f"{bytes_val // (1024 * 1024)}MB"

# 获取警告标记
def get_warn_indicator(percent):
    """根据百分比返回警告标记"""
    if percent >= 80:
        return "!"  # 严重警告
    elif percent >= 60:
        return "*"  # 轻微警告
    else:
        return ""   # 无警告

# 计算性能评分（新增）
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

# 循环读取UART数据并更新显示
update_count = 0
max_cpu = 0
max_memory = 0
cpu_sum = 0  # 累计CPU使用率
mem_sum = 0  # 累计内存使用率
indicator_state = 0  # 指示灯状态（0或1）

while True:
    try:
        line = sys.stdin.readline().strip()
        if line:
            update_count = (update_count + 1) % 10000  # 每10000次重置，防止溢出
            data = ujson.loads(line)
            
            # 更新时间
            time_str = data['time']
            time_value.set_text(f"{time_str[:10]}")
            time_detail.set_text(f"{time_str[11:]}")
            
            # 更新CPU和进度条
            cpu_val = data['cpu']
            cpu_sum += cpu_val  # 累计用于平均值计算
            if cpu_val > max_cpu:
                max_cpu = cpu_val
            cpu_value.set_text(f"{cpu_val:.1f}%")
            cpu_bar_label.set_text(make_bar(cpu_val))
            cpu_warn.set_text(get_warn_indicator(cpu_val))
            
            # 更新内存和进度条
            mem_val = data['memory']
            mem_sum += mem_val  # 累计用于平均值计算
            if mem_val > max_memory:
                max_memory = mem_val
            memory_value.set_text(f"{mem_val:.1f}%")
            mem_bar_label.set_text(make_bar(mem_val))
            mem_warn.set_text(get_warn_indicator(mem_val))
            
            process_value.set_text(f"{data['processes']}")
            
            # 更新网络速率信息，转换为可读单位
            sent_formatted = format_bytes(data['net_sent'])
            recv_formatted = format_bytes(data['net_recv'])
            net_sent_label.set_text(f"^ {sent_formatted}/s")
            net_recv_label.set_text(f"v {recv_formatted}/s")
            
            # 更新统计信息 - 显示当前Updates和最高值
            stats_label.set_text(f"{update_count:05d}")
            max_label.set_text(f"C-{max_cpu:.0f}% M-{max_memory:.0f}%")
            
            # 计算平均值（每更新100次计算一次）
            if update_count % 100 == 0:
                avg_cpu = cpu_sum / 100
                avg_mem = mem_sum / 100
                avg_label.set_text(f"C-{avg_cpu:.0f}% M-{avg_mem:.0f}%")
                # 计算性能评分
                score = get_performance_score(avg_cpu, avg_mem)
                performance_label.set_text(f"{score}")
                # 重置累计值
                cpu_sum = 0
                mem_sum = 0
            
            # 指示灯动画效果（每5次闪烁一次）
            if update_count % 5 == 0:
                indicator_state = 1 - indicator_state
                color_key = 'indicator_on' if indicator_state == 0 else 'indicator_off'
                status_indicator.set_style_text_color(lv.color_hex(THEME[color_key]), 0)
            
            lv.refr_now()  # 强制刷新屏幕
            print(f"Updated: {line}")  # 调试输出
    except Exception as e:
        print(f"Error parsing data: {e}")
    time.sleep(0.1)