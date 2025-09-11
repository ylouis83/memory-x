#!/usr/bin/env python3
"""
调试记忆处理功能
"""

import sys
import os
sys.path.append('.')

def debug_memory_processing():
    """调试记忆处理功能"""
    print("🔍 调试记忆处理功能")
    print("=" * 50)
    
    try:
        from src.core.memory_manager import SimpleMemoryIntegratedAI
        
        # 创建记忆AI实例
        memory_ai = SimpleMemoryIntegratedAI()
        print("✅ SimpleMemoryIntegratedAI 实例创建成功")
        
        # 测试用户信息
        user_id = "debug_user"
        message = "我是演示患者，我是成年人，我对青霉素过敏，我家有遗传病史（糖尿病）"
        
        print(f"用户ID: {user_id}")
        print(f"测试消息: {message}")
        print("-" * 50)
        
        # 分步调试process_message方法
        print("\n🔍 开始分步调试...")
        
        # 1. 获取记忆管理器
        try:
            memory_manager = memory_ai.get_memory_manager(user_id)
            print("✅ 记忆管理器获取成功")
            print(f"   类型: {type(memory_manager)}")
        except Exception as e:
            print(f"❌ 记忆管理器获取失败: {e}")
            return False
        
        # 2. 测试意图检测
        try:
            intent = memory_ai._detect_intent(message)
            print(f"✅ 意图检测成功: {intent}")
        except Exception as e:
            print(f"❌ 意图检测失败: {e}")
            return False
        
        # 3. 测试实体识别
        try:
            entities = memory_ai._recognize_entities(message)
            print(f"✅ 实体识别成功: {entities}")
        except Exception as e:
            print(f"❌ 实体识别失败: {e}")
            return False
        
        # 4. 测试重要性评估
        try:
            importance = memory_ai._evaluate_importance(intent, entities)
            print(f"✅ 重要性评估成功: {importance}")
        except Exception as e:
            print(f"❌ 重要性评估失败: {e}")
            return False
        
        # 5. 测试长期记忆检索 - 这里可能是问题所在
        try:
            print("\n🔍 测试长期记忆检索...")
            retrieved = memory_manager.search_long_term_memory(message)
            print(f"✅ 长期记忆检索成功: 找到 {len(retrieved)} 条记忆")
            if retrieved:
                for i, mem in enumerate(retrieved[:2], 1):
                    print(f"   记忆 {i}: {str(mem)[:100]}...")
        except Exception as e:
            print(f"❌ 长期记忆检索失败: {e}")
            print(f"   错误类型: {type(e)}")
            import traceback
            traceback.print_exc()
            # 继续执行其他测试
        
        # 6. 测试回复生成
        try:
            ai_response = memory_ai._generate_response(message, intent, entities)
            print(f"✅ 回复生成成功: {ai_response}")
        except Exception as e:
            print(f"❌ 回复生成失败: {e}")
            return False
        
        # 7. 测试对话存储
        try:
            print("\n🔍 测试对话存储...")
            success = memory_manager.add_conversation(
                message, ai_response, entities, intent, importance
            )
            print(f"✅ 对话存储成功: {success}")
        except Exception as e:
            print(f"❌ 对话存储失败: {e}")
            print(f"   错误类型: {type(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        # 8. 完整的process_message测试
        print("\n🔍 测试完整的process_message...")
        try:
            result = memory_ai.process_message(message, user_id)
            print(f"✅ 完整处理成功: {result['success']}")
            if result['success']:
                print(f"   AI回复: {result['response']}")
                print(f"   检测意图: {result['intent']}")
                print(f"   记忆信息: {result['memory_info']}")
            else:
                print(f"❌ 处理失败: {result}")
        except Exception as e:
            print(f"❌ 完整处理异常: {e}")
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
    success = debug_memory_processing()
    if success:
        print("\n🎉 调试完成！")
    else:
        print("\n❌ 调试失败！")