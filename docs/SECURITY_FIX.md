# Memory-X 安全修复指南

## 🚨 发现的安全问题

### 1. 硬编码API密钥
在多个文件中发现了硬编码的DashScope API密钥：
- `<YOUR_DASHSCOPE_API_KEY>`

### 2. 重复环境变量配置
在 `~/.zshrc` 中有3行重复的API密钥配置

## 🔧 修复步骤

### 步骤1: 清理环境变量配置

```bash
# 备份当前配置
cp ~/.zshrc ~/.zshrc.backup

# 编辑.zshrc文件，只保留一行API密钥配置
nano ~/.zshrc
```

**修改内容**：
```bash
# 删除重复的行，只保留一行
export DASHSCOPE_API_KEY="<YOUR_DASHSCOPE_API_KEY>"
```

### 步骤2: 移除硬编码密钥

需要修改以下文件，将硬编码的API密钥替换为环境变量：

#### 1. rag-searx/demos/simple_video_rag_demo.py
```python
# 替换
os.environ['DASHSCOPE_API_KEY'] = '<YOUR_DASHSCOPE_API_KEY>'

# 为
api_key = os.getenv('DASHSCOPE_API_KEY')
if not api_key:
    raise ValueError("DASHSCOPE_API_KEY环境变量未设置")
os.environ['DASHSCOPE_API_KEY'] = api_key
```

#### 2. rag-searx/ragflow_integration/enhanced_video_rag_pipeline.py
```python
# 替换
os.environ['DASHSCOPE_API_KEY'] = '<YOUR_DASHSCOPE_API_KEY>'

# 为
api_key = os.getenv('DASHSCOPE_API_KEY')
if not api_key:
    raise ValueError("DASHSCOPE_API_KEY环境变量未设置")
os.environ['DASHSCOPE_API_KEY'] = api_key
```

#### 3. rag-searx/ragflow_integration/video_rag_pipeline.py
```python
# 替换
os.environ['DASHSCOPE_API_KEY'] = '<YOUR_DASHSCOPE_API_KEY>'

# 为
api_key = os.getenv('DASHSCOPE_API_KEY')
if not api_key:
    raise ValueError("DASHSCOPE_API_KEY环境变量未设置")
os.environ['DASHSCOPE_API_KEY'] = api_key
```

#### 4. AI-score/configs/llm_config.py
```python
# 替换
'api_key': '<YOUR_DASHSCOPE_API_KEY>',

# 为
'api_key': os.getenv('DASHSCOPE_API_KEY'),
```

#### 5. AI-score/examples/*.py
对所有示例文件进行类似修改

#### 6. AI-安主任/configs/config.py
```python
# 替换
API_KEY = "<YOUR_DASHSCOPE_API_KEY>"

# 为
API_KEY = os.getenv('DASHSCOPE_API_KEY')
if not API_KEY:
    raise ValueError("DASHSCOPE_API_KEY环境变量未设置")
```

### 步骤3: 轮换API密钥

1. **访问阿里云控制台**
   - 登录 [DashScope控制台](https://dashscope.console.aliyun.com/)
   - 进入API密钥管理页面

2. **创建新密钥**
   - 生成新的API密钥
   - 设置适当的权限和限制

3. **更新环境变量**
   ```bash
   # 更新.zshrc中的API密钥
   export DASHSCOPE_API_KEY="新的API密钥"
   
   # 重新加载配置
   source ~/.zshrc
   ```

4. **验证新密钥**
   ```bash
   # 测试新密钥是否工作
   python3 simple_business_test.py
   ```

5. **删除旧密钥**
   - 在DashScope控制台中删除旧的API密钥

### 步骤4: 添加.gitignore规则

确保以下文件不被提交到Git：

```gitignore
# 环境变量文件
.env
.env.local
.env.production

# 配置文件
config.ini
secrets.json

# 日志文件
*.log

# 临时文件
*.tmp
*.temp
```

### 步骤5: 创建环境变量模板

创建 `.env.example` 文件：

```bash
# DashScope API配置
DASHSCOPE_API_KEY=your-api-key-here

# 其他配置
MEMORY_DEBUG=true
MEMORY_SERVICE_HOST=0.0.0.0
MEMORY_SERVICE_PORT=5000
```

## 🔍 验证修复

### 1. 检查环境变量
```bash
echo $DASHSCOPE_API_KEY
# 应该显示新的API密钥
```

### 2. 运行测试
```bash
python3 simple_business_test.py
# 应该正常运行
```

### 3. 检查Git状态
```bash
git status
# 不应该显示包含API密钥的文件
```

## 🛡️ 安全最佳实践

### 1. 密钥管理
- ✅ 使用环境变量存储敏感信息
- ✅ 定期轮换API密钥
- ✅ 使用最小权限原则
- ✅ 监控API使用情况

### 2. 代码安全
- ✅ 避免硬编码敏感信息
- ✅ 使用.gitignore排除敏感文件
- ✅ 定期进行安全审计
- ✅ 实施代码审查

### 3. 环境安全
- ✅ 使用不同的密钥用于不同环境
- ✅ 限制API密钥的访问范围
- ✅ 启用API使用监控
- ✅ 设置使用配额

## 📋 检查清单

- [ ] 清理.zshrc中的重复配置
- [ ] 移除所有硬编码的API密钥
- [ ] 轮换API密钥
- [ ] 更新.gitignore规则
- [ ] 创建.env.example模板
- [ ] 验证所有功能正常工作
- [ ] 检查Git提交历史
- [ ] 设置API使用监控

## 🚨 紧急联系人

如果发现API密钥泄露：
1. 立即在DashScope控制台禁用密钥
2. 生成新的API密钥
3. 更新所有环境变量
4. 检查是否有未授权的使用

---

**注意**: 完成修复后，请确保所有团队成员都了解新的安全要求。
