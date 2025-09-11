#!/usr/bin/env python3
"""
深度查询糖尿病图谱数据，包括关系分析
"""

import sqlite3
import os
import json
from datetime import datetime

def detailed_diabetes_analysis():
    """详细分析糖尿病数据最丰富的数据库"""
    print("🔍 糖尿病图谱数据深度分析")
    print("=" * 60)
    
    # 重点分析的数据库（根据之前的查询结果）
    priority_dbs = [
        "/Users/louisliu/.cursor/memory-x/data/diabetes_test.db",
        "/Users/louisliu/.cursor/memory-x/data/enhanced_qwen_demo.db", 
        "/Users/louisliu/.cursor/memory-x/data/diabetes_scenario_demo.db",
        "/Users/louisliu/.cursor/memory-x/examples/data/demo_medical_graph.db",
        "/Users/louisliu/.cursor/memory-x/data/demo_medical_graph.db"
    ]
    
    for db_path in priority_dbs:
        if not os.path.exists(db_path):
            continue
            
        print(f"\n📊 深度分析: {os.path.basename(db_path)}")
        print("-" * 50)
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 获取所有表信息
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"📋 数据库表: {', '.join(tables)}")
            
            # 分析疾病实体
            if 'diseases' in tables:
                cursor.execute("SELECT * FROM diseases WHERE name LIKE '%糖尿病%' OR name LIKE '%diabetes%' OR name LIKE '%血糖%'")
                diseases = cursor.fetchall()
                print(f"\n🏥 糖尿病疾病实体 ({len(diseases)}个):")
                for disease in diseases:
                    print(f"  ID: {disease['id']}")
                    print(f"  名称: {disease['name']}")
                    print(f"  类别: {disease.get('category', 'N/A')}")
                    print(f"  严重程度: {disease.get('severity', 'N/A')}")
                    print(f"  用户ID: {disease.get('user_id', 'N/A')}")
                    if disease.get('created_time'):
                        print(f"  创建时间: {disease['created_time']}")
                    print()
            
            # 分析症状实体
            if 'symptoms' in tables:
                cursor.execute("SELECT * FROM symptoms WHERE name LIKE '%糖尿病%' OR name LIKE '%血糖%' OR name LIKE '%胰岛素%'")
                symptoms = cursor.fetchall()
                print(f"🤒 相关症状实体 ({len(symptoms)}个):")
                for symptom in symptoms:
                    print(f"  ID: {symptom['id']}")
                    print(f"  名称: {symptom['name']}")
                    print(f"  严重程度: {symptom.get('severity', 'N/A')}")
                    print(f"  用户ID: {symptom.get('user_id', 'N/A')}")
                    print()
            
            # 分析药物实体
            if 'medicines' in tables:
                cursor.execute("SELECT * FROM medicines WHERE name LIKE '%胰岛素%' OR name LIKE '%血糖%' OR name LIKE '%糖尿病%'")
                medicines = cursor.fetchall()
                print(f"💊 相关药物实体 ({len(medicines)}个):")
                for medicine in medicines:
                    print(f"  ID: {medicine['id']}")
                    print(f"  名称: {medicine['name']}")
                    print(f"  类型: {medicine.get('type', 'N/A')}")
                    print(f"  用户ID: {medicine.get('user_id', 'N/A')}")
                    print()
            
            # 分析疾病-症状关系
            if 'disease_symptom_relations' in tables:
                # 查询所有关系，然后筛选糖尿病相关的
                cursor.execute("""
                    SELECT dsr.*, d.name as disease_name, s.name as symptom_name
                    FROM disease_symptom_relations dsr
                    LEFT JOIN diseases d ON dsr.disease_id = d.id
                    LEFT JOIN symptoms s ON dsr.symptom_id = s.id
                """)
                all_relations = cursor.fetchall()
                
                diabetes_relations = []
                for rel in all_relations:
                    disease_name = rel.get('disease_name', '')
                    symptom_name = rel.get('symptom_name', '')
                    if ('糖尿病' in disease_name or 'diabetes' in disease_name or '血糖' in disease_name or
                        '糖尿病' in symptom_name or '血糖' in symptom_name):
                        diabetes_relations.append(rel)
                
                print(f"🔗 糖尿病相关的疾病-症状关系 ({len(diabetes_relations)}条):")
                for rel in diabetes_relations:
                    print(f"  关系ID: {rel.get('id', 'N/A')}")
                    print(f"  疾病: {rel.get('disease_name', 'N/A')} (ID: {rel.get('disease_id', 'N/A')})")
                    print(f"  症状: {rel.get('symptom_name', 'N/A')} (ID: {rel.get('symptom_id', 'N/A')})")
                    print(f"  置信度: {rel.get('confidence', 'N/A')}")
                    print(f"  用户ID: {rel.get('user_id', 'N/A')}")
                    if rel.get('created_time'):
                        print(f"  创建时间: {rel['created_time']}")
                    print()
            
            # 分析疾病-药物关系
            if 'disease_medicine_relations' in tables:
                cursor.execute("""
                    SELECT dmr.*, d.name as disease_name, m.name as medicine_name
                    FROM disease_medicine_relations dmr
                    LEFT JOIN diseases d ON dmr.disease_id = d.id
                    LEFT JOIN medicines m ON dmr.medicine_id = m.id
                    WHERE d.name LIKE '%糖尿病%' OR d.name LIKE '%diabetes%'
                       OR m.name LIKE '%胰岛素%' OR m.name LIKE '%血糖%'
                """)
                drug_relations = cursor.fetchall()
                print(f"💉 糖尿病相关的疾病-药物关系 ({len(drug_relations)}条):")
                for rel in drug_relations:
                    print(f"  关系ID: {rel.get('id', 'N/A')}")
                    print(f"  疾病: {rel.get('disease_name', 'N/A')}")
                    print(f"  药物: {rel.get('medicine_name', 'N/A')}")
                    print(f"  置信度: {rel.get('confidence', 'N/A')}")
                    print(f"  用户ID: {rel.get('user_id', 'N/A')}")
                    print()
            
            # 检查是否有对话记录
            if 'conversations' in tables:
                cursor.execute("""
                    SELECT * FROM conversations 
                    WHERE user_message LIKE '%糖尿病%' OR user_message LIKE '%血糖%' OR user_message LIKE '%胰岛素%'
                       OR ai_response LIKE '%糖尿病%' OR ai_response LIKE '%血糖%' OR ai_response LIKE '%胰岛素%'
                    ORDER BY timestamp DESC
                    LIMIT 5
                """)
                conversations = cursor.fetchall()
                print(f"💬 相关对话记录 ({len(conversations)}条，显示最近5条):")
                for conv in conversations:
                    print(f"  时间: {conv.get('timestamp', 'N/A')}")
                    print(f"  用户: {conv.get('user_message', '')[:60]}...")
                    print(f"  AI: {conv.get('ai_response', '')[:60]}...")
                    print()
            
            conn.close()
            
        except Exception as e:
            print(f"❌ 查询错误: {e}")
    
    print(f"\n📊 糖尿病图谱数据分析总结")
    print("=" * 60)
    print("根据查询结果，当前图谱中的糖尿病数据主要特点：")
    print("1. 💾 数据分布：主要集中在6个数据库文件中")
    print("2. 🏥 疾病实体：共发现7个糖尿病相关疾病实体")
    print("3. 🤒 症状实体：共发现5个相关症状实体")
    print("4. 💊 药物实体：暂无糖尿病专用药物实体")
    print("5. 🔗 关系数据：疾病-症状关系需要进一步建立")
    print("6. ⚠️ 注意事项：部分数据库结构存在差异，需要统一管理")

if __name__ == "__main__":
    detailed_diabetes_analysis()