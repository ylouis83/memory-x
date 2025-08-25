# Memory-X DashScope集成指南

## 概述

Memory-X项目已集成阿里云DashScope API，提供基于大语言模型的智能记忆管理和AI对话功能。本集成支持医疗场景的智能对话、实体识别、意图检测和记忆检索。

## 功能特性

### 🧠 智能记忆管理
- **多层级记忆**: 短期记忆、工作记忆、长期记忆
- **向量化存储**: 使用DashScope嵌入模型进行记忆向量化
- **相似度搜索**: 基于余弦相似度的记忆检索
- **重要性评估**: 自动评估记忆重要性并决定存储策略

### 🤖 AI对话能力
- **意图检测**: 自动识别用户意图（医疗咨询、用药咨询等）
- **实体识别**: 提取人名、疾病、药品、过敏史等实体
- **上下文理解**: 基于历史记忆的连续对话
- **个性化回复**: 根据用户病史和过敏史提供个性化建议

### 🔍 记忆检索
- **语义搜索**: 基于向量相似度的记忆检索
- **实体查询**: 按实体类型查询相关记忆
- **时间查询**: 支持时间范围的记忆查询
- **重要性排序**: 按重要性排序的检索结果

## 安装配置

### 1. 环境要求

```bash
# Python 3.8+
python3 --version

# 安装依赖
pip install -r requirements-dev.txt
```

### 2. DashScope API配置

#### 获取API密钥
1. 访问 [阿里云DashScope控制台](https://dashscope.console.aliyun.com/)
2. 开通DashScope服务
3. 创建API密钥

#### 设置环境变量

```bash
# 设置DashScope API密钥
export DASHSCOPE_API_KEY='your-api-key-here'

# 或者创建.env文件
echo "DASHSCOPE_API_KEY=your-api-key-here" > .env
```

### 3. 数据库初始化

```bash
# 初始化数据库
python3 src/core/init_database.py
```

## 使用方法

### 1. 基础使用

```python
from src.core.dashscope_memory_manager import DashScopeMemoryManager

# 创建记忆管理器
memory_manager = DashScopeMemoryManager("user_123")

# 处理用户消息
result = memory_manager.process_message("我对青霉素过敏")
print(result['response'])
print(result['intent'])
print(result['entities'])
```

### 2. 记忆搜索

```python
# 搜索相关记忆
results = memory_manager.search_memories("过敏", top_k=5)
for memory in results:
    print(f"相似度: {memory['similarity']}")
    print(f"用户消息: {memory['user_message']}")
    print(f"AI回复: {memory['ai_response']}")
```

### 3. 获取统计信息

```python
# 获取用户统计
stats = memory_manager.get_stats()
print(f"总记忆数: {stats['total_memories']}")
print(f"重要记忆数: {stats['important_memories']}")
```

## API接口

### 聊天接口

**POST** `/api/dashscope/chat`

```json
{
    "message": "我对青霉素过敏",
    "user_id": "user_123"
}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "response": "好的，我已经记录下你对青霉素过敏的信息...",
        "intent": "MEDICAL_INFO",
        "entities": {
            "ALLERGY": ["青霉素"]
        },
        "importance": 3,
        "embedding": true
    }
}
```

### 记忆搜索接口

**POST** `/api/dashscope/search`

```json
{
    "query": "过敏",
    "user_id": "user_123",
    "top_k": 5
}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "query": "过敏",
        "results": [
            {
                "user_message": "我对青霉素过敏",
                "ai_response": "好的，我已经记录下...",
                "similarity": 0.85,
                "importance": 3
            }
        ],
        "count": 1
    }
}
```

### 统计信息接口

**GET** `/api/dashscope/stats/{user_id}`

**响应**:
```json
{
    "success": true,
    "data": {
        "user_id": "user_123",
        "short_term_count": 5,
        "working_memory_size": 3,
        "total_memories": 10,
        "important_memories": 3,
        "session_id": "session_20250825"
    }
}
```

### 工作记忆接口

**GET** `/api/dashscope/working-memory/{user_id}`

**响应**:
```json
{
    "success": true,
    "data": {
        "user_id": "user_123",
        "working_memory": {
            "PERSON": ["张三"],
            "ALLERGY": ["青霉素"],
            "DISEASE": ["高血压"]
        },
        "short_term_count": 5
    }
}
```

## 测试

### 1. 运行集成测试

```bash
# 运行DashScope集成测试
python3 test_dashscope_integration.py
```

### 2. 运行使用示例

```bash
# 运行DashScope使用示例
python3 examples/dashscope_usage.py
```

### 3. 运行API测试

```bash
# 启动服务器
python3 run.py

# 在另一个终端运行API测试
python3 test_dashscope_api.py
```

### 4. 运行单元测试

```bash
# 运行所有测试
python3 -m pytest tests/ -v
```

## 配置选项

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DASHSCOPE_API_KEY` | - | DashScope API密钥（必需） |
| `MEMORY_DEBUG` | true | 调试模式 |
| `MEMORY_SERVICE_HOST` | 0.0.0.0 | 服务主机 |
| `MEMORY_SERVICE_PORT` | 5000 | 服务端口 |
| `MEMORY_DB_PATH` | ./memory_db/memory.db | 数据库路径 |
| `MEMORY_MAX_SHORT_TERM` | 10 | 短期记忆最大数量 |
| `MEMORY_MAX_WORKING_MEMORY` | 100 | 工作记忆最大数量 |
| `MEMORY_IMPORTANCE_THRESHOLD` | 3 | 重要性阈值 |

### 模型配置

```python
# DashScope模型配置
self.model = "qwen-turbo"  # 对话模型
embedding_model = "text-embedding-v1"  # 嵌入模型
```

## 架构设计

### 核心组件

```
Memory-X DashScope集成
├── DashScopeMemoryManager (核心管理器)
├── 记忆存储层 (SQLite + 向量存储)
├── AI处理层 (意图检测 + 实体识别)
├── API服务层 (Flask + RESTful API)
└── 测试验证层 (单元测试 + 集成测试)
```

### 数据流

```
用户输入 → 意图检测 → 实体识别 → 重要性评估 → 
AI回复生成 → 记忆存储 → 向量化 → 数据库持久化
```

### 记忆层级

1. **短期记忆**: 最近10轮对话，用于上下文理解
2. **工作记忆**: 当前会话的实体信息，用于快速访问
3. **长期记忆**: 重要信息持久化存储，支持向量搜索

## 性能优化

### 1. 缓存策略
- 短期记忆使用内存缓存
- 工作记忆使用字典结构
- 长期记忆使用SQLite + 向量索引

### 2. 批量处理
- 支持批量记忆存储
- 批量向量化处理
- 批量搜索优化

### 3. 异步处理
- API调用异步化
- 向量计算异步化
- 数据库操作异步化

## 故障排除

### 常见问题

1. **API密钥错误**
   ```
   错误: DASHSCOPE_API_KEY环境变量未设置
   解决: 设置正确的API密钥
   ```

2. **网络连接问题**
   ```
   错误: API连接失败
   解决: 检查网络连接和防火墙设置
   ```

3. **数据库错误**
   ```
   错误: 数据库存储失败
   解决: 检查数据库权限和磁盘空间
   ```

### 日志查看

```bash
# 查看应用日志
tail -f logs/memory.log

# 查看错误日志
grep "ERROR" logs/memory.log
```

## 扩展开发

### 1. 添加新的实体类型

```python
# 在DashScopeMemoryManager中扩展实体识别
def _extract_entities(self, message: str) -> Dict:
    # 添加新的实体类型
    entities = {
        "PERSON": [],
        "AGE": [],
        "DISEASE": [],
        "MEDICINE": [],
        "ALLERGY": [],
        "SYMPTOM": [],  # 新增症状实体
        "TREATMENT": []  # 新增治疗实体
    }
    # 实现实体识别逻辑
    return entities
```

### 2. 添加新的意图类型

```python
# 扩展意图检测
def _detect_intent(self, message: str) -> str:
    # 添加新的意图类型
    intent_types = [
        "INTRODUCE", "MEDICAL_INFO", "REQUEST_MEDICINE",
        "PRESCRIPTION_INQUIRY", "EMERGENCY", "NORMAL_CONSULTATION",
        "SYMPTOM_REPORT", "TREATMENT_QUERY"  # 新增意图
    ]
    # 实现意图检测逻辑
    return detected_intent
```

### 3. 自定义重要性评估

```python
# 自定义重要性评估规则
def _evaluate_importance(self, intent: str, entities: Dict) -> int:
    importance = 1
    
    # 自定义规则
    if intent == "EMERGENCY":
        importance = 5  # 紧急情况最高优先级
    elif "DISEASE" in entities:
        importance = 4  # 疾病信息高优先级
    
    return importance
```

## 最佳实践

### 1. 安全考虑
- 不要在代码中硬编码API密钥
- 使用环境变量管理敏感信息
- 定期轮换API密钥
- 监控API使用量

### 2. 性能优化
- 合理设置记忆容量限制
- 定期清理过期记忆
- 使用连接池管理数据库连接
- 实现记忆压缩和归档

### 3. 用户体验
- 提供清晰的错误提示
- 实现记忆搜索建议
- 支持记忆导出和导入
- 提供记忆可视化界面

## 更新日志

### v1.0.0 (2025-08-25)
- 初始DashScope集成
- 基础记忆管理功能
- RESTful API接口
- 向量搜索功能
- 医疗场景优化

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues: [项目地址]
- 邮箱: [联系邮箱]
