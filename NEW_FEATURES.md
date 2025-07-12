# 新功能说明

## 概述

我们已经成功添加了四个新的功能模块，大大增强了IRS非营利组织数据平台的功能：

## 1. 搜索API (api/search.py)

### 功能特点
- **智能搜索**: 支持关键词搜索，自动匹配多个字段
- **字段选择**: 可以指定搜索特定字段
- **结果排序**: 按相关性自动排序
- **高级搜索**: 支持多条件组合搜索

### API端点
- `GET /api/search` - 基本搜索
- `GET /api/search/advanced` - 高级搜索

### 使用示例
```bash
# 基本搜索
GET /api/search?q=hospital&fields=name,address&limit=20

# 高级搜索
GET /api/search/advanced?state=CA&min_income=1000000&limit=50
```

## 2. 导出API (api/export.py)

### 功能特点
- **多格式支持**: CSV、JSON、Excel格式导出
- **筛选导出**: 支持按条件筛选后导出
- **文件命名**: 自动生成带时间戳的文件名
- **大数据处理**: 支持大量数据的分批导出

### API端点
- `POST /api/export/csv` - 导出CSV
- `POST /api/export/json` - 导出JSON
- `POST /api/export/excel` - 导出Excel
- `GET /api/export/status` - 获取导出状态

### 使用示例
```bash
# 导出JSON格式
POST /api/export/json
{
  "filters": {"state": "CA"},
  "limit": 1000
}

# 导出CSV格式
POST /api/export/csv
{
  "filters": {"income": {"operator": "greater_than", "value": 1000000}},
  "limit": 500
}
```

## 3. 高级筛选API (api/filter.py)

### 功能特点
- **复杂条件**: 支持AND/OR逻辑组合
- **多种操作符**: 等于、不等于、包含、大于、小于、范围等
- **分页支持**: 内置分页功能
- **排序功能**: 支持多字段排序
- **字段验证**: 自动验证字段名和操作符

### API端点
- `POST /api/filter` - 高级筛选
- `GET /api/filter/fields` - 获取可用字段
- `GET /api/filter/examples` - 获取筛选示例

### 支持的操作符
- `equals` - 等于
- `not_equals` - 不等于
- `contains` - 包含
- `in` - 在列表中
- `not_in` - 不在列表中
- `greater_than` - 大于
- `less_than` - 小于
- `greater_equal` - 大于等于
- `less_equal` - 小于等于
- `between` - 在范围内
- `is_null` - 为空
- `is_not_null` - 不为空

### 使用示例
```bash
# 复杂筛选
POST /api/filter
{
  "conditions": [
    {"field": "state", "operator": "equals", "value": "CA"},
    {"field": "income", "operator": "between", "value": [1000000, 5000000]},
    {"field": "org_type", "operator": "in", "value": ["501(c)(3)", "501(c)(4)"]}
  ],
  "logic": "AND",
  "limit": 100,
  "order_by": "income",
  "order_direction": "DESC"
}
```

## 4. 工具函数 (utils/helpers.py)

### 功能特点
- **数据格式化**: 货币、数字、日期格式化
- **参数验证**: 分页参数、字段名验证
- **安全处理**: SQL注入防护
- **错误处理**: 统一的数据库错误处理
- **日志记录**: API调用日志
- **统计功能**: 数据库统计信息

### 主要函数
- `format_currency()` - 货币格式化
- `format_number()` - 数字格式化
- `validate_pagination_params()` - 分页参数验证
- `sanitize_sql_input()` - SQL输入清理
- `get_database_stats()` - 数据库统计
- `handle_database_error()` - 错误处理

## 项目结构

```
backend/
├── main.py              # 主应用文件（已重命名）
├── api/                 # API模块
│   ├── __init__.py
│   ├── search.py        # 搜索API
│   ├── export.py        # 导出API
│   └── filter.py        # 筛选API
├── utils/               # 工具函数
│   ├── __init__.py
│   └── helpers.py       # 辅助函数
├── test_new_features.py # 测试脚本
└── NEW_FEATURES.md      # 本文档
```

## 测试新功能

运行测试脚本验证所有新功能：

```bash
cd backend
python test_new_features.py
```

## 启动服务器

```bash
cd backend
python main.py
```

服务器将在 `http://localhost:8001` 启动，包含所有新功能。

## API文档

启动服务器后，可以访问：
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## 注意事项

1. **Excel导出**: 需要安装 `openpyxl` 库
   ```bash
   pip install openpyxl
   ```

2. **数据量限制**: 导出功能默认限制10000条记录，可根据需要调整

3. **性能优化**: 对于大数据量查询，建议使用分页和适当的筛选条件

4. **错误处理**: 所有API都包含完善的错误处理和日志记录

## 下一步计划

1. 添加数据可视化API
2. 实现数据缓存机制
3. 添加用户权限管理
4. 支持更多数据格式
5. 添加数据质量检查功能 