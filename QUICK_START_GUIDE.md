# 🚀 WRDS风格查询系统 - 快速启动指南

## 📋 系统要求

- Python 3.8+
- Node.js 16+
- 现代浏览器（Chrome, Firefox, Safari, Edge）

## 🔧 启动步骤

### 1. 启动后端服务

```bash
# 进入后端目录
cd backend

# 激活虚拟环境（如果已创建）
source venv/bin/activate

# 或者创建新的虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 启动服务器
python main.py
```

后端服务将在 `http://localhost:8000` 启动

### 2. 启动前端服务

```bash
# 新开一个终端，进入前端目录
cd frontend/vite-project

# 安装依赖（如果未安装）
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

### 3. 访问系统

在浏览器中打开 `http://localhost:5173`，点击 **Query Form** 开始使用！

## 🎯 使用流程

### Step 1: 选择年份
1. 从下拉菜单选择数据年份
2. 点击"下一步：范围筛选"

### Step 2: 范围筛选
1. **地理位置**：选择州和城市
2. **财务规模**：设置收入和资产范围
3. **运营规模**：设置ILU/ALU最小值
4. 点击"执行筛选"

### Step 3: 精确定位
1. 选择"全部选择"或"精确选择"
2. 如果精确选择，输入组织名称或EIN
3. 查看筛选结果预览
4. 点击"确认选择"

### Step 4: 变量选择
1. 按类别选择需要的字段：
   - 基本信息
   - 财务数据
   - 薪酬数据
   - 资产负债
   - 运营数据
2. 可以按类别全选或单独选择
3. 点击"查询数据"

### Step 5: 导出数据
1. 选择输出格式（XLSX/CSV/JSON）
2. 预览查询结果
3. 点击"导出数据"下载文件

## 🔍 API 测试

可以直接测试后端API：

```bash
# 获取可用年份
curl http://localhost:8000/api/available-years

# 获取可用州
curl http://localhost:8000/api/available-states

# 查看API文档
open http://localhost:8000/docs
```

## 📊 示例查询

### 查询加州的大型养老机构
1. 年份：选择 "12/2023"
2. 范围筛选：
   - 州：CA
   - 总收入：> $10,000,000
   - ILU：> 100
3. 组织选择：全部选择
4. 变量选择：基本信息 + 财务数据 + 运营数据

### 查询特定组织的薪酬信息
1. 年份：选择目标年份
2. 范围筛选：可跳过
3. 组织选择：精确选择，输入EIN号码
4. 变量选择：基本信息 + 薪酬数据

## ⚠️ 注意事项

1. **服务启动顺序**：先启动后端，再启动前端
2. **端口冲突**：确保8000和5173端口未被占用
3. **数据库**：确保 `backend/irs.db` 文件存在
4. **虚拟环境**：建议使用虚拟环境避免依赖冲突

## 🐛 故障排除

### 后端服务无法启动
```bash
# 检查依赖是否安装
pip list | grep fastapi

# 重新安装依赖
pip install -r requirements.txt

# 检查数据库
ls -la irs.db
```

### 前端服务无法启动
```bash
# 清除缓存重新安装
rm -rf node_modules package-lock.json
npm install
```

### API连接失败
1. 确认后端在8000端口运行
2. 检查CORS设置
3. 查看浏览器控制台错误

## 📈 数据统计

当前系统包含：
- **201个非营利组织**
- **164个数据字段**
- **33个州的数据**
- **172个城市**
- **2022-2024年度数据**

## 🎯 核心功能

✅ **类WRDS查询体验**  
✅ **5步分层筛选**  
✅ **164字段完整覆盖**  
✅ **多格式数据导出**  
✅ **实时数据预览**  
✅ **智能字段分类**  

---

**🎉 您的专业级非营利组织数据查询系统已就绪！**