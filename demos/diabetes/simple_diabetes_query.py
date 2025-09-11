#!/usr/bin/env python3
"""
简化糖尿病图谱数据查询
"""

import sqlite3
import os

def simple_query():
    """简化查询糖尿病数据"""
    print("🔍 糖尿病图谱数据查询")
    print("=" * 50)
    
    databases = [
        "/Users/louisliu/.cursor/memory-x/data/demo_medical_graph.db",
        "/Users/louisliu/.cursor/memory-x/examples/data/demo_medical_graph.db", 
        "/Users/louisliu/.cursor/memory-x/data/diabetes_test.db",
        "/Users/louisliu/.cursor/memory-x/data/diabetes_scenario_demo.db",
        "/Users/louisliu/.cursor/memory-x/data/enhanced_qwen_demo.db",
        "/Users/louisliu/.cursor/memory-x/data/update_demo.db"
    ]
    
    global_stats = {
        'total_diseases': 0,
        'total_symptoms': 0,
        'total_medicines': 0,
        'total_relations': 0
    }
    
    for db_path in databases:
        if not os.path.exists(db_path):
            continue
            
        db_name = os.path.basename(db_path)
        print(f"\n📊 {db_name}")
        print("-" * 30)
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 查询疾病
            cursor.execute("SELECT id, name FROM diseases WHERE name LIKE '%糖尿病%' OR name LIKE '%diabetes%'")
            diseases = cursor.fetchall()
            
            if diseases:
                print(f"🏥 疾病实体 ({len(diseases)}个):")
                for disease_id, disease_name in diseases:
                    print(f"  • {disease_name} (ID: {disease_id})")
                global_stats['total_diseases'] += len(diseases)
            
            # 查询症状
            cursor.execute("SELECT id, name FROM symptoms WHERE name LIKE '%头晕%' OR name LIKE '%口渴%' OR name LIKE '%血糖%'")
            symptoms = cursor.fetchall()
            
            if symptoms:
                print(f"🤒 相关症状 ({len(symptoms)}个):")
                for symptom_id, symptom_name in symptoms:
                    print(f"  • {symptom_name} (ID: {symptom_id})")
                global_stats['total_symptoms'] += len(symptoms)
            
            # 查询药物
            cursor.execute("SELECT id, name FROM medicines WHERE name LIKE '%胰岛素%'")
            medicines = cursor.fetchall()
            
            if medicines:
                print(f"💊 相关药物 ({len(medicines)}个):")
                for med_id, med_name in medicines:
                    print(f"  • {med_name} (ID: {med_id})")
                global_stats['total_medicines'] += len(medicines)
            
            # 查询疾病-症状关系
            cursor.execute("""
                SELECT dsr.id, d.name as disease_name, s.name as symptom_name, dsr.confidence
                FROM disease_symptom_relations dsr
                JOIN diseases d ON dsr.disease_id = d.id
                JOIN symptoms s ON dsr.symptom_id = s.id
                WHERE d.name LIKE '%糖尿病%' OR d.name LIKE '%diabetes%'
            """)
            relations = cursor.fetchall()
            
            if relations:
                print(f"🔗 疾病-症状关系 ({len(relations)}条):")
                for rel_id, disease_name, symptom_name, confidence in relations:
                    print(f"  • {disease_name} → {symptom_name} (置信度: {confidence})")
                global_stats['total_relations'] += len(relations)
            
            if not (diseases or symptoms or medicines or relations):
                print("⚪ 无糖尿病相关数据")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ 查询错误: {e}")
    
    print(f"\n🌍 全局统计")
    print("=" * 50)
    print(f"🏥 糖尿病疾病实体: {global_stats['total_diseases']}个")
    print(f"🤒 相关症状实体: {global_stats['total_symptoms']}个")
    print(f"💊 相关药物实体: {global_stats['total_medicines']}个")
    print(f"🔗 疾病-症状关系: {global_stats['total_relations']}条")
    
    total = sum(global_stats.values())
    print(f"📊 总计: {total}项糖尿病相关数据")
    
    if total > 0:
        print(f"\n✅ 发现糖尿病图谱数据！")
        if global_stats['total_relations'] > 0:
            print(f"🔗 已建立糖尿病症状关联")
        else:
            print(f"⚠️ 糖尿病实体存在，但症状关联待建立")
    else:
        print(f"\n💭 未发现糖尿病图谱数据")

if __name__ == "__main__":
    simple_query()