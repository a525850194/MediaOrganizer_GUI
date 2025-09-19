#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代化样式定义
"""

class ModernStyles:
    """现代化样式类"""
    
    @staticmethod
    def get_main_style():
        """获取主窗口样式"""
        return """
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """
    
    @staticmethod
    def get_title_style():
        """获取标题样式"""
        return """
            QLabel {
                color: #2c3e50;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 15px;
                color: white;
                margin-bottom: 10px;
            }
        """
    
    @staticmethod
    def get_tab_style():
        """获取选项卡样式"""
        return """
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                background-color: #ecf0f1;
            }
            QTabBar::tab {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
            }
            QTabBar::tab:hover {
                background-color: #2980b9;
            }
        """
    
    @staticmethod
    def get_group_style():
        """获取分组框样式"""
        return """
            QGroupBox {
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #2c3e50;
                font-weight: bold;
            }
        """
    
    @staticmethod
    def get_input_style():
        """获取输入框样式"""
        return """
            QLineEdit, QComboBox {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 8px 12px;
                background-color: white;
                font-size: 12px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #3498db;
            }
        """
    
    @staticmethod
    def get_button_style():
        """获取按钮样式"""
        return """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """
    
    @staticmethod
    def get_primary_button_style():
        """获取主要按钮样式"""
        return """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """
    
    @staticmethod
    def get_danger_button_style():
        """获取危险按钮样式"""
        return """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """
    
    @staticmethod
    def get_list_style():
        """获取列表样式"""
        return """
            QListWidget {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                padding: 10px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """
    
    @staticmethod
    def get_log_style():
        """获取日志样式"""
        return """
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', monospace;
            }
        """
