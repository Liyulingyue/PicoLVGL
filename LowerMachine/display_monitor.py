"""
系统监控显示程序 - 重构版
支持多页面切换，触摸屏交互
"""
import machine
import usys as sys
sys.path.append('')

import lvgl as lv
import lv_utils
import ujson
import time

# 导入自定义模块
from page_monitor import MonitorPage
from page_clock import ClockPage  # 第三步：解除时钟页面导入
from page_manager import PageManager

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

# 初始化驱动
if not lv_utils.event_loop.is_running():
    drv = driver()
    drv.init_gui()

# === 初始化页面系统 ===
page_manager = PageManager()

# 创建并添加监控页面
monitor_page = MonitorPage()
page_manager.add_page(monitor_page)

# 创建并添加时钟页面
clock_page = ClockPage()
page_manager.add_page(clock_page)

# 加载第一个页面
page_manager.load_current_page()

# 主循环 - 读取UART数据并更新显示
while True:
    try:
        line = sys.stdin.readline().strip()
        if line:
            data = ujson.loads(line)
            
            # 更新当前页面
            page_manager.update_current_page(data)
            
            # 检查触摸并切换页面
            page_manager.check_touch_and_switch()
            
            # 刷新屏幕
            lv.refr_now()
            
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(0.1)
