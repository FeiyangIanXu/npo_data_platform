import pandas as pd
import sqlite3
import re
import os

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

    # 步骤4：连接数据库并写入数据
    print(f"\n步骤 4/4: 连接数据库并写入数据...")
    try:
        print(f"  > 正在连接数据库: {db_path}")
        conn = sqlite3.connect(db_path)
        
        print(f"  > 正在写入表 '{table_name}'（完全替换模式）...")
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        conn.close()
        print(f"  > 成功写入 {len(df)} 行数据，{len(df.columns)} 列")
        
    except Exception as e:
        print(f"错误：写入数据库时发生异常: {e}")
        return

    print("\n" + "=" * 50)
    print("[OK] 四行语义化表头数据管道执行成功！")
    print(f"[OK] 数据库 {db_path} 中的表 '{table_name}' 已更新")
    print("=" * 50)

# 脚本入口点
if __name__ == "__main__":
    run_data_pipeline()