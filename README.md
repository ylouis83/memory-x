# Memory‑X | 智能记忆管理系统

Memory‑X 参考 Google Vertex AI Memory Bank 设计，提供统一的 `MemoryManager` 与可插拔的 `MemoryStore`。默认使用轻量级 `SQLiteMemoryStore`，并预留 `SpannerMemoryStore` 以便未来接入 Cloud Spanner 实现全球分布式记忆存储。通过 `Mem0MemoryStore`，可直接复用 [mem0](https://github.com/mem0ai/mem0) 的向量化能力。

## ✨ 特性
- 层次化记忆：短期、工作和长期记忆分层管理
- 向量相似检索：`search_memories` 通过余弦相似度召回相关记忆
- 可插拔存储后端：`SQLiteMemoryStore` 开箱即用，`SpannerMemoryStore` 便于扩展
- RESTful API：基于 Flask，可选 DashScope 集成
- 易于配置：支持环境变量或配置文件
- 完善测试覆盖：单元测试与业务级场景测试
- FHIR 风格的用药记忆：`medical_memory` 模块实现 Append/Update/Merge 规则

## 📦 安装
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

## 🗄️ 存储后端
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
- `scripts/run_api.sh`：启动最小 API
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
