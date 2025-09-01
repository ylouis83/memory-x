# Memory-X | 智能记忆管理系统

 Memory-X 是一个参考 Google Vertex AI Memory Bank 设计的 Python 记忆管理系统。它提供统一的 `MemoryManager` 与可插拔的 `MemoryStore`，默认使用轻量级的 `SQLiteMemoryStore`，并预留 `SpannerMemoryStore` 以便未来接入 Cloud Spanner 等云数据库，实现全球分布式记忆存储。此外，通过 `Mem0MemoryStore`，项目可以直接复用 [mem0](https://github.com/mem0ai/mem0) 的向量化记忆能力。

## ✨ 特性
- 层次化记忆：短期、工作和长期记忆分层管理
- 向量相似检索：`search_memories` 通过余弦相似度召回相关记忆
- 可插拔存储后端：`SQLiteMemoryStore` 开箱即用，`SpannerMemoryStore` 便于扩展
- RESTful API：基于 Flask，可选 DashScope 集成
- 易于配置：支持环境变量或配置文件
- 完善测试覆盖：单元测试与业务级场景测试

## 📦 安装
```bash
# 克隆项目并进入目录
git clone https://github.com/ylouis/memory-x.git
cd memory-x

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Windows 使用 venv\\Scripts\\activate

# 安装依赖
pip install -r requirements.txt
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
pytest -q
```

## 📚 文档
更多设计细节、API 说明和业务测试示例请见 [docs/](docs) 与 [examples/](examples)。

## 🤝 贡献
欢迎提交 Issue 或 PR。代码风格遵循 PEP 8，并请附带单元测试。

## 📄 许可证
项目采用 [MIT License](LICENSE)。

