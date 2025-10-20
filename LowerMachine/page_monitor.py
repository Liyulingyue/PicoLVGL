"""
系统监控页面
"""
import lvgl as lv
from config import THEME, LAYOUT, SCREEN
from ui_components import (create_label, create_card, make_bar, 
                          format_bytes, get_warn_indicator, get_performance_score)

class MonitorPage:
    """系统监控页面类"""
    
    def __init__(self):
        """初始化监控页面"""
        self.scr = lv.obj()
        self.scr.set_style_bg_color(lv.color_hex(THEME['bg_primary']), 0)
        
        # 统计变量
        self.update_count = 0
        self.max_cpu = 0
        self.max_memory = 0
        self.cpu_sum = 0
        self.mem_sum = 0
        self.indicator_state = 0
        
        self._create_ui()
    
    def _create_ui(self):
        """创建UI元素"""
        # 标题和状态指示灯
        self.title_label = create_label(self.scr, 10, 8, "SYSTEM MONITOR", 'text_title')
        self.status_indicator = create_label(self.scr, 460, 8, "●", 'indicator_on')
        
        # 主容器
        main_container = lv.obj(self.scr)
        main_container.set_size(SCREEN['width'], 295)
        main_container.set_pos(0, 25)
        main_container.set_style_bg_color(lv.color_hex(THEME['bg_primary']), 0)
        main_container.set_style_border_width(0, 0)
        main_container.set_style_pad_all(LAYOUT['container_padding'], 0)
        main_container.add_flag(lv.obj.FLAG.EVENT_BUBBLE)  # 允许事件穿透
        
        # 卡片1：性能监控区域 (CPU + Memory)
        card_performance = create_card(main_container, 10, 0, 220, 140)
        card_performance.add_flag(lv.obj.FLAG.EVENT_BUBBLE)  # 允许事件穿透
        
        # 卡片2：系统信息区域 (Time + Process)
        card_system = create_card(main_container, 240, 0, 220, 140)
        card_system.add_flag(lv.obj.FLAG.EVENT_BUBBLE)  # 允许事件穿透
        
        # 卡片3：网络和统计区域
        card_network = create_card(main_container, 10, 150, 450, 110)
        card_network.add_flag(lv.obj.FLAG.EVENT_BUBBLE)  # 允许事件穿透
        
        # === 卡片1内容：性能监控 ===
        # CPU 信息
        cpu_icon = create_label(card_performance, 5, 5, "[C]", 'text_cpu')
        cpu_label = create_label(card_performance, 30, 5, "CPU", 'text_cpu')
        self.cpu_value = create_label(card_performance, 145, 5, "0.0%", 'text_cpu')
        self.cpu_warn = create_label(card_performance, 195, 5, "", 'text_cpu')
        self.cpu_bar_label = create_label(card_performance, 30, 22, "[==========]", 'text_cpu')
        
        # 内存信息
        mem_icon = create_label(card_performance, 5, 70, "[M]", 'text_memory')
        memory_label = create_label(card_performance, 30, 70, "Memory", 'text_memory')
        self.memory_value = create_label(card_performance, 145, 70, "0.0%", 'text_memory')
        self.mem_warn = create_label(card_performance, 195, 70, "", 'text_memory')
        self.mem_bar_label = create_label(card_performance, 30, 87, "[==========]", 'text_memory')
        
        # === 卡片2内容：系统信息 ===
        # 时间信息
        time_icon = create_label(card_system, 5, 5, "[T]", 'text_time')
        time_label = create_label(card_system, 30, 5, "Time", 'text_time')
        self.time_value = create_label(card_system, 30, 22, "Loading...", 'text_time_dim')
        self.time_detail = create_label(card_system, 30, 37, "", 'text_time')
        
        # 进程信息
        proc_icon = create_label(card_system, 5, 70, "[P]", 'text_process')
        process_label = create_label(card_system, 30, 70, "Processes", 'text_process')
        self.process_value = create_label(card_system, 30, 87, "0", 'text_process')
        
        # === 卡片3内容：网络和统计 ===
        # 网络信息
        net_icon = create_label(card_network, 5, 5, "[N]", 'text_network')
        net_label = create_label(card_network, 30, 5, "Network", 'text_network')
        self.net_sent_label = create_label(card_network, 30, 22, "^ 0B", 'text_network')
        self.net_recv_label = create_label(card_network, 160, 22, "v 0B", 'text_network')
        
        # 统计信息 - 左列
        stats_icon = create_label(card_network, 5, 50, "[#]", 'text_stats')
        self.stats_label = create_label(card_network, 30, 50, "00000", 'text_stats')
        self.avg_label = create_label(card_network, 30, 67, "C-0% M-0%", 'text_avg')
        
        # 统计信息 - 右列
        max_icon = create_label(card_network, 240, 50, "MAX", 'text_max')
        self.max_label = create_label(card_network, 270, 50, "C-0% M-0%", 'text_max')
        perf_icon = create_label(card_network, 240, 67, "Score", 'text_score')
        self.performance_label = create_label(card_network, 280, 67, "A", 'text_score')
    
    def update(self, data):
        """更新页面数据"""
        self.update_count = (self.update_count + 1) % 10000
        
        # 更新时间
        time_str = data['time']
        self.time_value.set_text(f"{time_str[:10]}")
        self.time_detail.set_text(f"{time_str[11:]}")
        
        # 更新CPU
        cpu_val = data['cpu']
        self.cpu_sum += cpu_val
        if cpu_val > self.max_cpu:
            self.max_cpu = cpu_val
        self.cpu_value.set_text(f"{cpu_val:.1f}%")
        self.cpu_bar_label.set_text(make_bar(cpu_val))
        self.cpu_warn.set_text(get_warn_indicator(cpu_val))
        
        # 更新内存
        mem_val = data['memory']
        self.mem_sum += mem_val
        if mem_val > self.max_memory:
            self.max_memory = mem_val
        self.memory_value.set_text(f"{mem_val:.1f}%")
        self.mem_bar_label.set_text(make_bar(mem_val))
        self.mem_warn.set_text(get_warn_indicator(mem_val))
        
        # 更新进程
        self.process_value.set_text(f"{data['processes']}")
        
        # 更新网络
        sent_formatted = format_bytes(data['net_sent'])
        recv_formatted = format_bytes(data['net_recv'])
        self.net_sent_label.set_text(f"^ {sent_formatted}/s")
        self.net_recv_label.set_text(f"v {recv_formatted}/s")
        
        # 更新统计信息
        self.stats_label.set_text(f"{self.update_count:05d}")
        self.max_label.set_text(f"C-{self.max_cpu:.0f}% M-{self.max_memory:.0f}%")
        
        # 每100次计算平均值
        if self.update_count % 100 == 0:
            avg_cpu = self.cpu_sum / 100
            avg_mem = self.mem_sum / 100
            self.avg_label.set_text(f"C-{avg_cpu:.0f}% M-{avg_mem:.0f}%")
            score = get_performance_score(avg_cpu, avg_mem)
            self.performance_label.set_text(f"{score}")
            self.cpu_sum = 0
            self.mem_sum = 0
        
        # 指示灯闪烁
        if self.update_count % 5 == 0:
            self.indicator_state = 1 - self.indicator_state
            color_key = 'indicator_on' if self.indicator_state == 0 else 'indicator_off'
            self.status_indicator.set_style_text_color(lv.color_hex(THEME[color_key]), 0)
    
    def get_screen(self):
        """返回屏幕对象"""
        return self.scr
