#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建脚本 - 将Python应用打包为Windows可执行文件
"""

import PyInstaller.__main__
import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
os.environ["PYTHONIOENCODING"] = "utf-8"

def build():
    """构建可执行文件"""
    
    # 构建参数
    args = [
        'src/main.py',                    # 主文件
        '--paths=src',                    # <— 新增
        '--onefile',                      # 打包为单个文件
        '--windowed',                     # 无控制台窗口
        '--name=MediaOrganizer_v7.0',     # 输出文件名
        '--add-data=README.md;.',         # 添加README文件
        '--clean',                        # 清理临时文件
        '--noconfirm'                     # 不询问确认
    ]
    
    print("开始构建...")
    print(f"构建参数: {' '.join(args)}")
    
    try:
        PyInstaller.__main__.run(args)
        print("构建完成！")
        print("可执行文件位置: dist/MediaOrganizer_v7.0.exe")
    except Exception as e:
        print(f"构建失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    build()
