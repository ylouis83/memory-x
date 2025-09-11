#!/usr/bin/env python3
"""
综合查询所有数据库中的糖尿病相关数据
"""

import sqlite3
import json
import os
from typing import Dict, List, Any
from datetime import datetime

def query_diabetes_data_from_db(db_path: str) -> Dict[str, Any]:
    """从单个数据库查询糖尿病相关数据"""
    results = {
        'db_path': db_path,
        'db_name': os.path.basename(db_path),
        'exists': os.path.exists(db_path),
        'diseases': [],
        'symptoms': [],
        'medicines': [],
        'disease_symptom_relations': [],
        'disease_medicine_relations': [],
        'conversations': [],
        'error': None
    }
    
    if not os.path.exists(db_path):
        results['error'] = "数据库文件不存在"
        return results
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        results['tables'] = tables
        
        # 查询糖尿病相关的疾病实体
        if 'diseases' in tables:
            cursor.execute("""
                SELECT * FROM diseases 
                WHERE name LIKE '%糖尿病%' OR name LIKE '%diabetes%' OR name LIKE '%血糖%'
                   OR description LIKE '%糖尿病%' OR description LIKE '%diabetes%'
            """)
            results['diseases'] = [dict(row) for row in cursor.fetchall()]
        
        # 查询糖尿病相关的症状实体
        if 'symptoms' in tables:
            cursor.execute("""
                SELECT * FROM symptoms 
                WHERE name LIKE '%糖尿病%' OR name LIKE '%血糖%' OR name LIKE '%胰岛素%'
                   OR description LIKE '%糖尿病%' OR description LIKE '%diabetes%'
            """)
            results['symptoms'] = [dict(row) for row in cursor.fetchall()]
        
        # 查询糖尿病相关的药物实体
        if 'medicines' in tables:
            cursor.execute("""
                SELECT * FROM medicines 
                WHERE name LIKE '%胰岛素%' OR name LIKE '%血糖%' OR name LIKE '%糖尿病%'
                   OR description LIKE '%糖尿病%' OR description LIKE '%diabetes%'
            """)
            results['medicines'] = [dict(row) for row in cursor.fetchall()]
        
        # 查询糖尿病相关的疾病-症状关系
        if 'disease_symptom_relations' in tables:
            cursor.execute("""
                SELECT dsr.*, d.name as disease_name, s.name as symptom_name
                FROM disease_symptom_relations dsr
                LEFT JOIN diseases d ON dsr.disease_id = d.id
                LEFT JOIN symptoms s ON dsr.symptom_id = s.id
                WHERE d.name LIKE '%糖尿病%' OR d.name LIKE '%diabetes%' OR d.name LIKE '%血糖%'
                   OR s.name LIKE '%糖尿病%' OR s.name LIKE '%血糖%'
            """)
            results['disease_symptom_relations'] = [dict(row) for row in cursor.fetchall()]
        
        # 查询糖尿病相关的疾病-药物关系
        if 'disease_medicine_relations' in tables:
            cursor.execute("""
                SELECT dmr.*, d.name as disease_name, m.name as medicine_name
                FROM disease_medicine_relations dmr
                LEFT JOIN diseases d ON dmr.disease_id = d.id
                LEFT JOIN medicines m ON dmr.medicine_id = m.id
                WHERE d.name LIKE '%糖尿病%' OR d.name LIKE '%diabetes%'
                   OR m.name LIKE '%胰岛素%' OR m.name LIKE '%血糖%'
            """)
            results['disease_medicine_relations'] = [dict(row) for row in cursor.fetchall()]
        
        # 查询糖尿病相关的对话记录
        if 'conversations' in tables:
            cursor.execute("""
                SELECT * FROM conversations 
                WHERE user_message LIKE '%糖尿病%' OR user_message LIKE '%血糖%' OR user_message LIKE '%胰岛素%'
                   OR ai_response LIKE '%糖尿病%' OR ai_response LIKE '%血糖%' OR ai_response LIKE '%胰岛素%'
                   OR entities LIKE '%糖尿病%' OR entities LIKE '%血糖%' OR entities LIKE '%胰岛素%'
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            results['conversations'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
    except Exception as e:
        results['error'] = str(e)
    
    return results

def analyze_all_databases():
    """分析所有数据库中的糖尿病数据"""
    print("🔍 综合查询所有数据库中的糖尿病相关数据")
    print("=" * 80)
    
    # 所有数据库路径
    db_paths = [
        "/Users/louisliu/.cursor/memory-x/memory_db/spanner_memory.db",
        "/Users/louisliu/.cursor/memory-x/memory_db/user_memories.db",
        "/Users/louisliu/.cursor/memory-x/examples/data/demo_medical_graph.db",
        "/Users/louisliu/.cursor/memory-x/examples/data/simple_memory.db",
        "/Users/louisliu/.cursor/memory-x/data/demo_medical_graph.db",
        "/Users/louisliu/.cursor/memory-x/data/diabetes_test.db",
        "/Users/louisliu/.cursor/memory-x/data/qwen_update_demo.db",
        "/Users/louisliu/.cursor/memory-x/data/qwen_demo.db",
        "/Users/louisliu/.cursor/memory-x/data/simple_memory.db",
        "/Users/louisliu/.cursor/memory-x/data/diabetes_scenario_demo.db",
        "/Users/louisliu/.cursor/memory-x/data/update_demo.db",
        "/Users/louisliu/.cursor/memory-x/data/enhanced_qwen_demo.db",
        "/Users/louisliu/.cursor/memory-x/data/dashscope_memory.db",
        "/Users/louisliu/.cursor/memory-x/data/test.db",
        "/Users/louisliu/.cursor/memory-x/data/qwen_multi_demo.db"
    ]
    
    all_results = []
    global_stats = {
        'total_databases': 0,
        'databases_with_diabetes_data': 0,
        'total_diseases': 0,
        'total_symptoms': 0,
        'total_medicines': 0,
        'total_disease_symptom_relations': 0,
        'total_disease_medicine_relations': 0,
        'total_conversations': 0
    }
    
    for db_path in db_paths:
        print(f"\n📊 查询数据库: {os.path.basename(db_path)}")
        print("-" * 50)
        
        results = query_diabetes_data_from_db(db_path)
        
        if results['exists']:
            global_stats['total_databases'] += 1
            
            # 统计本数据库的糖尿病数据
            db_diabetes_count = (len(results['diseases']) + 
                               len(results['symptoms']) + 
                               len(results['medicines']) +
                               len(results['disease_symptom_relations']) +
                               len(results['disease_medicine_relations']) +
                               len(results['conversations']))
            
            if db_diabetes_count > 0:
                global_stats['databases_with_diabetes_data'] += 1
                global_stats['total_diseases'] += len(results['diseases'])
                global_stats['total_symptoms'] += len(results['symptoms'])
                global_stats['total_medicines'] += len(results['medicines'])
                global_stats['total_disease_symptom_relations'] += len(results['disease_symptom_relations'])
                global_stats['total_disease_medicine_relations'] += len(results['disease_medicine_relations'])
                global_stats['total_conversations'] += len(results['conversations'])
                
                print(f"✅ 包含糖尿病数据: {db_diabetes_count}项")
                print(f"   疾病实体: {len(results['diseases'])}个")
                print(f"   症状实体: {len(results['symptoms'])}个")
                print(f"   药物实体: {len(results['medicines'])}个")
                print(f"   疾病-症状关系: {len(results['disease_symptom_relations'])}条")
                print(f"   疾病-药物关系: {len(results['disease_medicine_relations'])}条")
                print(f"   相关对话: {len(results['conversations'])}条")
                
                # 显示具体的糖尿病实体
                if results['diseases']:
                    print(f"   📋 糖尿病疾病实体:")
                    for disease in results['diseases']:
                        print(f"     - {disease['name']} (ID: {disease.get('id', 'N/A')})")
                
                if results['disease_symptom_relations']:
                    print(f"   🔗 糖尿病相关症状关系:")
                    for rel in results['disease_symptom_relations']:
                        print(f"     - {rel.get('disease_name', 'N/A')} → {rel.get('symptom_name', 'N/A')} (置信度: {rel.get('confidence', 'N/A')})")
                
            else:
                print(f"⚪ 无糖尿病数据")
            
            if results['error']:
                print(f"⚠️ 查询错误: {results['error']}")
        else:
            print(f"❌ 数据库文件不存在")
        
        all_results.append(results)
    
    # 全局统计总结
    print(f"\n🌍 全局糖尿病数据统计")
    print("=" * 80)
    print(f"📁 总数据库数量: {global_stats['total_databases']}")
    print(f"📊 包含糖尿病数据的数据库: {global_stats['databases_with_diabetes_data']}")
    print(f"🏥 糖尿病疾病实体总数: {global_stats['total_diseases']}")
    print(f"🤒 相关症状实体总数: {global_stats['total_symptoms']}")
    print(f"💊 相关药物实体总数: {global_stats['total_medicines']}")
    print(f"🔗 疾病-症状关系总数: {global_stats['total_disease_symptom_relations']}")
    print(f"🔗 疾病-药物关系总数: {global_stats['total_disease_medicine_relations']}")
    print(f"💬 相关对话记录总数: {global_stats['total_conversations']}")
    
    # 数据分布分析
    print(f"\n📈 数据分布分析")
    print("-" * 50)
    
    diabetes_dbs = []
    for result in all_results:
        if result['exists']:
            db_count = (len(result['diseases']) + 
                       len(result['symptoms']) + 
                       len(result['medicines']) +
                       len(result['disease_symptom_relations']) +
                       len(result['disease_medicine_relations']) +
                       len(result['conversations']))
            if db_count > 0:
                diabetes_dbs.append({
                    'name': result['db_name'],
                    'count': db_count,
                    'diseases': len(result['diseases']),
                    'relations': len(result['disease_symptom_relations'])
                })
    
    # 按数据量排序
    diabetes_dbs.sort(key=lambda x: x['count'], reverse=True)
    
    print(f"🏆 糖尿病数据最丰富的数据库:")
    for i, db_info in enumerate(diabetes_dbs[:5], 1):
        print(f"  {i}. {db_info['name']}: {db_info['count']}项数据 ({db_info['diseases']}疾病, {db_info['relations']}关系)")
    
    if global_stats['total_diseases'] > 0:
        print(f"\n✅ 发现糖尿病相关数据！")
        print(f"   主要分布在 {global_stats['databases_with_diabetes_data']} 个数据库中")
        print(f"   共计 {sum([global_stats['total_diseases'], global_stats['total_symptoms'], global_stats['total_medicines'], global_stats['total_disease_symptom_relations'], global_stats['total_disease_medicine_relations']])} 项医疗图谱数据")
    else:
        print(f"\n💭 未发现糖尿病相关的图谱数据")
    
    # 保存详细报告
    report_path = "/Users/louisliu/.cursor/memory-x/diabetes_comprehensive_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'global_stats': global_stats,
            'database_results': all_results,
            'top_databases': diabetes_dbs
        }, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n📄 详细报告已保存至: {report_path}")
    
    return all_results, global_stats

if __name__ == "__main__":
    analyze_all_databases()