import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
import time
import threading

# 设置页面配置
st.set_page_config(
    page_title="牧场数据CPK分析系统",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_password():
    """返回 True 如果用户输入了正确的密码"""
    
    def password_entered():
        """检查输入的密码是否正确"""
        from config import SYSTEM_PASSWORD
        if st.session_state["password"] == SYSTEM_PASSWORD:  # 从配置文件读取密码
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 删除密码，避免在内存中保留
        else:
            st.session_state["password_correct"] = False

    # 如果还没有验证过密码
    if "password_correct" not in st.session_state:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔒 牧场数据CPK分析系统")
            st.markdown("#### 请输入访问密码")
            st.text_input(
                "密码", 
                type="password", 
                on_change=password_entered, 
                key="password"
            )
            st.info("请联系管理员获取访问密码")
        return False
    
    # 如果密码错误
    elif not st.session_state["password_correct"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔒 牧场数据CPK分析系统")
            st.markdown("#### 请输入访问密码")
            st.text_input(
                "密码", 
                type="password", 
                on_change=password_entered, 
                key="password"
            )
            st.error("❌ 密码错误，请重试")
        return False
    
    # 密码正确
    else:
        return True

# 检查密码
if not check_password():
    st.stop()

# 设置中文显示
import locale
try:
    locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
except:
    pass

# 导入其他模块
from utils.data_processor import DataProcessor
from utils.statistics_calculator import StatisticsCalculator
from utils.data_processor_async import AsyncDataProcessor

# 初始化数据处理器和统计计算器
data_processor = DataProcessor()
stats_calculator = StatisticsCalculator()
async_processor = AsyncDataProcessor()

# 侧边栏配置
with st.sidebar:
    st.title("系统配置")
    
    # 添加登出按钮
    if st.button("🚪 退出系统", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # 季节配置
    st.subheader("季节参数设置")
    
    # 夏季时间段
    summer_start = st.date_input("夏季开始日期", value=datetime(2024, 5, 1))
    summer_end = st.date_input("夏季结束日期", value=datetime(2024, 9, 30))
    
    # 过程值差值系数配置
    st.subheader("过程值差值系数")
    
    season = st.radio("选择季节系数", ["夏季", "冬季"])
    
    if season == "夏季":
        coef_fat = st.number_input("脂肪系数", value=3.2, step=0.1)
        coef_protein = st.number_input("蛋白系数", value=2.9, step=0.1)
        coef_dry = st.number_input("干物质系数", value=11.8, step=0.1)
        coef_cell = st.number_input("体细胞系数", value=20.0, step=1.0)
    else:
        coef_fat = st.number_input("脂肪系数", value=3.4, step=0.1)
        coef_protein = st.number_input("蛋白系数", value=3.0, step=0.1)
        coef_dry = st.number_input("干物质系数", value=11.9, step=0.1)
        coef_cell = st.number_input("体细胞系数", value=20.0, step=1.0)
    
    # 酸度特殊参数
    st.subheader("酸度参数")
    acid_min = st.number_input("酸度最小值", value=12.0, step=0.1)
    acid_max = st.number_input("酸度最大值", value=17.5, step=0.1)
    
    # 公差设置
    st.subheader("公差设置")
    tolerance_acid = st.number_input("酸度公差", value=5.5, step=0.1)
    
    # CPK异常判定设置
    st.subheader("CPK异常判定")
    cpk_threshold_type = st.radio(
        "判定方式",
        options=["小于阈值为异常", "自定义范围"],
        index=0,
        key="sidebar_cpk_type"
    )
    
    if cpk_threshold_type == "小于阈值为异常":
        cpk_threshold = st.number_input("CPK阈值", value=1.0, step=0.1, help="CPK小于此值为异常")
        st.caption("默认：CPK < 1.0 为异常")
        # 内部使用
        cpk_min = -999
        cpk_max = cpk_threshold
    else:
        st.write("CPK正常范围")
        col_min, col_max = st.columns(2)
        with col_min:
            cpk_min = st.number_input("最小值", value=1.0, step=0.1, key="cpk_min_input")
        with col_max:
            cpk_max = st.number_input("最大值", value=999.0, step=0.1, key="cpk_max_input")
        st.caption("CPK在此范围外为异常")

# 确保CPK判定变量在全局作用域可用
if 'cpk_min' not in locals():
    cpk_min = -999
    cpk_max = 1.0
if 'cpk_threshold' not in locals():
    cpk_threshold = 1.0

# 主界面
st.title("🐄 牧场数据CPK分析系统")

# 数据上传
uploaded_file = st.file_uploader("请选择Excel数据文件", type=['xlsx', 'xls'])

if uploaded_file is not None:
    # 检查是否已经加载过这个文件
    file_key = f"df_{uploaded_file.name}_{uploaded_file.size}"
    
    if file_key not in st.session_state:
        # 读取数据
        progress_container = st.container()
        with progress_container:
            progress_text = st.empty()
            progress_bar = st.progress(0)
            
            # 获取文件大小
            file_size_mb = uploaded_file.size / (1024 * 1024)
            
            # 显示文件信息
            progress_text.text(f"正在读取 {uploaded_file.name} ({file_size_mb:.1f}MB)")
            status_text = st.empty()
            
            # 开始计时
            start_time = time.time()
            
            # 直接读取数据（简化流程）
            try:
                status_text.text("正在打开Excel文件...")
                progress_bar.progress(0.1)
                
                # 重置文件指针
                uploaded_file.seek(0)
                
                # 读取数据
                df = pd.read_excel(uploaded_file, engine='openpyxl')
                progress_bar.progress(0.4)
                
                status_text.text(f"已读取 {len(df):,} 条记录，正在处理...")
                
                # 筛选列
                required_cols = ['大区', '区域', '地区', '奶源地编码', '奶源地名称', 
                               '入库日期', '上号日期', '脂肪', '蛋白', '干物质', 
                               '酸度', '体细胞']
                cols_to_keep = [col for col in required_cols if col in df.columns]
                df = df[cols_to_keep]
                progress_bar.progress(0.6)
                
                # 转换日期
                status_text.text("正在转换日期格式...")
                date_columns = ['上号日期', '入库日期']
                for col in date_columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                progress_bar.progress(0.8)
                
                # 添加月份列
                if '入库日期' in df.columns:
                    df['年月'] = df['入库日期'].dt.to_period('M')
                
                progress_bar.progress(1.0)
                elapsed_time = int(time.time() - start_time)
                status_text.text(f"数据加载完成！用时 {elapsed_time} 秒")
                
                # 保存到session state
                st.session_state[file_key] = df
                
                # 短暂显示完成信息
                time.sleep(1)
                
            except Exception as e:
                st.error(f"加载数据失败: {str(e)}")
                df = None
            
            # 清理进度显示
            progress_text.empty()
            progress_bar.empty()
            status_text.empty()
    else:
        # 使用缓存的数据
        df = st.session_state[file_key]
        
    if df is not None:
        st.success(f"成功加载数据！共 {len(df)} 条记录")
        
        # 数据筛选
        st.header("数据筛选")
        
        # 添加全选/清除按钮行
        button_col1, button_col2, button_col3, button_col4, button_col5 = st.columns(5)
        
        with button_col1:
            col1_1, col1_2 = st.columns(2)
            with col1_1:
                if st.button("全选大区", use_container_width=True):
                    st.session_state['select_all_zones'] = True
            with col1_2:
                if st.button("清除大区", use_container_width=True):
                    st.session_state['select_all_zones'] = False
        
        with button_col2:
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                if st.button("全选区域", use_container_width=True):
                    st.session_state['select_all_regions'] = True
            with col2_2:
                if st.button("清除区域", use_container_width=True):
                    st.session_state['select_all_regions'] = False
        
        with button_col3:
            col3_1, col3_2 = st.columns(2)
            with col3_1:
                if st.button("全选地区", use_container_width=True):
                    st.session_state['select_all_areas'] = True
            with col3_2:
                if st.button("清除地区", use_container_width=True):
                    st.session_state['select_all_areas'] = False
        
        with button_col4:
            col4_1, col4_2 = st.columns(2)
            with col4_1:
                if st.button("全选奶源地", use_container_width=True):
                    st.session_state['select_all_farms'] = True
            with col4_2:
                if st.button("清除奶源地", use_container_width=True):
                    st.session_state['select_all_farms'] = False
        
        with button_col5:
            st.empty()  # 时间段不需要全选
        
        # 筛选控件 - 5列布局
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            # 大区筛选
            all_zones = sorted(list(df['大区'].unique())) if '大区' in df.columns else []
            default_zones = all_zones if st.session_state.get('select_all_zones', False) else []
            zones = st.multiselect(
                "选择大区",
                options=all_zones,
                default=default_zones,
                key="zone_select"
            )
        
        with col2:
            # 区域筛选 - 根据选择的大区过滤
            if zones:
                # 只显示选中大区的区域
                filtered_df_for_regions = df[df['大区'].isin(zones)]
                all_regions = sorted(list(filtered_df_for_regions['区域'].unique())) if '区域' in filtered_df_for_regions.columns else []
            else:
                # 没有选择大区时显示所有区域
                all_regions = sorted(list(df['区域'].unique())) if '区域' in df.columns else []
            
            default_regions = all_regions if st.session_state.get('select_all_regions', False) else []
            # 清理无效的默认值
            default_regions = [region for region in default_regions if region in all_regions]
            
            regions = st.multiselect(
                "选择区域",
                options=all_regions,
                default=default_regions,
                key="region_select"
            )
        
        with col3:
            # 地区筛选 - 根据选择的大区和区域过滤
            temp_df = df.copy()
            if zones:
                temp_df = temp_df[temp_df['大区'].isin(zones)]
            if regions:
                temp_df = temp_df[temp_df['区域'].isin(regions)]
            
            all_areas = sorted(list(temp_df['地区'].unique())) if '地区' in temp_df.columns else []
            
            default_areas = all_areas if st.session_state.get('select_all_areas', False) else []
            # 清理无效的默认值
            default_areas = [area for area in default_areas if area in all_areas]
            
            areas = st.multiselect(
                "选择地区",
                options=all_areas,
                default=default_areas,
                key="area_select"
            )
        
        with col4:
            # 奶源地筛选 - 根据选择的大区、区域和地区过滤
            temp_df = df.copy()
            if zones:
                temp_df = temp_df[temp_df['大区'].isin(zones)]
            if regions:
                temp_df = temp_df[temp_df['区域'].isin(regions)]
            if areas:
                temp_df = temp_df[temp_df['地区'].isin(areas)]
            
            all_farms = sorted(list(temp_df['奶源地名称'].unique())) if '奶源地名称' in temp_df.columns else []
            
            default_farms = all_farms if st.session_state.get('select_all_farms', False) else []
            # 清理无效的默认值
            default_farms = [farm for farm in default_farms if farm in all_farms]
            
            farms = st.multiselect(
                "选择奶源地",
                options=all_farms,
                default=default_farms,
                key="farm_select"
            )
        
        with col5:
            # 时间段筛选 - 移到最后
            date_range = st.date_input(
                "选择时间段",
                value=[],
                help="选择开始和结束日期（包含所选日期当天）",
                key="date_select"
            )
        
        # 添加快捷操作按钮
        quick_col1, quick_col2, quick_col3 = st.columns([1, 1, 3])
        with quick_col1:
            if st.button("🔄 全部选择", use_container_width=True):
                st.session_state['select_all_zones'] = True
                st.session_state['select_all_regions'] = True
                st.session_state['select_all_areas'] = True
                st.session_state['select_all_farms'] = True
                st.rerun()
        
        with quick_col2:
            if st.button("🗑️ 全部清除", use_container_width=True):
                st.session_state['select_all_zones'] = False
                st.session_state['select_all_regions'] = False
                st.session_state['select_all_areas'] = False
                st.session_state['select_all_farms'] = False
                st.rerun()
        
        # 应用筛选
        filtered_df = data_processor.filter_data(df, zones, regions, areas, date_range, farms)
        
        # 显示筛选结果统计
        if len(zones) > 0 or len(regions) > 0 or len(areas) > 0 or len(farms) > 0 or date_range:
            st.info(f"筛选后数据: {len(filtered_df)} 条记录 (原始数据: {len(df)} 条)")
        
        # 计算统计数据
        if st.button("计算分析指标"):
            with st.spinner('正在计算...'):
                # 准备系数
                coefficients = {
                    '脂肪': coef_fat,
                    '蛋白': coef_protein,
                    '干物质': coef_dry,
                    '体细胞': coef_cell,
                    '酸度_min': acid_min,
                    '酸度_max': acid_max,
                    '酸度_tolerance': tolerance_acid
                }
                
                # 计算整体汇总统计
                summary_table = stats_calculator.calculate_summary_table(filtered_df, coefficients)
                
                # 显示整体分析结果
                st.header("📊 整体能力分析结果")
                
                # 创建样式函数
                def style_dataframe(df):
                    """为数据框添加样式"""
                    # 创建一个样式数组
                    styles = pd.DataFrame('', index=df.index, columns=df.columns)
                    
                    # 第一列（能力分析）设置背景色
                    styles.iloc[:, 0] = 'background-color: #e6f3ff; font-weight: bold'
                    
                    # 找到cpk行并设置颜色
                    if 'cpk' in df['能力分析'].values:
                        cpk_idx = df[df['能力分析'] == 'cpk'].index[0]
                        for col in df.columns[1:]:
                            try:
                                val = float(df.loc[cpk_idx, col])
                                if val < 1.0:
                                    styles.loc[cpk_idx, col] = 'background-color: #ffcccc'  # 浅红色
                                elif val >= 1.33:
                                    styles.loc[cpk_idx, col] = 'background-color: #ccffcc'  # 浅绿色
                                else:
                                    styles.loc[cpk_idx, col] = 'background-color: #ffffcc'  # 浅黄色
                            except:
                                pass
                    
                    return styles
                
                # 应用样式
                styled_summary = summary_table.style.apply(style_dataframe, axis=None)
                st.dataframe(styled_summary, use_container_width=True)
                
                # 添加说明
                with st.expander("📋 指标说明"):
                    st.markdown("""
                    - **σ（标准差）**：数据的离散程度，越小越好
                    - **X（平均值）**：数据的集中趋势
                    - **过程值差值**：实际均值与目标值的差异
                    - **6σ/3σ**：过程能力的衡量标准
                    - **CPK**：过程能力指数，≥1.33为优秀，1.0-1.33为良好，<1.0需改进
                    - **公差**：允许的变动范围
                    - **CP**：潜在过程能力指数
                    """)
                
                # 计算详细统计指标
                st.header("📈 详细分析结果")
                results = stats_calculator.calculate_statistics(filtered_df, coefficients)
                st.dataframe(results, use_container_width=True)
                
                # 下载结果
                col1, col2 = st.columns(2)
                with col1:
                    # 下载汇总表
                    summary_csv = summary_table.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="下载整体分析结果",
                        data=summary_csv,
                        file_name=f"cpk_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime='text/csv'
                    )
                
                with col2:
                    # 下载详细结果
                    csv = results.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="下载详细分析结果",
                        data=csv,
                        file_name=f"cpk_details_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime='text/csv'
                    )
        
        # CPK异常筛选
        st.header("CPK异常筛选")
        st.info("💡 CPK异常筛选使用全部数据，不受上方数据筛选条件限制")
        
        # 显示当前判定标准
        if cpk_threshold_type == "小于阈值为异常":
            st.success(f"📊 当前判定标准：CPK < {cpk_threshold} 为异常")
        else:
            st.success(f"📊 当前判定标准：CPK < {cpk_min} 或 CPK > {cpk_max} 为异常")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("筛选时间范围")
            # 时间范围选择
            cpk_date_range = st.date_input(
                "选择分析时间段",
                value=[],
                help="留空则分析全部时间数据",
                key="cpk_date_select"
            )
            
            # 分析粒度
            analysis_period = st.radio(
                "分析粒度",
                options=["按月", "按季度", "按年"],
                index=0
            )
        
        with col2:
            st.subheader("筛选对象范围")
            filter_object = st.radio(
                "选择分析维度",
                options=["按大区", "按区域", "按牧场"],
                index=1  # 默认选中"按区域"
            )
        
        if st.button("筛选CPK异常"):
            with st.spinner('正在筛选异常数据...'):
                # 计算统计数据
                coefficients = {
                    '脂肪': coef_fat,
                    '蛋白': coef_protein,
                    '干物质': coef_dry,
                    '体细胞': coef_cell,
                    '酸度_min': acid_min,
                    '酸度_max': acid_max,
                    '酸度_tolerance': tolerance_acid
                }
                
                # 使用全部数据进行CPK异常筛选，不受数据筛选影响
                cpk_df = df.copy()  # 使用原始完整数据
                
                # 应用时间范围筛选
                if cpk_date_range and len(cpk_date_range) == 2:
                    start_date, end_date = cpk_date_range
                    if '入库日期' in cpk_df.columns:
                        start_datetime = pd.Timestamp(start_date).replace(hour=0, minute=0, second=0)
                        end_datetime = pd.Timestamp(end_date).replace(hour=23, minute=59, second=59)
                        mask = (cpk_df['入库日期'] >= start_datetime) & (cpk_df['入库日期'] <= end_datetime)
                        cpk_df = cpk_df[mask]
                
                # 根据分析粒度添加时间列
                if '入库日期' in cpk_df.columns:
                    if analysis_period == "按月":
                        cpk_df['时间段'] = cpk_df['入库日期'].dt.to_period('M')
                    elif analysis_period == "按季度":
                        cpk_df['时间段'] = cpk_df['入库日期'].dt.to_period('Q')
                    elif analysis_period == "按年":
                        cpk_df['时间段'] = cpk_df['入库日期'].dt.to_period('Y')
                
                # 根据筛选范围计算
                if True:  # 始终执行分析
                    # 单月分析
                    if filter_object == "按大区":
                        # 按大区和月份分组计算
                        results_list = []
                        
                        # 获取所有大区和时间段的组合
                        if '时间段' in cpk_df.columns and '大区' in cpk_df.columns:
                            grouped = cpk_df.groupby(['时间段', '大区'])
                            
                            for (period, zone), group_data in grouped:
                                # 计算每个大区每个时间段的统计指标
                                period_summary = stats_calculator.calculate_summary_table(group_data, coefficients)
                                
                                # 提取CPK值
                                cpk_row = period_summary[period_summary['能力分析'] == 'cpk']
                                if not cpk_row.empty:
                                    row_dict = {
                                        '时间段': str(period),
                                        '大区': zone,
                                        '数据量': len(group_data)
                                    }
                                    
                                    # 添加各性状的CPK值
                                    for trait in ['脂肪', '蛋白', '干物质', '酸度', '体细胞']:
                                        if trait in cpk_row.columns:
                                            cpk_value = cpk_row[trait].values[0]
                                            try:
                                                cpk_float = float(cpk_value)
                                                row_dict[f'{trait}_CPK'] = cpk_float
                                                # 判断是否异常
                                                row_dict[f'{trait}_状态'] = '异常' if (cpk_float < cpk_min or cpk_float > cpk_max) else '正常'
                                            except:
                                                row_dict[f'{trait}_CPK'] = '-'
                                                row_dict[f'{trait}_状态'] = '-'
                                    
                                    results_list.append(row_dict)
                        
                        if results_list:
                            results_df = pd.DataFrame(results_list)
                            
                            # 筛选异常记录
                            status_columns = [col for col in results_df.columns if col.endswith('_状态')]
                            if status_columns:
                                mask = results_df[status_columns].apply(lambda row: '异常' in row.values, axis=1)
                                abnormal_results = results_df[mask]
                                
                                if len(abnormal_results) > 0:
                                    st.warning(f"发现 {len(abnormal_results)} 个大区/时间段存在CPK异常")
                                    st.dataframe(abnormal_results, use_container_width=True)
                                    
                                    # 下载异常结果
                                    csv = abnormal_results.to_csv(index=False, encoding='utf-8-sig')
                                    st.download_button(
                                        label="下载异常数据",
                                        data=csv,
                                        file_name=f"cpk_zone_period_abnormal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime='text/csv'
                                    )
                                else:
                                    st.success("未发现CPK异常数据")
                            else:
                                st.error("无法计算CPK值")
                        else:
                            st.warning("没有足够的数据进行分析")
                    
                    elif filter_object == "按区域":
                        # 按区域和时间段分组计算
                        results_list = []
                        
                        # 获取所有区域和时间段的组合
                        if '时间段' in cpk_df.columns and '区域' in cpk_df.columns:
                            grouped = cpk_df.groupby(['时间段', '区域'])
                            
                            for (period, region), group_data in grouped:
                                # 计算每个区域每个时间段的统计指标
                                period_summary = stats_calculator.calculate_summary_table(group_data, coefficients)
                                
                                # 提取CPK值
                                cpk_row = period_summary[period_summary['能力分析'] == 'cpk']
                                if not cpk_row.empty:
                                    row_dict = {
                                        '时间段': str(period),
                                        '区域': region,
                                        '数据量': len(group_data)
                                    }
                                    
                                    # 添加各性状的CPK值
                                    for trait in ['脂肪', '蛋白', '干物质', '酸度', '体细胞']:
                                        if trait in cpk_row.columns:
                                            cpk_value = cpk_row[trait].values[0]
                                            try:
                                                cpk_float = float(cpk_value)
                                                row_dict[f'{trait}_CPK'] = cpk_float
                                                # 判断是否异常
                                                row_dict[f'{trait}_状态'] = '异常' if (cpk_float < cpk_min or cpk_float > cpk_max) else '正常'
                                            except:
                                                row_dict[f'{trait}_CPK'] = '-'
                                                row_dict[f'{trait}_状态'] = '-'
                                    
                                    results_list.append(row_dict)
                        
                        if results_list:
                            results_df = pd.DataFrame(results_list)
                            
                            # 筛选异常记录
                            status_columns = [col for col in results_df.columns if col.endswith('_状态')]
                            if status_columns:
                                mask = results_df[status_columns].apply(lambda row: '异常' in row.values, axis=1)
                                abnormal_results = results_df[mask]
                                
                                if len(abnormal_results) > 0:
                                    st.warning(f"发现 {len(abnormal_results)} 个区域/时间段存在CPK异常")
                                    st.dataframe(abnormal_results, use_container_width=True)
                                    
                                    # 下载异常结果
                                    csv = abnormal_results.to_csv(index=False, encoding='utf-8-sig')
                                    st.download_button(
                                        label="下载异常数据",
                                        data=csv,
                                        file_name=f"cpk_period_abnormal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime='text/csv'
                                    )
                                else:
                                    st.success("未发现CPK异常数据")
                            else:
                                st.error("无法计算CPK值")
                        else:
                            st.warning("没有足够的数据进行分析")
                    
                    elif filter_object == "按牧场":
                        # 按牧场和时间段分组计算
                        results = stats_calculator.calculate_statistics(cpk_df, coefficients)
                        
                        # 筛选CPK异常
                        cpk_columns = [col for col in results.columns if col.endswith('_cpk')]
                        
                        # 创建异常标记
                        for col in cpk_columns:
                            results[f'{col}_异常'] = results[col].apply(
                                lambda x: '异常' if pd.notna(x) and (x < cpk_min or x > cpk_max) else '正常'
                            )
                        
                        # 筛选包含异常的行
                        abnormal_columns = [col for col in results.columns if col.endswith('_异常')]
                        mask = results[abnormal_columns].apply(lambda row: '异常' in row.values, axis=1)
                        abnormal_results = results[mask]
                        
                        if len(abnormal_results) > 0:
                            st.warning(f"发现 {len(abnormal_results)} 条CPK异常记录")
                            st.dataframe(abnormal_results, use_container_width=True)
                            
                            # 下载异常结果
                            csv = abnormal_results.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                label="下载异常数据",
                                data=csv,
                                file_name=f"cpk_period_farm_abnormal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime='text/csv'
                            )
                        else:
                            st.success("未发现CPK异常数据")
                else:
                    # 整体分析（原有逻辑）
                    st.info("整体分析模式已移除，请选择单月分析")

else:
    # 默认数据路径
    default_path = "/Users/Shared/Files From d.localized/projects/cpk_data_analyze/data/2024年全年数据.xlsx"
    if os.path.exists(default_path):
        if st.button("使用默认数据文件"):
            st.session_state['use_default'] = True
            st.rerun()
    
    # 检查是否需要加载默认数据
    if 'use_default' in st.session_state and st.session_state['use_default']:
        with st.spinner('正在读取数据（首次加载需要一些时间）...'):
            df = data_processor.load_data(default_path)
            if df is not None:
                st.session_state['df'] = df
                st.session_state['use_default'] = False
                st.rerun()