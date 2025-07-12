# 快速启动指南

## 问题诊断

如果您的主页面登录和注册功能无法使用，请按照以下步骤检查和修复：

## 步骤 1: 检查后端服务

### 方法 1: 使用启动脚本（推荐）
```bash
# 在项目根目录运行
start.bat
```

### 方法 2: 手动启动
```bash
# 1. 进入后端目录
cd backend

# 2. 初始化数据库
python db_init.py

# 3. 启动后端服务
python start_server.py
```

## 步骤 2: 检查前端服务

```bash
# 1. 进入前端目录
cd frontend/vite-project

# 2. 安装依赖（如果需要）
npm install

# 3. 启动前端服务
npm run dev
```

## 步骤 3: 验证服务状态

### 检查后端服务
- 后端地址: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/health

### 检查前端服务
- 前端地址: http://localhost:5173
- 登录页面: http://localhost:5173/login
- 注册页面: http://localhost:5173/register

## 步骤 4: 测试登录功能

1. 打开浏览器访问 http://localhost:5173
2. 点击右上角的 "Register" 按钮
3. 创建一个新账户
4. 使用新账户登录
5. 登录成功后会自动跳转到仪表板

## 常见问题解决

### 问题 1: 后端服务无法启动
**错误信息**: `python: can't open file 'main.py'`
**解决方案**: 
- 确保在 `backend` 目录中运行命令
- 使用 `python start_server.py` 而不是 `python main.py`

### 问题 2: 前端无法连接到后端
**错误信息**: `Failed to fetch data`
**解决方案**:
- 确保后端服务在 http://localhost:8000 运行
- 检查浏览器控制台是否有CORS错误
- 确保防火墙没有阻止连接

### 问题 3: 数据库错误
**错误信息**: `database is locked` 或 `table not found`
**解决方案**:
- 运行 `python db_init.py` 重新初始化数据库
- 确保没有其他程序正在使用数据库文件

### 问题 4: 依赖包缺失
**错误信息**: `ModuleNotFoundError`
**解决方案**:
```bash
cd backend
pip install -r requirements.txt
```

## 测试脚本

运行测试脚本来验证所有功能是否正常：

```bash
cd backend
python test_backend.py
```

## 系统架构说明

- **前端**: React + Vite (端口 5173)
- **后端**: FastAPI + SQLite (端口 8000)
- **数据库**: SQLite (irs.db)
- **认证**: JWT令牌

## 登录流程

1. 用户访问主页 (http://localhost:5173)
2. 点击 "Register" 创建账户
3. 填写用户名和密码
4. 注册成功后跳转到登录页面
5. 使用账户信息登录
6. 登录成功后跳转到仪表板 (/dashboard)

## 联系支持

如果问题仍然存在，请检查：
1. 控制台错误信息
2. 网络连接状态
3. 端口是否被占用
4. 防火墙设置