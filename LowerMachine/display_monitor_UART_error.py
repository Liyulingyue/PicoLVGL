# 失败了，似乎通过UART接收上位机数据没办法成功，但是可以通过UART发送数据成功

import machine
import usys as sys
sys.path.append('') # See: https://github.com/micropython/micropython/issues/6419

import lvgl as lv
import lv_utils
import ujson
from machine import UART
import time

lv.init()

# 初始化串口 (使用USB CDC虚拟串口，在大多数Pico板上)
uart = UART(0, baudrate=115200, tx=machine.Pin(0), rx=machine.Pin(1))

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

scr = lv.obj()

# 设置背景颜色为深色
scr.set_style_bg_color(lv.color_hex(0x1a1a2e), lv.PART.MAIN)

# 创建标题
title = lv.label(scr)
title.set_pos(10, 10)
title.set_text("System Monitor")
title.set_style_text_font(lv.font_large, lv.PART.MAIN)
title.set_style_text_color(lv.color_hex(0x00d4ff), lv.PART.MAIN)

# 创建分割线
line = lv.obj(scr)
line.set_size(460, 2)
line.set_pos(10, 40)
line.set_style_bg_color(lv.color_hex(0x00d4ff), lv.PART.MAIN)
line.set_style_border_width(0, lv.PART.MAIN)

# 时间显示
time_label = lv.label(scr)
time_label.set_pos(10, 55)
time_label.set_style_text_color(lv.color_hex(0xffffff), lv.PART.MAIN)
time_label.set_style_text_font(lv.font_default, lv.PART.MAIN)
time_label.set_text("Time: Loading...")

# CPU显示 - 添加背景容器
cpu_container = lv.obj(scr)
cpu_container.set_size(220, 60)
cpu_container.set_pos(10, 90)
cpu_container.set_style_bg_color(lv.color_hex(0x0f3460), lv.PART.MAIN)
cpu_container.set_style_border_color(lv.color_hex(0x00d4ff), lv.PART.MAIN)
cpu_container.set_style_border_width(2, lv.PART.MAIN)
cpu_container.set_style_radius(8, lv.PART.MAIN)

cpu_label = lv.label(cpu_container)
cpu_label.set_pos(10, 8)
cpu_label.set_style_text_color(lv.color_hex(0x00d4ff), lv.PART.MAIN)
cpu_label.set_text("CPU Usage")

cpu_value = lv.label(cpu_container)
cpu_value.set_pos(10, 30)
cpu_value.set_style_text_color(lv.color_hex(0xffffff), lv.PART.MAIN)
cpu_value.set_style_text_font(lv.font_large, lv.PART.MAIN)
cpu_value.set_text("0.0%")

# 内存显示 - 添加背景容器
mem_container = lv.obj(scr)
mem_container.set_size(220, 60)
mem_container.set_pos(240, 90)
mem_container.set_style_bg_color(lv.color_hex(0x0f3460), lv.PART.MAIN)
mem_container.set_style_border_color(lv.color_hex(0x00d4ff), lv.PART.MAIN)
mem_container.set_style_border_width(2, lv.PART.MAIN)
mem_container.set_style_radius(8, lv.PART.MAIN)

mem_label = lv.label(mem_container)
mem_label.set_pos(10, 8)
mem_label.set_style_text_color(lv.color_hex(0x00d4ff), lv.PART.MAIN)
mem_label.set_text("Memory Usage")

mem_value = lv.label(mem_container)
mem_value.set_pos(10, 30)
mem_value.set_style_text_color(lv.color_hex(0xffffff), lv.PART.MAIN)
mem_value.set_style_text_font(lv.font_large, lv.PART.MAIN)
mem_value.set_text("0.0%")

# 进程显示 - 添加背景容器
process_container = lv.obj(scr)
process_container.set_size(220, 60)
process_container.set_pos(10, 170)
process_container.set_style_bg_color(lv.color_hex(0x0f3460), lv.PART.MAIN)
process_container.set_style_border_color(lv.color_hex(0x00d4ff), lv.PART.MAIN)
process_container.set_style_border_width(2, lv.PART.MAIN)
process_container.set_style_radius(8, lv.PART.MAIN)

process_label = lv.label(process_container)
process_label.set_pos(10, 8)
process_label.set_style_text_color(lv.color_hex(0x00d4ff), lv.PART.MAIN)
process_label.set_text("Processes")

process_value = lv.label(process_container)
process_value.set_pos(10, 30)
process_value.set_style_text_color(lv.color_hex(0xffffff), lv.PART.MAIN)
process_value.set_style_text_font(lv.font_large, lv.PART.MAIN)
process_value.set_text("0")

# 网络显示 - 添加背景容器
net_container = lv.obj(scr)
net_container.set_size(220, 60)
net_container.set_pos(240, 170)
net_container.set_style_bg_color(lv.color_hex(0x0f3460), lv.PART.MAIN)
net_container.set_style_border_color(lv.color_hex(0x00d4ff), lv.PART.MAIN)
net_container.set_style_border_width(2, lv.PART.MAIN)
net_container.set_style_radius(8, lv.PART.MAIN)

net_label = lv.label(net_container)
net_label.set_pos(10, 8)
net_label.set_style_text_color(lv.color_hex(0x00d4ff), lv.PART.MAIN)
net_label.set_text("Network Traffic")

net_value = lv.label(net_container)
net_value.set_pos(10, 30)
net_value.set_style_text_color(lv.color_hex(0xffffff), lv.PART.MAIN)
net_value.set_text("S:0 R:0")

lv.scr_load(scr)

# 循环读取UART数据并更新显示
while True:
    if uart.any():
        try:
            line = uart.readline().decode('utf-8').strip()
            if line:
                data = ujson.loads(line)
                time_label.set_text(f"Time: {data['time']}")
                cpu_label.set_text(f"CPU: {data['cpu']:.1f}%")
                memory_label.set_text(f"Memory: {data['memory']:.1f}%")
                process_label.set_text(f"Processes: {data['processes']}")
                net_label.set_text(f"Net Sent: {data['net_sent']} Recv: {data['net_recv']}")
                lv.refr_now()  # 强制刷新屏幕
                print(f"Updated: {line}")  # 调试输出
        except Exception as e:
            print(f"Error parsing data: {e}")
    time.sleep(0.1)
