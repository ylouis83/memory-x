# Memory-X | 智能医疗记忆管理系统

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![API Status](https://img.shields.io/badge/API-Ready-brightgreen.svg)](http://localhost:5000)

**🏥 专为医疗AI场景设计的智能记忆管理系统**

*参考 Google Vertex AI Memory Bank 架构，集成百炼Qwen3模型，提供层次化记忆管理和医疗知识图谱*

</div>

---

# 介绍

Memory-X 是一个专门为医疗AI场景设计的智能记忆管理系统，能够记住患者信息、医疗历史，并提供个性化的医疗建议。系统支持症状诊断、风险评估、用药安全检查，是医疗AI应用的理想选择。

### 核心特性

**记忆管理:**
- 🧠 **层次化记忆**: 短期记忆、工作记忆、长期记忆的统一管理
- 🔍 **向量检索**: 高效的语义搜索和相关性分析
- 🔌 **可插拔存储**: 支持SQLite、Cloud Spanner、Mem0多种存储后端

**医疗AI专用:**
- 🏥 **症状诊断**: 智能分析症状与疾病的关联性
- 💊 **用药安全**: 过敏史保护和用药安全检查
- 📊 **知识图谱**: 疾病-症状-药物关联建模
- 🤖 **AI驱动**: 集成百炼Qwen3模型，0.9+高置信度诊断

**应用场景:**
- AI医疗助手: 个性化医疗咨询和建议
- 在线问诊: 基于患者历史的智能诊断
- 医院系统: 患者档案管理和风险评估
- 健康管理: 家族史分析和预防建议

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/ylouis83/memory-x.git
cd memory-x

# 设置环境
bash scripts/setup_venv.sh
source .venv/bin/activate

# 配置API密钥
export DASHSCOPE_API_KEY=your-api-key-here
```

### 基础使用

Memory-X 需要百炼API来提供AI能力，默认使用Qwen3模型。

```python
from src.core.memory_manager import MemoryManager
from configs.dashscope_client import DashScopeClientFactory

# 创建记忆管理器
mm = MemoryManager(user_id="patient_001")

# 添加医疗对话
mm.add_conversation(
    user_message="我最近总是感到乏力，口渴",
    ai_response="这可能是血糖异常的症状，建议检查血糖水平",
)

# 搜索相关记忆
memories = mm.search_memories("血糖 症状")
print(memories)

# 使用医疗AI客户端
client = DashScopeClientFactory.create_medical_client()
answer = client.generate_response("糖尿病的早期症状有哪些？")
print(answer)
```

### 启动完整应用

```bash
# 一键启动前端+后端
bash scripts/start_all.sh
```

访问地址:
- 🌐 前端界面: http://localhost:5173
- 🔌 API服务: http://localhost:5000

## 🔗 演示和集成

- **糖尿病诊断演示**: `python demos/diabetes/diabetes_scenario_demo.py`
- **通用医疗咨询**: `python demos/general_medical_demo.py`
- **在线问诊场景**: `python demos/diabetes/online_consult_diabetes_fatigue_demo.py`
- **百炼API客户端**: `python demos/unified_client_demo.py`

## 🛠️ 技术架构

- **后端**: Python 3.9+ + Flask + SQLAlchemy
- **前端**: React 19 + TypeScript + Material-UI
- **AI引擎**: 百炼DashScope API + Qwen3模型
- **存储**: SQLite / Cloud Spanner / Mem0
- **标准**: FHIR兼容的医疗数据格式

## 📚 文档

- 完整文档: [docs/](docs/)
- API参考: [docs/api-reference.md](docs/api-reference.md)
- 配置指南: [docs/configuration.md](docs/configuration.md)
- 前端文档: [frontend/README.md](frontend/README.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！请遵循PEP 8代码规范，并为新功能添加测试用例。

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件