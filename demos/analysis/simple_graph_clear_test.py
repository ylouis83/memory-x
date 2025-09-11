#!/usr/bin/env python3
"""
简单的图谱糖尿病数据清除测试
"""

import sys
sys.path.append('/Users/louisliu/.cursor/memory-x')

from examples.enhanced_qwen_graph_demo import EnhancedQwenGraphDemo

def simple_test():
    print("🧪 简单图谱糖尿病数据清除测试")
    print("=" * 50)
    
    # 初始化
    demo = EnhancedQwenGraphDemo('sk-b70842d25c884aa9aa18955b00c24d37')
    
    # 1. 查看当前糖尿病数据
    print("1. 查看当前糖尿病相关数据...")
    diabetes_data = demo.graph_manager.get_diabetes_related_data(user_id=demo.user_id)
    
    total_before = (len(diabetes_data['diseases']) + 
                   len(diabetes_data['symptoms']) + 
                   len(diabetes_data['medicines']) +
                   len(diabetes_data['disease_symptom_relations']) +
                   len(diabetes_data['disease_medicine_relations']))
    
    print(f"   找到 {total_before} 项糖尿病相关数据")
    print(f"   疾病: {len(diabetes_data['diseases'])} 个")
    print(f"   症状: {len(diabetes_data['symptoms'])} 个") 
    print(f"   药物: {len(diabetes_data['medicines'])} 个")
    print(f"   疾病-症状关系: {len(diabetes_data['disease_symptom_relations'])} 条")
    print(f"   疾病-药物关系: {len(diabetes_data['disease_medicine_relations'])} 条")
    
    # 显示具体数据
    if diabetes_data['diseases']:
        print("   疾病实体:")
        for disease in diabetes_data['diseases']:
            print(f"     - {disease['name']}")
    
    if diabetes_data['disease_symptom_relations']:
        print("   疾病-症状关系:")
        for rel in diabetes_data['disease_symptom_relations']:
            print(f"     - {rel['disease_name']} → {rel['symptom_name']}")
    
    # 2. 执行删除
    if total_before > 0:
        print(f"\n2. 执行删除...")
        removal_result = demo.graph_manager.remove_diabetes_related_graph_data(user_id=demo.user_id)
        
        if removal_result['success']:
            total_removed = (removal_result['removed_diseases'] + 
                           removal_result['removed_symptoms'] + 
                           removal_result['removed_medicines'] +
                           removal_result['removed_disease_symptom_relations'] +
                           removal_result['removed_disease_medicine_relations'])
            print(f"   ✅ 成功删除 {total_removed} 项数据")
        else:
            print(f"   ❌ 删除失败: {removal_result['errors']}")
    else:
        print(f"\n2. 无数据需要删除")
    
    # 3. 验证结果
    print(f"\n3. 验证删除结果...")
    after_data = demo.graph_manager.get_diabetes_related_data(user_id=demo.user_id)
    total_after = (len(after_data['diseases']) + 
                  len(after_data['symptoms']) + 
                  len(after_data['medicines']) +
                  len(after_data['disease_symptom_relations']) +
                  len(after_data['disease_medicine_relations']))
    
    print(f"   删除后剩余: {total_after} 项糖尿病相关数据")
    
    if total_after == 0:
        print(f"   ✅ 验证成功: 糖尿病数据已完全清除")
    else:
        print(f"   ⚠️ 验证失败: 仍有数据残留")
    
    print(f"\n🎉 测试完成!")
    return total_before, total_after

if __name__ == "__main__":
    simple_test()