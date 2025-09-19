#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
媒体整理器 v7.0 - 现代化GUI版本
主程序入口
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ui.main_window import ModernMediaOrganizer

def main():
    """主函数"""
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("媒体整理器")
    app.setApplicationVersion("7.0")
    
    # 设置应用程序字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    # 创建主窗口
    window = ModernMediaOrganizer()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
