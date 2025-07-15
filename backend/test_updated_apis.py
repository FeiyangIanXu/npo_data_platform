#!/usr/bin/env python3
"""
测试所有更新后的API端点
验证标准化列的使用是否正确
"""

import requests
import json
import os
import sys

# API基础URL
BASE_URL = "http://localhost:8000"

def test_api_endpoint(endpoint, method="GET", data=None, description=""):
    """测试API端点"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n🔍 测试: {description}")
    print(f"   {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 成功 - 状态码: {response.status_code}")
            return result
        else:
            print(f"   ❌ 失败 - 状态码: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ 连接失败 - 请确保后端服务正在运行")
        return None
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return None

def main():
    print("🚀 开始测试所有更新后的API端点...")
    print("=" * 60)
    
    # 1. 测试可用年份API（使用标准化列）
    print("\n📅 测试年份相关API...")
    years_result = test_api_endpoint(
        "/api/available-years", 
        description="获取可用年份（标准化 fiscal_year 列）"
    )
    
    available_year = None
    if years_result and years_result.get('years'):
        available_year = years_result['years'][0]
        print(f"   📊 可用年份: {years_result['years']}")
    
    # 2. 测试可用月份API（使用标准化列）
    if available_year:
        months_result = test_api_endpoint(
            f"/api/available-months?year={available_year}",
            description=f"获取{available_year}年的可用月份（标准化 fiscal_month 列）"
        )
        
        if months_result:
            print(f"   📊 {available_year}年可用月份: {months_result.get('months', [])}")
    
    # 3. 测试基础搜索API
    print("\n🔍 测试搜索相关API...")
    search_result = test_api_endpoint(
        "/api/search?q=hospital&limit=5",
        description="基础搜索功能"
    )
    
    if search_result:
        print(f"   📊 搜索结果数量: {search_result.get('count', 0)}")
    
    # 4. 测试高级搜索API（包含财年和月份）
    if available_year:
        advanced_search_result = test_api_endpoint(
            f"/api/search/advanced?fiscal_year={available_year}&limit=3",
            description=f"高级搜索 - 按财年{available_year}筛选"
        )
        
        if advanced_search_result:
            print(f"   📊 {available_year}年组织数量: {advanced_search_result.get('count', 0)}")
    
    # 5. 测试筛选API字段信息
    print("\n🎛️ 测试筛选相关API...")
    filter_fields_result = test_api_endpoint(
        "/api/filter/fields",
        description="获取筛选字段信息（包含标准化列）"
    )
    
    if filter_fields_result:
        fields = filter_fields_result.get('fields', {})
        if 'fiscal_year' in fields and 'fiscal_month' in fields:
            print(f"   ✅ 标准化字段已正确添加:")
            print(f"      - fiscal_year: {fields['fiscal_year']['description']}")
            print(f"      - fiscal_month: {fields['fiscal_month']['description']}")
        else:
            print(f"   ❌ 缺少标准化字段")
    
    # 6. 测试筛选示例
    filter_examples_result = test_api_endpoint(
        "/api/filter/examples",
        description="获取筛选示例（包含财年和月份示例）"
    )
    
    if filter_examples_result:
        examples = filter_examples_result.get('examples', [])
        fiscal_examples = [ex for ex in examples if any('fiscal' in str(cond.get('field', '')) for cond in ex.get('conditions', []))]
        print(f"   📊 财年相关示例数量: {len(fiscal_examples)}")
    
    # 7. 测试实际筛选功能
    if available_year:
        filter_data = {
            "conditions": [
                {"field": "fiscal_year", "operator": "equals", "value": available_year}
            ],
            "logic": "AND",
            "limit": 3
        }
        
        filter_result = test_api_endpoint(
            "/api/filter",
            method="POST",
            data=filter_data,
            description=f"实际筛选测试 - 财年 {available_year}"
        )
        
        if filter_result:
            print(f"   📊 筛选结果: {filter_result.get('filtered_count', 0)} 条记录")
            
            # 检查返回的数据是否包含标准化列
            results = filter_result.get('results', [])
            if results and len(results) > 0:
                first_result = results[0]
                if 'fiscal_year' in first_result and 'fiscal_month' in first_result:
                    print(f"   ✅ 返回数据包含标准化列:")
                    print(f"      示例: fiscal_year={first_result['fiscal_year']}, fiscal_month={first_result['fiscal_month']}")
                else:
                    print(f"   ❌ 返回数据缺少标准化列")
    
    print("\n" + "=" * 60)
    print("🎉 API测试完成！")
    print("\n💡 如果所有测试都通过，说明'治本'方案成功实施：")
    print("   - 数据库包含干净的 fiscal_year 和 fiscal_month 列")
    print("   - 所有API都使用标准化列，不再需要复杂的日期解析")
    print("   - 前端应该能够正常加载年份和月份数据")

if __name__ == "__main__":
    main() 