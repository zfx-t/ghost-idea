# Ghost Idea

AI 辅助生成想法的项目

## 项目结构

```
ghost-idea/
├── frontend/          # React 前端
└── src/              # Python 后端
    ├── api.py        # FastAPI 接口
    ├── main.py       # TUI 入口
    └── agents/       # AI Agent 逻辑
```

## 快速开始

### 1. 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
```

### 2. 配置环境变量

创建 `.env` 文件，配置 API Key：

```env
DASHSCOPE_API_KEY=your_api_key
DASHCOPE_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 3. 启动服务

**终端 1 - 启动后端 API：**
```bash
python src/api.py
```

**终端 2 - 启动前端：**
```bash
cd frontend
npm run dev
```

### 4. 访问

打开浏览器访问：http://localhost:5173

## 功能

- 💬 AI 对话沟通
- 🎨 词云标签生成
- 💡 创意想法生成
