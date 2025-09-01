#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DashScope API测试脚本
测试DashScope集成的API端点
"""

import os
import sys
import requests
import json
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_dashscope_api():
    """测试DashScope API"""
    print("🚀 Memory-X DashScope API测试")
    print("=" * 50)
    
    # 检查API密钥
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ 未设置DASHSCOPE_API_KEY环境变量")
        print("请设置环境变量：export DASHSCOPE_API_KEY='your-api-key'")
        return False
    
    print(f"✅ API密钥已设置: {api_key[:10]}...")
    
    # 启动服务器（这里假设服务器已经在运行）
    base_url = "http://localhost:5000"
    
    # 测试健康检查
    print("\n🧪 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/api/dashscope/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过: {data}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False
    
    # 测试连接检查
    print("\n🧪 测试DashScope连接...")
    try:
        response = requests.post(f"{base_url}/api/dashscope/test-connection")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 连接测试通过: {data['message']}")
        else:
            print(f"❌ 连接测试失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接测试异常: {e}")
        return False
    
    # 测试聊天功能
    print("\n🧪 测试聊天功能...")
    test_messages = [
        "你好，我叫李四",
        "我对海鲜过敏",
        "我有糖尿病，需要注意什么？"
    ]
    
    user_id = "api_test_user"
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- 聊天测试 {i} ---")
        print(f"用户: {message}")
        
        try:
            response = requests.post(
                f"{base_url}/api/dashscope/chat",
                json={
                    'message': message,
                    'user_id': user_id
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    result = data['data']
                    print(f"AI: {result['response'][:100]}...")
                    print(f"意图: {result['intent']}")
                    print(f"重要性: {result['importance']}")
                else:
                    print(f"❌ 聊天失败: {data.get('error', '未知错误')}")
                    return False
            else:
                print(f"❌ 聊天请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 聊天异常: {e}")
            return False
    
    # 测试记忆搜索
    print("\n🧪 测试记忆搜索...")
    search_queries = ["过敏", "糖尿病", "李四"]
    
    for query in search_queries:
        print(f"\n搜索: '{query}'")
        try:
            response = requests.post(
                f"{base_url}/api/dashscope/search",
                json={
                    'query': query,
                    'user_id': user_id,
                    'top_k': 3
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    results = data['data']['results']
                    print(f"找到 {len(results)} 条相关记忆")
                    for i, memory in enumerate(results, 1):
                        print(f"  {i}. 相似度: {memory['similarity']:.3f}")
                        print(f"     用户: {memory['user_message']}")
                else:
                    print(f"❌ 搜索失败: {data.get('error', '未知错误')}")
            else:
                print(f"❌ 搜索请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 搜索异常: {e}")
    
    # 测试统计信息
    print("\n🧪 测试统计信息...")
    try:
        response = requests.get(f"{base_url}/api/dashscope/stats/{user_id}")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                stats = data['data']
                print("📊 用户统计:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
            else:
                print(f"❌ 获取统计失败: {data.get('error', '未知错误')}")
        else:
            print(f"❌ 统计请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 统计异常: {e}")
    
    # 测试工作记忆
    print("\n🧪 测试工作记忆...")
    try:
        response = requests.get(f"{base_url}/api/dashscope/working-memory/{user_id}")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                working_memory = data['data']['working_memory']
                print("🧠 工作记忆:")
                for entity_type, entities in working_memory.items():
                    print(f"  {entity_type}: {entities}")
            else:
                print(f"❌ 获取工作记忆失败: {data.get('error', '未知错误')}")
        else:
            print(f"❌ 工作记忆请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 工作记忆异常: {e}")
    
    print("\n✅ DashScope API测试完成！")
    return True

def main():
    """主函数"""
    success = test_dashscope_api()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
