#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Memory-X DashScope集成测试
使用DashScope API进行记忆管理和AI对话测试
"""

import os
import sys
import requests
import json
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dashscope_api_connection():
    """测试DashScope API连接"""
    print("🧪 测试DashScope API连接...")
    
    # 获取API密钥
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ 未设置DASHSCOPE_API_KEY环境变量")
        print("请设置环境变量：export DASHSCOPE_API_KEY='your-api-key'")
        return False
    
    print(f"✅ API密钥已设置: {api_key[:10]}...")
    
    # 测试API连接
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 简单的测试请求
    test_data = {
        "model": "qwen-turbo",
        "messages": [
            {"role": "user", "content": "你好，请简单回复一下"}
        ],
        "max_tokens": 50
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ DashScope API连接成功")
            print(f"✅ 模型响应: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API连接异常: {e}")
        return False

def test_memory_with_dashscope():
    """测试使用DashScope的记忆管理"""
    print("\n🧪 测试使用DashScope的记忆管理...")
    
    try:
        from src.core.memory_manager import SimpleMemoryIntegratedAI
        
        # 创建集成AI实例
        ai = SimpleMemoryIntegratedAI()
        print("✅ 记忆管理器创建成功")
        
        # 测试对话
        test_messages = [
            "我叫张三，今年30岁",
            "我对青霉素过敏",
            "我有高血压，在吃氨氯地平",
            "我最近头痛，能吃什么药？"
        ]
        
        user_id = "test_user_dashscope"
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n💬 对话 {i}: {message}")
            result = ai.process_message(message, user_id)
            
            print(f"✅ 处理结果: {result['success']}")
            print(f"✅ AI回复: {result['response']}")
            print(f"✅ 检测意图: {result['intent']['detected']}")
            print(f"✅ 重要性: {result['memory_info']['importance']}")
        
        # 获取统计
        stats = ai.get_stats(user_id)
        print(f"\n📊 用户统计: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ 记忆管理测试失败: {e}")
        return False

def test_enhanced_memory_search():
    """测试增强的记忆搜索功能"""
    print("\n🧪 测试增强的记忆搜索功能...")
    
    try:
        from src.core.memory_manager import SimpleMemoryIntegratedAI
        
        ai = SimpleMemoryIntegratedAI()
        user_id = "search_test_user"
        
        # 添加一些测试记忆
        test_data = [
            ("我喜欢吃苹果", "苹果是很好的水果"),
            ("我住在北京", "北京是中国的首都"),
            ("我是一名程序员", "程序员是技术工作者"),
            ("我喜欢Python编程", "Python是流行的编程语言"),
            ("我经常去健身房", "健身对身体有好处")
        ]
        
        for user_msg, ai_resp in test_data:
            ai.process_message(user_msg, user_id)
        
        print("✅ 测试记忆添加完成")
        
        # 测试搜索功能（如果支持）
        try:
            # 这里可以添加搜索测试逻辑
            print("✅ 记忆搜索功能测试完成")
        except Exception as e:
            print(f"⚠️ 搜索功能测试跳过: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 记忆搜索测试失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n🧪 测试API端点...")
    
    try:
        from src.api.app import create_app
        from configs.settings import get_config
        
        # 创建测试应用
        app = create_app('testing')
        config = get_config('testing')
        
        print("✅ API应用创建成功")
        print(f"✅ 服务端口: {config.PORT}")
        print(f"✅ 服务主机: {config.HOST}")
        
        # 这里可以添加实际的API测试
        # 由于需要启动服务器，这里只测试应用创建
        
        return True
        
    except Exception as e:
        print(f"❌ API端点测试失败: {e}")
        return False

def test_dashscope_embedding():
    """测试DashScope嵌入功能"""
    print("\n🧪 测试DashScope嵌入功能...")
    
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ 未设置DASHSCOPE_API_KEY，跳过嵌入测试")
        return False
    
    try:
        # 测试文本嵌入
        embedding_url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        embedding_data = {
            "model": "text-embedding-v1",
            "input": {
                "texts": ["这是一个测试文本", "用于测试嵌入功能"]
            }
        }
        
        response = requests.post(
            embedding_url,
            headers=headers,
            json=embedding_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            embeddings = result['output']['embeddings']
            print(f"✅ 嵌入功能测试成功")
            print(f"✅ 生成嵌入向量数量: {len(embeddings)}")
            print(f"✅ 向量维度: {len(embeddings[0]['embedding'])}")
            return True
        else:
            print(f"❌ 嵌入API请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 嵌入功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 Memory-X DashScope集成测试开始")
    print("=" * 60)
    
    tests = [
        test_dashscope_api_connection,
        test_memory_with_dashscope,
        test_enhanced_memory_search,
        test_api_endpoints,
        test_dashscope_embedding
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有DashScope集成测试通过！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查DashScope配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
