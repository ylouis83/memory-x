#!/usr/bin/env python3
"""
测试记忆模式的AI模型调用
"""

import requests
import json
import time
from datetime import datetime

def test_memory_api_directly():
    """直接测试记忆API"""
    print("🧠 记忆模式AI调用测试")
    print("=" * 50)
    
    # 使用Python requests模拟前端调用
    base_url = "http://localhost:5002"
    test_user = "direct_test_user"
    
    # 测试消息序列
    test_messages = [
        "我有高血压，在吃氨氯地平",
        "我对青霉素过敏",
        "现在感冒了，能吃抗生素吗？"
    ]
    
    print(f"📱 模拟前端API调用...")
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n第{i}轮测试:")
        print(f"👤 发送消息: {message}")
        
        try:
            # 模拟前端发送记忆聊天请求
            response = requests.post(
                f"{base_url}/memory-chat",
                json={
                    'message': message,
                    'user_id': test_user
                },
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    print(f"✅ API调用成功")
                    print(f"🤖 AI回复: {data['response']}")
                    print(f"🔍 检测意图: {data['intent']['detected']} ({data['intent']['confidence']}%)")
                    print(f"💾 记忆重要性: {data['memory_info']['importance']}")
                    print(f"🔗 使用长期记忆: {data['memory_info']['used_long_term']}")
                else:
                    print(f"❌ API返回错误: {data.get('error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"   响应内容: {response.text[:100]}...")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败: 应用未启动或端口不可达")
            break
        except requests.exceptions.Timeout:
            print("❌ 请求超时: AI模型响应过慢")
        except Exception as e:
            print(f"❌ 请求异常: {e}")
        
        time.sleep(1)
    
    # 测试记忆统计
    print(f"\n📊 测试记忆统计API...")
    try:
        stats_response = requests.get(f"{base_url}/memory-stats/{test_user}", timeout=5)
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            if stats_data.get('success'):
                stats = stats_data['stats']
                print(f"✅ 记忆统计获取成功:")
                print(f"   短期记忆: {stats['short_term_count']} 轮")
                print(f"   工作记忆: {stats['working_memory_size']} 项")
                print(f"   长期记忆: {stats['total_long_term']} 条")
            else:
                print(f"❌ 统计API错误: {stats_data.get('error')}")
        else:
            print(f"❌ 统计HTTP错误: {stats_response.status_code}")
            
    except Exception as e:
        print(f"❌ 统计请求异常: {e}")

if __name__ == "__main__":
    test_memory_api_directly()
