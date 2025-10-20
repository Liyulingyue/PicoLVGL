"""
时间页面 - 大号显示当前时间，底部显示系统状态
"""
import lvgl as lv
from config import THEME, LAYOUT, SCREEN
from ui_components import create_label, format_bytes

class ClockPage:
    """时间页面类"""
    
    def __init__(self):
        """初始化时间页面"""
        self.scr = lv.obj()
        self.scr.set_style_bg_color(lv.color_hex(THEME['bg_primary']), 0)
        
        self._create_ui()
    
    def _create_ui(self):
        """创建UI元素"""
        # 标题
        self.title_label = create_label(self.scr, 10, 8, "CLOCK", 'text_title')
        
        # 主容器 - 时间显示区域
        time_container = lv.obj(self.scr)
        time_container.set_size(SCREEN['width'] - 20, 190)
        time_container.set_pos(10, 30)
        time_container.set_style_bg_color(lv.color_hex(THEME['bg_card']), 0)
        time_container.set_style_border_width(1, 0)
        time_container.set_style_border_color(lv.color_hex(THEME['divider']), 0)
        time_container.set_style_pad_all(10, 0)
        time_container.set_style_radius(8, 0)
        # 允许点击事件穿透
        time_container.add_flag(lv.obj.FLAG.EVENT_BUBBLE)
        
        # 大号时间显示 (HH:MM:SS) - 尝试使用最大的内置字体
        self.time_large = lv.label(time_container)
        self.time_large.set_text("00:00:00")
        self.time_large.set_style_text_color(lv.color_hex(THEME['text_time']), 0)
        self.time_large.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        
        # 尝试使用更大的字体
        try:
            # 尝试使用 montserrat 36 字体
            self.time_large.set_style_text_font(lv.font_montserrat_36, 0)
        except:
            try:
                # 如果36不存在，尝试28
                self.time_large.set_style_text_font(lv.font_montserrat_28, 0)
            except:
                # 如果都不存在，使用默认字体但增加字符间距
                pass
        
        self.time_large.set_size(440, 80)
        self.time_large.set_pos(10, 40)
        
        # 日期显示 - 居中，使用较大字体
        self.date_label = lv.label(time_container)
        self.date_label.set_text("0000-00-00")
        self.date_label.set_style_text_color(lv.color_hex(THEME['text_time_dim']), 0)
        self.date_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        
        # 尝试为日期使用较大字体
        try:
            self.date_label.set_style_text_font(lv.font_montserrat_20, 0)
        except:
            try:
                self.date_label.set_style_text_font(lv.font_montserrat_16, 0)
            except:
                pass
        
        self.date_label.set_size(440, 40)
        self.date_label.set_pos(10, 130)
        
        # 底部状态栏容器
        status_container = lv.obj(self.scr)
        status_container.set_size(SCREEN['width'] - 20, 70)
        status_container.set_pos(10, 230)
        status_container.set_style_bg_color(lv.color_hex(THEME['bg_card']), 0)
        status_container.set_style_border_width(1, 0)
        status_container.set_style_border_color(lv.color_hex(THEME['divider']), 0)
        status_container.set_style_pad_all(8, 0)
        status_container.set_style_radius(8, 0)
        # 允许点击事件穿透
        status_container.add_flag(lv.obj.FLAG.EVENT_BUBBLE)
        
        # 底部状态信息 - CPU
        cpu_icon = create_label(status_container, 5, 5, "CPU", 'text_cpu')
        self.cpu_status = create_label(status_container, 5, 25, "0.0%", 'text_cpu')
        
        # 底部状态信息 - Memory
        mem_icon = create_label(status_container, 100, 5, "MEM", 'text_memory')
        self.mem_status = create_label(status_container, 100, 25, "0.0%", 'text_memory')
        
        # 底部状态信息 - 网络上传
        net_up_icon = create_label(status_container, 200, 5, "UP", 'text_network')
        self.net_up_status = create_label(status_container, 200, 25, "0B/s", 'text_network')
        
        # 底部状态信息 - 网络下载
        net_down_icon = create_label(status_container, 320, 5, "DOWN", 'text_network')
        self.net_down_status = create_label(status_container, 320, 25, "0B/s", 'text_network')
    
    def update(self, data):
        """更新页面数据"""
        # 更新时间
        time_str = data['time']
        # 格式: "2024-10-20 14:30:45"
        date_part = time_str[:10]  # "2024-10-20"
        time_part = time_str[11:]  # "14:30:45"
        
        # 直接显示时间，不添加额外空格
        self.time_large.set_text(time_part)
        self.date_label.set_text(date_part)
        
        # 更新底部状态
        self.cpu_status.set_text(f"{data['cpu']:.1f}%")
        self.mem_status.set_text(f"{data['memory']:.1f}%")
        
        # 更新网络状态
        sent_formatted = format_bytes(data['net_sent'])
        recv_formatted = format_bytes(data['net_recv'])
        self.net_up_status.set_text(f"{sent_formatted}/s")
        self.net_down_status.set_text(f"{recv_formatted}/s")
    
    def get_screen(self):
        """返回屏幕对象"""
        return self.scr
