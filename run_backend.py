#!/usr/bin/env python3
"""
简单的后端启动脚本
"""

import os
import sys

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# 切换到backend目录
os.chdir(backend_dir)

# 启动FastAPI服务
if __name__ == "__main__":
    import uvicorn
    print("🚀 启动IRS非营利组织数据平台后端服务...")
    print("📍 服务地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 