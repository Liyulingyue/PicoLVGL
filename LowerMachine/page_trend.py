"""
趋势页面 - 显示CPU、内存、网络上传下载的趋势图
"""
import lvgl as lv
from config import THEME, LAYOUT, SCREEN
from ui_components import create_label

class TrendPage:
    """趋势页面类"""

    def __init__(self):
        """初始化趋势页面"""
        self.scr = lv.obj()
        self.scr.set_style_bg_color(lv.color_hex(THEME['bg_primary']), 0)

        # 初始化数据历史记录
        self.max_points = 50  # 最多显示50个数据点
        self.cpu_history = []
        self.mem_history = []
        self.up_history = []
        self.down_history = []

        self._create_ui()

    def _create_ui(self):
        """创建UI元素"""
        # 标题 - 简洁设计
        self.title_label = create_label(self.scr, 10, 8, "TREND", 'text_title')

        # 创建4个趋势图容器
        self._create_trend_containers()

    def _create_trend_containers(self):
        """创建4个趋势图容器"""
        container_width = (SCREEN['width'] - 30) // 2  # 两个容器一行
        container_height = (SCREEN['height'] - 60) // 2  # 两行容器

        # CPU趋势图 - 左上
        self.cpu_container = self._create_trend_container(
            10, 35, container_width, container_height, "CPU %", 'text_cpu'
        )
        self.cpu_chart = self._create_chart(self.cpu_container)

        # MEM趋势图 - 右上
        self.mem_container = self._create_trend_container(
            20 + container_width, 35, container_width, container_height, "MEM %", 'text_memory'
        )
        self.mem_chart = self._create_chart(self.mem_container)

        # UP趋势图 - 左下
        self.up_container = self._create_trend_container(
            10, 45 + container_height, container_width, container_height, "UP B/s", 'text_network'
        )
        self.up_chart = self._create_chart(self.up_container)

        # DOWN趋势图 - 右下
        self.down_container = self._create_trend_container(
            20 + container_width, 45 + container_height, container_width, container_height, "DOWN B/s", 'text_network'
        )
        self.down_chart = self._create_chart(self.down_container)

    def _create_trend_container(self, x, y, width, height, title, title_style):
        """创建单个趋势图容器"""
        container = lv.obj(self.scr)
        container.set_size(width, height)
        container.set_pos(x, y)
        container.set_style_bg_color(lv.color_hex(THEME['bg_card']), 0)
        container.set_style_border_width(1, 0)
        container.set_style_border_color(lv.color_hex(THEME['divider']), 0)
        container.set_style_pad_all(5, 0)
        container.set_style_radius(8, 0)
        container.add_flag(lv.obj.FLAG.EVENT_BUBBLE)

        # 容器标题
        title_label = create_label(container, 5, 5, title, title_style)

        return container

    def _create_chart(self, parent):
        """在容器中创建字符画图表"""
        # 创建标签来显示字符画
        chart_label = lv.label(parent)
        chart_label.set_size(parent.get_width() - 10, parent.get_height() - 30)
        chart_label.set_pos(5, 25)
        chart_label.set_style_text_color(lv.color_hex(THEME['text_time']), 0)
        chart_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
        chart_label.set_long_mode(lv.label.LONG.WRAP)
        chart_label.set_text("Loading...")

        # 使用等宽字体
        try:
            chart_label.set_style_text_font(lv.font_monospace_12, 0)
        except:
            try:
                chart_label.set_style_text_font(lv.font_montserrat_12, 0)
            except:
                pass

        return chart_label

    def update(self, data):
        """更新趋势图显示"""
        try:
            # 更新数据历史
            self._update_data_history(data)

            # 更新各个图表
            self._update_charts()

        except Exception as e:
            print(f"Trend page update error: {e}")

    def _update_data_history(self, data):
        """更新数据历史记录"""
        # CPU数据
        cpu_value = data['cpu']
        self.cpu_history.append(cpu_value)
        if len(self.cpu_history) > self.max_points:
            self.cpu_history.pop(0)

        # 内存数据
        mem_value = data['memory']
        self.mem_history.append(mem_value)
        if len(self.mem_history) > self.max_points:
            self.mem_history.pop(0)

        # 上传数据
        up_value = data['net_sent']
        self.up_history.append(up_value)
        if len(self.up_history) > self.max_points:
            self.up_history.pop(0)

        # 下载数据
        down_value = data['net_recv']
        self.down_history.append(down_value)
        if len(self.down_history) > self.max_points:
            self.down_history.pop(0)

    def _update_charts(self):
        """更新所有图表显示"""
        # 更新CPU图表
        self._update_single_chart(self.cpu_chart, self.cpu_history, 0, 100)

        # 更新内存图表
        self._update_single_chart(self.mem_chart, self.mem_history, 0, 100)

        # 更新上传图表 - 根据数据范围调整
        if self.up_history:
            max_up = max(self.up_history)
            up_range = max(100, max_up * 1.2)  # 至少100，至少比最大值大20%
            self._update_single_chart(self.up_chart, self.up_history, 0, int(up_range))

        # 更新下载图表 - 根据数据范围调整
        if self.down_history:
            max_down = max(self.down_history)
            down_range = max(100, max_down * 1.2)  # 至少100，至少比最大值大20%
            self._update_single_chart(self.down_chart, self.down_history, 0, int(down_range))

    def _update_single_chart(self, chart_label, data, y_min, y_max):
        """更新单个字符画图表"""
        if not data:
            chart_label.set_text("No data")
            return

        # 生成字符画
        ascii_chart = self._generate_ascii_chart(data, y_min, y_max)
        chart_label.set_text(ascii_chart)

    def _generate_ascii_chart(self, data, y_min, y_max):
        """生成ASCII字符画趋势图"""
        if not data:
            return "No data"

        # 图表尺寸
        width = 20  # 字符宽度
        height = 8  # 字符高度

        # 归一化数据到0-height范围
        normalized_data = []
        for value in data[-width:]:  # 只取最后width个数据点
            if y_max > y_min:
                normalized = int((value - y_min) / (y_max - y_min) * (height - 1))
                normalized = max(0, min(height - 1, normalized))
            else:
                normalized = 0
            normalized_data.append(normalized)

        # 生成字符画
        lines = []
        for y in range(height - 1, -1, -1):  # 从上到下
            line = ""
            for x in range(len(normalized_data)):
                if normalized_data[x] == y:
                    line += "●"  # 数据点
                elif y == 0:
                    line += "─"  # X轴
                else:
                    line += " "  # 空白
            lines.append(line)

        # 添加X轴标签
        x_axis = "└" + "─" * (width - 2) + "┘"
        lines.append(x_axis)

        return "\n".join(lines)

    def get_screen(self):
        """返回屏幕对象"""
        return self.scr