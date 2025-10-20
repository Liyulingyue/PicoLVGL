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
    'btn_active': 0x00d4ff,      # 激活按钮
    'btn_inactive': 0x2a3850,    # 未激活按钮
}

# UI布局配置
LAYOUT = {
    'header_height': 35,
    'navbar_height': 45,
    'container_padding': 10,
    'card_padding': 8,
    'card_spacing': 8,
    'label_spacing_y': 35,
    'bar_offset_y': 15,
    'warn_offset_x': 400,
}

############################################################################################
# 全局数据存储
system_data = {
    'time': 'Loading...',
    'cpu': 0.0,
    'memory': 0.0,
    'processes': 0,
    'net_sent': 0,
    'net_recv': 0,
}

# 统计数据
stats_data = {
    'update_count': 0,
    'max_cpu': 0,
    'max_memory': 0,
    'cpu_sum': 0,
    'mem_sum': 0,
    'avg_cpu': 0,
    'avg_mem': 0,
    'score': 'A',
    'cpu_history': [],  # 最近20个CPU数据点
    'mem_history': [],  # 最近20个内存数据点
}

# 当前页面索引
current_page = 0

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
    card.set_style_radius(4, 0)
    return card

# 生成进度条显示函数
def make_bar(percent):
    """生成文本进度条，percent为0-100"""
    if percent < 0:
        percent = 0
    elif percent > 100:
        percent = 100
    filled = int(percent / 10)
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
        return "!"
    elif percent >= 60:
        return "*"
    else:
        return ""

# 计算性能评分
def get_performance_score(avg_cpu, avg_mem):
    """根据平均CPU和内存计算性能评分"""
    avg_usage = (avg_cpu + avg_mem) / 2
    if avg_usage < 30:
        return "A"
    elif avg_usage < 50:
        return "B"
    elif avg_usage < 70:
        return "C"
    elif avg_usage < 85:
        return "D"
    else:
        return "F"

############################################################################################
# 主屏幕
scr = lv.obj()
scr.set_style_bg_color(lv.color_hex(THEME['bg_primary']), 0)

# 标题栏
title_label = create_label(scr, 10, 8, "SYSTEM MONITOR", 'text_title')
status_indicator = create_label(scr, 460, 8, "●", 'indicator_on')

# 创建页面容器（用于存放不同页面）
page_container = lv.obj(scr)
page_container.set_size(480, 240)
page_container.set_pos(0, LAYOUT['header_height'])
page_container.set_style_bg_color(lv.color_hex(THEME['bg_primary']), 0)
page_container.set_style_border_width(0, 0)
page_container.set_style_pad_all(0, 0)

############################################################################################
# 页面1：概览页（原来的主页面）
page1 = lv.obj(page_container)
page1.set_size(480, 240)
page1.set_pos(0, 0)
page1.set_style_bg_color(lv.color_hex(THEME['bg_primary']), 0)
page1.set_style_border_width(0, 0)
page1.set_style_pad_all(LAYOUT['container_padding'], 0)

# 卡片1：性能监控
card1_perf = create_card(page1, 10, 0, 220, 110)
cpu_icon_p1 = create_label(card1_perf, 5, 5, "[C]", 'text_cpu')
cpu_label_p1 = create_label(card1_perf, 30, 5, "CPU", 'text_cpu')
cpu_value_p1 = create_label(card1_perf, 145, 5, "0.0%", 'text_cpu')
cpu_warn_p1 = create_label(card1_perf, 195, 5, "", 'text_cpu')
cpu_bar_p1 = create_label(card1_perf, 30, 22, "[==========]", 'text_cpu')

mem_icon_p1 = create_label(card1_perf, 5, 60, "[M]", 'text_memory')
mem_label_p1 = create_label(card1_perf, 30, 60, "Memory", 'text_memory')
mem_value_p1 = create_label(card1_perf, 145, 60, "0.0%", 'text_memory')
mem_warn_p1 = create_label(card1_perf, 195, 60, "", 'text_memory')
mem_bar_p1 = create_label(card1_perf, 30, 77, "[==========]", 'text_memory')

# 卡片2：系统信息
card2_sys = create_card(page1, 240, 0, 220, 110)
time_icon_p1 = create_label(card2_sys, 5, 5, "[T]", 'text_time')
time_label_p1 = create_label(card2_sys, 30, 5, "Time", 'text_time')
time_value_p1 = create_label(card2_sys, 30, 22, "Loading...", 'text_time_dim')
time_detail_p1 = create_label(card2_sys, 30, 37, "", 'text_time')

proc_icon_p1 = create_label(card2_sys, 5, 60, "[P]", 'text_process')
proc_label_p1 = create_label(card2_sys, 30, 60, "Processes", 'text_process')
proc_value_p1 = create_label(card2_sys, 30, 77, "0", 'text_process')

# 卡片3：网络和统计
card3_net = create_card(page1, 10, 120, 450, 100)
net_icon_p1 = create_label(card3_net, 5, 5, "[N]", 'text_network')
net_label_p1 = create_label(card3_net, 30, 5, "Network", 'text_network')
net_sent_p1 = create_label(card3_net, 30, 22, "^ 0B/s", 'text_network')
net_recv_p1 = create_label(card3_net, 160, 22, "v 0B/s", 'text_network')

stats_icon_p1 = create_label(card3_net, 5, 50, "[#]", 'text_stats')
stats_label_p1 = create_label(card3_net, 30, 50, "00000", 'text_stats')
avg_label_p1 = create_label(card3_net, 30, 67, "C-0% M-0%", 'text_avg')

max_icon_p1 = create_label(card3_net, 240, 50, "MAX", 'text_max')
max_label_p1 = create_label(card3_net, 270, 50, "C-0% M-0%", 'text_max')
perf_icon_p1 = create_label(card3_net, 240, 67, "Score", 'text_score')
perf_label_p1 = create_label(card3_net, 280, 67, "A", 'text_score')

############################################################################################
# 页面2：详细信息页
page2 = lv.obj(page_container)
page2.set_size(480, 240)
page2.set_pos(0, 0)
page2.set_style_bg_color(lv.color_hex(THEME['bg_primary']), 0)
page2.set_style_border_width(0, 0)
page2.set_style_pad_all(LAYOUT['container_padding'], 0)
page2.add_flag(lv.obj.FLAG.HIDDEN)  # 初始隐藏

# 详细信息卡片
detail_card = create_card(page2, 10, 0, 450, 220)
detail_title = create_label(detail_card, 10, 5, "DETAILED STATISTICS", 'text_title')

# CPU详细信息
cpu_detail_label = create_label(detail_card, 10, 30, "CPU Information", 'text_cpu')
cpu_current_p2 = create_label(detail_card, 10, 50, "Current: 0.0%", 'text_stats')
cpu_max_p2 = create_label(detail_card, 10, 65, "Max: 0.0%", 'text_max')
cpu_avg_p2 = create_label(detail_card, 10, 80, "Avg: 0.0%", 'text_avg')

# 内存详细信息
mem_detail_label = create_label(detail_card, 240, 30, "Memory Information", 'text_memory')
mem_current_p2 = create_label(detail_card, 240, 50, "Current: 0.0%", 'text_stats')
mem_max_p2 = create_label(detail_card, 240, 65, "Max: 0.0%", 'text_max')
mem_avg_p2 = create_label(detail_card, 240, 80, "Avg: 0.0%", 'text_avg')

# 网络详细信息
net_detail_label = create_label(detail_card, 10, 110, "Network Information", 'text_network')
net_sent_p2 = create_label(detail_card, 10, 130, "Upload: 0B/s", 'text_stats')
net_recv_p2 = create_label(detail_card, 10, 145, "Download: 0B/s", 'text_stats')

# 系统详细信息
sys_detail_label = create_label(detail_card, 240, 110, "System Information", 'text_process')
sys_proc_p2 = create_label(detail_card, 240, 130, "Processes: 0", 'text_stats')
sys_updates_p2 = create_label(detail_card, 240, 145, "Updates: 00000", 'text_stats')
sys_score_p2 = create_label(detail_card, 240, 160, "Score: A", 'text_score')

############################################################################################
# 页面3：关于页
page3 = lv.obj(page_container)
page3.set_size(480, 240)
page3.set_pos(0, 0)
page3.set_style_bg_color(lv.color_hex(THEME['bg_primary']), 0)
page3.set_style_border_width(0, 0)
page3.set_style_pad_all(LAYOUT['container_padding'], 0)
page3.add_flag(lv.obj.FLAG.HIDDEN)  # 初始隐藏

# 关于信息卡片
about_card = create_card(page3, 10, 0, 450, 220)
about_title = create_label(about_card, 10, 10, "SYSTEM MONITOR v2.0", 'text_title')

about_info1 = create_label(about_card, 10, 40, "Platform: Raspberry Pi Pico", 'text_stats')
about_info2 = create_label(about_card, 10, 60, "Display: ili9488 (480x320)", 'text_stats')
about_info3 = create_label(about_card, 10, 80, "Touch: ft6236", 'text_stats')
about_info4 = create_label(about_card, 10, 100, "LVGL Version: 8.3", 'text_stats')
about_info5 = create_label(about_card, 10, 120, "CPU Freq: 240 MHz", 'text_stats')

about_hint = create_label(about_card, 10, 160, "Tap navigation buttons below", 'text_time_dim')
about_hint2 = create_label(about_card, 10, 180, "to switch pages", 'text_time_dim')

############################################################################################
# 底部导航栏
navbar = lv.obj(scr)
navbar.set_size(480, LAYOUT['navbar_height'])
navbar.set_pos(0, 320 - LAYOUT['navbar_height'])
navbar.set_style_bg_color(lv.color_hex(THEME['bg_header']), 0)
navbar.set_style_border_width(0, 0)
navbar.set_style_pad_all(5, 0)

# 导航按钮事件处理
def nav_btn_clicked(event):
    global current_page
    btn = event.get_target()
    btn_index = btn.get_user_data()
    
    if btn_index == current_page:
        return  # 已经在当前页面
    
    # 隐藏所有页面
    page1.add_flag(lv.obj.FLAG.HIDDEN)
    page2.add_flag(lv.obj.FLAG.HIDDEN)
    page3.add_flag(lv.obj.FLAG.HIDDEN)
    
    # 显示选中的页面
    if btn_index == 0:
        page1.clear_flag(lv.obj.FLAG.HIDDEN)
    elif btn_index == 1:
        page2.clear_flag(lv.obj.FLAG.HIDDEN)
    elif btn_index == 2:
        page3.clear_flag(lv.obj.FLAG.HIDDEN)
    
    # 更新按钮样式
    for i, b in enumerate([nav_btn1, nav_btn2, nav_btn3]):
        if i == btn_index:
            b.set_style_bg_color(lv.color_hex(THEME['btn_active']), 0)
        else:
            b.set_style_bg_color(lv.color_hex(THEME['btn_inactive']), 0)
    
    current_page = btn_index
    lv.refr_now()

# 创建导航按钮
def create_nav_button(parent, x, text, index):
    btn = lv.btn(parent)
    btn.set_size(150, 35)
    btn.set_pos(x, 5)
    btn.set_style_radius(5, 0)
    btn.set_user_data(index)
    btn.add_event_cb(nav_btn_clicked, lv.EVENT.CLICKED, None)
    
    if index == 0:
        btn.set_style_bg_color(lv.color_hex(THEME['btn_active']), 0)
    else:
        btn.set_style_bg_color(lv.color_hex(THEME['btn_inactive']), 0)
    
    label = lv.label(btn)
    label.set_text(text)
    label.set_style_text_color(lv.color_hex(0xffffff), 0)
    label.center()
    
    return btn

nav_btn1 = create_nav_button(navbar, 10, "[1] Overview", 0)
nav_btn2 = create_nav_button(navbar, 165, "[2] Details", 1)
nav_btn3 = create_nav_button(navbar, 320, "[3] About", 2)

lv.scr_load(scr)

############################################################################################
# 更新UI函数
def update_page1():
    """更新页面1的显示"""
    # CPU
    cpu_val = system_data['cpu']
    cpu_value_p1.set_text(f"{cpu_val:.1f}%")
    cpu_bar_p1.set_text(make_bar(cpu_val))
    cpu_warn_p1.set_text(get_warn_indicator(cpu_val))
    
    # 内存
    mem_val = system_data['memory']
    mem_value_p1.set_text(f"{mem_val:.1f}%")
    mem_bar_p1.set_text(make_bar(mem_val))
    mem_warn_p1.set_text(get_warn_indicator(mem_val))
    
    # 时间
    time_str = system_data['time']
    time_value_p1.set_text(f"{time_str[:10]}")
    time_detail_p1.set_text(f"{time_str[11:]}")
    
    # 进程
    proc_value_p1.set_text(f"{system_data['processes']}")
    
    # 网络
    sent_formatted = format_bytes(system_data['net_sent'])
    recv_formatted = format_bytes(system_data['net_recv'])
    net_sent_p1.set_text(f"^ {sent_formatted}/s")
    net_recv_p1.set_text(f"v {recv_formatted}/s")
    
    # 统计
    stats_label_p1.set_text(f"{stats_data['update_count']:05d}")
    max_label_p1.set_text(f"C-{stats_data['max_cpu']:.0f}% M-{stats_data['max_memory']:.0f}%")
    avg_label_p1.set_text(f"C-{stats_data['avg_cpu']:.0f}% M-{stats_data['avg_mem']:.0f}%")
    perf_label_p1.set_text(f"{stats_data['score']}")

def update_page2():
    """更新页面2的显示"""
    # CPU详细
    cpu_current_p2.set_text(f"Current: {system_data['cpu']:.1f}%")
    cpu_max_p2.set_text(f"Max: {stats_data['max_cpu']:.1f}%")
    cpu_avg_p2.set_text(f"Avg: {stats_data['avg_cpu']:.1f}%")
    
    # 内存详细
    mem_current_p2.set_text(f"Current: {system_data['memory']:.1f}%")
    mem_max_p2.set_text(f"Max: {stats_data['max_memory']:.1f}%")
    mem_avg_p2.set_text(f"Avg: {stats_data['avg_mem']:.1f}%")
    
    # 网络详细
    sent_formatted = format_bytes(system_data['net_sent'])
    recv_formatted = format_bytes(system_data['net_recv'])
    net_sent_p2.set_text(f"Upload: {sent_formatted}/s")
    net_recv_p2.set_text(f"Download: {recv_formatted}/s")
    
    # 系统详细
    sys_proc_p2.set_text(f"Processes: {system_data['processes']}")
    sys_updates_p2.set_text(f"Updates: {stats_data['update_count']:05d}")
    sys_score_p2.set_text(f"Score: {stats_data['score']}")

############################################################################################
# 主循环
indicator_state = 0

while True:
    try:
        line = sys.stdin.readline().strip()
        if line:
            data = ujson.loads(line)
            
            # 更新系统数据
            system_data['time'] = data['time']
            system_data['cpu'] = data['cpu']
            system_data['memory'] = data['memory']
            system_data['processes'] = data['processes']
            system_data['net_sent'] = data['net_sent']
            system_data['net_recv'] = data['net_recv']
            
            # 更新统计数据
            stats_data['update_count'] = (stats_data['update_count'] + 1) % 10000
            stats_data['cpu_sum'] += data['cpu']
            stats_data['mem_sum'] += data['memory']
            
            if data['cpu'] > stats_data['max_cpu']:
                stats_data['max_cpu'] = data['cpu']
            if data['memory'] > stats_data['max_memory']:
                stats_data['max_memory'] = data['memory']
            
            # 计算平均值
            if stats_data['update_count'] % 100 == 0:
                stats_data['avg_cpu'] = stats_data['cpu_sum'] / 100
                stats_data['avg_mem'] = stats_data['mem_sum'] / 100
                stats_data['score'] = get_performance_score(stats_data['avg_cpu'], stats_data['avg_mem'])
                stats_data['cpu_sum'] = 0
                stats_data['mem_sum'] = 0
            
            # 更新当前显示的页面
            if current_page == 0:
                update_page1()
            elif current_page == 1:
                update_page2()
            # 页面3是静态的，不需要更新
            
            # 指示灯动画
            if stats_data['update_count'] % 5 == 0:
                indicator_state = 1 - indicator_state
                color_key = 'indicator_on' if indicator_state == 0 else 'indicator_off'
                status_indicator.set_style_text_color(lv.color_hex(THEME[color_key]), 0)
            
            lv.refr_now()
            print(f"Updated: {line}")
    except Exception as e:
        print(f"Error parsing data: {e}")
    time.sleep(0.1)
