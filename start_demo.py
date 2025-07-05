#!/usr/bin/env python3
"""
IRS非营利组织数据平台 - Demo启动脚本
"""

import os
import sys
import subprocess
import time

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n🔄 {description}...")
    print(f"执行命令: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 成功")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败")
        print(f"错误信息: {e.stderr}")
        return False

def main():
    print("🚀 IRS非营利组织数据平台 - Demo启动")
    print("=" * 50)
    
    # 切换到后端目录
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    # 步骤1: 初始化数据库
    print("\n📊 步骤1: 初始化数据库")
    if not run_command("python db_init.py", "初始化数据库"):
        return False
    
    # 步骤2: 运行数据管道
    print("\n📊 步骤2: 运行数据管道")
    if not run_command("python data_pipeline.py", "处理数据并导入数据库"):
        return False
    
    # 步骤3: 启动FastAPI服务
    print("\n🌐 步骤3: 启动FastAPI服务")
    print("后端服务将在 http://localhost:8000 启动")
    print("API文档: http://localhost:8000/docs")
    print("按 Ctrl+C 停止服务")
    
    try:
        subprocess.run("python start_server.py", shell=True)
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止")
    
    return True

if __name__ == "__main__":
    main() 