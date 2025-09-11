#!/usr/bin/env python3
"""
查询糖尿病图谱数据 - 专注数据展示
"""

import sqlite3
import os
import json
from datetime import datetime

def query_single_database(db_path: str):
    """查询单个数据库的糖尿病数据"""
    if not os.path.exists(db_path):
        return None
    
    print(f"\n📊 查询数据库: {os.path.basename(db_path)}")
    print("-" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表信息
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 包含表: {', '.join(tables)}")
        
        diabetes_data = {
            'diseases': [],
            'symptoms': [],
            'medicines': [],
            'disease_symptom_relations': []
        }
        
        # 查询糖尿病疾病实体
        if 'diseases' in tables:
            cursor.execute("""
                SELECT id, name, category, severity, user_id, created_time 
                FROM diseases 
                WHERE name LIKE '%糖尿病%' OR name LIKE '%diabetes%' OR name LIKE '%血糖%'
            """)
            for row in cursor.fetchall():
                diabetes_data['diseases'].append({
                    'id': row[0],
                    'name': row[1],
                    'category': row[2] if len(row) > 2 else None,
                    'severity': row[3] if len(row) > 3 else None,
                    'user_id': row[4] if len(row) > 4 else None,
                    'created_time': row[5] if len(row) > 5 else None
                })
        
        # 查询相关症状
        if 'symptoms' in tables:
            cursor.execute("""
                SELECT id, name, severity, user_id, created_time 
                FROM symptoms 
                WHERE name LIKE '%糖尿病%' OR name LIKE '%血糖%' OR name LIKE '%胰岛素%'
            """)
            for row in cursor.fetchall():
                diabetes_data['symptoms'].append({
                    'id': row[0],
                    'name': row[1],
                    'severity': row[2] if len(row) > 2 else None,
                    'user_id': row[3] if len(row) > 3 else None,
                    'created_time': row[4] if len(row) > 4 else None
                })
        
        # 查询相关药物
        if 'medicines' in tables:
            cursor.execute("""
                SELECT id, name, type, user_id, created_time 
                FROM medicines 
                WHERE name LIKE '%胰岛素%' OR name LIKE '%血糖%' OR name LIKE '%糖尿病%'
            """)
            for row in cursor.fetchall():
                diabetes_data['medicines'].append({
                    'id': row[0],
                    'name': row[1],
                    'type': row[2] if len(row) > 2 else None,
                    'user_id': row[3] if len(row) > 3 else None,
                    'created_time': row[4] if len(row) > 4 else None
                })
        
        # 查询疾病-症状关系
        if 'disease_symptom_relations' in tables:
            cursor.execute("""
                SELECT dsr.id, dsr.disease_id, dsr.symptom_id, dsr.confidence, dsr.user_id, dsr.created_time,
                       d.name as disease_name, s.name as symptom_name
                FROM disease_symptom_relations dsr
                LEFT JOIN diseases d ON dsr.disease_id = d.id
                LEFT JOIN symptoms s ON dsr.symptom_id = s.id
                WHERE d.name LIKE '%糖尿病%' OR d.name LIKE '%diabetes%' OR d.name LIKE '%血糖%'
                   OR s.name LIKE '%糖尿病%' OR s.name LIKE '%血糖%'
            """)
            for row in cursor.fetchall():
                diabetes_data['disease_symptom_relations'].append({
                    'id': row[0],
                    'disease_id': row[1],
                    'symptom_id': row[2],
                    'confidence': row[3],
                    'user_id': row[4],
                    'created_time': row[5],
                    'disease_name': row[6],
                    'symptom_name': row[7]
                })
        
        # 显示结果
        total_items = (len(diabetes_data['diseases']) + len(diabetes_data['symptoms']) + 
                      len(diabetes_data['medicines']) + len(diabetes_data['disease_symptom_relations']))
        
        if total_items > 0:
            print(f"✅ 发现糖尿病数据: {total_items}项")
            
            if diabetes_data['diseases']:
                print(f"\n🏥 疾病实体 ({len(diabetes_data['diseases'])}个):")
                for disease in diabetes_data['diseases']:
                    print(f"  • {disease['name']} (ID: {disease['id']})")
                    if disease['user_id']:
                        print(f"    用户: {disease['user_id']}")
                    if disease['category']:
                        print(f"    类别: {disease['category']}")
                    if disease['severity']:
                        print(f"    严重程度: {disease['severity']}")
            
            if diabetes_data['symptoms']:
                print(f"\n🤒 症状实体 ({len(diabetes_data['symptoms'])}个):")
                for symptom in diabetes_data['symptoms']:
                    print(f"  • {symptom['name']} (ID: {symptom['id']})")
                    if symptom['user_id']:
                        print(f"    用户: {symptom['user_id']}")
                    if symptom['severity']:
                        print(f"    严重程度: {symptom['severity']}")
            
            if diabetes_data['medicines']:
                print(f"\n💊 药物实体 ({len(diabetes_data['medicines'])}个):")
                for medicine in diabetes_data['medicines']:
                    print(f"  • {medicine['name']} (ID: {medicine['id']})")
                    if medicine['user_id']:
                        print(f"    用户: {medicine['user_id']}")
                    if medicine['type']:
                        print(f"    类型: {medicine['type']}")
            
            if diabetes_data['disease_symptom_relations']:
                print(f"\n🔗 疾病-症状关系 ({len(diabetes_data['disease_symptom_relations'])}条):")
                for rel in diabetes_data['disease_symptom_relations']:
                    print(f"  • {rel['disease_name']} → {rel['symptom_name']}")
                    print(f"    置信度: {rel['confidence']}")
                    if rel['user_id']:
                        print(f"    用户: {rel['user_id']}")
        else:
            print("⚪ 无糖尿病相关数据")
        
        conn.close()
        return diabetes_data
        
    except Exception as e:
        print(f"❌ 查询出错: {e}")
        return None

def main():
    """主查询函数"""
    print("🔍 糖尿病图谱数据查询")
    print("=" * 60)
    
    # 要查询的数据库列表（按重要性排序）
    databases = [
        "/Users/louisliu/.cursor/memory-x/data/demo_medical_graph.db",
        "/Users/louisliu/.cursor/memory-x/data/diabetes_test.db", 
        "/Users/louisliu/.cursor/memory-x/data/diabetes_scenario_demo.db",
        "/Users/louisliu/.cursor/memory-x/data/enhanced_qwen_demo.db",
        "/Users/louisliu/.cursor/memory-x/examples/data/demo_medical_graph.db",
        "/Users/louisliu/.cursor/memory-x/data/update_demo.db"
    ]
    
    all_data = {}
    total_stats = {
        'databases_checked': 0,
        'databases_with_data': 0,
        'total_diseases': 0,
        'total_symptoms': 0,
        'total_medicines': 0,
        'total_relations': 0
    }
    
    for db_path in databases:
        total_stats['databases_checked'] += 1
        result = query_single_database(db_path)
        
        if result and any(len(v) > 0 for v in result.values()):
            total_stats['databases_with_data'] += 1
            total_stats['total_diseases'] += len(result['diseases'])
            total_stats['total_symptoms'] += len(result['symptoms'])
            total_stats['total_medicines'] += len(result['medicines'])
            total_stats['total_relations'] += len(result['disease_symptom_relations'])
            
            all_data[os.path.basename(db_path)] = result
    
    # 汇总报告
    print(f"\n📊 糖尿病数据汇总报告")
    print("=" * 60)
    print(f"🔍 检查数据库: {total_stats['databases_checked']}个")
    print(f"💾 包含数据的数据库: {total_stats['databases_with_data']}个")
    print(f"🏥 糖尿病疾病实体总计: {total_stats['total_diseases']}个")
    print(f"🤒 相关症状实体总计: {total_stats['total_symptoms']}个")
    print(f"💊 相关药物实体总计: {total_stats['total_medicines']}个")
    print(f"🔗 疾病-症状关系总计: {total_stats['total_relations']}条")
    
    if total_stats['databases_with_data'] > 0:
        print(f"\n📈 数据分布详情:")
        for db_name, data in all_data.items():
            item_count = len(data['diseases']) + len(data['symptoms']) + len(data['medicines']) + len(data['disease_symptom_relations'])
            print(f"  • {db_name}: {item_count}项 (疾病{len(data['diseases'])}, 症状{len(data['symptoms'])}, 关系{len(data['disease_symptom_relations'])})")
        
        print(f"\n✅ 糖尿病图谱数据查询完成！")
        if total_stats['total_relations'] > 0:
            print(f"   图谱中已建立糖尿病相关的症状关联")
        else:
            print(f"   图谱中糖尿病实体存在，但症状关联有待建立")
    else:
        print(f"\n💭 未发现糖尿病相关的图谱数据")
    
    # 保存查询结果
    report = {
        'timestamp': datetime.now().isoformat(),
        'statistics': total_stats,
        'detailed_data': all_data
    }
    
    report_path = "/Users/louisliu/.cursor/memory-x/diabetes_query_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n📄 详细报告已保存: {report_path}")

if __name__ == "__main__":
    main()