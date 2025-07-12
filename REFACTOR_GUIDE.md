# 代码重构指南

## 🎯 重构目标

将700多行的 `main.py` 拆分成多个模块，提高代码的可维护性和可读性。

## 📁 新的项目结构

```
backend/
├── main.py                 # 主应用入口 (50行)
├── api/                    # API路由模块
│   ├── __init__.py
│   ├── auth.py            # 认证相关API (注册/登录)
│   ├── data.py            # 数据查询API
│   ├── search.py          # 搜索相关API (待添加)
│   └── export.py          # 导出相关API (待添加)
├── models/                 # 数据模型
│   ├── __init__.py
│   └── schemas.py         # 数据模型定义
├── core/                   # 核心功能
│   ├── __init__.py
│   ├── config.py          # 配置
│   ├── database.py        # 数据库连接
│   └── security.py        # 安全相关 (JWT, 密码加密)
└── utils/                  # 工具函数 (待添加)
    ├── __init__.py
    └── helpers.py         # 辅助函数
```

## 🔧 重构内容

### 1. 数据模型 (`models/schemas.py`)
- ✅ `UserLogin` - 登录请求模型
- ✅ `UserRegister` - 注册请求模型

### 2. 核心配置 (`core/`)
- ✅ `config.py` - 应用配置 (密钥、算法等)
- ✅ `database.py` - 数据库连接和会话管理
- ✅ `security.py` - 密码加密、JWT令牌处理

### 3. API路由 (`api/`)
- ✅ `auth.py` - 认证相关API (注册/登录)
- ✅ `data.py` - 数据查询API (字段、查询、统计)

### 4. 主应用 (`main_new.py`)
- ✅ 简化的主应用文件
- ✅ 路由注册
- ✅ CORS配置

## 📊 重构效果

### 重构前
- `main.py`: 726行
- 所有功能混在一起
- 难以维护和扩展

### 重构后
- `main_new.py`: 50行
- 功能按模块分离
- 易于维护和扩展

## 🚀 使用方法

### 1. 测试新结构
```bash
cd backend
python main_new.py
```

### 2. 如果测试成功，替换原文件
```bash
# 备份原文件
mv main.py main_old.py
# 使用新文件
mv main_new.py main.py
```

## 📋 待完成的部分

### 1. 搜索API (`api/search.py`)
- `GET /api/search` - 搜索组织
- `GET /api/available-years` - 可用年份
- `GET /api/available-states` - 可用州
- `GET /api/available-cities` - 可用城市
- `GET /api/field-info` - 字段信息

### 2. 导出API (`api/export.py`)
- `GET /api/export` - 导出数据

### 3. 高级筛选API (`api/filter.py`)
- `POST /api/step1-filter` - 第一步筛选
- `POST /api/step2-filter` - 第二步筛选
- `POST /api/final-query` - 最终查询

### 4. 工具函数 (`utils/helpers.py`)
- `format_field_name()` - 格式化字段名
- `categorize_field()` - 字段分类

## 💡 重构优势

1. **模块化**: 每个文件职责单一，易于理解
2. **可维护性**: 修改某个功能只需要改对应文件
3. **可扩展性**: 添加新功能只需创建新模块
4. **可测试性**: 每个模块可以独立测试
5. **团队协作**: 不同开发者可以同时修改不同模块

## 🔄 迁移步骤

1. **测试新结构**: 确保所有功能正常工作
2. **备份原文件**: 保留原始代码作为备份
3. **逐步迁移**: 一个模块一个模块地迁移
4. **更新文档**: 更新相关文档和说明
5. **团队培训**: 确保团队成员了解新结构

## ⚠️ 注意事项

1. **导入路径**: 确保所有导入路径正确
2. **依赖关系**: 注意模块间的依赖关系
3. **测试覆盖**: 确保重构后所有功能正常
4. **文档更新**: 更新API文档和项目说明 