# Financial Benchmarking Platform for Single-Campus Senior Living Organizations

一个专门为单校区（独立）老年生活组织设计的财务基准数据库和分析平台。通过从公开的IRS Form 990中手动提取和整理关键财务数据，我们正在构建一个专有数据集，使这些独特的组织能够与真正的同行群体进行准确的性能比较。

## 🎯 项目目标

### 核心价值主张
- **解决市场情报缺口**: 为单校区老年生活组织提供相关的同行比较数据
- **消除数据孤岛**: 提供外部基准，超越仅依赖内部历史数据的限制
- **战略优势**: 为财务管理、高管薪酬和资源分配提供数据驱动的决策支持

### 技术目标
- 提供IRS Form 990数据的便捷查询和分析服务
- 支持按组织名称、EIN、州、城市等字段查询
- 实现分页显示和CSV导出功能
- 后续支持订阅和支付服务

## 🏗️ 技术栈

### 后端
- **Python FastAPI** - 现代异步Web框架
- **SQLite** - 数据库
- **SQLAlchemy** - ORM框架
- **Uvicorn** - ASGI服务器
- **Python-Jose** - JWT认证
- **Passlib** - 密码加密

### 前端
- **React 18** - 前端框架
- **Vite** - 构建工具
- **Ant Design** - UI组件库
- **Axios** - HTTP客户端
- **React Router** - 路由管理

## 📊 关键数据点与分析

数据库专注于Form 990中最关键的财务和运营指标：

### Part I (摘要)
- 关键财务活动和概览

### 收入与支出
- 项目服务收入
- 捐赠收入
- 总收入
- 总支出
- 净收入

### 资产负债表
- 总资产
- 负债
- 净资产

### 薪酬数据
- 关键高管数据
- 最高薪酬员工信息

## 📁 项目结构

```
npo_data_platform/
├── backend/                 # 后端代码
│   ├── app.py              # FastAPI主应用
│   ├── data_pipeline.py    # 数据处理管道
│   ├── db_init.py          # 数据库初始化
│   ├── data/               # 数据文件
│   │   ├── First100.xlsx
│   │   └── nonprofits_100.csv
│   └── irs.db              # SQLite数据库
├── frontend/               # 前端代码
│   └── vite-project/
│       ├── src/
│       │   ├── pages/      # 页面组件
│       │   ├── App.jsx     # 主应用
│       │   └── main.jsx    # 入口文件
│       └── package.json
├── start_demo.py           # 启动脚本
└── README.md              # 项目文档
```

## 🚀 快速开始

### 1. 环境准备

确保已安装：
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 2. 后端设置

```bash
# 进入后端目录
cd backend

# 安装Python依赖
pip install -r requirements.txt

# 初始化数据库并启动服务
python start_demo.py
```

### 3. 前端设置

```bash
# 进入前端目录
cd frontend/vite-project

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 📊 功能特性

### 数据查询
- ✅ 按组织名称搜索
- ✅ 按EIN号码搜索
- ✅ 按州/城市筛选
- ✅ 分页显示结果
- ✅ 实时统计信息

### 数据展示
- ✅ 表格形式展示
- ✅ 字段说明文档
- ✅ 使用手册
- ✅ 知识库

### 用户系统
- ✅ 用户注册
- ✅ 用户登录
- ✅ JWT认证

## 🔧 API接口

### 数据查询
- `GET /api/query` - 查询数据（支持分页和筛选）
- `GET /api/fields` - 获取字段信息
- `GET /api/statistics` - 获取统计信息

### 用户认证
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录

## 📈 开发阶段规划

### 第一阶段：概念验证 (当前阶段)
- ✅ 从Form 990 PDF手动数据录入
- ✅ 构建100-200个独立组织的样本数据集
- ✅ 创建有意义的同行群体
- ✅ 功能性数据库原型

### 第二阶段：自动化与扩展 (未来愿景)
- 📋 探索和实施自动数据提取方法
- 📋 利用EIN作为唯一标识符构建年度数据更新系统
- 📋 显著减少人工劳动的可扩展数据管道

### 第三阶段：平台开发与商业化
- 📋 开发用户友好的Web前端
- 📋 趋势分析仪表板（创建"面板数据"跟踪时间性能）
- 📋 可定制的同行群体选择
- 📋 报告生成功能
- 📋 订阅服务商业模式

## 🎯 问题陈述

### 缺乏相关同行
大多数可用的行业报告（如Ziegler 100）专注于最大的多站点组织。将单校区实体与这些大型系统进行比较是"苹果与橙子"的比较，会产生误导性的见解。

### 内部数据孤岛
在缺乏外部基准的情况下，许多组织被迫仅依赖自己的历史数据（年度性能），这无法考虑更广泛的市场趋势和竞争定位。

### 战略劣势
这种信息缺口使独立社区在财务管理、高管薪酬和资源分配等关键决策方面处于战略劣势。

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 项目Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

---

**注意**: 本项目仅用于演示目的，数据来源于IRS公开数据。长期愿景是提供订阅服务，为单校区老年生活组织提供有价值的财务基准分析。 