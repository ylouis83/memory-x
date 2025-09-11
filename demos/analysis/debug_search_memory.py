#!/usr/bin/env python3
"""
调试search_long_term_memory方法
"""

import sys
import os
sys.path.append('.')

def debug_search_memory():
    """详细调试search_long_term_memory"""
    print("🔍 调试search_long_term_memory方法")
    print("=" * 50)
    
    try:
        from src.core.memory_manager import SimpleMemoryManager
        
        # 创建记忆管理器
        user_id = "debug_search_user"
        memory_manager = SimpleMemoryManager(user_id)
        print("✅ 记忆管理器创建成功")
        
        # 1. 测试store.search_memories直接调用
        print("\n🔍 测试 store.search_memories 直接调用...")
        try:
            query = "测试查询"
            results = memory_manager.store.search_memories(user_id, query, 5)
            print(f"✅ store.search_memories 成功: 找到 {len(results)} 条记忆")
            
            for i, result in enumerate(results[:2], 1):
                print(f"   记忆 {i}: {type(result)} - {list(result.keys()) if isinstance(result, dict) else str(result)[:100]}")
                
        except Exception as e:
            print(f"❌ store.search_memories 失败: {e}")
            print(f"   错误类型: {type(e)}")
            import traceback
            traceback.print_exc()
        
        # 2. 测试retrieve_memories调用
        print("\n🔍 测试 retrieve_memories 调用...")
        try:
            results = memory_manager.retrieve_memories(query, 5)
            print(f"✅ retrieve_memories 成功: 找到 {len(results)} 条记忆")
            
            for i, result in enumerate(results[:2], 1):
                print(f"   记忆 {i}: {type(result)} - {list(result.keys()) if isinstance(result, dict) else str(result)[:100]}")
                
        except Exception as e:
            print(f"❌ retrieve_memories 失败: {e}")
            print(f"   错误类型: {type(e)}")
            import traceback
            traceback.print_exc()
        
        # 3. 测试search_long_term_memory调用
        print("\n🔍 测试 search_long_term_memory 调用...")
        try:
            results = memory_manager.search_long_term_memory(query, 5)
            print(f"✅ search_long_term_memory 成功: 找到 {len(results)} 条记忆")
            
            for i, result in enumerate(results[:2], 1):
                print(f"   记忆 {i}: {type(result)} - {list(result.keys()) if isinstance(result, dict) else str(result)[:100]}")
                
        except Exception as e:
            print(f"❌ search_long_term_memory 失败: {e}")
            print(f"   错误类型: {type(e)}")
            import traceback
            traceback.print_exc()
        
        # 4. 先添加一条记忆，然后再查询
        print("\n🔍 添加测试记忆后再查询...")
        try:
            # 添加一条测试记忆
            success = memory_manager.add_conversation(
                "我是测试用户",
                "好的，我记住了",
                entities={'PERSON': [('测试用户', 2, 6)]},
                intent='NORMAL_CONSULTATION',
                importance=3
            )
            print(f"✅ 添加测试记忆: {success}")
            
            # 再次查询
            results = memory_manager.search_long_term_memory("测试", 5)
            print(f"✅ 查询测试记忆: 找到 {len(results)} 条记忆")
            
            for i, result in enumerate(results[:2], 1):
                print(f"   记忆 {i}: {result}")
                
        except Exception as e:
            print(f"❌ 测试记忆操作失败: {e}")
            print(f"   错误类型: {type(e)}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ 调试过程异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_search_memory()
    if success:
        print("\n🎉 调试完成！")
    else:
        print("\n❌ 调试失败！")