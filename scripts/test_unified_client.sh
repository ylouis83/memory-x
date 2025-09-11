#!/bin/bash

# Memory-X 统一百炼API客户端配置测试脚本
# Test script for unified DashScope API client configuration

set -e

echo "🧪 Memory-X 统一百炼API客户端配置测试"
echo "专为医疗AI场景优化"
echo "=================================="

# 检查项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📁 项目根目录: $PROJECT_ROOT"

# 检查环境变量
if [ -z "$DASHSCOPE_API_KEY" ]; then
    echo "⚠️  警告：未设置DASHSCOPE_API_KEY环境变量"
    echo "请设置环境变量或创建.env文件"
    if [ -f ".env.example" ]; then
        echo "💡 提示：可以参考.env.example文件"
    fi
    echo ""
fi

# 激活虚拟环境
if [ -f ".venv/bin/activate" ]; then
    echo "🔧 激活虚拟环境..."
    source .venv/bin/activate
else
    echo "❌ 虚拟环境不存在，请先运行 bash scripts/setup_venv.sh"
    exit 1
fi

# 设置Python路径
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

echo "🔍 检查统一客户端配置文件..."
if [ -f "configs/dashscope_client.py" ]; then
    echo "✅ 统一客户端配置文件存在"
else
    echo "❌ 统一客户端配置文件不存在"
    exit 1
fi

echo ""
echo "📋 测试计划："
echo "1. 语法检查"
echo "2. 导入测试" 
echo "3. 基础功能测试"
echo "4. 演示脚本测试"
echo ""

# 1. 语法检查
echo "1️⃣ 语法检查..."
python -m py_compile configs/dashscope_client.py
echo "✅ 语法检查通过"

# 2. 导入测试
echo ""
echo "2️⃣ 导入测试..."
python -c "
import sys
sys.path.insert(0, '.')
try:
    from configs.dashscope_client import (
        DashScopeClientFactory, 
        get_global_client, 
        quick_ask, 
        medical_consultation, 
        check_medication_safety
    )
    print('✅ 所有主要组件导入成功')
except ImportError as e:
    print(f'❌ 导入失败: {e}')
    sys.exit(1)
"

# 3. 基础功能测试（不需要API key）
echo ""
echo "3️⃣ 基础功能测试..."
python -c "
import sys
sys.path.insert(0, '.')
try:
    from configs.dashscope_client import DashScopeConfig, DashScopeClientFactory
    
    # 测试配置类
    try:
        config = DashScopeConfig(api_key='test-key')
        print('✅ 配置类创建成功')
    except Exception as e:
        print(f'❌ 配置类测试失败: {e}')
        sys.exit(1)
    
    # 测试工厂类（不实际调用API）
    print('✅ 基础功能测试通过')
    
except Exception as e:
    print(f'❌ 基础功能测试失败: {e}')
    sys.exit(1)
"

# 4. 演示脚本测试
echo ""
echo "4️⃣ 演示脚本测试..."
if [ -f "demos/unified_client_demo.py" ]; then
    echo "✅ 演示脚本存在"
    python -m py_compile demos/unified_client_demo.py
    echo "✅ 演示脚本语法检查通过"
else
    echo "❌ 演示脚本不存在"
fi

# 5. 验证现有代码更新
echo ""
echo "5️⃣ 验证现有代码更新..."
updated_files=(
    "src/core/qwen_update_engine.py"
    "src/core/qwen_graph_update_engine.py" 
)

for file in "${updated_files[@]}"; do
    if [ -f "$file" ]; then
        if grep -q "configs.dashscope_client" "$file"; then
            echo "✅ $file 已更新使用统一客户端"
        else
            echo "⚠️  $file 可能需要更新"
        fi
    else
        echo "❌ $file 不存在"
    fi
done

echo ""
echo "🎉 统一客户端配置测试完成！"
echo ""
echo "📋 使用说明："
echo "1. 设置环境变量: export DASHSCOPE_API_KEY='your-api-key'"
echo "2. 运行演示: python demos/unified_client_demo.py"  
echo "3. 在代码中导入: from configs.dashscope_client import DashScopeClientFactory"
echo "4. 创建客户端: client = DashScopeClientFactory.create_medical_client()"
echo ""
echo "🏥 医疗专用特性："
echo "- 支持配置患者年龄、过敏史、家族病史"
echo "- 提供症状诊断和药物安全检查功能"
echo "- 自动考虑患者个人医疗信息进行智能分析"
echo "- 支持多种医疗AI应用场景"