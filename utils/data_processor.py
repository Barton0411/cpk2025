import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
from .cache_helper import load_excel_file, get_file_hash

class DataProcessor:
    def __init__(self):
        self.trait_columns = {
            '脂肪': '脂肪',
            '蛋白': '蛋白',
            '干物质': '干物质',
            '酸度': '酸度',
            '体细胞': '体细胞'
        }
    
    def load_data(self, file_path):
        """加载Excel数据"""
        try:
            # 使用缓存的加载函数
            if hasattr(file_path, 'read'):
                # 上传的文件对象
                df = load_excel_file(file_path)
            else:
                # 文件路径，使用文件hash作为缓存键
                file_hash = get_file_hash(file_path)
                df = load_excel_file(file_path, file_hash)
            
            return df
        except Exception as e:
            print(f"加载数据出错: {e}")
            st.error(f"加载数据失败: {str(e)}")
            return None
    
    def filter_data(self, df, zones=None, regions=None, areas=None, date_range=None, farms=None):
        """根据条件筛选数据"""
        filtered_df = df.copy()
        
        # 大区筛选
        if zones and len(zones) > 0:
            filtered_df = filtered_df[filtered_df['大区'].isin(zones)]
        
        # 区域筛选
        if regions and len(regions) > 0:
            filtered_df = filtered_df[filtered_df['区域'].isin(regions)]
        
        # 地区筛选
        if areas and len(areas) > 0:
            filtered_df = filtered_df[filtered_df['地区'].isin(areas)]
        
        # 时间段筛选
        if date_range and len(date_range) == 2:
            start_date, end_date = date_range
            if '入库日期' in filtered_df.columns:
                # 设置开始日期为当天的00:00:00，结束日期为当天的23:59:59
                start_datetime = pd.Timestamp(start_date).replace(hour=0, minute=0, second=0)
                end_datetime = pd.Timestamp(end_date).replace(hour=23, minute=59, second=59)
                
                mask = (filtered_df['入库日期'] >= start_datetime) & \
                       (filtered_df['入库日期'] <= end_datetime)
                filtered_df = filtered_df[mask]
        
        # 奶源地筛选
        if farms and len(farms) > 0:
            filtered_df = filtered_df[filtered_df['奶源地名称'].isin(farms)]
        
        return filtered_df
    
    def group_data_by_month_and_farm(self, df):
        """按月份和牧场分组数据"""
        if '年月' not in df.columns:
            if '入库日期' in df.columns:
                df['年月'] = df['入库日期'].dt.to_period('M')
        
        # 按月份和奶源地分组
        grouped = df.groupby(['年月', '奶源地名称'])
        
        return grouped
    
    def clean_numeric_data(self, df, columns):
        """清理数值列数据"""
        for col in columns:
            if col in df.columns:
                # 转换为数值类型，非数值转为NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df