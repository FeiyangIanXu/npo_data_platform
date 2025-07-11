#!/usr/bin/env python3
"""
后端诊断脚本
检查后端启动问题
"""

import os
import sys
import subprocess
import importlib.util

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python版本过低，需要3.8+")
        return False
    return True

def check_virtual_environment():
    """检查虚拟环境"""
    print("🔍 检查虚拟环境...")
    
    # 检查是否在虚拟环境中
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 当前在虚拟环境中")
        return True
    else:
        print("⚠️ 当前不在虚拟环境中")
        return False

def check_backend_directory():
    """检查后端目录"""
    print("🔍 检查后端目录...")
    
    if not os.path.exists("backend"):
        print("❌ backend目录不存在")
        return False
    
    if not os.path.exists("backend/main.py"):
        print("❌ backend/main.py不存在")
        return False
    
    print("✅ backend目录和main.py存在")
    return True

def check_virtual_envs():
    """检查虚拟环境目录"""
    print("🔍 检查虚拟环境目录...")
    
    venv_paths = [
        "backend/.venv",
        "backend/venv",
        ".venv",
        "venv"
    ]
    
    found_venvs = []
    for venv_path in venv_paths:
        if os.path.exists(venv_path):
            python_exe = os.path.join(venv_path, "Scripts", "python.exe")
            if os.path.exists(python_exe):
                found_venvs.append((venv_path, python_exe))
                print(f"✅ 找到虚拟环境: {venv_path}")
    
    if not found_venvs:
        print("❌ 未找到可用的虚拟环境")
        return None
    
    return found_venvs

def check_dependencies(venv_path, python_exe):
    """检查依赖包"""
    print(f"🔍 检查依赖包 (使用 {venv_path})...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pandas",
        "requests"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            result = subprocess.run([python_exe, "-c", f"import {package}"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {package}")
            else:
                print(f"❌ {package} - 缺失")
                missing_packages.append(package)
        except Exception as e:
            print(f"❌ {package} - 检查失败: {e}")
            missing_packages.append(package)
    
    return missing_packages

def test_backend_startup(venv_path, python_exe):
    """测试后端启动"""
    print(f"🔍 测试后端启动 (使用 {venv_path})...")
    
    try:
        # 切换到backend目录
        original_dir = os.getcwd()
        os.chdir("backend")
        
        # 尝试启动（但只运行几秒钟）
        import threading
        import time
        
        def run_server():
            try:
                subprocess.run([python_exe, "main.py"], 
                             timeout=10,  # 10秒超时
                             capture_output=True, text=True)
            except subprocess.TimeoutExpired:
                print("✅ 服务器启动成功（10秒后停止）")
            except Exception as e:
                print(f"❌ 服务器启动失败: {e}")
        
        # 在后台线程中运行
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        
        # 等待几秒钟
        time.sleep(5)
        
        # 切换回原目录
        os.chdir(original_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ 启动测试失败: {e}")
        os.chdir(original_dir)
        return False

def main():
    """主诊断函数"""
    print("🔧 后端诊断工具")
    print("=" * 50)
    
    # 基本检查
    if not check_python_version():
        return
    
    if not check_backend_directory():
        return
    
    # 检查虚拟环境
    venvs = check_virtual_envs()
    if not venvs:
        print("\n💡 建议:")
        print("1. 创建虚拟环境: python -m venv backend/.venv")
        print("2. 激活虚拟环境: backend/.venv/Scripts/activate")
        print("3. 安装依赖: pip install fastapi uvicorn sqlalchemy pandas")
        return
    
    # 检查依赖
    print("\n📦 依赖检查:")
    for venv_path, python_exe in venvs:
        missing = check_dependencies(venv_path, python_exe)
        if missing:
            print(f"\n💡 安装缺失的依赖包:")
            print(f"   {python_exe} -m pip install {' '.join(missing)}")
        else:
            print(f"✅ {venv_path} 依赖完整")
    
    # 测试启动
    print("\n🚀 启动测试:")
    for venv_path, python_exe in venvs:
        if test_backend_startup(venv_path, python_exe):
            print(f"✅ {venv_path} 可以正常启动")
        else:
            print(f"❌ {venv_path} 启动失败")
    
    print("\n" + "=" * 50)
    print("🎯 诊断完成！")
    print("\n💡 如果仍有问题，请:")
    print("1. 检查防火墙设置")
    print("2. 确保端口8000未被占用")
    print("3. 查看错误日志")

if __name__ == "__main__":
    main() 