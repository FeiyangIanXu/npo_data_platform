# 🔧 前端页面空白问题 - 故障排除指南

## 🚨 问题描述
访问前端网站时页面完全空白，没有任何内容显示。

## 🔍 可能的原因和解决方案

### 1. **React版本兼容性问题** ✅ 已修复
**问题**: React 19与Ant Design不兼容
**解决方案**: 
- 已降级到React 18.2.0
- 重新安装依赖: `npm install`

### 2. **依赖未正确安装**
**检查方法**:
```bash
cd frontend/vite-project
npm list react antd
```

**解决方案**:
```bash
# 删除node_modules并重新安装
rm -rf node_modules package-lock.json
npm install
```

### 3. **开发服务器未启动**
**检查方法**:
- 确认终端显示 "Local: http://localhost:5173/"
- 浏览器访问 http://localhost:5173

**解决方案**:
```bash
cd frontend/vite-project
npm run dev
```

### 4. **浏览器缓存问题**
**解决方案**:
- 按 `Ctrl + F5` 强制刷新
- 或按 `F12` 打开开发者工具，右键刷新按钮选择"清空缓存并硬性重新加载"

### 5. **JavaScript错误**
**检查方法**:
1. 按 `F12` 打开开发者工具
2. 查看 Console 标签页是否有红色错误信息
3. 查看 Network 标签页是否有失败的请求

### 6. **端口冲突**
**检查方法**:
```bash
# Windows
netstat -ano | findstr :5173

# 如果端口被占用，杀死进程
taskkill /PID <进程ID> /F
```

## 🚀 快速修复步骤

### 方法1: 使用批处理文件（推荐）
1. 双击 `start_backend.bat` 启动后端
2. 双击 `start_frontend.bat` 启动前端
3. 等待服务器启动完成
4. 访问 http://localhost:5173

### 方法2: 手动启动
```bash
# 终端1: 启动后端
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pandas
python main.py

# 终端2: 启动前端
cd frontend/vite-project
npm install
npm run dev
```

## 🔍 诊断工具

### 简化版测试页面
我已经创建了一个简化版的QueryForm组件，用于测试基本功能：
- 基础界面测试
- API连接测试
- 系统信息显示

### 浏览器开发者工具
1. **Console**: 查看JavaScript错误
2. **Network**: 查看API请求状态
3. **Elements**: 检查HTML结构

## 📋 检查清单

- [ ] 后端服务器在8000端口运行
- [ ] 前端服务器在5173端口运行
- [ ] 浏览器控制台无错误
- [ ] 网络请求正常
- [ ] React和Ant Design版本兼容

## 🆘 如果问题仍然存在

1. **查看错误日志**:
   - 后端: 查看终端输出
   - 前端: 查看浏览器控制台

2. **尝试不同浏览器**:
   - Chrome
   - Firefox
   - Edge

3. **检查防火墙设置**:
   - 确保端口5173和8000未被阻止

4. **重新克隆项目**:
   ```bash
   git clone <your-repo>
   cd npo_data_platform
   # 重新安装依赖
   ```

## 📞 获取帮助

如果以上方法都无法解决问题，请提供以下信息：
1. 操作系统版本
2. Node.js版本 (`node -v`)
3. npm版本 (`npm -v`)
4. 浏览器控制台错误信息
5. 终端输出日志

---

**💡 提示**: 大多数情况下，重新安装依赖和清除浏览器缓存可以解决问题。 