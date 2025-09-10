#!/usr/bin/env python3
"""
记忆系统验证测试
"""

import sys
import os
sys.path.append('.')

def test_imports():
    """测试模块导入"""
    print("📦 测试模块导入...")
    
    try:
        from src.core.memory_manager import SimpleMemoryIntegratedAI
        print("✅ 简化记忆管理器导入成功")
        
        # 创建实例
        memory_ai = SimpleMemoryIntegratedAI()
        print("✅ 记忆AI实例创建成功")
        
        # 测试基本功能
        result = memory_ai.process_message("测试消息", "test_user")
        
        if result['success']:
            print("✅ 基本消息处理功能正常")
            print(f"   AI回复: {result['response'][:50]}...")
            print(f"   检测意图: {result['intent']['detected']}")
            return True
        else:
            print(f"❌ 消息处理失败: {result['error']}")
            return False
            
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_database():
    """测试数据库功能"""
    print("\n💾 测试数据库功能...")
    
    try:
        from src.core.memory_manager import SimpleMemoryManager
        
        # 创建记忆管理器
        manager = SimpleMemoryManager("test_user", "data/test.db")
        print("✅ 记忆管理器创建成功")
        
        # 测试添加对话
        success = manager.add_conversation(
            "我头痛",
            "建议休息",
            {'SYMPTOM': [('头痛', 1, 3)]},
            'SYMPTOM_DESCRIPTION',
            2
        )
        
        if success:
            print("✅ 对话添加成功")
            
            # 测试统计
            stats = manager.get_memory_stats()
            print(f"✅ 统计获取成功: {stats}")
            
            return True
        else:
            print("❌ 对话添加失败")
            return False
            
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧠 AI-安主任记忆系统验证测试")
    print("=" * 50)
    
    # 测试导入
    import_test = test_imports()
    
    # 测试数据库
    db_test = test_database()
    
    print(f"\n📊 测试结果:")
    print(f"   模块导入: {'✅ 通过' if import_test else '❌ 失败'}")
    print(f"   数据库功能: {'✅ 通过' if db_test else '❌ 失败'}")
    
    if import_test and db_test:
        print("\n🎉 记忆系统验证通过！")
        print("💡 建议:")
        print("   1. 启动应用: python app.py")
        print("   2. 访问: http://localhost:5001/test-memory")
        print("   3. 测试记忆功能开关")
        return True
    else:
        print("\n❌ 验证失败，请检查错误")
        return False

if __name__ == "__main__":
    main()
