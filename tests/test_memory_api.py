#!/usr/bin/env python3
"""
记忆系统API功能测试
"""

import sys
sys.path.append('.')

from modules.simple_memory_manager import SimpleMemoryIntegratedAI

def test_memory_api():
    """测试记忆API功能"""
    print("🧠 记忆系统API功能测试")
    print("=" * 50)
    
    # 创建记忆AI实例
    memory_ai = SimpleMemoryIntegratedAI()
    test_user = "api_test_user"
    
    # 测试对话序列
    conversations = [
        {
            'message': "我有高血压，在吃氨氯地平",
            'expected_intent': 'NORMAL_CONSULTATION',
            'expected_importance': 3
        },
        {
            'message': "我对青霉素过敏",
            'expected_intent': 'NORMAL_CONSULTATION', 
            'expected_importance': 4
        },
        {
            'message': "现在感冒了，能吃抗生素吗？",
            'expected_intent': 'PRESCRIPTION_INQUIRY',
            'expected_importance': 3
        }
    ]
    
    print("💬 测试对话处理...")
    
    for i, conv in enumerate(conversations, 1):
        print(f"\n第{i}轮测试:")
        print(f"👤 用户: {conv['message']}")
        
        # 处理消息
        result = memory_ai.process_message(conv['message'], test_user)
        
        if result['success']:
            print(f"🤖 AI回复: {result['response']}")
            print(f"🔍 检测意图: {result['intent']['detected']}")
            print(f"💾 记忆重要性: {result['memory_info']['importance']}")
            print(f"🔗 使用长期记忆: {result['memory_info']['used_long_term']}")
            
            # 验证结果
            actual_intent = result['intent']['detected']
            actual_importance = result['memory_info']['importance']
            
            intent_correct = actual_intent == conv['expected_intent']
            importance_correct = actual_importance >= conv['expected_importance'] - 1
            
            print(f"✅ 意图检测: {'正确' if intent_correct else '错误'}")
            print(f"✅ 重要性评估: {'合理' if importance_correct else '偏差'}")
        else:
            print(f"❌ 处理失败: {result['error']}")
    
    # 测试记忆统计
    print(f"\n📊 记忆统计测试:")
    stats = memory_ai.get_stats(test_user)
    print(f"   用户ID: {stats['user_id']}")
    print(f"   短期记忆: {stats['short_term_count']} 轮")
    print(f"   工作记忆: {stats['working_memory_size']} 项") 
    print(f"   长期记忆: {stats['total_long_term']} 条")
    
    # 测试记忆连续性
    print(f"\n🔗 记忆连续性测试:")
    continuity_result = memory_ai.process_message("之前提到的药物有什么注意事项？", test_user)
    
    if continuity_result['success']:
        print(f"✅ 连续性回复: {continuity_result['response']}")
        print(f"✅ 使用长期记忆: {continuity_result['memory_info']['used_long_term']}")
    else:
        print(f"❌ 连续性测试失败")
    
    # 测试清空功能
    print(f"\n🧹 测试清空功能:")
    memory_ai.clear_user_session(test_user)
    
    # 验证清空后的统计
    stats_after_clear = memory_ai.get_stats(test_user)
    print(f"   清空后短期记忆: {stats_after_clear['short_term_count']} 轮")
    print(f"   清空后工作记忆: {stats_after_clear['working_memory_size']} 项")
    
    if stats_after_clear['short_term_count'] == 0:
        print("✅ 清空功能正常")
    else:
        print("❌ 清空功能异常")
    
    print(f"\n🎉 记忆系统API测试完成！")
    return True

if __name__ == "__main__":
    test_memory_api()
