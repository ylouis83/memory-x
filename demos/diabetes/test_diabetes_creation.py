#!/usr/bin/env python3
"""
直接测试糖尿病关系创建功能
"""

import os
import sys
sys.path.append('/Users/louisliu/.cursor/memory-x')

from src.core.medical_graph_manager import MedicalGraphManager
from src.core.qwen_graph_update_engine import QwenGraphUpdateEngine

def test_diabetes_relation_creation():
    print("🧪 测试糖尿病关系创建功能")
    print("=" * 50)
    
    # 初始化组件
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        raise ValueError("请设置DASHSCOPE_API_KEY环境变量")
    graph_manager = MedicalGraphManager("/Users/louisliu/.cursor/memory-x/data/diabetes_test.db")
    qwen_engine = QwenGraphUpdateEngine(graph_manager, api_key)
    
    user_id = "liuyang_diabetes_test"
    current_symptoms = ["头晕"]
    context = "患者柳阳，40岁，有糖尿病家族史，最近出现头晕症状"
    
    print(f"👤 患者: 柳阳，40岁，糖尿病家族史")
    print(f"💭 症状: {current_symptoms}")
    print(f"📝 背景: {context}")
    
    # 直接调用分析
    print(f"\n🤖 调用Qwen AI分析...")
    decision = qwen_engine.analyze_update_scenario(
        current_symptoms=current_symptoms,
        user_id=user_id,
        context=context
    )
    
    print(f"\n📊 分析结果:")
    print(f"  动作: {decision.action.value}")
    print(f"  置信度: {decision.confidence}")
    print(f"  分析理由: {decision.reasoning[:200]}...")
    
    if decision.diabetes_risk_assessment:
        print(f"  糖尿病风险评估: {decision.diabetes_risk_assessment}")
    
    # 如果识别为糖尿病关系，执行创建
    if decision.action.value == "create_diabetes_relation":
        print(f"\n🌱 执行糖尿病关系创建...")
        execution_result = qwen_engine.execute_diabetes_relation_creation(
            symptoms=current_symptoms,
            user_id=user_id,
            diabetes_risk_assessment=decision.diabetes_risk_assessment or "高风险"
        )
        
        if execution_result["success"]:
            print(f"✅ 成功!")
            print(f"  创建实体: {len(execution_result['created_entities'])}个")
            print(f"  创建关系: {len(execution_result['created_relations'])}个")
            
            for entity in execution_result["created_entities"]:
                print(f"    - {entity['type']}: {entity['name']}")
            
            for relation in execution_result["created_relations"]:
                print(f"    - 关系: {relation['disease']} → {relation['symptom']} (置信度: {relation['confidence']})")
        else:
            print(f"❌ 失败: {execution_result['errors']}")
    else:
        print(f"\n⚠️  AI没有识别为糖尿病关系创建")
        print(f"   实际动作: {decision.action.value}")
        print(f"   需要进一步优化提示工程")
    
    # 验证图谱中的关系
    print(f"\n🔍 验证创建的图谱关系:")
    relations = graph_manager.get_disease_symptom_relations(user_id=user_id)
    
    diabetes_relations = [r for r in relations if "糖尿病" in r.get('disease_name', '')]
    
    if diabetes_relations:
        print(f"✅ 找到 {len(diabetes_relations)} 个糖尿病相关关系:")
        for rel in diabetes_relations:
            print(f"  - {rel['disease_name']} → {rel['symptom_name']} (置信度: {rel['confidence']})")
    else:
        print(f"❌ 未找到糖尿病相关关系")

if __name__ == "__main__":
    test_diabetes_relation_creation()