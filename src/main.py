#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys

# HiDPI 支持（必须在 QApplication 创建前设置）
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "RoundPreferFloor"

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QFont

from ui.main_window import ModernMediaOrganizer

def main():
	# 高分屏属性
	QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
	QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

	app = QApplication(sys.argv)

	# 以 96DPI 为基准计算缩放
	dpi = app.primaryScreen().logicalDotsPerInch() or 96
	scale = max(1.0, min(dpi / 96.0, 3.0))  # 限制 1.0~3.0，5K 一般在 2 左右
	# 如需更大可放开下一行：scale *= 1.15
	base_pt = int(10 * scale)
	app.setFont(QFont("Microsoft YaHei", base_pt))
	app.setStyleSheet(f"QWidget{{font-size:{int(12*scale)}px;}}")

	window = ModernMediaOrganizer(scale=scale)
	window.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
