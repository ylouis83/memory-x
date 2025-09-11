#!/usr/bin/env python3
"""
直接测试记忆存储功能
"""

import json
import requests

def test_direct_memory_storage():
    """直接测试记忆存储功能"""
    base_url = "http://127.0.0.1:5000"
    
    # 准备测试数据
    user_id = "demo_user"
    test_message = "我叫柳阳，我今年40岁，我对青霉素过敏，我家有遗传病史（糖尿病）"
    
    print(f"🧪 测试直接记忆存储功能")
    print(f"用户ID: {user_id}")
    print(f"测试消息: {test_message}")
    print("-" * 50)
    
    # 1. 首先检查服务器健康状态
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ 服务器健康检查通过")
        else:
            print(f"❌ 服务器健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return False
    
    # 2. 测试聊天API
    print("\n💬 测试聊天API...")
    try:
        chat_data = {
            "user_id": user_id,
            "message": test_message
        }
        
        response = requests.post(
            f"{base_url}/api/memory/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"聊天API响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('success'):
                print("✅ 聊天API调用成功")
            else:
                print(f"❌ 聊天API调用失败: {result}")
                return False
        else:
            print(f"❌ 聊天API调用失败: {response.status_code}")
            print(f"错误内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 聊天API调用异常: {e}")
        return False
    
    # 3. 查询记忆检索功能
    print("\n🔍 测试记忆检索功能...")
    
    # 查询关键词
    test_queries = ["柳阳", "40岁", "青霉素", "过敏", "糖尿病", "遗传病"]
    
    for query in test_queries:
        try:
            response = requests.get(
                f"{base_url}/api/memory/{user_id}",
                params={"query": query, "limit": 5}
            )
            
            if response.status_code == 200:
                result = response.json()
                memories = result.get('memories', [])
                print(f"查询 '{query}': 找到 {len(memories)} 条记忆")
                
                if memories:
                    for i, memory in enumerate(memories[:2], 1):  # 只显示前2条
                        print(f"  记忆 {i}: {memory.get('user_message', 'N/A')[:50]}...")
                else:
                    print(f"  ⚠️ 未找到包含 '{query}' 的记忆")
            else:
                print(f"❌ 查询 '{query}' 失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 查询 '{query}' 异常: {e}")
    
    # 4. 检查记忆统计
    print(f"\n📊 检查用户 {user_id} 的记忆统计...")
    try:
        response = requests.get(f"{base_url}/api/memory/{user_id}/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"记忆统计: {json.dumps(stats, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 获取统计失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 获取统计异常: {e}")
    
    return True

if __name__ == "__main__":
    success = test_direct_memory_storage()
    if success:
        print("\n🎉 测试完成！")
    else:
        print("\n❌ 测试失败！")