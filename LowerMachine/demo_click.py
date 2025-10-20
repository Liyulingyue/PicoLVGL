import machine
import usys as sys
sys.path.append('') # See: https://github.com/micropython/micropython/issues/6419

import lvgl as lv
import lv_utils
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

# 按钮点击事件回调函数
def btn_event_cb(event):
    if event.get_code() == lv.EVENT.CLICKED:
        # 通过串口发送消息
        uart.write("Button clicked at {}\n".format(time.ticks_ms()))
        print("Button clicked - message sent via UART")

if not lv_utils.event_loop.is_running():
    drv = driver()
    drv.init_gui()

    scr = lv.obj()
    btn = lv.btn(scr)
    btn.align(lv.ALIGN.CENTER, 0, 0)
    btn.add_event_cb(btn_event_cb, lv.EVENT.CLICKED, None)  # 添加点击事件回调
    
    label = lv.label(btn)
    label.set_text('Click Me!')
    lv.scr_load(scr)

