"""
页面管理器 - 管理多个页面的切换
"""
import lvgl as lv

class PageManager:
    """页面管理器，支持多页面切换"""
    
    def __init__(self):
        """初始化页面管理器"""
        self.pages = []  # 存储所有页面对象
        self.current_page_index = 0
        self.current_page = None
        self.touch_button = None  # 用于捕获触摸的透明按钮
    
    def add_page(self, page):
        """添加页面到管理器"""
        self.pages.append(page)
        if len(self.pages) == 1:
            self.current_page = page
            self.current_page_index = 0
    
    def load_current_page(self):
        """加载当前页面"""
        if self.current_page:
            scr = self.current_page.get_screen()
            lv.scr_load(scr)
            
            # 如果有多个页面，创建一个透明的全屏按钮用于切换
            if len(self.pages) > 1:
                self.switch_btn = lv.btn(scr)
                self.switch_btn.set_size(480, 320)  # 全屏
                self.switch_btn.set_pos(0, 0)
                
                # 设置为完全透明
                self.switch_btn.set_style_bg_opa(0, 0)  # 背景透明
                self.switch_btn.set_style_bg_opa(0, lv.STATE.PRESSED)  # 按下时也透明
                self.switch_btn.set_style_border_width(0, 0)  # 无边框
                self.switch_btn.set_style_shadow_width(0, 0)  # 无阴影
                self.switch_btn.set_style_outline_width(0, 0)  # 无轮廓
                
                # 绑定点击事件
                self.switch_btn.add_event_cb(lambda e: self.next_page(), lv.EVENT.CLICKED, None)
                
                # 将按钮移到最顶层，确保能接收所有点击事件
                self.switch_btn.move_foreground()
                
                # 设置按钮不阻挡点击，让点击事件能被子元素接收
                self.switch_btn.add_flag(lv.obj.FLAG.CLICKABLE)
                self.switch_btn.clear_flag(lv.obj.FLAG.CLICK_FOCUSABLE)
    
    def _touch_event_handler(self, event):
        """触摸事件处理器 - 点击屏幕切换页面"""
        print("Touch detected! Switching page...")  # 调试信息
        # 切换到下一页
        self.next_page()
    
    def next_page(self):
        """切换到下一页"""
        if len(self.pages) <= 1:
            return
        
        self.current_page_index = (self.current_page_index + 1) % len(self.pages)
        self.current_page = self.pages[self.current_page_index]
        self.load_current_page()
    
    def prev_page(self):
        """切换到上一页"""
        if len(self.pages) <= 1:
            return
        
        self.current_page_index = (self.current_page_index - 1) % len(self.pages)
        self.current_page = self.pages[self.current_page_index]
        self.load_current_page()
    
    def get_current_page(self):
        """获取当前页面对象"""
        return self.current_page
    
    def update_current_page(self, data):
        """更新当前页面数据"""
        if self.current_page:
            self.current_page.update(data)
    
    def check_touch_and_switch(self):
        """检查触摸输入并切换页面（在主循环中调用）"""
        if len(self.pages) <= 1:
            return False
        
        # 初始化状态变量
        if not hasattr(self, '_last_touch_state'):
            self._last_touch_state = False
        
        # 获取触摸输入设备
        indev = lv.indev_get_next(None)
        if indev:
            # 检查是否有触摸
            point = lv.point_t()
            state = indev.get_point(point)
            
            # 检测从按下到释放的转变
            is_pressed = (state == lv.INDEV_STATE.PRESSED or state == lv.INDEV_STATE.REL)
            
            if self._last_touch_state and not is_pressed:
                # 从按下变为释放，切换页面
                self._last_touch_state = False
                self.next_page()
                return True
            
            self._last_touch_state = is_pressed
        
        return False
