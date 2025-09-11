#!/usr/bin/env python3
"""
测试清除图谱中糖尿病相关数据的功能
"""

import os
import sys
sys.path.append('/Users/louisliu/.cursor/memory-x')

from examples.enhanced_qwen_graph_demo import EnhancedQwenGraphDemo

def test_clear_graph_diabetes():
    print("🧪 测试清除图谱中糖尿病相关数据的功能")
    print("=" * 60)
    
    # 初始化演示系统
    demo = EnhancedQwenGraphDemo(os.getenv('DASHSCOPE_API_KEY') or "请设置DASHSCOPE_API_KEY环境变量")
    
    print("📊 1. 查看当前图谱状态...")
    
    # 1. 先查看当前图谱中的所有关系
    ds_relations = demo.graph_manager.get_disease_symptom_relations(user_id=demo.user_id)
    dm_relations = demo.graph_manager.get_disease_medicine_relations(user_id=demo.user_id)
    
    print(f"  疾病-症状关系: {len(ds_relations)}条")
    print(f"  疾病-药物关系: {len(dm_relations)}条")
    
    # 显示所有关系
    if ds_relations:
        print(f"  📋 疾病-症状关系详情:")
        for i, rel in enumerate(ds_relations, 1):
            print(f"    {i}. {rel['disease_name']} → {rel['symptom_name']} (置信度: {rel['confidence']})")
    
    # 2. 生成一些糖尿病相关的图谱数据以便测试删除
    print(f"\n📝 2. 生成糖尿病相关测试数据...")
    
    # 添加糖尿病症状关联（通过查询来触发）
    test_queries = [
        "医生，我有糖尿病家族史，最近头晕",
        "我的血糖有点高，需要注意什么？"
    ]
    
    for query in test_queries:
        print(f"  🔍 处理查询: {query}")
        try:
            result = demo.analyze_query_with_graph_update(query)
            print(f"    ✓ 查询处理完成")
        except Exception as e:
            print(f"    ⚠️ 查询处理出错: {e}")
    
    # 3. 查看糖尿病相关数据
    print(f"\n🔍 3. 预览图谱中的糖尿病相关数据...")
    
    diabetes_data = demo.graph_manager.get_diabetes_related_data(user_id=demo.user_id)
    
    print(f"  糖尿病相关疾病实体: {len(diabetes_data['diseases'])}个")
    for disease in diabetes_data['diseases']:
        print(f"    - {disease['name']} (ID: {disease['id']})")
    
    print(f"  糖尿病相关症状实体: {len(diabetes_data['symptoms'])}个")
    for symptom in diabetes_data['symptoms']:
        print(f"    - {symptom['name']} (ID: {symptom['id']})")
    
    print(f"  糖尿病相关药物实体: {len(diabetes_data['medicines'])}个")
    for medicine in diabetes_data['medicines']:
        print(f"    - {medicine['name']} (ID: {medicine['id']})")
    
    print(f"  糖尿病相关疾病-症状关系: {len(diabetes_data['disease_symptom_relations'])}条")
    for rel in diabetes_data['disease_symptom_relations']:
        print(f"    - {rel['disease_name']} → {rel['symptom_name']} (置信度: {rel['confidence']})")
    
    print(f"  糖尿病相关疾病-药物关系: {len(diabetes_data['disease_medicine_relations'])}条")
    for rel in diabetes_data['disease_medicine_relations']:
        print(f"    - {rel['disease_name']} → {rel['medicine_name']}")
    
    total_diabetes_items = (len(diabetes_data['diseases']) + 
                           len(diabetes_data['symptoms']) + 
                           len(diabetes_data['medicines']) +
                           len(diabetes_data['disease_symptom_relations']) +
                           len(diabetes_data['disease_medicine_relations']))
    
    print(f"  📊 总计糖尿病相关数据: {total_diabetes_items}项")
    
    # 4. 执行删除操作
    if total_diabetes_items > 0:
        print(f"\n🗑️ 4. 执行糖尿病数据删除...")
        
        removal_result = demo.graph_manager.remove_diabetes_related_graph_data(user_id=demo.user_id)
        
        if removal_result['success']:
            print(f"  ✅ 删除成功:")
            print(f"    - 删除疾病实体: {removal_result['removed_diseases']}个")
            print(f"    - 删除症状实体: {removal_result['removed_symptoms']}个")
            print(f"    - 删除药物实体: {removal_result['removed_medicines']}个")
            print(f"    - 删除疾病-症状关系: {removal_result['removed_disease_symptom_relations']}条")
            print(f"    - 删除疾病-药物关系: {removal_result['removed_disease_medicine_relations']}条")
            
            total_removed = (removal_result['removed_diseases'] + 
                           removal_result['removed_symptoms'] + 
                           removal_result['removed_medicines'] +
                           removal_result['removed_disease_symptom_relations'] +
                           removal_result['removed_disease_medicine_relations'])
            print(f"  📊 总计删除: {total_removed}项")
        else:
            print(f"  ❌ 删除失败: {removal_result['errors']}")
    else:
        print(f"\n💭 4. 没有找到糖尿病相关数据需要删除")
    
    # 5. 验证删除结果
    print(f"\n🔍 5. 验证删除结果...")
    
    after_diabetes_data = demo.graph_manager.get_diabetes_related_data(user_id=demo.user_id)
    remaining_diabetes_items = (len(after_diabetes_data['diseases']) + 
                               len(after_diabetes_data['symptoms']) + 
                               len(after_diabetes_data['medicines']) +
                               len(after_diabetes_data['disease_symptom_relations']) +
                               len(after_diabetes_data['disease_medicine_relations']))
    
    print(f"  删除后剩余糖尿病相关数据: {remaining_diabetes_items}项")
    
    if remaining_diabetes_items == 0:
        print(f"  ✅ 验证成功: 图谱中已无糖尿病相关数据")
    else:
        print(f"  ⚠️ 验证失败: 仍有 {remaining_diabetes_items} 项糖尿病相关数据")
        
        # 显示剩余数据
        if after_diabetes_data['diseases']:
            print(f"    剩余疾病: {[d['name'] for d in after_diabetes_data['diseases']]}")
        if after_diabetes_data['symptoms']:
            print(f"    剩余症状: {[s['name'] for s in after_diabetes_data['symptoms']]}")
        if after_diabetes_data['disease_symptom_relations']:
            relations_str = [f"{r['disease_name']}→{r['symptom_name']}" for r in after_diabetes_data['disease_symptom_relations']]
            print(f"    剩余关系: {relations_str}")
    
    # 6. 查看删除后的完整图谱状态
    print(f"\n📊 6. 删除后图谱整体状态...")
    
    final_ds_relations = demo.graph_manager.get_disease_symptom_relations(user_id=demo.user_id)
    final_dm_relations = demo.graph_manager.get_disease_medicine_relations(user_id=demo.user_id)
    
    print(f"  总疾病-症状关系: {len(final_ds_relations)}条")
    print(f"  总疾病-药物关系: {len(final_dm_relations)}条")
    
    if final_ds_relations:
        print(f"  📋 剩余疾病-症状关系:")
        for i, rel in enumerate(final_ds_relations, 1):
            print(f"    {i}. {rel['disease_name']} → {rel['symptom_name']} (置信度: {rel['confidence']})")
    
    print(f"\n🎉 测试完成!")
    
    if total_diabetes_items > 0 and remaining_diabetes_items == 0:
        print(f"✅ 糖尿病图谱数据清除功能测试成功!")
        print(f"   成功删除了 {total_diabetes_items} 项糖尿病相关数据")
    elif total_diabetes_items == 0:
        print(f"💭 没有糖尿病数据需要删除")
    else:
        print(f"⚠️ 删除功能需要进一步优化")

if __name__ == "__main__":
    test_clear_graph_diabetes()
