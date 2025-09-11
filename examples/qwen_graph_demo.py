#!/usr/bin/env python3
"""
Qwen3增强医疗知识图谱更新演示
Enhanced Medical Knowledge Graph Update Demo with Qwen3
支持所有记忆查询和直接问题输入分析
"""

import sys
import os
import sqlite3
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict

# 添加项目路径
sys.path.append('/Users/louisliu/.cursor/memory-x')

from src.core.medical_graph_manager import MedicalGraphManager
from src.core.qwen_update_engine import QwenGraphUpdateEngine
from src.core.memory_manager import SimpleMemoryManager, SimpleMemoryIntegratedAI
from src.storage.sqlite_store import SQLiteMemoryStore


class EnhancedQwenGraphDemo:
    """增强版Qwen图谱演示类，支持所有记忆查询和直接问题分析"""
    
    def __init__(self, api_key: str, db_path: str = None):
        self.api_key = api_key
        self.db_path = db_path or "/Users/louisliu/.cursor/memory-x/data/enhanced_qwen_demo.db"
        self.user_id = "liuyang_enhanced_demo"
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 初始化组件
        self.graph_manager = MedicalGraphManager(self.db_path)
        self.qwen_engine = QwenGraphUpdateEngine(self.graph_manager, api_key)
        self.memory_ai = SimpleMemoryIntegratedAI()
        self.memory_manager = self.memory_ai.get_memory_manager(self.user_id)
        
        # 初始化数据
        self._setup_demo_data()
    
    def _setup_demo_data(self):
        """设置演示数据（包括图谱和记忆数据）"""
        print("📊 设置演示数据...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建表结构
        self._create_tables(cursor)
        
        # 插入历史医疗记录
        self._insert_historical_medical_data(cursor)
        
        # 插入记忆数据
        self._insert_memory_data()
        
        conn.commit()
        conn.close()
        
        print("✅ 演示数据设置完成")
    
    def _create_tables(self, cursor):
        """创建数据库表"""
        # 疾病表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diseases (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                category VARCHAR(100),
                severity VARCHAR(20),
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 症状表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS symptoms (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                body_part VARCHAR(100),
                intensity VARCHAR(20),
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 药物表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                type VARCHAR(100),
                dosage VARCHAR(100),
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 疾病-症状关系表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disease_symptom_relations (
                id VARCHAR(50) PRIMARY KEY,
                disease_id VARCHAR(50) NOT NULL,
                symptom_id VARCHAR(50) NOT NULL,
                relation_type VARCHAR(20) DEFAULT 'CONSULT',
                source VARCHAR(50) NOT NULL,
                confidence DECIMAL(3,2) DEFAULT 0.50,
                context TEXT,
                user_id VARCHAR(50),
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 疾病-药物关系表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disease_medicine_relations (
                id VARCHAR(50) PRIMARY KEY,
                disease_id VARCHAR(50) NOT NULL,
                medicine_id VARCHAR(50) NOT NULL,
                relation_type VARCHAR(20) DEFAULT 'TREATMENT',
                effectiveness VARCHAR(20),
                source VARCHAR(50) NOT NULL,
                confidence DECIMAL(3,2) DEFAULT 0.50,
                context TEXT,
                user_id VARCHAR(50),
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def _insert_historical_medical_data(self, cursor):
        """插入历史医疗数据"""
        # 历史记录时间
        two_months_ago = datetime.now() - timedelta(days=60)
        one_week_ago = datetime.now() - timedelta(days=7)
        
        # 疾病实体
        diseases = [
            ("disease_cold_001", "感冒", "呼吸系统疾病", "mild", two_months_ago.isoformat()),
            ("disease_hypertension_001", "高血压", "心血管疾病", "moderate", one_week_ago.isoformat()),
        ]
        
        for disease in diseases:
            cursor.execute('''
                INSERT OR REPLACE INTO diseases 
                (id, name, category, severity, created_time, updated_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', disease + (disease[4],))
        
        # 症状实体
        symptoms = [
            ("symptom_dizzy_001", "头晕", "头部", "mild", two_months_ago.isoformat()),
            ("symptom_headache_001", "头痛", "头部", "moderate", one_week_ago.isoformat()),
            ("symptom_fever_001", "发热", "全身", "mild", two_months_ago.isoformat()),
        ]
        
        for symptom in symptoms:
            cursor.execute('''
                INSERT OR REPLACE INTO symptoms 
                (id, name, body_part, intensity, created_time, updated_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', symptom + (symptom[4],))
        
        # 药物实体
        medicines = [
            ("medicine_paracetamol_001", "对乙酯氨基酚", "解热镇痛", "500mg", two_months_ago.isoformat()),
            ("medicine_amlodipine_001", "氨氯地平", "降压药", "5mg", one_week_ago.isoformat()),
        ]
        
        for medicine in medicines:
            cursor.execute('''
                INSERT OR REPLACE INTO medicines 
                (id, name, type, dosage, created_time, updated_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', medicine + (medicine[4],))
        
        # 疾病-症状关系
        ds_relations = [
            ("rel_cold_dizzy_001", "disease_cold_001", "symptom_dizzy_001", "CONSULT", "online_consult", 0.8, "用户咁询头晕症状，医生诊断为感冒", self.user_id, two_months_ago.isoformat()),
            ("rel_cold_fever_001", "disease_cold_001", "symptom_fever_001", "CONSULT", "online_consult", 0.9, "感冒伴有发热症状", self.user_id, two_months_ago.isoformat()),
        ]
        
        for relation in ds_relations:
            cursor.execute('''
                INSERT OR REPLACE INTO disease_symptom_relations 
                (id, disease_id, symptom_id, relation_type, source, confidence, context, user_id, created_time, updated_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', relation + (relation[8],))
        
        # 疾病-药物关系
        dm_relations = [
            ("rel_cold_paracetamol_001", "disease_cold_001", "medicine_paracetamol_001", "TREATMENT", "effective", "prescription", 0.9, "感冒期间服用对乙酯氨基酚退热", self.user_id, two_months_ago.isoformat()),
        ]
        
        for relation in dm_relations:
            cursor.execute('''
                INSERT OR REPLACE INTO disease_medicine_relations 
                (id, disease_id, medicine_id, relation_type, effectiveness, source, confidence, context, user_id, created_time, updated_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', relation + (relation[8],))
    
    def _insert_memory_data(self):
        """插入记忆数据"""
        # 模拟历史对话记忆
        conversations = [
            {
                "message": "医生，我最近头晕，还有点发热",
                "response": "根据您的症状，初步判断可能是感冒。建议您多休息，多喝水。",
                "entities": {"SYMPTOM": [["头晕", 0, 2], ["发热", 0, 2]], "DISEASE": [["感冒", 0, 2]]},
                "intent": "medical_consultation",
                "importance": 4,
                "days_ago": 60
            },
            {
                "message": "吃了对乙酯氨基酚后热度下降了",
                "response": "很好，说明药物起作用了。请按时服药，注意休息。",
                "entities": {"MEDICINE": [["对乙酯氨基酚", 0, 6]], "SYMPTOM": [["热度下降", 0, 4]]},
                "intent": "treatment_feedback",
                "importance": 3,
                "days_ago": 58
            },
            {
                "message": "今天又开始头痛了，和之前的头晕不太一样",
                "response": "头痛和头晕是不同的症状。请描述一下头痛的具体情况。",
                "entities": {"SYMPTOM": [["头痛", 0, 2], ["头晕", 0, 2]]},
                "intent": "medical_consultation",
                "importance": 4,
                "days_ago": 1
            }
        ]
        
        for conv in conversations:
            # 计算时间
            timestamp = datetime.now() - timedelta(days=conv["days_ago"])
            conv_data = {
                "user_message": conv["message"],
                "ai_response": conv["response"],
                "timestamp": timestamp,
                "entities": conv["entities"],
                "intent": conv["intent"],
                "importance": conv["importance"]
            }
            
            # 添加到记忆管理器
            self.memory_manager.add_conversation(
                conv["message"],
                conv["response"],
                conv["entities"],
                conv["intent"],
                conv["importance"]
            )
    """设置演示数据"""
    print("📊 设置演示数据...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建表结构
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diseases (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            category VARCHAR(100),
            severity VARCHAR(20),
            created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS symptoms (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            body_part VARCHAR(100),
            intensity VARCHAR(20),
            created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS disease_symptom_relations (
            id VARCHAR(50) PRIMARY KEY,
            disease_id VARCHAR(50) NOT NULL,
            symptom_id VARCHAR(50) NOT NULL,
            relation_type VARCHAR(20) DEFAULT 'CONSULT',
            source VARCHAR(50) NOT NULL,
            confidence DECIMAL(3,2) DEFAULT 0.50,
            context TEXT,
            user_id VARCHAR(50),
            created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建历史记录（两个月前的感冒诊断）
    two_months_ago = datetime.now() - timedelta(days=60)
    
    # 插入疾病实体
    disease_id = "disease_cold_qwen_001"
    cursor.execute('''
        INSERT OR REPLACE INTO diseases 
        (id, name, category, severity, created_time, updated_time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (disease_id, "感冒", "呼吸系统疾病", "mild", 
          two_months_ago.isoformat(), two_months_ago.isoformat()))
    
    # 插入症状实体
    symptom_id = "symptom_dizzy_qwen_001"
    cursor.execute('''
        INSERT OR REPLACE INTO symptoms 
        (id, name, body_part, intensity, created_time, updated_time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (symptom_id, "头晕", "头部", "mild", 
          two_months_ago.isoformat(), two_months_ago.isoformat()))
    
    # 插入疾病-症状关系
    relation_id = "rel_cold_dizzy_qwen_001"
    cursor.execute('''
        INSERT OR REPLACE INTO disease_symptom_relations 
        (id, disease_id, symptom_id, source, confidence, context, user_id, created_time, updated_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (relation_id, disease_id, symptom_id, "online_consult", 0.8, 
          "用户咨询头晕症状，医生诊断为感冒", user_id, 
          two_months_ago.isoformat(), two_months_ago.isoformat()))
    
    conn.commit()
    conn.close()
    
    print(f"✅ 演示数据设置完成：{two_months_ago.strftime('%Y-%m-%d')} - 感冒诊断（头晕症状）")


def demonstrate_qwen_analysis():
    """演示Qwen3增强分析"""
    print("🤖 Qwen3增强医疗知识图谱更新演示")
    print("=" * 60)
    
    # 配置
    api_key = "sk-b70842d25c884aa9aa18955b00c24d37"
    db_path = "/Users/louisliu/.cursor/memory-x/data/qwen_demo.db"
    user_id = "liuyang_qwen_demo"
    
    # 确保数据目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        # 设置演示数据
        setup_demo_data(db_path, user_id)
        
        # 初始化组件
        print("\n🔧 初始化组件...")
        graph_manager = MedicalGraphManager(db_path)
        qwen_engine = QwenGraphUpdateEngine(graph_manager, api_key)
        
        # 测试场景
        print(f"\n📋 测试场景：两个月前感冒（头晕）→ 现在头疼")
        print("-" * 50)
        
        current_symptoms = ["头疼"]
        context = "患者柳阳，40岁，再次咨询头疼症状，两个月前曾因头晕诊断为感冒"
        
        print(f"当前症状：{', '.join(current_symptoms)}")
        print(f"上下文：{context}")
        
        # 基础规则分析
        print(f"\n🔧 基础规则分析...")
        base_decision = qwen_engine.analyze_update_scenario(
            current_symptoms=current_symptoms,
            user_id=user_id,
            context=context
        )
        
        print(f"基础分析结果：")
        print(f"  动作: {base_decision.action.value}")
        print(f"  置信度: {base_decision.confidence:.2f}")
        print(f"  原因: {base_decision.reasoning}")
        
        # Qwen3增强分析
        print(f"\n🤖 Qwen3增强分析...")
        ai_decision = qwen_engine.analyze_with_ai(
            current_symptoms=current_symptoms,
            user_id=user_id,
            context=context
        )
        
        print(f"\n🎯 Qwen3增强分析结果：")
        print(f"  推荐动作: {ai_decision.action.value}")
        print(f"  置信度: {ai_decision.confidence:.2f}")
        print(f"  分析原因: {ai_decision.reasoning}")
        
        if ai_decision.recommendations:
            print(f"\n💡 医疗建议：")
            for i, rec in enumerate(ai_decision.recommendations[:5], 1):
                print(f"  {i}. {rec}")
        
        if ai_decision.risk_factors:
            print(f"\n⚠️ 风险因素：")
            for i, risk in enumerate(ai_decision.risk_factors[:3], 1):
                print(f"  {i}. {risk}")
        
        # 对比分析
        print(f"\n📊 分析对比：")
        print(f"  基础规则置信度: {base_decision.confidence:.2f}")
        print(f"  AI增强置信度: {ai_decision.confidence:.2f}")
        print(f"  置信度提升: {ai_decision.confidence - base_decision.confidence:+.2f}")
        
        # 生成医疗报告
        print(f"\n📋 生成医疗分析报告...")
        report = qwen_engine.generate_medical_report(user_id, [ai_decision])
        
        print(f"\n📄 医疗分析报告：")
        print("-" * 40)
        print(report)
        
        print(f"\n🎉 Qwen3增强分析演示完成！")
        
    except Exception as e:
        print(f"❌ 演示过程发生错误: {e}")
        import traceback
        traceback.print_exc()


def test_multiple_scenarios():
    """测试多种场景"""
    print("\n🔬 测试多种医疗场景")
    print("=" * 40)
    
    api_key = "sk-b70842d25c884aa9aa18955b00c24d37"
    db_path = "/Users/louisliu/.cursor/memory-x/data/qwen_multi_demo.db"
    
    # 确保数据目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        graph_manager = MedicalGraphManager(db_path)
        qwen_engine = QwenGraphUpdateEngine(graph_manager, api_key)
        
        # 测试场景列表
        scenarios = [
            {
                "name": "急性疾病复发",
                "user_id": "test_user_1",
                "current_symptoms": ["发热", "咳嗽"],
                "context": "用户一周前感冒已愈，现在又出现发热咳嗽"
            },
            {
                "name": "慢性疾病进展",
                "user_id": "test_user_2", 
                "current_symptoms": ["多尿", "视力模糊"],
                "context": "糖尿病患者，最近血糖控制不佳，出现新症状"
            },
            {
                "name": "症状演变",
                "user_id": "test_user_3",
                "current_symptoms": ["胸痛"],
                "context": "患者从胸闷发展为胸痛，需要评估病情变化"
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n📋 场景 {i}: {scenario['name']}")
            print(f"症状: {', '.join(scenario['current_symptoms'])}")
            print(f"上下文: {scenario['context']}")
            
            try:
                decision = qwen_engine.analyze_with_ai(
                    current_symptoms=scenario['current_symptoms'],
                    user_id=scenario['user_id'],
                    context=scenario['context']
                )
                
                print(f"结果: {decision.action.value} (置信度: {decision.confidence:.2f})")
                print(f"原因: {decision.reasoning[:100]}...")
                
            except Exception as e:
                print(f"❌ 场景 {i} 分析失败: {e}")
        
        print(f"\n✅ 多场景测试完成")
        
    except Exception as e:
        print(f"❌ 多场景测试失败: {e}")


if __name__ == "__main__":
    print("🔄 此脚本已升级为增强版本")
    print("请使用以下命令运行增强版演示:")
    print("")
    print("1. 交互模式:")
    print("   python enhanced_qwen_graph_demo.py --interactive")
    print("")
    print("2. 直接分析问题:")
    print("   python enhanced_qwen_graph_demo.py --query '我现在头痛'")
    print("")
    print("3. 查询所有记忆:")
    print("   python enhanced_qwen_graph_demo.py --interactive")
    print("   然后输入: memories 头痛")
    print("")
    print("4. 完整分析流程:")
    print("   python enhanced_qwen_graph_demo.py --query '我头痛，之前有过头晕的情况'")
    print("")
    print("✨ 新功能包括:")
    print("  - 支持所有记忆查询(短期、长期、图谱关系)")
    print("  - 直接输入问题进行智能分析")
    print("  - 完整的图谱更新逻辑分析")
    print("  - 交互式命令界面")
    print("  - 详细的分析流程展示")
    
    # 为了兼容性，仍然运行原有演示
    print("\n" + "="*50)
    print("运行兼容性演示...")
    try:
        # 运行原有演示
        demonstrate_qwen_analysis()
        test_multiple_scenarios()
    except Exception as e:
        print(f"❌ 兼容性演示失败: {e}")
        print("请使用增强版脚本: enhanced_qwen_graph_demo.py")