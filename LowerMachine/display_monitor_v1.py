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

scr = lv.obj()

# 创建标签显示信息
time_label = lv.label(scr)
time_label.set_pos(10, 10)
time_label.set_text("Time: Loading...")

cpu_label = lv.label(scr)
cpu_label.set_pos(10, 40)
cpu_label.set_text("CPU: Loading...")

memory_label = lv.label(scr)
memory_label.set_pos(10, 70)
memory_label.set_text("Memory: Loading...")

process_label = lv.label(scr)
process_label.set_pos(10, 100)
process_label.set_text("Processes: Loading...")

net_label = lv.label(scr)
net_label.set_pos(10, 130)
net_label.set_text("Network: Loading...")

lv.scr_load(scr)

# 循环读取UART数据并更新显示
while True:
    try:
        line = sys.stdin.readline().strip()
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