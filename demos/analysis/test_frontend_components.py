#!/usr/bin/env python3
"""
测试前端MemoryBrowser组件加载
"""

import requests
import time

def test_frontend_component_loading():
    """测试前端组件是否正确加载"""
    print("🔍 测试前端组件加载状态...")
    
    FRONTEND_URL = "http://localhost:5176"
    
    try:
        # 获取前端页面HTML
        response = requests.get(FRONTEND_URL)
        if response.status_code != 200:
            print(f"❌ 前端页面不可访问: {response.status_code}")
            return False
        
        content = response.text
        print("✅ 前端页面可访问")
        
        # 检查关键脚本是否加载
        checks = {
            "Vite客户端": "/@vite/client" in content,
            "React热重载": "@react-refresh" in content,
            "ES模块": 'type="module"' in content,
            "主应用脚本": "/src/main.tsx" in content,
        }
        
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check_name}: {'已加载' if result else '未找到'}")
        
        # 检查页面标题和描述
        if "Memory-X" in content:
            print("✅ 页面标题正确")
        
        if "智能记忆管理系统" in content:
            print("✅ 页面描述正确")
        
        print(f"\n💡 诊断信息:")
        print(f"- 如果记忆浏览页面显示白屏，可能原因：")
        print(f"  1. React组件有运行时错误")
        print(f"  2. API调用失败")
        print(f"  3. 用户Context没有正确初始化")
        print(f"  4. Material-UI组件渲染问题")
        
        print(f"\n🔧 建议排查步骤:")
        print(f"1. 打开浏览器开发者工具 (F12)")
        print(f"2. 查看Console标签页是否有JavaScript错误")
        print(f"3. 查看Network标签页是否有API请求失败")
        print(f"4. 刷新页面重新加载React应用")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_frontend_component_loading()