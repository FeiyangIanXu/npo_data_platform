#!/usr/bin/env python3
"""
IRS非营利组织数据平台系统测试脚本
"""

import requests
import json
import time

# 配置
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def test_backend_health():
    """测试后端健康状态"""
    print("🔍 测试后端健康状态...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 后端健康检查通过: {data}")
            return True
        else:
            print(f"❌ 后端健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return False

def test_statistics_api():
    """测试统计API"""
    print("\n📊 测试统计API...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/statistics")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 统计API正常: 总记录数 {data.get('total_records', 0)}")
            return True
        else:
            print(f"❌ 统计API失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 统计API错误: {e}")
        return False

def test_fields_api():
    """测试字段API"""
    print("\n📋 测试字段API...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/fields")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 字段API正常: 字段数量 {data.get('count', 0)}")
            return True
        else:
            print(f"❌ 字段API失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 字段API错误: {e}")
        return False

def test_query_api():
    """测试查询API"""
    print("\n🔍 测试查询API...")
    try:
        # 测试基本查询
        response = requests.get(f"{BACKEND_URL}/api/query?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 基本查询正常: 返回 {len(data.get('data', []))} 条记录")
            
            # 测试带条件查询
            response2 = requests.get(f"{BACKEND_URL}/api/query?organization_name=Frasier&limit=5")
            if response2.status_code == 200:
                data2 = response2.json()
                print(f"✅ 条件查询正常: 找到 {data2.get('total', 0)} 条匹配记录")
                return True
            else:
                print(f"❌ 条件查询失败: {response2.status_code}")
                return False
        else:
            print(f"❌ 基本查询失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 查询API错误: {e}")
        return False

def test_frontend():
    """测试前端连接"""
    print("\n🌐 测试前端连接...")
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            print("✅ 前端服务正常")
            return True
        else:
            print(f"❌ 前端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端连接失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 IRS非营利组织数据平台系统测试")
    print("=" * 50)
    
    tests = [
        test_backend_health,
        test_statistics_api,
        test_fields_api,
        test_query_api,
        test_frontend
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(0.5)  # 避免请求过快
    
    print("\n" + "=" * 50)
    print(f"📈 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统运行正常")
        print(f"\n🌐 前端地址: {FRONTEND_URL}")
        print(f"🔧 后端API: {BACKEND_URL}/docs")
    else:
        print("⚠️  部分测试失败，请检查系统状态")
    
    return passed == total

if __name__ == "__main__":
    main() 