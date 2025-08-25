# Memory-X | 智能记忆管理系统

Memory-X 是一个参考 Google Vertex AI Memory Bank 设计的 Python 记忆管理系统。它提供统一的 `MemoryManager` 和可插拔的 `MemoryStore`，默认使用轻量级的 `SQLiteStore`，同时预留了 `SpannerStore` 接口以便将来接入 Cloud Spanner 等云数据库，实现全球分布式记忆存储。

## ✨ 特性
- 多层次记忆：短期、工作和长期记忆分层管理
- 向量相似检索：`search_memories` 通过余弦相似度召回相关记忆
- 可插拔存储后端：`SQLiteStore` 开箱即用，`SpannerStore` 便于扩展
- RESTful API 与可选 DashScope 集成
- 单元测试与集成测试覆盖核心功能

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
    ai_response="你好张三，很高兴认识你！"
)
print(mm.search_memories("张三"))
```

## ⚙️ 配置
所有敏感信息通过环境变量提供：
```bash
MEMORY_DB_TYPE=sqlite        # 或 spanner
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

## 📄 许可证
项目采用 [MIT License](LICENSE)。
