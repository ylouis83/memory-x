#!/usr/bin/env python3
"""
最终糖尿病图谱数据查询 - 自适应表结构
"""

import sqlite3
import os
import json
from datetime import datetime

def get_table_columns(cursor, table_name):
    """获取表的列信息"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]

def query_diabetes_data():
    """查询所有数据库中的糖尿病数据"""
    print("🔍 糖尿病图谱数据最终查询")
    print("=" * 60)
    
    # 重要的数据库文件
    databases = [
        "/Users/louisliu/.cursor/memory-x/data/demo_medical_graph.db",
        "/Users/louisliu/.cursor/memory-x/examples/data/demo_medical_graph.db", 
        "/Users/louisliu/.cursor/memory-x/data/diabetes_test.db",
        "/Users/louisliu/.cursor/memory-x/data/diabetes_scenario_demo.db",
        "/Users/louisliu/.cursor/memory-x/data/enhanced_qwen_demo.db",
        "/Users/louisliu/.cursor/memory-x/data/update_demo.db"
    ]
    
    all_results = {}
    global_stats = {
        'total_diseases': 0,
        'total_symptoms': 0,
        'total_medicines': 0,
        'total_disease_symptom_relations': 0,
        'total_disease_medicine_relations': 0
    }
    
    for db_path in databases:
        if not os.path.exists(db_path):
            continue
            
        db_name = os.path.basename(db_path)
        print(f"\n📊 分析数据库: {db_name}")
        print("-" * 50)
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取表列表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            db_results = {
                'diseases': [],
                'symptoms': [],
                'medicines': [],
                'disease_symptom_relations': [],
                'disease_medicine_relations': []
            }
            
            # 查询疾病实体
            if 'diseases' in tables:
                columns = get_table_columns(cursor, 'diseases')
                base_columns = "id, name"
                optional_columns = []
                if 'category' in columns:
                    optional_columns.append('category')
                if 'severity' in columns:
                    optional_columns.append('severity')
                if 'user_id' in columns:
                    optional_columns.append('user_id')
                if 'created_time' in columns:
                    optional_columns.append('created_time')
                
                query_columns = base_columns
                if optional_columns:
                    query_columns += ", " + ", ".join(optional_columns)
                
                cursor.execute(f"""
                    SELECT {query_columns} FROM diseases 
                    WHERE name LIKE '%糖尿病%' OR name LIKE '%diabetes%' OR name LIKE '%血糖%'
                """)
                
                for row in cursor.fetchall():
                    disease = {'id': row[0], 'name': row[1]}
                    col_idx = 2
                    if 'category' in columns and col_idx < len(row):
                        disease['category'] = row[col_idx]
                        col_idx += 1
                    if 'severity' in columns and col_idx < len(row):
                        disease['severity'] = row[col_idx]
                        col_idx += 1
                    if 'user_id' in columns and col_idx < len(row):
                        disease['user_id'] = row[col_idx]
                        col_idx += 1
                    if 'created_time' in columns and col_idx < len(row):
                        disease['created_time'] = row[col_idx]
                    
                    db_results['diseases'].append(disease)
            
            # 查询症状实体
            if 'symptoms' in tables:
                columns = get_table_columns(cursor, 'symptoms')
                base_columns = "id, name"
                optional_columns = []
                if 'severity' in columns:
                    optional_columns.append('severity')
                if 'user_id' in columns:
                    optional_columns.append('user_id')
                if 'created_time' in columns:
                    optional_columns.append('created_time')
                
                query_columns = base_columns
                if optional_columns:
                    query_columns += ", " + ", ".join(optional_columns)
                
                cursor.execute(f"""
                    SELECT {query_columns} FROM symptoms 
                    WHERE name LIKE '%糖尿病%' OR name LIKE '%血糖%' OR name LIKE '%头晕%' OR name LIKE '%口渴%'
                """)
                
                for row in cursor.fetchall():
                    symptom = {'id': row[0], 'name': row[1]}
                    col_idx = 2
                    if 'severity' in columns and col_idx < len(row):
                        symptom['severity'] = row[col_idx]
                        col_idx += 1
                    if 'user_id' in columns and col_idx < len(row):
                        symptom['user_id'] = row[col_idx]
                        col_idx += 1
                    if 'created_time' in columns and col_idx < len(row):
                        symptom['created_time'] = row[col_idx]
                    
                    db_results['symptoms'].append(symptom)
            
            # 查询药物实体
            if 'medicines' in tables:
                cursor.execute("SELECT id, name FROM medicines WHERE name LIKE '%胰岛素%' OR name LIKE '%血糖%'")
                for row in cursor.fetchall():
                    db_results['medicines'].append({'id': row[0], 'name': row[1]})
            
            # 查询疾病-症状关系
            if 'disease_symptom_relations' in tables:
                cursor.execute("""
                    SELECT dsr.id, dsr.disease_id, dsr.symptom_id, dsr.confidence,
                           d.name as disease_name, s.name as symptom_name
                    FROM disease_symptom_relations dsr
                    LEFT JOIN diseases d ON dsr.disease_id = d.id
                    LEFT JOIN symptoms s ON dsr.symptom_id = s.id
                    WHERE d.name LIKE '%糖尿病%' OR d.name LIKE '%diabetes%' OR d.name LIKE '%血糖%'
                       OR s.name LIKE '%糖尿病%' OR s.name LIKE '%血糖%' OR s.name LIKE '%头晕%'
                """)
                
                for row in cursor.fetchall():
                    db_results['disease_symptom_relations'].append({
                        'id': row[0],
                        'disease_id': row[1],  
                        'symptom_id': row[2],
                        'confidence': row[3],
                        'disease_name': row[4],
                        'symptom_name': row[5]
                    })
            
            # 查询疾病-药物关系
            if 'disease_medicine_relations' in tables:
                cursor.execute("""
                    SELECT dmr.id, dmr.disease_id, dmr.medicine_id, dmr.confidence,
                           d.name as disease_name, m.name as medicine_name
                    FROM disease_medicine_relations dmr
                    LEFT JOIN diseases d ON dmr.disease_id = d.id
                    LEFT JOIN medicines m ON dmr.medicine_id = m.id
                    WHERE d.name LIKE '%糖尿病%' OR d.name LIKE '%diabetes%'
                       OR m.name LIKE '%胰岛素%' OR m.name LIKE '%血糖%'
                """)
                
                for row in cursor.fetchall():
                    db_results['disease_medicine_relations'].append({
                        'id': row[0],
                        'disease_id': row[1],
                        'medicine_id': row[2],
                        'confidence': row[3],
                        'disease_name': row[4],
                        'medicine_name': row[5]
                    })
            
            # 统计当前数据库的数据
            total_items = (len(db_results['diseases']) + len(db_results['symptoms']) + 
                          len(db_results['medicines']) + len(db_results['disease_symptom_relations']) +
                          len(db_results['disease_medicine_relations']))
            
            if total_items > 0:
                print(f"✅ 发现糖尿病数据: {total_items}项")
                
                # 显示疾病实体
                if db_results['diseases']:
                    print(f"🏥 疾病实体 ({len(db_results['diseases'])}个):")
                    for disease in db_results['diseases']:
                        user_info = f" (用户: {disease.get('user_id', 'N/A')})" if disease.get('user_id') else ""
                        print(f"  • {disease['name']}{user_info}")
                        print(f"    ID: {disease['id']}")
                        if disease.get('category'):
                            print(f"    类别: {disease['category']}")
                        if disease.get('severity'):
                            print(f"    严重程度: {disease['severity']}")
                
                # 显示症状实体
                if db_results['symptoms']:
                    print(f"🤒 症状实体 ({len(db_results['symptoms'])}个):")
                    for symptom in db_results['symptoms']:
                        user_info = f" (用户: {symptom.get('user_id', 'N/A')})" if symptom.get('user_id') else ""
                        print(f"  • {symptom['name']}{user_info}")
                        print(f"    ID: {symptom['id']}")
                        if symptom.get('severity'):
                            print(f"    严重程度: {symptom['severity']}")
                
                # 显示药物实体
                if db_results['medicines']:
                    print(f"💊 药物实体 ({len(db_results['medicines'])}个):")
                    for medicine in db_results['medicines']:
                        print(f"  • {medicine['name']} (ID: {medicine['id']})")
                
                # 显示疾病-症状关系
                if db_results['disease_symptom_relations']:
                    print(f"🔗 疾病-症状关系 ({len(db_results['disease_symptom_relations'])}条):")
                    for rel in db_results['disease_symptom_relations']:
                        print(f"  • {rel['disease_name']} → {rel['symptom_name']}")
                        print(f"    置信度: {rel.get('confidence', 'N/A')}")
                        print(f"    关系ID: {rel['id']}")
                
                # 显示疾病-药物关系
                if db_results['disease_medicine_relations']:
                    print(f"💉 疾病-药物关系 ({len(db_results['disease_medicine_relations'])}条):")
                    for rel in db_results['disease_medicine_relations']:
                        print(f"  • {rel['disease_name']} → {rel['medicine_name']}")
                        print(f"    置信度: {rel.get('confidence', 'N/A')}")
                
                # 更新全局统计
                global_stats['total_diseases'] += len(db_results['diseases'])
                global_stats['total_symptoms'] += len(db_results['symptoms'])
                global_stats['total_medicines'] += len(db_results['medicines'])
                global_stats['total_disease_symptom_relations'] += len(db_results['disease_symptom_relations'])
                global_stats['total_disease_medicine_relations'] += len(db_results['disease_medicine_relations'])
                
                all_results[db_name] = db_results
            else:
                print("⚪ 无糖尿病相关数据")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ 查询错误: {e}")
    
    # 全局汇总
    print(f"\n🌍 糖尿病图谱数据全局汇总")
    print("=" * 60)
    
    total_all = sum(global_stats.values())
    if total_all > 0:
        print(f"📊 数据统计:")
        print(f"  • 糖尿病疾病实体: {global_stats['total_diseases']}个")
        print(f"  • 相关症状实体: {global_stats['total_symptoms']}个")
        print(f"  • 相关药物实体: {global_stats['total_medicines']}个")
        print(f"  • 疾病-症状关系: {global_stats['total_disease_symptom_relations']}条")
        print(f"  • 疾病-药物关系: {global_stats['total_disease_medicine_relations']}条")
        print(f"  • 总计: {total_all}项数据")
        
        print(f"\n📈 数据分布:")
        for db_name, results in all_results.items():
            db_total = (len(results['diseases']) + len(results['symptoms']) + 
                       len(results['medicines']) + len(results['disease_symptom_relations']) +
                       len(results['disease_medicine_relations']))
            print(f"  • {db_name}: {db_total}项")
        
        print(f"\n✅ 糖尿病图谱数据查询完成！")
        
        if global_stats['total_disease_symptom_relations'] > 0:
            print(f"🔗 图谱中已建立 {global_stats['total_disease_symptom_relations']} 条糖尿病-症状关联")
        else:
            print(f"⚠️ 图谱中有糖尿病实体，但尚未建立症状关联")
            
    else:
        print("💭 在所有数据库中未发现糖尿病相关数据")
    
    # 保存报告
    report = {
        'query_time': datetime.now().isoformat(),
        'global_statistics': global_stats,
        'database_details': all_results
    }
    
    report_file = "/Users/louisliu/.cursor/memory-x/diabetes_final_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n📄 完整报告已保存: {report_file}")

if __name__ == "__main__":
    query_diabetes_data()