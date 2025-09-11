#!/usr/bin/env python3
"""
演示交互式糖尿病记忆删除功能
"""

import os
import sys
sys.path.append('/Users/louisliu/.cursor/memory-x')

from examples.enhanced_qwen_graph_demo import EnhancedQwenGraphDemo

def demo_interactive_clear_diabetes():
    print("🎬 演示交互式糖尿病记忆删除功能")
    print("=" * 60)
    
    # 初始化演示系统
    demo = EnhancedQwenGraphDemo(os.getenv('DASHSCOPE_API_KEY') or "请设置DASHSCOPE_API_KEY环境变量")
    
    # 先添加一些糖尿病相关记忆以便演示
    print("📝 准备演示数据...")
    diabetes_memories = [
        {
            "user_message": "我有糖尿病家族史，担心自己也会得",
            "ai_response": "有家族史确实增加风险，建议定期体检监测血糖。",
            "entities": {"FAMILY_HISTORY": [["糖尿病家族史", 0, 6]]},
            "intent": "health_concern",
            "importance": 4
        },
        {
            "user_message": "最近总是口渴，会不会是糖尿病？",
            "ai_response": "口渴是糖尿病的典型症状之一，建议尽快检查血糖。",
            "entities": {"SYMPTOM": [["口渴", 0, 2]], "DISEASE": [["糖尿病", 0, 3]]},
            "intent": "symptom_inquiry",
            "importance": 4
        },
        {
            "user_message": "胰岛素应该怎么使用？",
            "ai_response": "胰岛素使用需要严格按医嘱，定时注射并监测血糖。",
            "entities": {"MEDICINE": [["胰岛素", 0, 3]]},
            "intent": "medication_inquiry",
            "importance": 3
        }
    ]
    
    for mem in diabetes_memories:
        demo.memory_manager.add_conversation(
            mem["user_message"],
            mem["ai_response"],
            mem["entities"],
            mem["intent"],
            mem["importance"]
        )
        print(f"  ✓ 添加: {mem['user_message']}")
    
    print(f"\n📊 当前记忆状态:")
    stats = demo.memory_manager.get_memory_stats()
    print(f"  短期记忆: {stats['short_term_count']}条")
    print(f"  工作记忆: {stats['working_memory_size']}项")
    
    print(f"\n📋 短期记忆列表:")
    diabetes_count = 0
    for i, mem in enumerate(demo.memory_manager.short_term_memory, 1):
        user_msg = mem.get('user_message', '')
        print(f"  {i}. {user_msg}")
        
        # 检查是否包含糖尿病相关内容
        diabetes_keywords = ['糖尿病', '血糖', '胰岛素', '家族史', '糖尿病风险', 'diabetes']
        if any(keyword in user_msg for keyword in diabetes_keywords):
            print(f"     🍯 糖尿病相关记忆")
            diabetes_count += 1
    
    print(f"\n🔍 找到 {diabetes_count} 条糖尿病相关记忆")
    
    # 模拟用户执行 clear_diabetes 命令
    print(f"\n🎯 执行 'clear_diabetes' 命令...")
    print(f"🧹 删除短期记忆中关于糖尿病的全部内容...")
    
    # 显示删除前统计
    before_stats = demo.memory_manager.get_memory_stats()
    print(f"  删除前: 短期记忆 {before_stats['short_term_count']}条, 工作记忆 {before_stats['working_memory_size']}项")
    
    # 执行删除
    removal_result = demo.memory_manager.remove_diabetes_related_memories()
    
    # 显示结果
    print(f"  ✅ 删除完成:")
    print(f"    - 删除短期记忆: {removal_result['removed_short_term']}条")
    print(f"    - 删除工作记忆键: {removal_result['removed_working_keys']}个")
    print(f"    - 剩余短期记忆: {removal_result['remaining_short_term']}条")
    print(f"    - 剩余工作记忆: {removal_result['remaining_working_memory']}项")
    
    if removal_result['removed_short_term'] > 0 or removal_result['removed_working_keys'] > 0:
        print(f"  🎉 成功清理糖尿病相关记忆！")
    else:
        print(f"  💭 未找到糖尿病相关记忆")
    
    print(f"\n📋 删除后剩余短期记忆:")
    if demo.memory_manager.short_term_memory:
        for i, mem in enumerate(demo.memory_manager.short_term_memory, 1):
            user_msg = mem.get('user_message', '')
            print(f"  {i}. {user_msg}")
    else:
        print("  (无剩余短期记忆)")
    
    # 验证删除效果
    print(f"\n✅ 删除功能验证:")
    remaining_diabetes_memories = 0
    for mem in demo.memory_manager.short_term_memory:
        user_msg = mem.get('user_message', '')
        if any(keyword in user_msg for keyword in ['糖尿病', '血糖', '胰岛素', '家族史']):
            remaining_diabetes_memories += 1
    
    if remaining_diabetes_memories == 0:
        print(f"  ✅ 验证成功：短期记忆中已无糖尿病相关内容")
    else:
        print(f"  ⚠️ 验证失败：仍有 {remaining_diabetes_memories} 条糖尿病相关记忆")
    
    print(f"\n🎬 演示完成！")
    print(f"📈 统计结果:")
    print(f"  - 原有短期记忆: {before_stats['short_term_count']}条")
    print(f"  - 成功删除: {removal_result['removed_short_term']}条糖尿病相关记忆")
    print(f"  - 保留记忆: {removal_result['remaining_short_term']}条非糖尿病记忆")

if __name__ == "__main__":
    demo_interactive_clear_diabetes()
