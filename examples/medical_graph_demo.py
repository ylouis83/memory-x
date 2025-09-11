#!/usr/bin/env python3
"""
医疗知识图谱演示
Medical Knowledge Graph Demo

演示如何从用户问答中提取实体信息构建医疗知识图谱
特别针对柳阳的个人医疗信息：40岁，青霉素过敏，糖尿病家族史
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.medical_graph_manager import MedicalGraphManager
from src.core.entity_extractor import MedicalEntityExtractor
import json
from datetime import datetime

def demo_personal_medical_info():
    """演示柳阳的个人医疗信息处理"""
    print("🏥 Medical Knowledge Graph Demo")
    print("=" * 60)
    print(f"用户：柳阳，40岁，青霉素过敏，糖尿病家族史")
    print("-" * 60)
    
    # 初始化图谱管理器和实体抽取器
    graph_manager = MedicalGraphManager("data/demo_medical_graph.db")
    entity_extractor = MedicalEntityExtractor(graph_manager)
    
    # 模拟用户的在线咨询对话
    user_messages = [
        "医生您好，我叫柳阳，今年40岁，我对青霉素过敏，我家有糖尿病遗传病史。",
        "最近感觉有点乏力，口干，多尿的症状，是不是糖尿病的前兆？",
        "我感冒了，能吃阿莫西林吗？我记得我对青霉素过敏。"
    ]
    
    print("\n💬 处理用户对话消息...")
    for i, message in enumerate(user_messages, 1):
        print(f"\n--- 对话 {i} ---")
        print(f"用户消息: {message}")
        
        # 处理消息并构建图谱
        result = entity_extractor.process_user_message(
            message, 
            user_id="liuyang_40", 
            session_id=f"session_{datetime.now().strftime('%Y%m%d')}"
        )
        
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"   存储统计: {result['stored_counts']}")
        else:
            print(f"❌ 处理失败")
    
    return graph_manager

def demo_graph_analysis(graph_manager):
    """演示图谱分析功能"""
    print(f"\n📊 个人医疗图谱分析")
    print("-" * 40)
    
    user_id = "liuyang_40"
    
    # 获取用户图谱摘要
    summary = graph_manager.get_user_graph_summary(user_id)
    print(f"\n📈 图谱摘要:")
    print(f"   疾病-症状关系: {summary['disease_symptom_relations']} 条")
    print(f"   疾病-药品关系: {summary['disease_medicine_relations']} 条")
    print(f"   涉及疾病: {summary['unique_diseases']} 种")
    print(f"   涉及症状: {summary['unique_symptoms']} 种")
    print(f"   涉及药品: {summary['unique_medicines']} 种")
    print(f"   数据来源: {', '.join(summary['data_sources'])}")
    
    # 查看疾病-症状关系
    print(f"\n🔍 疾病-症状关系详情:")
    ds_relations = graph_manager.get_disease_symptom_relations(user_id=user_id)
    for i, rel in enumerate(ds_relations[:5], 1):
        print(f"   {i}. {rel['disease_name']} → {rel['symptom_name']}")
        print(f"      置信度: {rel['confidence']:.2f}, 来源: {rel['source']}")
    
    # 查看疾病-药品关系
    print(f"\n💊 疾病-药品关系详情:")
    dm_relations = graph_manager.get_disease_medicine_relations(user_id=user_id)
    for i, rel in enumerate(dm_relations[:5], 1):
        effectiveness = rel.get('effectiveness', '未知')
        print(f"   {i}. {rel['disease_name']} → {rel['medicine_name']}")
        print(f"      疗效: {effectiveness}, 来源: {rel['source']}")
    
    # 实体搜索演示
    print(f"\n🔎 实体搜索演示:")
    
    # 搜索糖尿病相关
    diabetes_entities = graph_manager.search_entities_by_name('disease', '糖尿病')
    print(f"   搜索'糖尿病': 找到 {len(diabetes_entities)} 个疾病实体")
    
    # 搜索青霉素相关
    penicillin_entities = graph_manager.search_entities_by_name('medicine', '青霉素')
    print(f"   搜索'青霉素': 找到 {len(penicillin_entities)} 个药品实体")
    
    # 搜索症状
    symptom_entities = graph_manager.search_entities_by_name('symptom', '乏力')
    print(f"   搜索'乏力': 找到 {len(symptom_entities)} 个症状实体")

def demo_medical_risk_analysis(graph_manager):
    """演示医疗风险分析"""
    print(f"\n⚠️ 医疗风险分析")
    print("-" * 40)
    
    user_id = "liuyang_40"
    
    # 分析过敏风险
    print(f"\n🚨 过敏风险分析 (基于青霉素过敏史):")
    dm_relations = graph_manager.get_disease_medicine_relations(user_id=user_id)
    
    known_allergies = []
    for rel in dm_relations:
        if '过敏' in (rel.get('context', '') or '') or rel.get('effectiveness') == 'contraindicated':
            known_allergies.append(rel['medicine_name'])
    
    if known_allergies:
        print(f"   已知过敏药物: {', '.join(known_allergies)}")
        print(f"   高风险药物: 阿莫西林(青霉素类交叉过敏)")
        print(f"   中等风险药物: 头孢菌素(可能交叉过敏)")
        print(f"   安全替代: 红霉素、阿奇霉素(大环内酯类)")
    
    # 分析糖尿病风险
    print(f"\n📊 糖尿病风险分析 (基于家族史):")
    ds_relations = graph_manager.get_disease_symptom_relations(user_id=user_id)
    
    diabetes_symptoms = []
    for rel in ds_relations:
        if rel['symptom_name'] in ['多饮', '多尿', '多食', '乏力', '口干', '视力模糊']:
            diabetes_symptoms.append(rel['symptom_name'])
    
    print(f"   风险因素: 家族遗传史、年龄40岁")
    if diabetes_symptoms:
        print(f"   相关症状: {', '.join(diabetes_symptoms)}")
    print(f"   预防建议: 定期血糖监测、健康饮食、规律运动")

def demo_graph_visualization_data():
    """生成图谱可视化数据"""
    print(f"\n🎨 图谱可视化数据生成")
    print("-" * 40)
    
    user_id = "liuyang_40"
    graph_manager = MedicalGraphManager("data/demo_medical_graph.db")
    
    # 获取用户的所有关系
    ds_relations = graph_manager.get_disease_symptom_relations(user_id=user_id)
    dm_relations = graph_manager.get_disease_medicine_relations(user_id=user_id)
    
    # 构建图谱数据
    nodes = []
    edges = []
    node_ids = set()
    
    # 添加节点和边
    for rel in ds_relations:
        # 疾病节点
        if rel['disease_id'] not in node_ids:
            nodes.append({
                'id': rel['disease_id'],
                'name': rel['disease_name'],
                'type': 'disease',
                'color': '#ff4757'  # 红色
            })
            node_ids.add(rel['disease_id'])
        
        # 症状节点
        if rel['symptom_id'] not in node_ids:
            nodes.append({
                'id': rel['symptom_id'],
                'name': rel['symptom_name'],
                'type': 'symptom',
                'color': '#ffa502'  # 橙色
            })
            node_ids.add(rel['symptom_id'])
        
        # 关系边
        edges.append({
            'source': rel['disease_id'],
            'target': rel['symptom_id'],
            'type': 'consult',
            'weight': rel['confidence']
        })
    
    for rel in dm_relations:
        # 疾病节点
        if rel['disease_id'] not in node_ids:
            nodes.append({
                'id': rel['disease_id'],
                'name': rel['disease_name'],
                'type': 'disease',
                'color': '#ff4757'
            })
            node_ids.add(rel['disease_id'])
        
        # 药品节点
        if rel['medicine_id'] not in node_ids:
            color = '#ff3838' if '青霉素' in rel['medicine_name'] else '#2ed573'  # 过敏药物红色，其他绿色
            nodes.append({
                'id': rel['medicine_id'],
                'name': rel['medicine_name'],
                'type': 'medicine',
                'color': color
            })
            node_ids.add(rel['medicine_id'])
        
        # 关系边
        edge_color = '#ff3838' if rel.get('effectiveness') == 'contraindicated' else '#2f3542'
        edges.append({
            'source': rel['disease_id'],
            'target': rel['medicine_id'],
            'type': 'treatment',
            'color': edge_color
        })
    
    visualization_data = {
        'nodes': nodes,
        'edges': edges,
        'statistics': {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'disease_nodes': len([n for n in nodes if n['type'] == 'disease']),
            'symptom_nodes': len([n for n in nodes if n['type'] == 'symptom']),
            'medicine_nodes': len([n for n in nodes if n['type'] == 'medicine'])
        }
    }
    
    print(f"📊 图谱统计:")
    print(f"   节点总数: {visualization_data['statistics']['total_nodes']}")
    print(f"   边总数: {visualization_data['statistics']['total_edges']}")
    print(f"   疾病节点: {visualization_data['statistics']['disease_nodes']}")
    print(f"   症状节点: {visualization_data['statistics']['symptom_nodes']}")
    print(f"   药品节点: {visualization_data['statistics']['medicine_nodes']}")
    
    # 保存可视化数据
    with open('data/graph_visualization.json', 'w', encoding='utf-8') as f:
        json.dump(visualization_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 可视化数据已保存到 data/graph_visualization.json")
    
    return visualization_data

def main():
    """主函数"""
    try:
        # 确保数据目录存在
        os.makedirs('data', exist_ok=True)
        
        print("🚀 开始医疗知识图谱演示")
        
        # 1. 处理个人医疗信息
        graph_manager = demo_personal_medical_info()
        
        # 2. 图谱分析
        demo_graph_analysis(graph_manager)
        
        # 3. 医疗风险分析
        demo_medical_risk_analysis(graph_manager)
        
        # 4. 生成可视化数据
        demo_graph_visualization_data()
        
        print(f"\n🎉 演示完成！")
        print(f"数据库文件: data/demo_medical_graph.db")
        print(f"可视化数据: data/graph_visualization.json")
        
        return True
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
