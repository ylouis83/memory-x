#!/usr/bin/env python3
"""
Memory-X 前端后端集成测试脚本
测试前端和后端的主要功能是否正常工作
"""

import requests
import json
import time
from datetime import datetime

# 配置
BACKEND_URL = "http://localhost:5000"
FRONTEND_URL = "http://localhost:5176"
TEST_USER = "frontend_test_user"

def test_backend_health():
    """测试后端健康状态"""
    print("🔍 测试后端健康状态...")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 后端健康状态: {data}")
            return True
        else:
            print(f"❌ 后端健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return False

def test_frontend_access():
    """测试前端页面访问"""
    print("\n🔍 测试前端页面访问...")
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            print("✅ 前端页面可访问")
            return True
        else:
            print(f"❌ 前端页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端连接失败: {e}")
        return False

def test_chat_api():
    """测试聊天API"""
    print("\n🔍 测试聊天API...")
    try:
        payload = {
            "user_id": TEST_USER,
            "message": "我有一些头痛的症状，持续了3天"
        }
        response = requests.post(f"{BACKEND_URL}/api/memory/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 聊天API响应: {data.get('response', '未知响应')}")
            return True
        else:
            print(f"❌ 聊天API失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 聊天API错误: {e}")
        return False

def test_memory_retrieval():
    """测试记忆检索"""
    print("\n🔍 测试记忆检索...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/memory/{TEST_USER}")
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"✅ 记忆检索成功: 共 {count} 条记忆")
            if count > 0:
                print(f"   最新记忆: {data['memories'][0]['user_message'][:50]}...")
            return True
        else:
            print(f"❌ 记忆检索失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 记忆检索错误: {e}")
        return False

def test_memory_search():
    """测试记忆搜索"""
    print("\n🔍 测试记忆搜索...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/memory/{TEST_USER}?query=头痛")
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"✅ 记忆搜索成功: 找到 {count} 条相关记忆")
            return True
        else:
            print(f"❌ 记忆搜索失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 记忆搜索错误: {e}")
        return False

def test_medical_decision():
    """测试医疗决策API"""
    print("\n🔍 测试医疗决策API...")
    try:
        payload = {
            "current": {
                "rxnorm": "11111",
                "dose": "5 mg",
                "frequency": "qd",
                "route": "oral",
                "start": "2025-09-01T00:00:00",
                "provenance": "doctor"
            },
            "new": {
                "rxnorm": "11111",
                "dose": "10 mg",
                "frequency": "bid",
                "route": "oral",
                "start": "2025-09-10T00:00:00",
                "provenance": "chat"
            }
        }
        response = requests.post(f"{BACKEND_URL}/api/medical/decide", json=payload)
        if response.status_code == 200:
            data = response.json()
            action = data.get('action', '未知')
            confidence = data.get('confidence', 0)
            print(f"✅ 医疗决策成功: {action} (置信度: {confidence:.2f})")
            return True
        else:
            print(f"❌ 医疗决策失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 医疗决策错误: {e}")
        return False

def test_memory_stats():
    """测试记忆统计"""
    print("\n🔍 测试记忆统计...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/memory/{TEST_USER}/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 记忆统计成功: {data}")
            return True
        else:
            print(f"❌ 记忆统计失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 记忆统计错误: {e}")
        return False

def main():
    """运行所有测试"""
    print("🚀 Memory-X 前端后端集成测试开始")
    print("=" * 50)
    
    tests = [
        ("后端健康检查", test_backend_health),
        ("前端页面访问", test_frontend_access),
        ("聊天API", test_chat_api),
        ("记忆检索", test_memory_retrieval),
        ("记忆搜索", test_memory_search),
        ("医疗决策", test_medical_decision),
        ("记忆统计", test_memory_stats),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            time.sleep(0.5)  # 短暂延迟避免请求过快
        except Exception as e:
            print(f"❌ {name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！前端后端集成正常工作")
        return True
    else:
        print("⚠️ 部分测试失败，请检查服务状态")
        return False

if __name__ == "__main__":
    main()