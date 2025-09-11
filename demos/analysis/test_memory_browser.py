#!/usr/bin/env python3
"""
测试Memory-X前端记忆浏览页面功能
"""

import requests
import json

def test_memory_browser_data():
    """测试记忆浏览页面所需的API数据"""
    print("🔍 测试记忆浏览页面API数据...")
    
    BACKEND_URL = "http://localhost:5000"
    TEST_USER = "memory_browser_test"
    
    try:
        # 1. 先发送一些测试数据，创建记忆
        print("📝 创建测试记忆数据...")
        test_messages = [
            "我叫李明，今年25岁，程序员",
            "最近工作压力大，经常熬夜",
            "有时会头痛，需要吃布洛芬"
        ]
        
        for msg in test_messages:
            response = requests.post(f"{BACKEND_URL}/api/memory/chat", json={
                "user_id": TEST_USER,
                "message": msg
            })
            if response.status_code == 200:
                print(f"  ✅ 已创建记忆: {msg[:20]}...")
            else:
                print(f"  ❌ 创建记忆失败: {response.status_code}")
        
        # 2. 测试获取记忆列表（短期记忆）
        print("\n🔍 测试短期记忆获取...")
        response = requests.get(f"{BACKEND_URL}/api/memory/{TEST_USER}")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ 短期记忆: {data['count']} 条")
            if data['memories']:
                print(f"  💬 最新记忆: {data['memories'][0]['user_message'][:30]}...")
        else:
            print(f"  ❌ 获取短期记忆失败: {response.status_code}")
        
        # 3. 测试记忆搜索（长期记忆）
        print("\n🔍 测试长期记忆搜索...")
        response = requests.get(f"{BACKEND_URL}/api/memory/{TEST_USER}?query=头痛")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ 搜索结果: {data['count']} 条")
        else:
            print(f"  ❌ 搜索记忆失败: {response.status_code}")
        
        # 4. 测试记忆统计
        print("\n📊 测试记忆统计...")
        response = requests.get(f"{BACKEND_URL}/api/memory/{TEST_USER}/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data['stats']
            print(f"  ✅ 统计数据:")
            print(f"    - 短期记忆: {stats['short_term_count']}")
            print(f"    - 工作记忆: {stats['working_memory_size']}")
            print(f"    - 长期记忆: {stats['total_long_term']}")
            print(f"    - 会话ID: {stats['session_id']}")
        else:
            print(f"  ❌ 获取统计失败: {response.status_code}")
        
        print(f"\n🎉 记忆浏览页面API测试完成！")
        print(f"💡 现在可以在前端页面点击'记忆浏览'标签查看数据")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_memory_browser_data()