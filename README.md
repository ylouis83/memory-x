# Memory-X | 智能医疗记忆管理系统

<div align="center">

![Memory-X Logo](https://img.shields.io/badge/Memory--X-智能医疗AI-blue.svg?style=for-the-badge)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![API Status](https://img.shields.io/badge/API-Ready-brightgreen.svg)](http://localhost:5000)
[![Frontend](https://img.shields.io/badge/Frontend-React%20TypeScript-61dafb.svg)](frontend/)

**🏥 专为医疗AI场景设计的智能记忆管理系统**

*参考 Google Vertex AI Memory Bank 架构，提供层次化记忆管理、医疗知识图谱构建和AI驱动的智能分析能力*

[快速开始](#-快速开始) • [功能特性](#-核心特性) • [技术架构](#️-技术架构) • [演示案例](#-演示案例) • [文档](#-文档)

</div>

---

## 🌟 核心特性

<table>
<tr>
<td width="50%">

### 🧠 智能记忆管理
- **层次化记忆**: 短期记忆、工作记忆、长期记忆的统一管理
- **可插拔存储**: 支持SQLite、Cloud Spanner、Mem0多种存储后端
- **向量检索**: 高效的语义搜索和相关性分析

### 🏥 医疗AI专用
- **疾病风险评估**: 智能分析症状与疾病的关联性
- **家族史分析**: 基于遗传病史的风险评估
- **用药安全**: 过敏史保护和用药安全检查

</td>
<td width="50%">

### 🤖 AI驱动更新
- **百炼Qwen3集成**: 先进的大语言模型支持
- **智能图谱更新**: 自动建立和更新医疗实体关系
- **置信度评估**: 0.9+高置信度的诊断建议

### 📊 知识图谱
- **医疗实体建模**: 疾病-症状-药物关联分析
- **FHIR兼容**: 遵循医疗行业标准数据格式
- **时间序列分析**: 区分不同时期症状，避免误诊

</td>
</tr>
</table>

## 🚀 快速开始

### 🖥️ 完整应用（推荐）
```bash
# 克隆项目并进入目录
git clone https://github.com/ylouis83/memory-x.git
cd memory-x

# 设置百炼API密钥
export DASHSCOPE_API_KEY=your-api-key-here

# 一键启动前端+后端
bash scripts/start_all.sh
```

<div align="center">

**访问地址**
🌐 [前端界面](http://localhost:5173) • 🔌 [API 服务](http://localhost:5000) • 📊 [演示页面](http://localhost:5000/demo/mem0)

</div>

### 🐍 Python API 快速体验
```python
from src.core.memory_manager import MemoryManager

# 创建记忆管理器
mm = MemoryManager(user_id="patient_001")

# 添加对话记忆
mm.add_conversation(
    user_message="我最近总是感到乏力，口渴",
    ai_response="这可能是血糖异常的症状，建议检查血糖水平",
)

# 搜索相关记忆
memories = mm.search_memories("血糖 症状")
print(memories)
```

### 🤖 百炼API统一客户端
```python
from configs.dashscope_client import DashScopeClientFactory, quick_ask

# 创建医疗专用客户端
client = DashScopeClientFactory.create_medical_client()

# 快速医疗咨询
answer = quick_ask("糖尿病的早期症状有哪些？")

# 症状诊断分析
from configs.dashscope_client import medical_consultation
result = medical_consultation(["头晕", "乏力", "多饮"])

# 药物安全检查
from configs.dashscope_client import check_medication_safety
safety = check_medication_safety("二甲双胍")
```

## 💡 医疗应用场景

### 🩺 智能诊断系统
<details>
<summary><b>展开查看详细功能</b></summary>

- **症状关联分析**: 智能分析乏力、头晕等症状与各种疾病的关联性
- **家族史风险评估**: 基于患者家族病史进行风险分析
- **时间序列分析**: 区分不同时期的症状，避免误诊和重复诊断
- **置信度评估**: 提供0.9+高置信度的诊断建议

</details>

### 🌐 在线医疗咨询
<details>
<summary><b>展开查看详细功能</b></summary>

- **实时症状分析**: 支持在线咨询来源的患者症状分析
- **个性化建议**: 结合患者年龄、过敏史、家族史的个性化医疗建议
- **专业回复生成**: 符合临床实践的医生回复自动生成
- **多轮对话支持**: 维护完整的医患对话上下文

</details>

### 👤 患者档案管理
<details>
<summary><b>展开查看详细功能</b></summary>

- **过敏史保护**: 自动记录和保护患者过敏信息，避免危险用药
- **医疗历史追踪**: 维护完整的患者医疗历史和健康状态变化
- **家族史管理**: 记录和分析家族遗传病史风险因素
- **用药记录**: FHIR标准的用药记录管理和分析

</details>

## 🛠️ 技术架构

### 后端技术栈
<table>
<tr>
<td width="30%"><b>核心框架</b></td>
<td width="70%">Python 3.9+ | Flask 2.3.3 | SQLAlchemy 2.0.23</td>
</tr>
<tr>
<td><b>AI集成</b></td>
<td>百炼DashScope API | Qwen3大语言模型</td>
</tr>
<tr>
<td><b>数据处理</b></td>
<td>pandas 2.1.4 | numpy | scikit-learn</td>
</tr>
<tr>
<td><b>测试框架</b></td>
<td>pytest 7.4.3 | coverage | unittest</td>
</tr>
</table>

### 前端技术栈
<table>
<tr>
<td width="30%"><b>核心框架</b></td>
<td width="70%">React 19 | TypeScript | Vite</td>
</tr>
<tr>
<td><b>UI组件</b></td>
<td>Material-UI v7 | Emotion | React Router v6</td>
</tr>
<tr>
<td><b>状态管理</b></td>
<td>React Query | Zustand | Axios</td>
</tr>
<tr>
<td><b>开发工具</b></td>
<td>ESLint | Prettier | Storybook</td>
</tr>
</table>

### 数据存储架构
```
Memory-X 存储层
├── SQLite (默认开发)
├── Cloud Spanner (分布式生产)
├── Mem0 (向量化记忆)
└── 可插拔接口设计
```

## 🎨 前端界面展示

<div align="center">

![前端界面](https://img.shields.io/badge/界面-现代化设计-success)
![响应式](https://img.shields.io/badge/响应式-移动端支持-blue)
![主题](https://img.shields.io/badge/主题-明暗切换-purple)

</div>

### 主要功能模块
- **🧠 智能对话**: 与AI进行自然语言交互，自动记忆管理
- **🔍 记忆浏览**: 查看短期记忆和搜索长期记忆  
- **🏥 医疗决策**: FHIR风格的用药记忆合并分析
- **👤 用户管理**: 多用户支持和配置文件管理
- **📊 系统监控**: 实时API状态和性能指标

详细文档请参考 [frontend/README.md](frontend/README.md)

## 📋 演示案例

### 🎯 医疗场景演示

```bash
# 运行糖尿病诊断演示
python demos/diabetes/diabetes_scenario_demo.py

# 运行通用医疗咨询演示
python demos/general_medical_demo.py

# 运行在线咨询演示
python demos/diabetes/online_consult_diabetes_fatigue_demo.py
```

### 🔬 技术功能演示

```bash
# 百炼API客户端演示
python demos/unified_client_demo.py

# 知识图谱构建演示
python examples/medical_graph_demo.py

# Qwen智能分析演示
python examples/enhanced_qwen_graph_demo.py
```

## 🏗️ 存储后端配置

Memory-X 支持多种存储后端，通过环境变量轻松切换：

```bash
# SQLite (默认)
export MEMORY_DB_TYPE=sqlite
export MEMORY_DB_PATH=./memory_db/memory.db

# Cloud Spanner (生产环境)
export MEMORY_DB_TYPE=spanner
export MEMORY_DB_HOST=your-spanner-instance
export MEMORY_DB_USER=your-username
export MEMORY_DB_PASSWORD=your-password

# Mem0 (向量化存储)
export MEMORY_DB_TYPE=mem0
```

## 🧪 测试与质量保证

```bash
# 运行完整测试套件
pytest tests/ -v

# 运行覆盖率测试
pytest --cov=src tests/

# 运行特定功能测试
pytest tests/test_memory_manager.py -v

# 使用内置测试脚本
bash scripts/test.sh
```

## 🛠️ 开发工具脚本

Memory-X 提供了完整的开发工具链：

```bash
scripts/
├── setup_venv.sh      # 创建虚拟环境
├── run_api.sh         # 启动后端API
├── run_frontend.sh    # 启动前端服务
├── start_all.sh       # 一键启动全部服务
├── test.sh           # 运行测试套件
├── clean.sh          # 清理缓存文件
└── push.sh           # Git推送脚本
```

## 📊 项目统计

<div align="center">

![代码行数](https://img.shields.io/badge/代码行数-15K+-brightgreen)
![测试覆盖率](https://img.shields.io/badge/测试覆盖率-85%+-success)
![文档完整度](https://img.shields.io/badge/文档完整度-90%+-blue)

</div>

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

### 贡献方式
- 🐛 **报告Bug**: 通过Issues报告发现的问题
- 💡 **功能建议**: 提出新功能或改进建议
- 📝 **文档改进**: 完善文档和示例代码
- 🔧 **代码贡献**: 提交Pull Request

### 开发规范
- **代码风格**: 遵循PEP 8标准
- **测试要求**: 新功能必须包含测试用例
- **文档要求**: 公开API需要完整文档
- **提交规范**: 使用语义化提交信息

## 📚 相关文档

<table>
<tr>
<td width="50%">

### 📖 用户文档
- [快速开始指南](docs/quick-start.md)
- [API文档](docs/api-reference.md)
- [配置指南](docs/configuration.md)
- [部署指南](docs/deployment.md)

</td>
<td width="50%">

### 🔧 开发文档
- [架构设计](docs/architecture.md)
- [数据库设计](docs/database-schema.md)
- [插件开发](docs/plugin-development.md)
- [性能优化](docs/performance.md)

</td>
</tr>
</table>

## 🔗 生态系统

- **[mem0](https://github.com/mem0ai/mem0)**: 向量化记忆存储
- **[DashScope](https://dashscope.aliyun.com/)**: 阿里云百炼大模型平台
- **[FHIR](https://www.hl7.org/fhir/)**: 医疗数据交换标准

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个Star！**

[报告问题](https://github.com/ylouis83/memory-x/issues) • [功能请求](https://github.com/ylouis83/memory-x/issues/new) • [讨论交流](https://github.com/ylouis83/memory-x/discussions)

Made with ❤️ by Memory-X Team

</div>