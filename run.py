#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
媒体整理器启动脚本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from main import main
    main()
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所需依赖:")
    print("pip install -r requirements.txt")
    input("按回车键退出...")
except Exception as e:
    print(f"运行错误: {e}")
    input("按回车键退出...")
