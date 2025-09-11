#!/usr/bin/env python3
"""
测试Qwen3 API连接
"""

import os
import requests
import json

def test_qwen_api():
    """测试百炼API连接"""
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        raise ValueError("请设置DASHSCOPE_API_KEY环境变量")
    base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen-max",
        "input": {
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业的医疗AI助手。"
                },
                {
                    "role": "user",
                    "content": "请简单介绍感冒的典型病程。"
                }
            ]
        },
        "parameters": {
            "max_tokens": 200,
            "temperature": 0.1
        }
    }
    
    try:
        print("🔄 测试Qwen3 API连接...")
        response = requests.post(base_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ API调用成功！")
        print(f"响应状态: {response.status_code}")
        
        if "output" in result and "text" in result["output"]:
            answer = result["output"]["text"].strip()
            print(f"AI回答: {answer}")
            return True
        else:
            print(f"❌ 响应格式异常: {result}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 处理响应失败: {e}")
        return False

if __name__ == "__main__":
    test_qwen_api()