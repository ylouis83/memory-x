# Memory-X | 智能医疗记忆管理系统

📅 **最后更新**: 2025年9月11日  
👤 **项目维护者**: 柳阳，40岁，有糖尿病遗传病史，青霉素过敏  
🏥 **应用领域**: 医疗AI、智能记忆管理、知识图谱  

Memory-X 是一个专为医疗AI场景设计的智能记忆管理系统，参考 Google Vertex AI Memory Bank 架构，提供层次化记忆管理、医疗知识图谱构建和AI驱动的智能分析能力。

## 🌟 核心特性

- 🧠 **层次化记忆管理**: 短期记忆、工作记忆、长期记忆的统一管理
- 🏥 **医疗AI专用**: 支持糖尿病等疾病的智能诊断和风险评估
- 🤖 **AI驱动更新**: 集成百炼Qwen3模型，实现智能知识图谱更新
- 📊 **知识图谱**: 医疗实体关系建模，支持疾病-症状-药物关联
- 🔌 **可插拔存储**: 支持SQLite、Cloud Spanner、Mem0多种存储后端
- 🌐 **全栈架构**: React前端 + Flask后端 + AI引擎集成
- 🩺 **FHIR兼容**: 遵循医疗行业标准的数据格式

## 💡 医疗应用场景

### 🍯 糖尿病智能诊断
- **家族史风险评估**: 基于患者家族病史进行糖尿病风险分析
- **症状关联分析**: 智能分析乏力、头晕等症状与糖尿病的关联性
- **置信度评估**: 提供0.9+高置信度的诊断建议
- **时间序列分析**: 区分不同时期的症状，避免误诊

### 🌐 在线医疗咨询
- **实时症状分析**: 支持online_consult来源的患者咨询
- **个性化建议**: 结合患者年龄、过敏史、家族史的个性化医疗建议
- **专业回复生成**: 符合临床实践的医生回复自动生成

### 👤 患者记忆管理
- **过敏史保护**: 自动记录和保护患者过敏信息（如青霉素过敏）
### 📊 知识图谱构建
- **疾病-症状关联**: 自动建立疾病与症状的关联关系
- **药物-疾病关联**: 支持疾病与治疗药物的关系建模
- **动态更新**: AI驱动的知识图谱实时更新和优化

## 🛠️ 技术架构

### 后端技术栈
- **Python 3.9+**: 主要开发语言
- **Flask 2.3.3**: Web框架和RESTful API
- **SQLAlchemy 2.0.23**: ORM框架和数据库管理
- **pandas 2.1.4**: 数据处理和分析
- **DashScope API**: 百烼Qwen3模型集成
- **pytest 7.4.3**: 自动化测试框架

### 前端技术栈
- **React 19**: 现代化前端框架
- **TypeScript**: 类型安全的JavaScript
- **Material-UI v7**: 丰富的UI组件库
- **Vite**: 高性能构建工具
- **Axios**: HTTP客户端请求库

### 数据存储
- **SQLite**: 默认本地开发数据库
- **Cloud Spanner**: 分布式数据库支持
- **Mem0**: 向量化记忆存储集成

## 🚀 快速开始

### 🖥️ 完整应用（推荐）
```bash
# 克隆项目并进入目录
git clone https://github.com/ylouis83/memory-x.git
cd memory-x

# 一键启动前端+后端
bash scripts/start_all.sh
```

访问地址：
- 🌐 **前端界面**: http://localhost:5173
- 🔌 **API 服务**: http://localhost:5000
- 📊 **演示页面**: http://localhost:5000/demo/mem0

### 🔧 分别启动
```bash
# 1. 后端服务
bash scripts/setup_venv.sh
source .venv/bin/activate
bash scripts/run_api.sh

# 2. 前端应用（新终端）
bash scripts/run_frontend.sh
```

### 💻 仅后端 API
```bash
# 克隆项目并进入目录
git clone https://github.com/ylouis83/memory-x.git
cd memory-x

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Windows 使用 venv\\Scripts\\activate

# 安装依赖
pip install -r requirements.txt
```

或使用内置脚本快速启动：
```bash
bash scripts/setup_venv.sh
source .venv/bin/activate
```

## 🚀 快速开始
```python
from src.core.memory_manager import MemoryManager

mm = MemoryManager(user_id="user_001")
mm.add_conversation(
    user_message="我叫张三",
    ai_response="你好张三，很高兴认识你！",
)
print(mm.search_memories("张三"))
```

## 🎨 前端界面

基于 React + TypeScript + Material-UI 构建的现代化 Web 界面，提供完整的记忆管理可视化体验：

### 主要功能模块
- **🧠 智能对话**: 与AI进行自然语言交互，自动记忆管理
- **🔍 记忆浏览**: 查看短期记忆和搜索长期记忆  
- **🏥 医疗决策**: FHIR风格的用药记忆合并分析
- **👤 用户管理**: 多用户支持和配置文件管理
- **📊 系统监控**: 实时API状态和性能指标

### 界面特色
- 🌙 明暗主题切换
- 📱 响应式设计，支持移动端
- 🚀 流畅的动画和交互体验
- ♿ 无障碍设计支持

详细文档请参考 [frontend/README.md](frontend/README.md)

Memory-X 使用 `MemoryStore` 接口实现可插拔存储。

| 后端 | 说明 |
| --- | --- |
| `SQLiteMemoryStore` | 默认本地开发使用，支持向量搜索。 |
| `SpannerMemoryStore` | Cloud Spanner 适配层（示例/stub），参考 Vertex AI 的全局分布式记忆设计。 |
| `Mem0MemoryStore` | 基于 mem0 项目的存储后端，便于与其生态集成。 |

切换后端只需在配置中指定 `MEMORY_DB_TYPE`：
```bash
export MEMORY_DB_TYPE=sqlite   # 或 spanner 或 mem0
```

## 🧭 症状与用药的合并规则

项目在 `src/core/algorithms_reference.py` 中提供了“用药周期”和“症状发作”的 Append/Update/Merge 决策与置信度评分：

- 用药：`decide_update_merge_append` / `compute_merge_confidence`
- 症状：`decide_update_merge_append_symptom` / `compute_symptom_merge_confidence`

症状合并与用药不同，更宽容时间空窗（默认 ≤14 天），并在高危症状（如胸痛、呼吸困难）场景提升阈值以确保安全。

## 🩺 用药记忆的更新策略

项目新增的 `medical_memory` 模块参考 FHIR `MedicationStatement` 设计，
提供了 ``upsert_medication_entry`` 方法用于在 Append、Update、Merge 之间做出
决策：

- **Append**：发现全新疗程或不同方案时新增记录；
- **Update**：同一疗程内补充剂量、时间等字段，自动增加版本号；
- **Merge**：检测到被误分裂的疗程时合并时间区间，并写入新的版本。

每条记录同时维护事实时间（`start`/`end`）与系统更新时间
（`last_updated`/`version_id`），为审计和回溯提供基础。

## ⚙️ 配置
所有敏感信息通过环境变量提供：
```bash
MEMORY_DB_TYPE=sqlite        # 或 spanner 或 mem0
MEMORY_DB_PATH=./memory.db   # SQLite 时有效
MEMORY_DB_USER=your_user     # Cloud Spanner 时使用
MEMORY_DB_PASSWORD=your_password
```

## 🧪 测试
```bash
pytest -q           # 或
bash scripts/test.sh
```

## 🛠️ 常用脚本

- `scripts/setup_venv.sh`：创建并初始化虚拟环境
- `scripts/test.sh`：运行测试
- `scripts/run_api.sh`：启动后端 API 服务
- `scripts/run_frontend.sh`：启动前端开发服务器
- `scripts/start_all.sh`：一键启动前端+后端服务
- `scripts/clean.sh`：清理缓存/日志/测试报告
- `scripts/push.sh`：推送当前分支至远程

## 🧹 仓库卫生

- 已通过 `.gitignore` 排除本地数据库、日志、缓存与测试报告 JSON 文件：
  - `memory_db/*.db*`、`logs/`、`.pytest_cache/`、`.coverage`、`tests/*report*.json`、`tests/reports/*.json`
- 如需清理工作区中的这些生成文件，执行：
  ```bash
  bash scripts/clean.sh
  ```

## 📚 文档
更多设计细节、API 说明和业务测试示例请见 [docs/](docs) 与 [examples/](examples)。

## 🤝 贡献
欢迎提交 Issue 或 PR。代码风格遵循 PEP 8，并请附带单元测试。

## 📄 许可证
项目采用 [MIT License](LICENSE)。
