import streamlit as st
import pandas as pd
import hashlib
import os

@st.cache_data(show_spinner=False)
def load_excel_file(file_path_or_buffer, file_hash=None):
    """缓存的Excel文件读取函数"""
    # 使用更快的引擎
    if hasattr(file_path_or_buffer, 'read'):
        # 上传的文件对象
        df = pd.read_excel(file_path_or_buffer, engine='openpyxl')
    else:
        # 文件路径
        df = pd.read_excel(file_path_or_buffer, engine='openpyxl')
    
    # 只保留需要的列 - 确保大区列也被包含
    required_cols = ['大区', '区域', '地区', '奶源地编码', '奶源地名称', 
                   '入库日期', '上号日期', '脂肪', '蛋白', '干物质', 
                   '酸度', '体细胞']
    
    # 筛选存在的列
    cols_to_keep = [col for col in required_cols if col in df.columns]
    df = df[cols_to_keep]
    
    # 转换日期列
    date_columns = ['上号日期', '入库日期']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # 添加月份列用于月度分析
    if '入库日期' in df.columns:
        df['年月'] = df['入库日期'].dt.to_period('M')
    
    return df

def get_file_hash(file_path):
    """获取文件的hash值"""
    if os.path.exists(file_path):
        return str(os.path.getmtime(file_path))
    return None