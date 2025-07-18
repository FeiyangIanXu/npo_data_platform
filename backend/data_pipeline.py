import pandas as pd
import sqlite3
import re
import os
from typing import Optional, Tuple
# 不再需要旧的日期解析函数，现在使用内置的 parse_date 函数

def sanitize_name(name):
    """清理列名：将字符串转为小写，用下划线替换所有空格和特殊字符。"""
    s = str(name).lower()
    s = re.sub(r'[^a-z0-9_]+', '_', s)
    s = s.strip('_')
    s = re.sub(r'_+', '_', s)
    return s

def is_pure_numeric(value):
    """检查值是否为纯数字"""
    if pd.isna(value) or str(value).strip() == '':
        return False
    return str(value).strip().isdigit()

def parse_date(date_str: str) -> Optional[Tuple[int, int]]:
    """
    从各种不规则的日期字符串中解析出（年份, 月份）。
    能够处理 "M/YYYY", "YYYY/MM/DD", "M/D/YYYY" 等格式。
    这是彻底解决日期问题的核心函数。
    """
    if pd.isna(date_str):
        return None
    date_str = str(date_str).strip()

    # 格式 1: "M/YYYY" 或 "MM/YYYY" (e.g., "6/2023", "12/2022")
    match = re.fullmatch(r'(\d{1,2})/(\d{4})', date_str)
    if match:
        month, year = map(int, match.groups())
        return year, month

    # 格式 2: "YYYY/MM/DD" (e.g., "2022/12/31")
    match = re.fullmatch(r'(\d{4})/(\d{1,2})/\d{1,2}', date_str)
    if match:
        year, month = map(int, match.groups())
        return year, month

    # 格式 3: "M/D/YYYY" (e.g., "6/30/2023")
    match = re.fullmatch(r'(\d{1,2})/\d{1,2}/(\d{4})', date_str)
    if match:
        month, year = int(match.group(1)), int(match.group(2))
        return year, month

    # 格式 4: "YYYY-MM-DD" (e.g., "2023-06-30")
    match = re.fullmatch(r'(\d{4})-(\d{1,2})-\d{1,2}', date_str)
    if match:
        year, month = map(int, match.groups())
        return year, month

    # 如果都匹配不上，返回None
    return None

def process_four_row_semantic_header(csv_file_path):
    """
    处理四行语义化表头并返回处理后的数据和新列名
    """
    print("正在读取CSV文件的表头信息...")
    
    # 读取前5行来获取表头信息（第2、3、4、5行，即索引1、2、3、4）
    header_rows = pd.read_csv(csv_file_path, nrows=5, header=None)
    
    # 提取四行表头（索引1、2、3、4对应第2、3、4、5行）
    row2_part_info = header_rows.iloc[1]      # 第2行：Part信息
    row3_line_numbers = header_rows.iloc[2]   # 第3行：行号
    row4_field_desc = header_rows.iloc[3]     # 第4行：字段描述
    row5_year_info = header_rows.iloc[4]      # 第5行：年份信息
    
    print(f"  > 表头行数: {len(header_rows)}")
    print(f"  > 总列数: {len(row2_part_info)}")
    
    # 处理第2行：向前填充
    print("正在处理第2行（Part信息）：执行向前填充...")
    row2_filled = row2_part_info.fillna(method='ffill')
    
    # 处理第3行：只保留纯数字
    print("正在处理第3行（行号）：只保留纯数字...")
    row3_processed = []
    for value in row3_line_numbers:
        if is_pure_numeric(value):
            row3_processed.append(str(value).strip())
        else:
            row3_processed.append('')
    
    # 第4行和第5行保持原样
    print("第4行（字段描述）和第5行（年份信息）保持原样...")
    
    # 创建新的列名
    print("正在组合创建新列名...")
    new_column_names = []
    
    for i in range(len(row2_filled)):
        # 获取各行的值
        part_info = str(row2_filled.iloc[i]) if pd.notna(row2_filled.iloc[i]) and str(row2_filled.iloc[i]).strip() != '' else ''
        line_num = row3_processed[i] if i < len(row3_processed) else ''
        field_desc = str(row4_field_desc.iloc[i]) if pd.notna(row4_field_desc.iloc[i]) and str(row4_field_desc.iloc[i]).strip() != '' else ''
        year_info = str(row5_year_info.iloc[i]) if pd.notna(row5_year_info.iloc[i]) and str(row5_year_info.iloc[i]).strip() != '' else ''
        
        # 组合基础列名：(第2行内容)_(第3行内容)_(第4行内容)
        base_parts = []
        if part_info:
            base_parts.append(part_info)
        if line_num:
            base_parts.append(line_num)
        if field_desc:
            base_parts.append(field_desc)
        
        base_name = '_'.join(base_parts) if base_parts else f'column_{i}'
        
        # 根据第5行添加年份后缀
        year_suffix = ''
        if year_info.upper() == 'CY':
            year_suffix = '_cy'
        elif year_info.upper() == 'PY':
            year_suffix = '_py'
        
        final_name = base_name + year_suffix
        
        # 最终净化
        final_name = sanitize_name(final_name)
        new_column_names.append(final_name)
    
    print(f"  > 成功创建 {len(new_column_names)} 个语义化列名")
    
    # 读取真正的数据（从第6行开始，跳过前5行）
    print("正在读取真正的数据内容（从第6行开始）...")
    data_df = pd.read_csv(csv_file_path, skiprows=5, header=None)
    
    # 确保列名数量与数据列数匹配
    if len(new_column_names) != len(data_df.columns):
        print(f"警告：列名数量 ({len(new_column_names)}) 与数据列数 ({len(data_df.columns)}) 不匹配")
        # 调整以匹配实际数据列数
        if len(new_column_names) > len(data_df.columns):
            new_column_names = new_column_names[:len(data_df.columns)]
        else:
            for i in range(len(new_column_names), len(data_df.columns)):
                new_column_names.append(f'extra_column_{i}')
    
    # 应用新的语义化列名
    data_df.columns = new_column_names
    print(f"  > 成功读取 {len(data_df)} 行数据")
    
    return data_df, new_column_names

def run_data_pipeline():
    """主数据处理管道函数，负责将CSV数据清洗并存入SQLite数据库。"""
    # --- 配置区 ---
    # 获取脚本所在目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(script_dir, 'data', 'nonprofits_100.csv')
    db_path = os.path.join(script_dir, 'irs.db')  # 数据库文件在backend目录
    table_name = 'nonprofits'

    print("=== 开始执行四行语义化表头数据管道 ===")
    print(f"脚本目录: {script_dir}")
    print(f"源文件: {csv_file_path}")
    print(f"目标数据库: {db_path}")
    print(f"目标表名: {table_name}")
    print("-" * 50)

    # 步骤1：处理四行语义化表头并读取数据
    print("步骤 1/4: 处理四行语义化表头...")
    try:
        if not os.path.exists(csv_file_path):
            print(f"错误：找不到文件 '{csv_file_path}'")
            print(f"请确认文件是否存在于: {os.path.dirname(csv_file_path)}")
            return
        
        df, column_names = process_four_row_semantic_header(csv_file_path)
        
    except Exception as e:
        print(f"错误：处理表头时发生异常: {e}")
        return

    # 步骤2：删除第一个无用列
    print("\n步骤 2/4: 删除第一个无用列...")
    if len(df.columns) > 0:
        first_column = str(df.columns[0])
        print(f"  > 删除第一列: '{first_column}'")
        df = df.drop(columns=[first_column])
        print(f"  > 删除后剩余列数: {len(df.columns)}")
    else:
        print("  > 警告：没有列可删除")

    # 步骤3：处理重复列名和空列名
    print("\n步骤 3/4: 处理重复列名和空列名...")
    
    # 处理重复的列名
    original_columns = list(df.columns)
    seen = {}
    new_columns = []
    
    for col in original_columns:
        if col in seen:
            seen[col] += 1
            new_col = f"{col}_{seen[col]}"
            new_columns.append(new_col)
            print(f"  > 重复列名 '{col}' 重命名为 '{new_col}'")
        else:
            seen[col] = 0
            new_columns.append(col)
    
    df.columns = new_columns
    
    # 删除空列名的列
    empty_cols = [col for col in df.columns if str(col).strip() == '']
    if empty_cols:
        print(f"  > 删除空列名的列: {len(empty_cols)} 个")
        df = df.drop(columns=empty_cols)
    
    print(f"  > 最终列数: {len(df.columns)}")

    # 关键步骤：标准化财年和月份（V2版本 - 彻底治本）
    print("\n步骤 4/5: 标准化财年和月份（治本方案）...")
    
    # 查找财年结束日期列
    fy_end_column_name = None
    for col in df.columns:
        if 'fy_ending' in col.lower() or 'fiscal' in col.lower():
            fy_end_column_name = col
            break
    
    if fy_end_column_name:
        print(f"  > 找到财年结束日期列: '{fy_end_column_name}'")
        print(f"  > 正在应用强大的日期解析逻辑...")
        
        # 应用我们强大的解析函数
        parsed_dates = df[fy_end_column_name].apply(parse_date)

        # 创建新的、干净的列
        df['fiscal_year'] = parsed_dates.apply(lambda x: x[0] if x else None).astype('Int64')
        df['fiscal_month'] = parsed_dates.apply(lambda x: x[1] if x else None).astype('Int64')

        print(f"  > 成功创建 'fiscal_year' 和 'fiscal_month' 列")
        
        # 数据标准化抽样检查
        print(f"  > 数据标准化抽样检查:")
        sample_data = df[[fy_end_column_name, 'fiscal_year', 'fiscal_month']].head(10)
        for idx, row in sample_data.iterrows():
            original = row[fy_end_column_name]
            year = row['fiscal_year']
            month = row['fiscal_month']
            print(f"    '{original}' -> FY:{year}, Month:{month}")
        
        # 数据质量统计
        print(f"  > 数据质量统计:")
        total_records = len(df)
        successful_parses = df['fiscal_year'].notna().sum()
        print(f"    总记录数: {total_records}")
        print(f"    成功解析: {successful_parses}")
        print(f"    解析成功率: {successful_parses/total_records*100:.1f}%")
        
        # 年份分布
        print(f"  > 财年分布:")
        fiscal_year_counts = df['fiscal_year'].value_counts().head(5)
        for year, count in fiscal_year_counts.items():
            print(f"    FY {year}: {count} 条记录")
            
        # 月份分布
        print(f"  > 财报结束月份分布:")
        fiscal_month_counts = df['fiscal_month'].value_counts().sort_index()
        for month, count in fiscal_month_counts.items():
            print(f"    {month}月: {count} 条记录")
            
    else:
        print(f"  > 严重警告: 未找到财年结束日期列，日期标准化失败！")
        # 尝试查找其他可能的日期列
        date_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['date', 'year', 'period'])]
        if date_columns:
            print(f"  > 发现可能的日期列: {date_columns[:3]}")
        return

    # 步骤5：连接数据库并彻底重建数据
    print(f"\n步骤 5/5: 连接数据库并彻底重建数据...")
    try:
        # 删除旧数据库文件以确保完全重建
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"  > 已删除旧的数据库文件: {db_path}")
            
        print(f"  > 正在连接新数据库: {db_path}")
        conn = sqlite3.connect(db_path)
        
        print(f"  > 正在写入表 '{table_name}' 包含标准化的日期列...")
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        conn.close()
        print(f"  > 成功写入 {len(df)} 行数据，{len(df.columns)} 列")
        print(f"  > 其中包含干净的 'fiscal_year' 和 'fiscal_month' 列")
        
    except Exception as e:
        print(f"错误：写入数据库时发生异常: {e}")
        return

    print("\n" + "=" * 60)
    print("[OK] V2版数据管道执行成功！")
    print(f"[OK] 数据库 {db_path} 已被全新的、干净的数据覆盖")
    print("[OK] 日期标准化完成：fiscal_year 和 fiscal_month 列已创建")
    print("=" * 60)

# 脚本入口点
if __name__ == "__main__":
    run_data_pipeline()