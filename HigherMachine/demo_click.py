import serial
import time

# 配置串行通信参数  
com_port = 'COM31'  # Windows上的COM端口号，Linux/macOS上可能是'/dev/ttyUSB0'或类似
baud_rate = 115200  # 波特率，根据您的需要设置  

# 打开串行端口  
try:
    ser = serial.Serial(com_port, baud_rate, timeout=1)  # timeout是读取超时时间，单位是秒  
    print(f"Opened {com_port} successfully.")
except serial.SerialException as e:
    print(f"Failed to open {com_port}: {e}")
    exit(1)

# 读取数据的循环  
try:
    while True:
        # 检查是否有数据可读  
        if ser.in_waiting > 0:
            # 读取一行数据（假设数据是以换行符分隔的）  
            line = ser.readline().decode('utf-8').strip()  # decode将字节转换为字符串，strip去除末尾的换行符  
            print(f"Received data: {line}")

            # 如果没有数据可读，稍作等待以避免CPU占用过高
        time.sleep(0.1)  # 等待0.1秒  
except KeyboardInterrupt:
    # 如果用户按下Ctrl+C终止程序，关闭串行端口  
    print("Closing serial port...")
finally:
    ser.close()
    print("Serial port closed.")