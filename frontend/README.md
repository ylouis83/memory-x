# Memory-X 前端应用

基于 React + TypeScript + Material-UI 构建的现代化智能记忆管理系统前端界面。

## ✨ 功能特性

### 🧠 智能对话记忆
- 实时对话界面，支持多轮对话
- 自动意图识别和实体提取
- 记忆重要性评估和分类存储
- 对话历史记录和追踪

### 🔍 记忆浏览器
- 短期记忆查看（最近对话）
- 长期记忆语义搜索
- 记忆统计和可视化
- 按时间、重要性、类型筛选

### 🏥 医疗决策分析
- FHIR 风格的用药记忆管理
- Append/Update/Merge 智能决策
- 置信度评分和风险评估
- 医疗数据验证和安全处理

### 👤 用户管理
- 多用户支持和切换
- 用户配置文件管理
- 个性化设置和偏好

### 📊 系统状态监控
- 实时 API 状态检查
- 存储后端健康监控
- 系统性能指标展示
- 错误日志和诊断信息

## 🚀 快速开始

### 前置要求
- Node.js 18+ 
- npm 或 yarn
- Memory-X 后端服务运行中

### 安装和运行

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev

# 或者使用项目脚本
cd ..
bash scripts/run_frontend.sh
```

### 环境配置

创建 `.env` 文件配置 API 地址：

```env
# API 基础地址
VITE_API_BASE=http://localhost:5000

# 应用信息
VITE_APP_NAME=Memory-X
VITE_APP_VERSION=1.0.0
```

## 🏗️ 技术架构

### 技术栈
- **React 19** - 用户界面框架
- **TypeScript** - 类型安全的 JavaScript
- **Material-UI (MUI)** - 现代化 UI 组件库
- **Axios** - HTTP 客户端
- **Vite** - 快速构建工具
- **date-fns** - 日期处理工具

### 项目结构

```
frontend/
├── src/
│   ├── components/          # UI 组件
│   │   ├── ChatInterface.tsx      # 智能对话界面
│   │   ├── MemoryBrowser.tsx      # 记忆浏览器
│   │   ├── MedicalDecision.tsx    # 医疗决策分析
│   │   ├── UserSelector.tsx       # 用户选择器
│   │   └── SystemStatus.tsx       # 系统状态监控
│   ├── contexts/            # React Context
│   │   └── UserContext.tsx        # 用户状态管理
│   ├── services/            # API 服务
│   │   └── api.ts                 # API 客户端
│   ├── types/               # TypeScript 类型定义
│   │   └── memory.ts              # 记忆相关类型
│   ├── App.tsx              # 主应用组件
│   └── main.tsx             # 应用入口
├── public/                  # 静态资源
├── package.json             # 项目配置
└── vite.config.ts          # Vite 配置
```

## 🎨 界面设计

### 主要界面

1. **智能对话** - 与 AI 进行自然语言交互，自动记忆管理
2. **记忆浏览** - 查看和搜索历史记忆，支持筛选和排序
3. **医疗决策** - 专业的医疗记忆合并决策分析
4. **用户管理** - 多用户环境下的用户切换和管理
5. **系统监控** - 实时监控系统状态和性能指标

### 设计特色

- 🌙 明暗主题切换
- 📱 响应式设计，支持移动端
- 🎯 直观的图标和交互反馈
- 🚀 流畅的动画和过渡效果
- ♿ 无障碍设计支持

## 🔧 开发指南

### 可用脚本

```bash
npm run dev      # 启动开发服务器
npm run build    # 构建生产版本
npm run preview  # 预览生产构建
npm run lint     # 代码检查
```

### API 集成

前端通过 `src/services/api.ts` 与后端 API 通信：

```typescript
import { memoryApi } from '../services/api';

// 发送聊天消息
const response = await memoryApi.chat(userId, message);

// 搜索记忆
const memories = await memoryApi.searchMemories(userId, query);

// 医疗决策分析
const decision = await memoryApi.medicalDecision(request);
```

### 状态管理

使用 React Context 进行全局状态管理：

```typescript
import { useUser } from '../contexts/UserContext';

const { currentUser, setCurrentUser } = useUser();
```

## 📝 使用说明

### 基本流程

1. **选择用户** - 在用户管理页面选择或创建用户
2. **开始对话** - 在智能对话页面输入消息
3. **浏览记忆** - 查看短期记忆和搜索长期记忆
4. **医疗分析** - 使用医疗决策功能分析用药记录
5. **监控状态** - 在系统状态页面查看服务状态

### 最佳实践

- 💬 对话时提供完整的上下文信息
- 🔍 使用关键词进行精确的记忆搜索  
- 📋 医疗决策分析时填写准确的药物信息
- 👥 为不同场景创建不同的用户配置文件

## 🐛 故障排除

### 常见问题

1. **无法连接后端 API**
   - 确保后端服务已启动 (http://localhost:5000)
   - 检查 `.env` 文件中的 API 地址配置

2. **依赖安装失败**
   - 清除 `node_modules` 和 `package-lock.json`
   - 使用 `npm install` 重新安装

3. **页面白屏或错误**
   - 检查浏览器控制台错误信息
   - 确认 TypeScript 类型检查通过

### 调试模式

开启浏览器开发者工具，在 Console 中可以看到：
- API 请求和响应日志
- 应用状态变化
- 错误堆栈信息

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](../LICENSE) 文件了解详情。

## 🔗 相关链接

- [Memory-X 主项目](../README.md)
- [后端 API 文档](../docs/api.md)
- [Material-UI 文档](https://mui.com/)
- [React 官方文档](https://react.dev/)