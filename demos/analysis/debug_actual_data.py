#!/usr/bin/env python3
"""
使用实际数据调试
"""

import sys
import os
sys.path.append('.')

def debug_actual_data():
    """使用实际数据调试"""
    print("🔍 使用实际数据调试")
    print("=" * 50)
    
    try:
        from src.core.memory_manager import SimpleMemoryIntegratedAI
        
        # 创建记忆AI实例
        memory_ai = SimpleMemoryIntegratedAI()
        print("✅ SimpleMemoryIntegratedAI 实例创建成功")
        
        # 测试用户信息
        user_id = "actual_debug_user"
        message = "我是演示患者，我是成年人，我对青霉素过敏，我家有遗传病史（糖尿病）"
        
        print(f"用户ID: {user_id}")
        print(f"测试消息: {message}")
        print("-" * 50)
        
        # 获取记忆管理器
        memory_manager = memory_ai.get_memory_manager(user_id)
        
        # 分步处理
        intent = memory_ai._detect_intent(message)
        entities = memory_ai._recognize_entities(message)
        importance = memory_ai._evaluate_importance(intent, entities)
        
        print(f"\n实体数据: {entities}")
        print(f"重要性: {importance}")
        
        # 测试对话存储
        print("\n🔍 测试对话存储...")
        try:
            success = memory_manager.add_conversation(
                message, 
                "我理解您的情况", 
                entities, 
                intent, 
                importance
            )
            print(f"✅ 对话存储成功: {success}")
        except Exception as e:
            print(f"❌ 对话存储失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 测试记忆检索
        print("\n🔍 测试记忆检索...")
        try:
            retrieved = memory_manager.search_long_term_memory(message)
            print(f"✅ 记忆检索成功: 找到 {len(retrieved)} 条记忆")
            
            for i, mem in enumerate(retrieved[:2], 1):
                print(f"   记忆 {i}: {mem}")
        except Exception as e:
            print(f"❌ 记忆检索失败: {e}")
            print(f"   错误类型: {type(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        # 完整process_message测试
        print("\n🔍 完整process_message测试...")
        try:
            result = memory_ai.process_message(message, user_id)
            print(f"处理结果: {result}")
        except Exception as e:
            print(f"❌ 完整处理失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 调试过程异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_actual_data()
    if success:
        print("\n🎉 调试完成！")
    else:
        print("\n❌ 调试失败！")