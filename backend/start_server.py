#!/usr/bin/env python3
"""
IRS非营利组织数据平台 - FastAPI服务器启动脚本
"""

import uvicorn
import os
import sys

def main():
    """启动FastAPI服务器"""
    print("🚀 启动IRS非营利组织数据平台服务器...")
    print("📍 服务器地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("🔧 交互式API文档: http://localhost:8000/redoc")
    print("-" * 50)
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式自动重载
        log_level="info"
    )

if __name__ == "__main__":
    main() 