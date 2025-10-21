# Pico LVGL
Pico_DM_QD3503728 是基于树莓派 Pico 设计的一款低成本显示拓展板，用来学习、评估、开发LVGL或其他GUI应用。本项目的uf2包（LVGL V8.3）来源于 [embeddedboys](https://embeddedboys.github.io/Pico_DM_QD3503728/docs/env-setup/%E9%80%89%E6%8B%A9%E5%B7%A3%E7%A8%8B/#micropython-python)。

## 文件说明

### 文件配套关系

本项目包含多个版本的显示程序，不同文件之间有特定的配套关系：

#### HigherMachine 目录
- `demo_click.py` 和 `system_monitor.py` 配套使用
  - `demo_click.py`: 触摸点击演示程序
  - `system_monitor.py`: 系统监控数据源程序

#### LowerMachine 目录
- `demo_click.py` 和 `demo_hello_world.py` 配套使用
  - `demo_click.py`: 触摸点击演示程序
  - `demo_hello_world.py`: 基础显示程序

#### 显示程序版本说明

1. **display_monitor.py** (不推荐)
   - 功能: 包含翻页功能，支持多页面切换
   - 状态: 非稳定版
   - 问题: 部分功能可能不正常

2. **display_monitor_v3.py** (推荐)
   - 功能: 稳定的单页面显示程序
   - 状态: 稳定版
   - 优势: 无翻页功能，运行稳定可靠

3. **其他版本** (display_monitor_v1.py, display_monitor_v2.py 等)
   - 功能: 不同阶段的开发版本
   - 状态: 仅供参考，不推荐使用

### 推荐使用方案

- **学习触摸功能**: 使用 `demo_click.py` + `demo_hello_world.py`
- **系统监控**: 使用 `system_monitor.py` + `display_monitor_v3.py`
- **多页面功能**: 使用 `display_monitor.py` (注意可能存在不稳定因素)

### 运行方式

1. 将相应文件上传到树莓派 Pico
2. 运行数据源程序（如 `system_monitor.py`）
3. 运行显示程序（如 `display_monitor_v3.py`）
4. 通过 UART 连接传输数据

