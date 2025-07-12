# 项目结构分析报告

## 清理前的问题

### 1. 重复的数据库文件
- **根目录**: `irs.db` (1.0B, 1 lines) - 空文件
- **后端目录**: `backend/irs.db` (176KB, 222 lines) - 实际数据库
- **前端目录**: `frontend/vite-project/irs.db` (0.0B, 0 lines) - 空文件

**原因分析**:
- 后端代码使用相对路径 `"sqlite:///./irs.db"`，会在当前工作目录创建数据库
- 不同脚本在不同目录运行时，会在各自目录创建数据库文件
- 前端目录的数据库文件可能是误操作或测试时创建的

### 2. 重复的前端配置文件
- `frontend/package.json` (61B, 6 lines) - 简单配置
- `frontend/vite-project/package.json` (726B, 32 lines) - 实际项目配置
- `frontend/package-lock.json` (3.0KB, 96 lines)
- `frontend/vite-project/package-lock.json` (141KB, 4177 lines)

**原因分析**:
- 项目创建时可能先在 `frontend/` 目录创建了基础配置
- 后来又在 `frontend/vite-project/` 创建了完整的React项目
- 导致配置文件分散在两个层级

### 3. 重复的依赖目录
- `frontend/node_modules/`
- `frontend/vite-project/node_modules/`

**原因分析**:
- 两个package.json文件导致npm在不同位置安装依赖

## 清理后的改进

### 1. 数据库文件统一
- ✅ 删除了根目录的空数据库文件
- ✅ 删除了前端目录的空数据库文件
- ✅ 保留 `backend/irs.db` 作为唯一数据库文件
- ✅ 修复了所有脚本的数据库路径配置

### 2. 前端项目结构优化
- ✅ 删除了重复的package.json文件
- ✅ 删除了重复的package-lock.json文件
- ✅ 保留了 `frontend/vite-project/` 作为实际项目目录

### 3. 代码路径配置修复
- ✅ `backend/main.py`: 修复数据库URL路径
- ✅ `backend/data_pipeline.py`: 添加路径注释
- ✅ `backend/check_db.py`: 添加路径注释
- ✅ `backend/db_init.py`: 添加路径注释
- ✅ `backend/fix_database.py`: 添加路径注释

## 当前项目结构

```
npo_data_platform/
├── backend/                    # 后端服务
│   ├── irs.db                 # 唯一数据库文件
│   ├── main.py                # FastAPI主应用
│   ├── data_pipeline.py       # 数据处理管道
│   ├── db_init.py             # 数据库初始化
│   ├── check_db.py            # 数据库检查
│   ├── fix_database.py        # 数据库修复
│   ├── start_server.py        # 服务器启动
│   ├── requirements.txt       # Python依赖
│   └── data/                  # 数据文件
│       ├── nonprofits_100.csv
│       └── First100.xlsx
├── frontend/                  # 前端项目
│   └── vite-project/          # React + Vite项目
│       ├── src/               # 源代码
│       ├── public/            # 静态资源
│       ├── package.json       # 项目配置
│       └── vite.config.js     # Vite配置
├── start.bat                  # 启动脚本
├── diagnose_backend.py        # 后端诊断工具
└── 文档文件...
```

## 建议的最佳实践

### 1. 数据库管理
- 数据库文件应该只存在于后端目录
- 使用绝对路径或相对于后端目录的路径
- 避免在多个位置创建数据库文件

### 2. 前端项目结构
- 保持单一的项目根目录
- 避免在父目录创建额外的配置文件
- 使用标准的React/Vite项目结构

### 3. 启动脚本优化
- 确保所有脚本在正确的目录中运行
- 使用绝对路径或明确的相对路径
- 添加错误处理和状态检查

### 4. 开发环境管理
- 使用虚拟环境管理Python依赖
- 使用package.json管理Node.js依赖
- 定期清理缓存和临时文件

## 后续维护建议

1. **定期清理**: 运行 `python cleanup_project.py` 清理临时文件
2. **路径检查**: 新增脚本时确保使用正确的数据库路径
3. **依赖管理**: 定期更新依赖包版本
4. **文档更新**: 保持项目文档与代码同步 