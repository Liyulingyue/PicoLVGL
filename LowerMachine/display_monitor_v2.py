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
    'border': 0x1a2847,          # 边框颜色
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
    'container_padding': 15,
    'label_spacing_y': 35,       # 标签垂直间距
    'bar_offset_y': 15,          # 进度条相对标签偏移
    'warn_offset_x': 400,        # 警告标记位置
}

scr = lv.obj()
scr.set_style_bg_color(lv.color_hex(THEME['bg_primary']), 0)

# 辅助函数：创建标签
def create_label(parent, x, y, text, color_key):
    """创建并配置标签的辅助函数"""
    label = lv.label(parent)
    label.set_pos(x, y)
    label.set_text(text)
    label.set_style_text_color(lv.color_hex(THEME[color_key]), 0)
    return label

# 创建标题容器
header = lv.obj(scr)
header.set_size(480, LAYOUT['header_height'])
header.set_pos(0, 0)
header.set_style_bg_color(lv.color_hex(THEME['bg_header']), 0)
header.set_style_border_width(0, 0)

title_label = lv.label(header)
title_label.set_text("SYSTEM MONITOR")
title_label.set_style_text_color(lv.color_hex(THEME['text_title']), 0)
title_label.align(lv.ALIGN.CENTER, 0, 0)

status_indicator = create_label(header, 450, 12, "●", 'indicator_on')

# 创建信息容器
info_container = lv.obj(scr)
info_container.set_size(460, 270)
info_container.set_pos(10, 50)
info_container.set_style_bg_color(lv.color_hex(THEME['bg_secondary']), 0)
info_container.set_style_border_width(1, 0)
info_container.set_style_border_color(lv.color_hex(THEME['border']), 0)
info_container.set_style_pad_all(LAYOUT['container_padding'], 0)

# 时间信息区域
time_label = create_label(info_container, 10, 10, "Time: Loading...", 'text_time')
time_detail = create_label(info_container, 250, 10, "", 'text_time_dim')

# CPU 信息区域
y_cpu = 45
cpu_label = create_label(info_container, 10, y_cpu, "CPU: Loading...", 'text_cpu')
cpu_warn = create_label(info_container, LAYOUT['warn_offset_x'], y_cpu, "", 'text_cpu')
cpu_bar_label = create_label(info_container, 10, y_cpu + LAYOUT['bar_offset_y'], "[==========]", 'text_cpu')

# 内存信息区域
y_mem = y_cpu + LAYOUT['label_spacing_y'] + 15
memory_label = create_label(info_container, 10, y_mem, "Memory: Loading...", 'text_memory')
mem_warn = create_label(info_container, LAYOUT['warn_offset_x'], y_mem, "", 'text_memory')
mem_bar_label = create_label(info_container, 10, y_mem + LAYOUT['bar_offset_y'], "[==========]", 'text_memory')

# 进程信息
y_proc = y_mem + LAYOUT['label_spacing_y'] + 15
process_label = create_label(info_container, 10, y_proc, "Processes: Loading...", 'text_process')

# 网络信息区域
y_net = y_proc + LAYOUT['label_spacing_y']
net_label = create_label(info_container, 10, y_net, "Network:", 'text_network')
net_sent_label = create_label(info_container, 10, y_net + 20, "  Sent: Loading...", 'text_network')
net_recv_label = create_label(info_container, 240, y_net + 20, "Recv: Loading...", 'text_network')

# 底部统计信息区域
y_stats = y_net + 60
stats_label = create_label(info_container, 10, y_stats, "Updates: 0", 'text_stats')
max_label = create_label(info_container, 240, y_stats, "Max: C-0% M-0%", 'text_max')
avg_label = create_label(info_container, 10, y_stats + 20, "Avg: C-0% M-0%", 'text_avg')
performance_label = create_label(info_container, 240, y_stats + 20, "Score: A", 'text_score')

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
            time_label.set_text(f"Time: {time_str[:10]}")
            time_detail.set_text(f"{time_str[11:]}")
            
            # 更新CPU和进度条
            cpu_val = data['cpu']
            cpu_sum += cpu_val  # 累计用于平均值计算
            if cpu_val > max_cpu:
                max_cpu = cpu_val
            cpu_label.set_text(f"CPU: {cpu_val:.1f}%")
            cpu_bar_label.set_text(make_bar(cpu_val))
            cpu_warn.set_text(get_warn_indicator(cpu_val))
            
            # 更新内存和进度条
            mem_val = data['memory']
            mem_sum += mem_val  # 累计用于平均值计算
            if mem_val > max_memory:
                max_memory = mem_val
            memory_label.set_text(f"Memory: {mem_val:.1f}%")
            mem_bar_label.set_text(make_bar(mem_val))
            mem_warn.set_text(get_warn_indicator(mem_val))
            
            process_label.set_text(f"Processes: {data['processes']}")
            
            # 更新网络信息，转换为可读单位
            sent_formatted = format_bytes(data['net_sent'])
            recv_formatted = format_bytes(data['net_recv'])
            net_sent_label.set_text(f"  Sent: {sent_formatted}")
            net_recv_label.set_text(f"Recv: {recv_formatted}")
            
            # 更新统计信息 - 显示当前Updates和最高值
            stats_label.set_text(f"Updates: {update_count:05d}")
            max_label.set_text(f"Max: C-{max_cpu:.0f}% M-{max_memory:.0f}%")
            
            # 计算平均值（每更新100次计算一次）
            if update_count % 100 == 0:
                avg_cpu = cpu_sum / 100
                avg_mem = mem_sum / 100
                avg_label.set_text(f"Avg: C-{avg_cpu:.0f}% M-{avg_mem:.0f}%")
                # 计算性能评分
                score = get_performance_score(avg_cpu, avg_mem)
                performance_label.set_text(f"Score: {score}")
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