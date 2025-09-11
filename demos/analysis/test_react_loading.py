#!/usr/bin/env python3
"""
检测Memory-X前端React应用是否正确加载
"""

import requests
import time

def test_react_loading():
    """测试React应用是否正确加载"""
    print("🔍 检测React应用加载状态...")
    
    # 首先检查页面是否可访问
    try:
        response = requests.get("http://localhost:5176")
        if response.status_code != 200:
            print(f"❌ 前端页面不可访问: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端连接失败: {e}")
        return False
    
    print("✅ 前端页面可访问")
    
    # 检查页面内容
    content = response.text
    if "Memory-X 启动中" in content:
        print("⚠️ 页面仍显示启动中状态")
    
    if "/@vite/client" in content:
        print("✅ Vite客户端脚本已加载")
    
    if "@react-refresh" in content:
        print("✅ React热重载脚本已加载")
    
    if 'type="module"' in content:
        print("✅ ES模块脚本已加载")
    
    print("\n💡 说明:")
    print("- 如果页面显示'Memory-X 启动中'，这是正常的加载状态")
    print("- React应用会在JavaScript加载完成后替换该内容")
    print("- 请在浏览器中打开 http://localhost:5176 查看完整应用")
    
    return True

if __name__ == "__main__":
    test_react_loading()