#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
媒体整理器核心功能模块
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal

class MediaOrganizerWorker(QThread):
    """后台工作线程，处理文件整理"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, source_dir, target_dir, organize_by_date=True, 
                 organize_by_type=True, create_subfolders=True):
        super().__init__()
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.organize_by_date = organize_by_date
        self.organize_by_type = organize_by_type
        self.create_subfolders = create_subfolders
        self.is_running = True
        
    def run(self):
        """运行整理任务"""
        try:
            self.status.emit("开始整理媒体文件...")
            files = self._get_media_files()
            total_files = len(files)
            
            if total_files == 0:
                self.status.emit("未找到媒体文件")
                self.finished.emit()
                return
                
            for i, file_path in enumerate(files):
                if not self.is_running:
                    break
                    
                self._organize_file(file_path)
                progress = int((i + 1) / total_files * 100)
                self.progress.emit(progress)
                self.status.emit(f"正在处理: {file_path.name}")
                
            self.status.emit("文件整理完成！")
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(f"整理过程中出错: {str(e)}")
            
    def _get_media_files(self):
        """获取所有媒体文件"""
        media_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',  # 图片
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',    # 视频
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma',            # 音频
            '.pdf', '.doc', '.docx', '.txt', '.rtf'                      # 文档
        }
        
        files = []
        for file_path in Path(self.source_dir).rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in media_extensions:
                files.append(file_path)
        return files
        
    def _organize_file(self, file_path):
        """整理单个文件"""
        # 获取文件信息
        stat = file_path.stat()
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        
        # 创建目标路径
        target_path = Path(self.target_dir)
        
        if self.organize_by_type:
            file_type = self._get_file_type(file_path.suffix.lower())
            target_path = target_path / file_type
            
        if self.organize_by_date:
            year = modified_time.strftime('%Y')
            month = modified_time.strftime('%m')
            target_path = target_path / year / month
            
        if self.create_subfolders:
            target_path.mkdir(parents=True, exist_ok=True)
            
        # 移动文件
        new_file_path = target_path / file_path.name
        if not new_file_path.exists():
            shutil.move(str(file_path), str(new_file_path))
            
    def _get_file_type(self, extension):
        """根据文件扩展名获取文件类型"""
        type_mapping = {
            '.jpg': '图片', '.jpeg': '图片', '.png': '图片', '.gif': '图片',
            '.bmp': '图片', '.tiff': '图片', '.webp': '图片',
            '.mp4': '视频', '.avi': '视频', '.mkv': '视频', '.mov': '视频',
            '.wmv': '视频', '.flv': '视频', '.webm': '视频',
            '.mp3': '音频', '.wav': '音频', '.flac': '音频', '.aac': '音频',
            '.ogg': '音频', '.wma': '音频',
            '.pdf': '文档', '.doc': '文档', '.docx': '文档', '.txt': '文档', '.rtf': '文档'
        }
        return type_mapping.get(extension, '其他')
        
    def stop(self):
        """停止整理"""
        self.is_running = False
