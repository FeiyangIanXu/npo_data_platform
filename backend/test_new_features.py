#!/usr/bin/env python3
"""
测试新功能的脚本
"""

import requests
import json

BASE_URL = "http://localhost:8001/api"

def test_search_api():
    """测试搜索API"""
    print("=== 测试搜索API ===")
    
    # 基本搜索
    response = requests.get(f"{BASE_URL}/search", params={
        "q": "hospital",
        "fields": "name,address",
        "limit": 5
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 搜索成功: 找到 {data['count']} 条结果")
        for item in data['results'][:2]:
            print(f"  - {item.get('campus', 'N/A')}")
    else:
        print(f"❌ 搜索失败: {response.status_code} - {response.text}")

def test_filter_api():
    """测试筛选API"""
    print("\n=== 测试筛选API ===")
    
    # 获取筛选字段信息
    response = requests.get(f"{BASE_URL}/filter/fields")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 获取筛选字段成功: {len(data['fields'])} 个字段")
    else:
        print(f"❌ 获取筛选字段失败: {response.status_code}")
        return
    
    # 测试高级筛选
    filter_data = {
        "conditions": [
            {"field": "st", "operator": "equals", "value": "CA"},
            {"field": "part_i_summary_12_total_revenue_cy", "operator": "greater_than", "value": 1000000}
        ],
        "logic": "AND",
        "limit": 5
    }
    
    response = requests.post(f"{BASE_URL}/filter", json=filter_data)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 筛选成功: 找到 {data['filtered_count']} 条结果")
        for item in data['results'][:2]:
            print(f"  - {item.get('campus', 'N/A')} (收入: {item.get('part_i_summary_12_total_revenue_cy', 'N/A')})")
    else:
        print(f"❌ 筛选失败: {response.status_code} - {response.text}")

def test_export_api():
    """测试导出API"""
    print("\n=== 测试导出API ===")
    
    # 获取导出状态
    response = requests.get(f"{BASE_URL}/export/status")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 导出状态: 总记录数 {data['total_records']}")
        print(f"  支持格式: {', '.join(data['supported_formats'])}")
    else:
        print(f"❌ 获取导出状态失败: {response.status_code}")
        return
    
    # 测试JSON导出（小数据量）
    export_data = {
        "filters": {"st": "CA"},
        "limit": 10
    }
    
    response = requests.post(f"{BASE_URL}/export/json", json=export_data)
    if response.status_code == 200:
        print("✅ JSON导出成功")
        # 检查响应头
        content_disposition = response.headers.get('Content-Disposition', '')
        print(f"  文件名: {content_disposition}")
    else:
        print(f"❌ JSON导出失败: {response.status_code} - {response.text}")

def test_helpers():
    """测试工具函数"""
    print("\n=== 测试工具函数 ===")
    
    try:
        from utils.helpers import format_currency, format_number, get_database_stats
        
        # 测试格式化函数
        print(f"✅ 货币格式化: {format_currency(1234567)}")
        print(f"✅ 数字格式化: {format_number(1234567)}")
        
        # 测试数据库统计
        stats = get_database_stats()
        if "error" not in stats:
            print(f"✅ 数据库统计: {stats['total_records']} 条记录")
        else:
            print(f"❌ 数据库统计失败: {stats['error']}")
            
    except ImportError as e:
        print(f"❌ 导入工具函数失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试新功能...")
    
    try:
        test_search_api()
        test_filter_api()
        test_export_api()
        test_helpers()
        
        print("\n🎉 所有测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务器，请确保后端正在运行在端口8001")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    main() 