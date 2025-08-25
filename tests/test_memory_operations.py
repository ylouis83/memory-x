#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆系统完整操作流程测试脚本
测试INSERT、UPDATE、MERGE、DELETE、QUERY等操作
"""

import requests
import json
import time

def test_memory_operations():
    """测试记忆系统的完整操作流程"""
    
    base_url = "http://localhost:5002"
    user_id = "test_user_001"
    
    print("🧠 AI-安主任记忆系统完整操作测试")
    print("=" * 60)
    
    # 测试场景1：名字记忆测试
    print("\n📋 测试场景1：名字记忆测试")
    print("-" * 40)
    
    # 1.1 告诉名字
    print("👤 用户: 我叫李四")
    response = requests.post(f"{base_url}/memory-chat", 
                           json={"message": "我叫李四", "user_id": user_id})
    data = response.json()
    print(f"🤖 AI: {data['response']}")
    print("📊 记忆操作:")
    for op in data.get('memory_operations', []):
        print(f"  {op['type']} - {op['operation']}: {op['details']}")
    
    time.sleep(1)
    
    # 1.2 查询名字
    print("\n👤 用户: 我的名字叫什么？")
    response = requests.post(f"{base_url}/memory-chat", 
                           json={"message": "我的名字叫什么？", "user_id": user_id})
    data = response.json()
    print(f"🤖 AI: {data['response']}")
    print("📊 记忆操作:")
    for op in data.get('memory_operations', []):
        print(f"  {op['type']} - {op['operation']}: {op['details']}")
    
    time.sleep(1)
    
    # 测试场景2：过敏史测试
    print("\n📋 测试场景2：过敏史测试")
    print("-" * 40)
    
    # 2.1 告诉过敏史
    print("👤 用户: 我对青霉素过敏")
    response = requests.post(f"{base_url}/memory-chat", 
                           json={"message": "我对青霉素过敏", "user_id": user_id})
    data = response.json()
    print(f"🤖 AI: {data['response']}")
    print("📊 记忆操作:")
    for op in data.get('memory_operations', []):
        print(f"  {op['type']} - {op['operation']}: {op['details']}")
    
    time.sleep(1)
    
    # 2.2 用药咨询（应该考虑过敏史）
    print("\n👤 用户: 我感冒了，能吃什么药？")
    response = requests.post(f"{base_url}/memory-chat", 
                           json={"message": "我感冒了，能吃什么药？", "user_id": user_id})
    data = response.json()
    print(f"🤖 AI: {data['response']}")
    print("📊 记忆操作:")
    for op in data.get('memory_operations', []):
        print(f"  {op['type']} - {op['operation']}: {op['details']}")
    
    time.sleep(1)
    
    # 测试场景3：慢性病测试
    print("\n📋 测试场景3：慢性病测试")
    print("-" * 40)
    
    # 3.1 告诉慢性病
    print("👤 用户: 我有高血压，在吃氨氯地平")
    response = requests.post(f"{base_url}/memory-chat", 
                           json={"message": "我有高血压，在吃氨氯地平", "user_id": user_id})
    data = response.json()
    print(f"🤖 AI: {data['response']}")
    print("📊 记忆操作:")
    for op in data.get('memory_operations', []):
        print(f"  {op['type']} - {op['operation']}: {op['details']}")
    
    time.sleep(1)
    
    # 3.2 查询用药情况
    print("\n👤 用户: 我的血压控制得怎么样？")
    response = requests.post(f"{base_url}/memory-chat", 
                           json={"message": "我的血压控制得怎么样？", "user_id": user_id})
    data = response.json()
    print(f"🤖 AI: {data['response']}")
    print("📊 记忆操作:")
    for op in data.get('memory_operations', []):
        print(f"  {op['type']} - {op['operation']}: {op['details']}")
    
    time.sleep(1)
    
    # 测试场景4：完整流程测试
    print("\n📋 测试场景4：完整流程测试")
    print("-" * 40)
    
    # 4.1 综合查询
    print("👤 用户: 我头痛能吃什么止痛药？")
    response = requests.post(f"{base_url}/memory-chat", 
                           json={"message": "我头痛能吃什么止痛药？", "user_id": user_id})
    data = response.json()
    print(f"🤖 AI: {data['response']}")
    print("📊 记忆操作:")
    for op in data.get('memory_operations', []):
        print(f"  {op['type']} - {op['operation']}: {op['details']}")
    
    time.sleep(1)
    
    # 4.2 查询记忆统计
    print("\n📊 查询记忆统计:")
    response = requests.get(f"{base_url}/memory-stats/{user_id}")
    stats_data = response.json()
    if stats_data['success']:
        stats = stats_data['stats']
        print(f"  短期记忆: {stats['short_term_count']} 轮对话")
        print(f"  实体数量: {stats['entities_count']} 个")
        print(f"  长期记忆: {stats['long_term_count']} 条记录")
        print(f"  识别实体: {stats['entities']}")
    
    print("\n✅ 记忆系统测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_memory_operations()
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败：请确保AI-安主任应用正在运行 (http://localhost:5002)")
    except Exception as e:
        print(f"❌ 测试失败：{e}")
