#!/usr/bin/env python3
"""
测试删除糖尿病相关记忆功能
"""

import os
import sys
sys.path.append('/Users/louisliu/.cursor/memory-x')

from examples.enhanced_qwen_graph_demo import EnhancedQwenGraphDemo

def test_clear_diabetes_memories():
    print("🧪 测试删除糖尿病相关记忆功能")
    print("=" * 50)
    
    # 初始化演示系统
    demo = EnhancedQwenGraphDemo(os.getenv('DASHSCOPE_API_KEY') or "请设置DASHSCOPE_API_KEY环境变量")
    
    # 查看删除前的统计
    before_stats = demo.memory_manager.get_memory_stats()
    print(f"📊 删除前统计:")
    print(f"  短期记忆: {before_stats['short_term_count']}条")
    print(f"  工作记忆: {before_stats['working_memory_size']}项")
    
    # 显示短期记忆内容
    print(f"\n📋 当前短期记忆内容:")
    diabetes_related_count = 0
    for i, mem in enumerate(demo.memory_manager.short_term_memory, 1):
        user_msg = mem.get('user_message', '')
        ai_resp = mem.get('ai_response', '')
        entities = mem.get('entities', {})
        
        print(f"  {i}. {user_msg[:60]}...")
        print(f"     回复: {ai_resp[:60]}...")
        
        # 检查是否包含糖尿病相关内容
        is_diabetes_related = False
        diabetes_keywords = ['糖尿病', '血糖', '胰岛素', '家族史', '糖尿病风险', 'diabetes']
        
        for keyword in diabetes_keywords:
            if keyword in user_msg or keyword in ai_resp:
                is_diabetes_related = True
                break
        
        if not is_diabetes_related and entities:
            for entity_type, entity_list in entities.items():
                if isinstance(entity_list, list):
                    for entity_info in entity_list:
                        entity_text = entity_info[0] if isinstance(entity_info, (list, tuple)) else str(entity_info)
                        for keyword in diabetes_keywords:
                            if keyword in entity_text:
                                is_diabetes_related = True
                                break
                        if is_diabetes_related:
                            break
                if is_diabetes_related:
                    break
        
        if is_diabetes_related:
            print(f"     👆 包含糖尿病相关内容")
            diabetes_related_count += 1
    
    print(f"\n🔍 识别到 {diabetes_related_count} 条糖尿病相关记忆")
    
    # 执行删除操作
    print(f"\n🧹 执行糖尿病记忆删除...")
    removal_result = demo.memory_manager.remove_diabetes_related_memories()
    
    print(f"✅ 删除完成:")
    print(f"  - 删除短期记忆: {removal_result['removed_short_term']}条")
    print(f"  - 删除工作记忆键: {removal_result['removed_working_keys']}个")
    print(f"  - 剩余短期记忆: {removal_result['remaining_short_term']}条")
    print(f"  - 剩余工作记忆: {removal_result['remaining_working_memory']}项")
    
    # 显示删除后的记忆
    print(f"\n📋 删除后剩余短期记忆:")
    if demo.memory_manager.short_term_memory:
        for i, mem in enumerate(demo.memory_manager.short_term_memory, 1):
            user_msg = mem.get('user_message', '')
            print(f"  {i}. {user_msg[:60]}...")
    else:
        print("  (无剩余短期记忆)")
    
    # 验证结果
    if removal_result['removed_short_term'] > 0 or removal_result['removed_working_keys'] > 0:
        print(f"\n🎉 成功清理糖尿病相关记忆！")
        print(f"   删除了 {removal_result['removed_short_term']} 条短期记忆")
        print(f"   删除了 {removal_result['removed_working_keys']} 个工作记忆键")
    else:
        print(f"\n💭 未找到糖尿病相关记忆需要删除")
    
    return removal_result

if __name__ == "__main__":
    test_clear_diabetes_memories()