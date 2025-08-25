# Memory-X | 智能记忆管理系统

Memory-X 是一个用于对话式 AI 的记忆管理库，提供多层次记忆、内容检索以及可插拔的存储后端。默认使用 SQLite，本项目还提供一个遵循 Google Vertex AI Memory 设计的 Cloud Spanner 适配层，便于迁移到分布式、全球可用的存储。

## ✨ 特性

- **层次化记忆**：短期、工作、长期记忆分层管理，支持上下文延续。
- **内容检索**：`search_memories` API 支持向量相似度搜索，召回相关记忆。
- **可插拔存储**：通过 `MemoryStore` 抽象，可选择 SQLite、Spanner 等后端。
- **RESTful API**：基于 Flask，提供简单的 HTTP 接口，支持 DashScope 可选集成。
- **易于配置**：支持环境变量和配置文件。
- **完善测试**：包含单元测试、业务级场景测试。

## 🚀 快速开始

1. 克隆仓库并安装依赖

```bash
git clone https://github.com/ylouis/memory-x.git
cd memory-x
pip install -r requirements.txt
```

2. 初始化数据库并运行示例

```bash
python src/core/init_database.py
python examples/basic_usage.py
```

3. 启动 API 服务

```bash
python src/api/app.py
```

## 🗄️ 存储后端

Memory-X 使用 `MemoryStore` 接口实现可插拔存储。

| 后端 | 说明 |
| --- | --- |
| `SQLiteMemoryStore` | 默认本地开发使用，支持向量搜索。 |
| `SpannerMemoryStore` | Cloud Spanner 适配层（示例/stub），参考 Vertex AI 的全局分布式记忆设计。 |

切换后端只需在配置中指定 `MEMORY_DB_TYPE`：

```bash
export MEMORY_DB_TYPE=sqlite   # 或 spanner
```

## 📚 进一步阅读

- `docs/SECURITY_FIX.md` 安全配置说明
- `docs/dashscope_integration.md` DashScope 集成指南

## 🧪 测试

```bash
pytest -q
```

## 🤝 贡献

欢迎提交 Issue 或 PR。代码风格遵循 PEP 8，并请附带单元测试。

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE)。

