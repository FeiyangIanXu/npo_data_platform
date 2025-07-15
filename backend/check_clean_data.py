#!/usr/bin/env python3
"""
验证数据库中的标准化列脚本
检查 fiscal_year 和 fiscal_month 列是否正确创建
"""

import sqlite3
import os

def check_clean_data():
    """检查数据库中的干净数据列"""
    
    # 获取数据库路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'irs.db')
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    print("🔍 检查数据库中的标准化列...")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表结构
        print("📋 检查表结构...")
        cursor.execute("PRAGMA table_info(nonprofits)")
        columns = cursor.fetchall()
        
        # 查找关键列
        fiscal_year_exists = False
        fiscal_month_exists = False
        original_date_column = None
        
        for col in columns:
            col_name = col[1]  # 列名在索引1
            if col_name == 'fiscal_year':
                fiscal_year_exists = True
            elif col_name == 'fiscal_month':
                fiscal_month_exists = True
            elif 'fy_ending' in col_name.lower():
                original_date_column = col_name
        
        print(f"  ✅ fiscal_year 列存在: {fiscal_year_exists}")
        print(f"  ✅ fiscal_month 列存在: {fiscal_month_exists}")
        print(f"  📅 原始日期列: {original_date_column}")
        
        if not (fiscal_year_exists and fiscal_month_exists):
            print("❌ 标准化列不存在！请重新运行数据管道。")
            return
        
        # 显示数据对比
        print(f"\n📊 数据对比（原始 vs 标准化）...")
        print("-" * 60)
        
        if original_date_column:
            query = f"""
            SELECT 
                "{original_date_column}" as original_date,
                fiscal_year,
                fiscal_month
            FROM nonprofits 
            LIMIT 20
            """
        else:
            query = """
            SELECT 
                'N/A' as original_date,
                fiscal_year,
                fiscal_month
            FROM nonprofits 
            LIMIT 20
            """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"{'原始日期':<15} {'标准化年份':<10} {'标准化月份':<10}")
        print("-" * 40)
        
        for row in results:
            original = str(row[0]) if row[0] else 'NULL'
            year = str(row[1]) if row[1] else 'NULL'
            month = str(row[2]) if row[2] else 'NULL'
            print(f"{original:<15} {year:<10} {month:<10}")
        
        # 统计信息
        print(f"\n📈 数据质量统计...")
        print("-" * 30)
        
        # 总记录数
        cursor.execute("SELECT COUNT(*) FROM nonprofits")
        total_count = cursor.fetchone()[0]
        
        # 成功解析的记录数
        cursor.execute("SELECT COUNT(*) FROM nonprofits WHERE fiscal_year IS NOT NULL")
        year_success = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM nonprofits WHERE fiscal_month IS NOT NULL")
        month_success = cursor.fetchone()[0]
        
        print(f"总记录数: {total_count}")
        print(f"fiscal_year 解析成功: {year_success} ({year_success/total_count*100:.1f}%)")
        print(f"fiscal_month 解析成功: {month_success} ({month_success/total_count*100:.1f}%)")
        
        # 年份分布
        print(f"\n📅 财年分布:")
        cursor.execute("SELECT fiscal_year, COUNT(*) FROM nonprofits WHERE fiscal_year IS NOT NULL GROUP BY fiscal_year ORDER BY fiscal_year DESC")
        year_dist = cursor.fetchall()
        for year, count in year_dist[:5]:  # 显示前5个
            print(f"  FY {year}: {count} 条记录")
        
        # 月份分布
        print(f"\n📅 财报结束月份分布:")
        cursor.execute("SELECT fiscal_month, COUNT(*) FROM nonprofits WHERE fiscal_month IS NOT NULL GROUP BY fiscal_month ORDER BY fiscal_month")
        month_dist = cursor.fetchall()
        for month, count in month_dist:
            print(f"  {month}月: {count} 条记录")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ 数据检查完成！标准化列已正确创建。")
        print("💡 提示：API 现在使用的是 fiscal_year 和 fiscal_month 列，而不是原始的混乱日期列。")
        
    except Exception as e:
        print(f"❌ 检查数据时发生错误: {e}")

if __name__ == "__main__":
    check_clean_data() 