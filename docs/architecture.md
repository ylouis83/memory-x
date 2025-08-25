# Memory-X 架构设计文档

## 概述

Memory-X 是一个基于Python的智能记忆管理系统，采用模块化设计，支持多用户、多时态、多层次的记忆存储和查询功能。

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        Memory-X                             │
├─────────────────────────────────────────────────────────────┤
│  API Layer (Flask)                                          │
│  ├── REST API                                               │
│  ├── WebSocket API                                          │
│  └── Health Check                                           │
├─────────────────────────────────────────────────────────────┤
│  Business Logic Layer                                       │
│  ├── Memory Manager                                         │
│  ├── Entity Recognizer                                      │
│  ├── Intent Detector                                        │
│  └── Importance Evaluator                                   │
├─────────────────────────────────────────────────────────────┤
│  Data Access Layer                                          │
│  ├── SQLAlchemy ORM                                         │
│  ├── Database Connector                                     │
│  └── Cache Manager                                          │
├─────────────────────────────────────────────────────────────┤
│  Storage Layer                                              │
│  ├── SQLite (Default)                                       │
│  ├── MySQL                                                  │
│  ├── PostgreSQL                                             │
│  └── Redis Cache                                            │
└─────────────────────────────────────────────────────────────┘
```

## 核心模块

### 1. Memory Manager (记忆管理器)

**职责**: 管理用户的短期记忆、工作记忆和长期记忆

**主要功能**:
- 记忆的存储和检索
- 记忆重要性评估
- 记忆生命周期管理
- 上下文连续性维护

**核心类**:
```python
class MemoryManager:
    def add_conversation(self, user_message, ai_response, entities, intent, importance)
    def get_relevant_memories(self, query)
    def get_memory_stats(self)
    def clear_session(self)
```

### 2. Entity Recognizer (实体识别器)

**职责**: 识别用户消息中的关键实体

**支持的实体类型**:
- PERSON (人名)
- LOCATION (地点)
- ORGANIZATION (组织)
- MEDICINE (药品)
- SYMPTOM (症状)
- DISEASE (疾病)
- TREATMENT (治疗)

**核心类**:
```python
class EntityRecognizer:
    def recognize_entities(self, text)
    def extract_medical_entities(self, text)
    def extract_personal_info(self, text)
```

### 3. Intent Detector (意图检测器)

**职责**: 分析用户意图

**支持的意图类型**:
- INTRODUCE (自我介绍)
- REQUEST_MEDICINE (请求开药)
- PRESCRIPTION_INQUIRY (用药咨询)
- EMERGENCY (紧急情况)
- NORMAL_CONSULTATION (普通咨询)

**核心类**:
```python
class IntentDetector:
    def detect_intent(self, text)
    def get_confidence(self, intent)
    def get_intent_patterns(self)
```

### 4. Importance Evaluator (重要性评估器)

**职责**: 评估记忆内容的重要性

**评估因素**:
- 意图权重 (30%)
- 实体权重 (20%)
- 频率权重 (20%)
- 时效性权重 (15%)
- 用户反馈权重 (15%)

**重要性等级**:
- 1: 低重要性
- 2: 中等重要性
- 3: 高重要性
- 4: 关键重要性

## 数据模型

### 1. Fact Memory (事实记忆)

支持双时态查询的事实记忆表：

```sql
CREATE TABLE fact_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    importance INTEGER DEFAULT 2,
    confidence REAL DEFAULT 0.8,
    valid_from TEXT NOT NULL,      -- 生效时间
    valid_to TEXT,                 -- 失效时间
    commit_ts TEXT NOT NULL,       -- 提交时间
    expire_at TEXT,                -- 过期时间
    provenance TEXT,               -- 来源信息
    metadata TEXT,                 -- 元数据
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

### 2. Conversation Memory (对话记忆)

存储对话历史：

```sql
CREATE TABLE conversation_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    entities TEXT,
    intent TEXT,
    importance INTEGER DEFAULT 2,
    timestamp TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

### 3. Entity Memory (实体记忆)

存储识别到的实体：

```sql
CREATE TABLE entity_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_value TEXT NOT NULL,
    entity_metadata TEXT,
    frequency INTEGER DEFAULT 1,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    confidence REAL DEFAULT 0.8,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

## 记忆架构

### 三层记忆模型

```
┌─────────────────────────────────────────────────────────────┐
│                    长期记忆 (Long-term Memory)               │
│  ├── 事实记忆 (Fact Memory)                                 │
│  ├── 事件记忆 (Event Memory)                                │
│  └── 知识记忆 (Knowledge Memory)                            │
├─────────────────────────────────────────────────────────────┤
│                    工作记忆 (Working Memory)                 │
│  ├── 当前会话状态                                           │
│  ├── 活跃实体                                               │
│  └── 临时信息                                               │
├─────────────────────────────────────────────────────────────┤
│                    短期记忆 (Short-term Memory)             │
│  ├── 最近对话历史 (最近10轮)                                │
│  └── 即时信息                                               │
└─────────────────────────────────────────────────────────────┘
```

### 记忆流转机制

1. **短期记忆**: 所有对话首先进入短期记忆
2. **重要性评估**: 根据内容重要性决定是否进入长期记忆
3. **长期存储**: 重要信息存储到数据库
4. **检索机制**: 根据查询相关性检索相关记忆

## API设计

### RESTful API

#### 基础接口

- `GET /health` - 健康检查
- `POST /api/memory` - 添加记忆
- `GET /api/memory/{user_id}` - 查询记忆
- `GET /api/memory/{user_id}/stats` - 获取记忆统计
- `POST /api/memory/{user_id}/clear` - 清空用户记忆

#### 高级接口

- `POST /api/memory/chat` - 记忆聊天接口
- `POST /api/memory/query` - 高级记忆查询

### WebSocket API

- `/ws/memory/{user_id}` - 实时记忆同步

## 配置管理

### 环境变量

```bash
# 数据库配置
MEMORY_DB_TYPE=sqlite
MEMORY_DB_PATH=./memory_db/memory.db
MEMORY_DB_HOST=localhost
MEMORY_DB_PORT=3306

# 服务配置
MEMORY_SERVICE_HOST=0.0.0.0
MEMORY_SERVICE_PORT=5000
MEMORY_SERVICE_DEBUG=true

# 记忆配置
MEMORY_MAX_SHORT_TERM=10
MEMORY_IMPORTANCE_THRESHOLD=3
MEMORY_TTL_DAYS=365
```

### 配置文件

支持多环境配置：
- Development (开发环境)
- Production (生产环境)
- Testing (测试环境)

## 性能优化

### 1. 数据库优化

- 索引优化
- 查询优化
- 连接池管理

### 2. 缓存策略

- Redis缓存热点数据
- 内存缓存短期记忆
- 查询结果缓存

### 3. 并发处理

- 异步处理
- 连接池
- 负载均衡

## 安全设计

### 1. 数据安全

- 数据加密存储
- 访问权限控制
- 数据备份机制

### 2. API安全

- 身份认证
- 权限验证
- 请求限流

### 3. 隐私保护

- 用户数据隔离
- 敏感信息脱敏
- 数据生命周期管理

## 监控和日志

### 1. 监控指标

- 服务健康状态
- 性能指标
- 业务指标

### 2. 日志管理

- 结构化日志
- 日志轮转
- 日志分析

## 扩展性设计

### 1. 水平扩展

- 无状态服务设计
- 负载均衡
- 数据库分片

### 2. 功能扩展

- 插件化架构
- 模块化设计
- API版本管理

### 3. 存储扩展

- 多数据库支持
- 分布式存储
- 云存储集成

## 部署架构

### 1. 容器化部署

- Docker容器
- Kubernetes编排
- 服务网格

### 2. 云原生部署

- 微服务架构
- 服务发现
- 配置管理

### 3. 高可用部署

- 多实例部署
- 故障转移
- 数据备份

## 总结

Memory-X 采用现代化的架构设计，具有以下特点：

1. **模块化设计**: 清晰的模块分离，易于维护和扩展
2. **双时态架构**: 支持时间旅行查询和版本管理
3. **多数据库支持**: 灵活的存储选择
4. **RESTful API**: 标准化的接口设计
5. **配置化管理**: 支持多环境部署
6. **性能优化**: 多层次缓存和优化策略
7. **安全可靠**: 完善的安全机制和监控体系

这种架构设计使得 Memory-X 能够满足不同规模和需求的记忆管理应用场景。
