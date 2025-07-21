import pandas as pd
import numpy as np

class StatisticsCalculator:
    def __init__(self):
        self.traits = ['脂肪', '蛋白', '干物质', '酸度', '体细胞']
        self.display_traits = ['脂肪', '蛋白', '干物质', '酸度', '体细胞']
    
    def calculate_statistics(self, df, coefficients):
        """计算所有统计指标"""
        # 清理数据
        numeric_columns = self.traits
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 按月份和牧场分组
        results = []
        
        # 获取所有唯一的年月和奶源地组合
        if '年月' in df.columns and '奶源地名称' in df.columns:
            groups = df.groupby(['年月', '奶源地名称', '区域', '地区'])
        else:
            # 如果没有年月列，则只按奶源地分组
            groups = df.groupby(['奶源地名称', '区域', '地区'])
        
        for group_keys, group_data in groups:
            if len(group_keys) == 4:
                period, farm, region, area = group_keys
            else:
                farm, region, area = group_keys
                period = '全部'
            
            # 计算每个性状的统计指标
            row_data = {
                '时间': str(period),
                '区域': region,
                '地区': area,
                '奶源地': farm
            }
            
            for trait, display_trait in zip(self.traits, self.display_traits):
                if trait in group_data.columns:
                    trait_data = group_data[trait].dropna()
                    
                    if len(trait_data) > 0:
                        # 使用原始数据计算，避免累积舍入误差
                        # 计算基本统计量（不提前舍入）
                        # 使用ddof=1计算样本标准差（与Excel的STDEV.S相同）
                        sigma_raw = trait_data.std(ddof=1)
                        mean_raw = trait_data.mean()
                        
                        # 获取系数
                        if trait == '酸度':
                            # 酸度特殊处理
                            acid_min = coefficients.get('酸度_min', 12)
                            acid_max = coefficients.get('酸度_max', 17.5)
                            process_diff_raw = min(mean_raw - acid_min, acid_max - mean_raw)
                            tolerance = coefficients.get('酸度_tolerance', 5.5)
                        else:
                            coef = coefficients.get(trait, 0)
                            process_diff_raw = abs(mean_raw - coef)
                            tolerance = None
                        
                        # 使用原始值计算其他指标
                        six_sigma_raw = sigma_raw * 6
                        three_sigma_raw = sigma_raw * 3
                        
                        # 计算CPK（使用原始值）
                        if three_sigma_raw > 0:
                            cpk_raw = process_diff_raw / three_sigma_raw
                        else:
                            cpk_raw = 0
                        
                        # 计算CP（使用原始值）
                        if tolerance and six_sigma_raw > 0:
                            cp_raw = tolerance / six_sigma_raw
                        else:
                            cp_raw = None
                        
                        # 最后统一舍入显示
                        row_data[f'{display_trait}_σ'] = round(sigma_raw, 3)
                        row_data[f'{display_trait}_均值'] = round(mean_raw, 3)
                        row_data[f'{display_trait}_过程值差值'] = round(process_diff_raw, 3)
                        row_data[f'{display_trait}_6σ'] = round(six_sigma_raw, 3)
                        row_data[f'{display_trait}_3σ'] = round(three_sigma_raw, 3)
                        row_data[f'{display_trait}_cpk'] = round(cpk_raw, 3)
                        row_data[f'{display_trait}_公差'] = round(tolerance, 3) if tolerance else '/'
                        row_data[f'{display_trait}_cp'] = round(cp_raw, 3) if cp_raw else '/'
                    else:
                        # 没有数据时填充空值
                        for suffix in ['σ', '均值', '过程值差值', '6σ', '3σ', 'cpk', '公差', 'cp']:
                            row_data[f'{display_trait}_{suffix}'] = np.nan
            
            results.append(row_data)
        
        # 转换为DataFrame
        results_df = pd.DataFrame(results)
        
        # 排序
        if '时间' in results_df.columns:
            results_df = results_df.sort_values(['时间', '区域', '奶源地'])
        
        return results_df
    
    def calculate_summary_table(self, df, coefficients):
        """计算汇总表格（横向展示）"""
        # 清理数据
        numeric_columns = self.traits
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 准备结果表格
        result_data = {
            '能力分析': ['σ（标准差）', 'X（平均值）', '过程值差值', '6σ', '3σ', 'cpk', '公差', 'cp']
        }
        
        for trait, display_trait in zip(self.traits, self.display_traits):
            if trait in df.columns:
                trait_data = df[trait].dropna()
                
                if len(trait_data) > 0:
                    # 使用原始数据计算，避免累积舍入误差
                    # 计算基本统计量（不提前舍入）
                    # 使用ddof=1计算样本标准差（与Excel的STDEV.S相同）
                    sigma_raw = trait_data.std(ddof=1)
                    mean_raw = trait_data.mean()
                    
                    # 获取系数
                    if trait == '酸度':
                        # 酸度特殊处理
                        acid_min = coefficients.get('酸度_min', 12)
                        acid_max = coefficients.get('酸度_max', 17.5)
                        process_diff_raw = min(mean_raw - acid_min, acid_max - mean_raw)
                        tolerance = coefficients.get('酸度_tolerance', 5.5)
                    else:
                        coef = coefficients.get(trait, 0)
                        process_diff_raw = abs(mean_raw - coef)
                        tolerance = None
                    
                    # 使用原始值计算其他指标
                    six_sigma_raw = sigma_raw * 6
                    three_sigma_raw = sigma_raw * 3
                    
                    # 计算CPK（使用原始值）
                    if three_sigma_raw > 0:
                        cpk_raw = process_diff_raw / three_sigma_raw
                    else:
                        cpk_raw = 0
                    
                    # 计算CP（使用原始值）
                    if tolerance and six_sigma_raw > 0:
                        cp_raw = tolerance / six_sigma_raw
                    else:
                        cp_raw = None
                    
                    # 最后统一舍入显示
                    result_data[display_trait] = [
                        f"{sigma_raw:.3f}",
                        f"{mean_raw:.3f}",
                        f"{process_diff_raw:.3f}",
                        f"{six_sigma_raw:.3f}",
                        f"{three_sigma_raw:.3f}",
                        f"{cpk_raw:.3f}",
                        f"{tolerance:.1f}" if tolerance else "/",
                        f"{cp_raw:.3f}" if cp_raw else "/"
                    ]
                else:
                    result_data[display_trait] = ['-'] * 8
            else:
                result_data[display_trait] = ['-'] * 8
        
        # 转换为DataFrame
        summary_df = pd.DataFrame(result_data)
        return summary_df