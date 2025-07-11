import requests
import json

# 测试配置
BASE_URL = "http://127.0.0.1:8000"

def test_register():
    """测试注册功能"""
    print("=== 测试注册功能 ===")
    
    # 测试数据
    test_user = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/register",
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_user)
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 注册成功")
        else:
            print("❌ 注册失败")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_login():
    """测试登录功能"""
    print("\n=== 测试登录功能 ===")
    
    # 测试数据
    test_user = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_user)
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 登录成功")
            # 保存token用于后续测试
            data = response.json()
            return data.get("access_token")
        else:
            print("❌ 登录失败")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_health():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 服务器健康")
        else:
            print("❌ 服务器不健康")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    # 先测试健康检查
    test_health()
    
    # 测试注册
    test_register()
    
    # 测试登录
    token = test_login()
    
    if token:
        print(f"\n✅ 认证测试完成，获取到token: {token[:20]}...")
    else:
        print("\n❌ 认证测试失败") 