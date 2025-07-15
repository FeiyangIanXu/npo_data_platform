#!/usr/bin/env python3
"""
紧急修复脚本 - 快速重建数据库基本结构
当正常数据管道失败时使用
"""

import sqlite3
import os
import pandas as pd

def emergency_database_fix():
    """紧急修复数据库"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'irs.db')
    csv_path = os.path.join(script_dir, 'data', 'nonprofits_100.csv')
    
    print("🚨 紧急数据库修复开始...")
    print("=" * 50)
    
    # 删除损坏的数据库文件
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️  已删除损坏的数据库文件")
    
    # 检查CSV文件
    if not os.path.exists(csv_path):
        print("❌ CSV文件不存在，创建示例数据...")
        create_sample_data(csv_path)
    
    print(f"📁 CSV文件: {csv_path}")
    print(f"📊 CSV文件大小: {os.path.getsize(csv_path)} bytes")
    
    try:
        # 读取CSV文件（简化方式）
        print("📖 读取CSV文件...")
        df = pd.read_csv(csv_path, skiprows=5, header=None)
        
        # 简单的列名设置
        if len(df.columns) > 20:
            # 给前面几列设置基本的列名
            column_names = ['id', 'campus', 'address', 'city', 'st', 'zip', 'ein']
            column_names.extend([f'col_{i}' for i in range(7, len(df.columns))])
            df.columns = column_names[:len(df.columns)]
        
        # 创建示例的标准化列
        print("📅 创建标准化日期列...")
        df['fiscal_year'] = 2023  # 默认年份
        df['fiscal_month'] = 12   # 默认月份
        
        # 如果有类似财年的列，尝试解析
        for col in df.columns:
            if 'fy' in col.lower() or 'fiscal' in col.lower():
                print(f"🔍 发现可能的财年列: {col}")
                # 简单解析：提取年份
                for idx, value in enumerate(df[col]):
                    if pd.notna(value):
                        value_str = str(value)
                        if '2022' in value_str:
                            df.at[idx, 'fiscal_year'] = 2022
                        elif '2023' in value_str:
                            df.at[idx, 'fiscal_year'] = 2023
                        elif '2024' in value_str:
                            df.at[idx, 'fiscal_year'] = 2024
                        
                        # 提取月份
                        if '/' in value_str:
                            parts = value_str.split('/')
                            if len(parts) >= 2:
                                try:
                                    month = int(parts[0])
                                    if 1 <= month <= 12:
                                        df.at[idx, 'fiscal_month'] = month
                                except:
                                    pass
                break
        
        # 连接数据库并写入
        print("💾 写入数据库...")
        conn = sqlite3.connect(db_path)
        df.to_sql('nonprofits', conn, if_exists='replace', index=False)
        conn.close()
        
        print(f"✅ 成功写入 {len(df)} 行数据")
        print(f"✅ 包含 {len(df.columns)} 列")
        print("✅ 包含标准化的 fiscal_year 和 fiscal_month 列")
        
        # 验证结果
        verify_database(db_path)
        
        return True
        
    except Exception as e:
        print(f"❌ 紧急修复失败: {e}")
        return False

def create_sample_data(csv_path):
    """创建示例数据文件"""
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    sample_data = """Header1,Header2,Header3,Header4,Header5
Row2,Part1,Part2,Part3,Part4
Row3,Line1,Line2,Line3,Line4
Row4,Desc1,Desc2,Desc3,Desc4
Row5,Year1,Year2,Year3,Year4
1,Test Org 1,123 Main St,New York,NY,10001,12-1234567,6/2023
2,Test Org 2,456 Oak Ave,Los Angeles,CA,90001,98-7654321,12/2022
3,Test Org 3,789 Pine Rd,Chicago,IL,60001,45-9876543,9/2023
"""
    
    with open(csv_path, 'w') as f:
        f.write(sample_data)
    
    print(f"📝 已创建示例CSV文件: {csv_path}")

def verify_database(db_path):
    """验证数据库"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📋 数据库表: {[t[0] for t in tables]}")
        
        # 检查数据
        cursor.execute("SELECT COUNT(*) FROM nonprofits")
        count = cursor.fetchone()[0]
        print(f"📊 记录数: {count}")
        
        # 检查标准化列
        cursor.execute("SELECT DISTINCT fiscal_year FROM nonprofits WHERE fiscal_year IS NOT NULL")
        years = cursor.fetchall()
        print(f"📅 可用年份: {[y[0] for y in years]}")
        
        cursor.execute("SELECT DISTINCT fiscal_month FROM nonprofits WHERE fiscal_month IS NOT NULL")
        months = cursor.fetchall()
        print(f"📅 可用月份: {[m[0] for m in months]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")

if __name__ == "__main__":
    print("🚨 开始紧急数据库修复...")
    
    success = emergency_database_fix()
    
    if success:
        print("\n" + "🎉 紧急修复完成！" + "=" * 30)
        print("✅ 数据库已重建")
        print("✅ 基本功能应该恢复")
        print("🚀 现在可以启动服务器: python backend/main.py")
        print("🌐 然后测试前端功能")
    else:
        print("\n" + "❌ 紧急修复失败" + "=" * 30)
        print("💡 请检查CSV文件是否存在")
        print("💡 或者手动提供数据文件") 