#!/usr/bin/env python3
"""
完整演示：清除短期记忆和图谱中关于糖尿病的全部数据
"""

import os
import sys
sys.path.append('/Users/louisliu/.cursor/memory-x')

from examples.enhanced_qwen_graph_demo import EnhancedQwenGraphDemo

def complete_diabetes_clear_demo():
    print("🎉 完整糖尿病数据清除演示")
    print("=" * 60)
    print("演示患者（成年人，有糖尿病家族史，青霉素过敏）")
    print("=" * 60)
    
    # 初始化演示系统
    demo = EnhancedQwenGraphDemo(os.getenv('DASHSCOPE_API_KEY') or "请设置DASHSCOPE_API_KEY环境变量")
    
    # 第一部分：清除短期记忆中的糖尿病数据
    print("\n📝 第一部分：清除短期记忆中的糖尿病数据")
    print("-" * 50)
    
    # 1. 添加糖尿病相关的短期记忆
    print("1. 添加糖尿病相关记忆...")
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
        print(f"   ✓ 添加: {mem['user_message']}")
    
    # 2. 查看短期记忆状态
    before_stats = demo.memory_manager.get_memory_stats()
    print(f"\n2. 清除前短期记忆状态: {before_stats['short_term_count']}条")
    
    diabetes_count = 0
    for mem in demo.memory_manager.short_term_memory:
        user_msg = mem.get('user_message', '')
        if any(keyword in user_msg for keyword in ['糖尿病', '血糖', '胰岛素', '家族史']):
            diabetes_count += 1
    
    print(f"   其中糖尿病相关: {diabetes_count}条")
    
    # 3. 执行短期记忆清除
    print(f"\n3. 执行短期记忆清除...")
    memory_removal = demo.memory_manager.remove_diabetes_related_memories()
    print(f"   ✅ 删除短期记忆: {memory_removal['removed_short_term']}条")
    print(f"   ✅ 剩余短期记忆: {memory_removal['remaining_short_term']}条")
    
    # 第二部分：清除图谱中的糖尿病数据
    print(f"\n📊 第二部分：清除图谱中的糖尿病数据")
    print("-" * 50)
    
    # 1. 先生成糖尿病图谱数据
    print("1. 生成糖尿病图谱数据...")
    test_query = "医生，我有糖尿病家族史，最近头晕，需要检查血糖吗？"
    try:
        demo.analyze_query_with_graph_update(test_query)
        print(f"   ✓ 通过AI分析生成糖尿病图谱关系")
    except Exception as e:
        print(f"   ⚠️ 生成失败: {e}")
    
    # 2. 查看图谱糖尿病数据
    diabetes_data = demo.graph_manager.get_diabetes_related_data(user_id=demo.user_id)
    total_graph_items = (len(diabetes_data['diseases']) + 
                        len(diabetes_data['symptoms']) + 
                        len(diabetes_data['medicines']) +
                        len(diabetes_data['disease_symptom_relations']) +
                        len(diabetes_data['disease_medicine_relations']))
    
    print(f"\n2. 图谱中糖尿病数据统计: {total_graph_items}项")
    print(f"   疾病实体: {len(diabetes_data['diseases'])}个")
    print(f"   症状实体: {len(diabetes_data['symptoms'])}个")
    print(f"   药物实体: {len(diabetes_data['medicines'])}个")
    print(f"   疾病-症状关系: {len(diabetes_data['disease_symptom_relations'])}条")
    print(f"   疾病-药物关系: {len(diabetes_data['disease_medicine_relations'])}条")
    
    # 3. 执行图谱数据清除
    if total_graph_items > 0:
        print(f"\n3. 执行图谱数据清除...")
        graph_removal = demo.graph_manager.remove_diabetes_related_graph_data(user_id=demo.user_id)
        
        if graph_removal['success']:
            total_removed = (graph_removal['removed_diseases'] + 
                           graph_removal['removed_symptoms'] + 
                           graph_removal['removed_medicines'] +
                           graph_removal['removed_disease_symptom_relations'] +
                           graph_removal['removed_disease_medicine_relations'])
            print(f"   ✅ 成功删除图谱数据: {total_removed}项")
        else:
            print(f"   ❌ 删除失败: {graph_removal['errors']}")
    else:
        print(f"\n3. 无图谱数据需要清除")
    
    # 第三部分：验证清除结果
    print(f"\n🔍 第三部分：验证清除结果")
    print("-" * 50)
    
    # 1. 验证短期记忆
    after_memory_stats = demo.memory_manager.get_memory_stats()
    remaining_diabetes_memories = 0
    for mem in demo.memory_manager.short_term_memory:
        user_msg = mem.get('user_message', '')
        if any(keyword in user_msg for keyword in ['糖尿病', '血糖', '胰岛素', '家族史']):
            remaining_diabetes_memories += 1
    
    print(f"1. 短期记忆验证:")
    print(f"   总记忆数: {after_memory_stats['short_term_count']}条")
    print(f"   糖尿病相关: {remaining_diabetes_memories}条")
    print(f"   验证结果: {'✅ 清除成功' if remaining_diabetes_memories == 0 else '⚠️ 仍有残留'}")
    
    # 2. 验证图谱数据
    after_diabetes_data = demo.graph_manager.get_diabetes_related_data(user_id=demo.user_id)
    remaining_graph_items = (len(after_diabetes_data['diseases']) + 
                            len(after_diabetes_data['symptoms']) + 
                            len(after_diabetes_data['medicines']) +
                            len(after_diabetes_data['disease_symptom_relations']) +
                            len(after_diabetes_data['disease_medicine_relations']))
    
    print(f"\n2. 图谱数据验证:")
    print(f"   糖尿病相关数据: {remaining_graph_items}项")
    print(f"   验证结果: {'✅ 清除成功' if remaining_graph_items == 0 else '⚠️ 仍有残留'}")
    
    # 3. 验证保护机制
    final_relations = demo.graph_manager.get_disease_symptom_relations(user_id=demo.user_id)
    non_diabetes_relations = [r for r in final_relations if '糖尿病' not in r['disease_name']]
    
    print(f"\n3. 数据保护验证:")
    print(f"   非糖尿病医疗关系: {len(non_diabetes_relations)}条")
    if non_diabetes_relations:
        for rel in non_diabetes_relations:
            print(f"     - {rel['disease_name']} → {rel['symptom_name']}")
    print(f"   验证结果: {'✅ 非糖尿病数据得到保护' if len(non_diabetes_relations) > 0 else '⚠️ 可能过度删除'}")
    
    # 总结
    print(f"\n🎊 完整清除演示总结")
    print("=" * 60)
    
    memory_success = remaining_diabetes_memories == 0
    graph_success = remaining_graph_items == 0
    protection_success = len(non_diabetes_relations) > 0
    
    print(f"✅ 短期记忆糖尿病数据清除: {'成功' if memory_success else '失败'}")
    print(f"✅ 图谱糖尿病数据清除: {'成功' if graph_success else '失败'}")
    print(f"✅ 非糖尿病数据保护: {'成功' if protection_success else '需要检查'}")
    
    if memory_success and graph_success and protection_success:
        print(f"\n🎉 完整清除功能测试 100% 成功！")
        print(f"   演示患者的医疗系统中关于糖尿病的全部数据已被安全清除")
        print(f"   同时完好保护了其他重要的医疗记录")
        print(f"\n📊 清除统计:")
        print(f"   短期记忆清除: {memory_removal.get('removed_short_term', 0)}条")
        if total_graph_items > 0:
            print(f"   图谱数据清除: {total_removed if 'total_removed' in locals() else 0}项")
        print(f"   保护的非糖尿病关系: {len(non_diabetes_relations)}条")
    else:
        print(f"\n⚠️ 部分功能需要进一步优化")
    
    return {
        'memory_success': memory_success,
        'graph_success': graph_success, 
        'protection_success': protection_success
    }

if __name__ == "__main__":
    complete_diabetes_clear_demo()