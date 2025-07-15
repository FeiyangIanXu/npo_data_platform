#!/usr/bin/env python3
"""
数据库诊断脚本
检查数据库文件和表的状态，帮助快速定位问题
"""

import sqlite3
import os

def diagnose_database():
    """诊断数据库状态"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'irs.db')
    
    print("🔍 数据库诊断开始...")
    print("=" * 50)
    
    # 检查数据库文件是否存在
    print(f"📁 数据库路径: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在！")
        print("💡 解决方案：")
        print("   1. 运行: python backend/data_pipeline.py")
        print("   2. 确保CSV数据文件存在于 backend/data/ 目录")
        return False
    
    print("✅ 数据库文件存在")
    print(f"📊 文件大小: {os.path.getsize(db_path)} bytes")
    
    # 检查数据库连接
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✅ 数据库连接成功")
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("❌ 数据库中没有任何表！")
            print("💡 解决方案：重新运行数据管道")
            conn.close()
            return False
        
        print(f"📋 数据库中的表: {[table[0] for table in tables]}")
        
        # 检查 nonprofits 表
        if ('nonprofits',) not in tables:
            print("❌ 缺少 nonprofits 表！")
            print("💡 解决方案：重新运行数据管道")
            conn.close()
            return False
        
        print("✅ nonprofits 表存在")
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(nonprofits)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"📊 表中列数: {len(columns)}")
        
        # 检查关键的标准化列
        required_columns = ['fiscal_year', 'fiscal_month']
        missing_columns = []
        
        for col in required_columns:
            if col in column_names:
                print(f"✅ {col} 列存在")
            else:
                print(f"❌ {col} 列缺失")
                missing_columns.append(col)
        
        if missing_columns:
            print(f"💡 缺少标准化列: {missing_columns}")
            print("💡 解决方案：重新运行数据管道以创建标准化列")
            conn.close()
            return False
        
        # 检查数据量
        cursor.execute("SELECT COUNT(*) FROM nonprofits")
        total_count = cursor.fetchone()[0]
        print(f"📊 总记录数: {total_count}")
        
        if total_count == 0:
            print("❌ 表中没有数据！")
            print("💡 解决方案：重新运行数据管道以导入数据")
            conn.close()
            return False
        
        # 检查标准化列的数据质量
        cursor.execute("SELECT COUNT(*) FROM nonprofits WHERE fiscal_year IS NOT NULL")
        year_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM nonprofits WHERE fiscal_month IS NOT NULL")
        month_count = cursor.fetchone()[0]
        
        print(f"📊 有效 fiscal_year 记录: {year_count} ({year_count/total_count*100:.1f}%)")
        print(f"📊 有效 fiscal_month 记录: {month_count} ({month_count/total_count*100:.1f}%)")
        
        # 显示一些示例数据
        cursor.execute("SELECT fiscal_year, fiscal_month FROM nonprofits WHERE fiscal_year IS NOT NULL LIMIT 5")
        samples = cursor.fetchall()
        
        if samples:
            print("📋 数据示例:")
            for year, month in samples:
                print(f"   财年: {year}, 月份: {month}")
        
        conn.close()
        
        print("\n" + "=" * 50)
        print("✅ 数据库诊断完成 - 一切正常！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接或查询失败: {e}")
        print("💡 解决方案：重新运行数据管道")
        return False

def check_csv_data():
    """检查CSV源数据文件"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'data', 'nonprofits_100.csv')
    
    print("\n📁 检查CSV源数据文件...")
    print(f"📍 CSV路径: {csv_path}")
    
    if not os.path.exists(csv_path):
        print("❌ CSV文件不存在！")
        print("💡 请确保 nonprofits_100.csv 文件存在于 backend/data/ 目录")
        return False
    
    print("✅ CSV文件存在")
    print(f"📊 文件大小: {os.path.getsize(csv_path)} bytes")
    return True

if __name__ == "__main__":
    print("🚀 开始诊断数据库和源文件...")
    
    # 检查CSV文件
    csv_ok = check_csv_data()
    
    # 检查数据库
    db_ok = diagnose_database()
    
    print("\n" + "🎯 诊断总结 " + "=" * 40)
    
    if csv_ok and db_ok:
        print("✅ 所有检查都通过！系统应该正常工作。")
        print("🚀 现在可以启动服务器测试功能。")
    else:
        print("❌ 发现问题，请按照上述解决方案修复。")
        print("\n🔧 修复步骤：")
        print("1. 确保CSV文件存在: backend/data/nonprofits_100.csv")
        print("2. 重新运行数据管道: python backend/data_pipeline.py")
        print("3. 等待数据管道完成（应该看到成功信息）")
        print("4. 重新启动服务器: python backend/main.py") 