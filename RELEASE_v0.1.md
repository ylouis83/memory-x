# Memory-X v0.1 - 智能医疗记忆管理系统首个版本

🎉 **Memory-X v0.1 正式发布！**

这是Memory-X智能医疗记忆管理系统的第一个稳定版本，专为医疗AI场景设计，提供完整的记忆管理和智能诊断能力。

## ✨ 核心功能

### 🧠 智能记忆管理
- **层次化记忆**: 短期记忆、工作记忆、长期记忆的统一管理
- **向量检索**: 高效的语义搜索和相关性分析
- **可插拔存储**: 支持SQLite、Cloud Spanner、Mem0多种存储后端

### 🏥 医疗AI专用
- **症状诊断**: 智能分析症状与疾病的关联性
- **用药安全**: 过敏史保护和用药安全检查
- **知识图谱**: 疾病-症状-药物关联建模
- **AI驱动**: 集成百炼Qwen3模型，0.9+高置信度诊断

## 🛠️ 技术架构

- **后端**: Python 3.9+ + Flask + SQLAlchemy
- **前端**: React 19 + TypeScript + Material-UI  
- **AI引擎**: 百炼DashScope API + Qwen3模型
- **存储**: SQLite / Cloud Spanner / Mem0
- **标准**: FHIR兼容的医疗数据格式

## 🎯 应用场景

- **AI医疗助手**: 个性化医疗咨询和建议
- **在线问诊**: 基于患者历史的智能诊断
- **医院系统**: 患者档案管理和风险评估
- **健康管理**: 家族史分析和预防建议

## 🚀 快速开始

```bash
# 克隆项目
git clone https://github.com/ylouis83/memory-x.git
cd memory-x

# 设置环境
bash scripts/setup_venv.sh
source .venv/bin/activate

# 配置API密钥
export DASHSCOPE_API_KEY=your-api-key-here

# 启动应用
bash scripts/start_all.sh
```

## 📋 演示案例

- 糖尿病诊断演示: `python demos/diabetes/diabetes_scenario_demo.py`
- 通用医疗咨询: `python demos/general_medical_demo.py`
- 百炼API客户端: `python demos/unified_client_demo.py`

## 🔗 访问地址

- 🌐 前端界面: http://localhost:5173
- 🔌 API服务: http://localhost:5000

## 📚 文档

- [完整文档](docs/)
- [API参考](docs/api-reference.md)
- [配置指南](docs/configuration.md)
- [前端文档](frontend/README.md)

---

**这是一个完全通用化的医疗AI记忆管理系统，适用于各种医疗场景和患者群体。**

如有问题或建议，请通过 [Issues](https://github.com/ylouis83/memory-x/issues) 联系我们。