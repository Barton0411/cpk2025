import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
import time
import threading
from queue import Queue

class AsyncDataProcessor:
    """带进度显示的数据处理器"""
    
    def __init__(self):
        self.progress = 0
        self.status = ""
        self.result = None
        self.error = None
    
    def load_excel_with_progress(self, file_path_or_buffer):
        """带进度的Excel读取"""
        self.progress = 0
        self.status = "开始读取文件..."
        
        try:
            # 步骤1: 读取Excel文件 (30%)
            self.status = "正在打开Excel文件..."
            self.progress = 10
            
            # 重置文件指针到开始位置
            if hasattr(file_path_or_buffer, 'seek'):
                file_path_or_buffer.seek(0)
            
            if hasattr(file_path_or_buffer, 'read'):
                df = pd.read_excel(file_path_or_buffer, engine='openpyxl')
            else:
                df = pd.read_excel(file_path_or_buffer, engine='openpyxl')
            
            self.progress = 30
            total_rows = len(df)
            self.status = f"已读取 {total_rows:,} 条记录，正在处理数据..."
            
            # 步骤2: 筛选列 (40%)
            self.progress = 40
            required_cols = ['大区', '区域', '地区', '奶源地编码', '奶源地名称', 
                           '入库日期', '上号日期', '脂肪', '蛋白', '干物质', 
                           '酸度', '微生物', '体细胞']
            cols_to_keep = [col for col in required_cols if col in df.columns]
            df = df[cols_to_keep]
            
            # 步骤3: 转换日期 (60%)
            self.progress = 60
            self.status = "正在转换日期格式..."
            date_columns = ['上号日期', '入库日期']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # 步骤4: 添加月份列 (80%)
            self.progress = 80
            self.status = "正在生成月度分析数据..."
            if '入库日期' in df.columns:
                df['年月'] = df['入库日期'].dt.to_period('M')
            
            # 完成
            self.progress = 100
            self.status = "数据处理完成！"
            self.result = df
            
            return df
            
        except Exception as e:
            self.error = str(e)
            self.status = f"错误: {str(e)}"
            return None