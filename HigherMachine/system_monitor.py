import serial
import psutil
import datetime
import time
import json

# 配置串行通信参数
com_port = 'COM31'  # 根据实际端口修改
baud_rate = 115200

# 打开串行端口
try:
    ser = serial.Serial(com_port, baud_rate, timeout=1)
    print(f"Opened {com_port} successfully.")
except serial.SerialException as e:
    print(f"Failed to open {com_port}: {e}")
    exit(1)

# 初始化网络计数器和CPU监控
last_net_io = psutil.net_io_counters()
last_time = time.time()
# 首次调用CPU监控，初始化基准
psutil.cpu_percent(interval=None)

def get_system_info():
    global last_net_io, last_time
    
    # 先记录开始时间
    start_time = time.time()
    
    # 获取当前时间
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 获取CPU利用率（非阻塞模式）
    cpu_percent = psutil.cpu_percent(interval=None)

    # 获取内存利用率
    memory = psutil.virtual_memory()
    memory_percent = memory.percent

    # 获取进程数
    process_count = len(psutil.pids())

    # 计算网络速率（每秒字节数）
    current_net_io = psutil.net_io_counters()
    time_delta = start_time - last_time
    
    if time_delta > 0:
        bytes_sent_rate = int((current_net_io.bytes_sent - last_net_io.bytes_sent) / time_delta)
        bytes_recv_rate = int((current_net_io.bytes_recv - last_net_io.bytes_recv) / time_delta)
    else:
        bytes_sent_rate = 0
        bytes_recv_rate = 0
    
    # 更新上次记录
    last_net_io = current_net_io
    last_time = start_time

    data = {
        "time": current_time,
        "cpu": cpu_percent,
        "memory": memory_percent,
        "processes": process_count,
        "net_sent": bytes_sent_rate,
        "net_recv": bytes_recv_rate
    }

    return json.dumps(data)

try:
    while True:
        info = get_system_info()
        ser.write((info + '\n').encode('utf-8'))
        print(f"Sent: {info}")
        time.sleep(5)  # 每5秒发送一次
except KeyboardInterrupt:
    print("Closing serial port...")
finally:
    ser.close()
    print("Serial port closed.")