#!/usr/bin/env python3
"""
测试添加糖尿病记忆然后删除的功能
"""

import sys
sys.path.append('/Users/louisliu/.cursor/memory-x')

from examples.enhanced_qwen_graph_demo import EnhancedQwenGraphDemo

def test_diabetes_memory_lifecycle():
    print("🧪 测试糖尿病记忆的完整生命周期")
    print("=" * 50)
    
    # 初始化演示系统
    demo = EnhancedQwenGraphDemo('sk-b70842d25c884aa9aa18955b00c24d37')
    
    print("📊 初始状态:")
    before_stats = demo.memory_manager.get_memory_stats()
    print(f"  短期记忆: {before_stats['short_term_count']}条")
    
    # 1. 添加一些糖尿病相关的记忆
    print(f"\n➕ 添加糖尿病相关记忆...")
    
    diabetes_conversations = [
        {
            "user_message": "医生，我有糖尿病家族史，最近总是感到口渴",
            "ai_response": "鉴于您的糖尿病家族史和口渴症状，建议进行血糖检查。",
            "entities": {
                "FAMILY_HISTORY": [["糖尿病家族史", 0, 6]],
                "SYMPTOM": [["口渴", 0, 2]]
            },
            "intent": "medical_consultation",
            "importance": 4
        },
        {
            "user_message": "我的血糖检查结果是7.2mmol/L，这正常吗？",
            "ai_response": "空腹血糖7.2mmol/L超过正常范围，建议进一步检查确认是否为糖尿病。",
            "entities": {
                "TEST_RESULT": [["血糖7.2mmol/L", 0, 10]],
                "DISEASE": [["糖尿病", 0, 3]]
            },
            "intent": "test_result_inquiry",
            "importance": 4
        },
        {
            "user_message": "医生建议我注射胰岛素，我需要注意什么？",
            "ai_response": "胰岛素注射需要按时按量，注意监测血糖变化，避免低血糖。",
            "entities": {
                "MEDICINE": [["胰岛素", 0, 3]],
                "SYMPTOM": [["低血糖", 0, 3]]
            },
            "intent": "medication_inquiry",
            "importance": 3
        }
    ]
    
    for conv in diabetes_conversations:
        demo.memory_manager.add_conversation(
            conv["user_message"],
            conv["ai_response"],
            conv["entities"],
            conv["intent"],
            conv["importance"]
        )
        print(f"    ✓ 添加: {conv['user_message'][:40]}...")
    
    # 2. 查看添加后的状态
    print(f"\n📊 添加后状态:")
    after_add_stats = demo.memory_manager.get_memory_stats()
    print(f"  短期记忆: {after_add_stats['short_term_count']}条")
    print(f"  工作记忆: {after_add_stats['working_memory_size']}项")
    
    print(f"\n📋 当前短期记忆内容:")
    diabetes_related_count = 0
    for i, mem in enumerate(demo.memory_manager.short_term_memory, 1):
        user_msg = mem.get('user_message', '')
        print(f"  {i}. {user_msg[:60]}...")
        
        # 检查是否包含糖尿病相关内容
        diabetes_keywords = ['糖尿病', '血糖', '胰岛素', '家族史', '糖尿病风险', 'diabetes']
        is_diabetes_related = any(keyword in user_msg for keyword in diabetes_keywords)
        
        if not is_diabetes_related:
            entities = mem.get('entities', {})
            if entities:
                for entity_type, entity_list in entities.items():
                    if isinstance(entity_list, list):
                        for entity_info in entity_list:
                            entity_text = entity_info[0] if isinstance(entity_info, (list, tuple)) else str(entity_info)
                            if any(keyword in entity_text for keyword in diabetes_keywords):
                                is_diabetes_related = True
                                break
                        if is_diabetes_related:
                            break
        
        if is_diabetes_related:
            print(f"     👆 包含糖尿病相关内容")
            diabetes_related_count += 1
    
    print(f"\n🔍 识别到 {diabetes_related_count} 条糖尿病相关记忆")
    
    # 3. 执行删除操作
    print(f"\n🧹 执行糖尿病记忆删除...")
    removal_result = demo.memory_manager.remove_diabetes_related_memories()
    
    print(f"✅ 删除结果:")
    print(f"  - 删除短期记忆: {removal_result['removed_short_term']}条")
    print(f"  - 删除工作记忆键: {removal_result['removed_working_keys']}个")
    print(f"  - 剩余短期记忆: {removal_result['remaining_short_term']}条")
    print(f"  - 剩余工作记忆: {removal_result['remaining_working_memory']}项")
    
    # 4. 查看删除后的状态
    print(f"\n📋 删除后剩余短期记忆:")
    if demo.memory_manager.short_term_memory:
        for i, mem in enumerate(demo.memory_manager.short_term_memory, 1):
            user_msg = mem.get('user_message', '')
            print(f"  {i}. {user_msg[:60]}...")
    else:
        print("  (无剩余短期记忆)")
    
    # 5. 验证删除效果
    print(f"\n🎯 验证删除效果:")
    remaining_diabetes_count = 0
    for mem in demo.memory_manager.short_term_memory:
        user_msg = mem.get('user_message', '')
        diabetes_keywords = ['糖尿病', '血糖', '胰岛素', '家族史', '糖尿病风险', 'diabetes']
        if any(keyword in user_msg for keyword in diabetes_keywords):
            remaining_diabetes_count += 1
    
    if remaining_diabetes_count == 0:
        print(f"  ✅ 成功！短期记忆中已无糖尿病相关内容")
    else:
        print(f"  ⚠️ 仍有 {remaining_diabetes_count} 条糖尿病相关记忆未删除")
    
    # 最终统计
    final_stats = demo.memory_manager.get_memory_stats()
    print(f"\n📈 最终统计:")
    print(f"  删除前: {after_add_stats['short_term_count']}条短期记忆")
    print(f"  删除后: {final_stats['short_term_count']}条短期记忆")
    print(f"  实际删除: {after_add_stats['short_term_count'] - final_stats['short_term_count']}条")
    
    if removal_result['removed_short_term'] > 0:
        print(f"\n🎉 糖尿病记忆删除功能测试成功！")
        print(f"   成功删除了 {removal_result['removed_short_term']} 条糖尿病相关的短期记忆")
    else:
        print(f"\n💭 没有找到需要删除的糖尿病记忆")
    
    return removal_result

if __name__ == "__main__":
    test_diabetes_memory_lifecycle()
