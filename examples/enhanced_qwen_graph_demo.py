#!/usr/bin/env python3
"""
增强版Qwen图谱演示脚本
Enhanced Qwen Graph Demo Script
支持所有记忆查询和直接问题输入分析
"""

import os
import sys
import os
import sqlite3
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# 添加项目路径
sys.path.append('/Users/louisliu/.cursor/memory-x')

from src.core.medical_graph_manager import MedicalGraphManager
from src.core.qwen_graph_update_engine import QwenGraphUpdateEngine
from src.core.memory_manager import SimpleMemoryManager, SimpleMemoryIntegratedAI


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
        self._insert_historical_data(cursor)
        
        # 插入记忆数据
        self._insert_memory_data()
        
        conn.commit()
        conn.close()
        
        print("✅ 演示数据设置完成")
    
    def _create_tables(self, cursor):
        """创建数据库表"""
        tables = [
            '''CREATE TABLE IF NOT EXISTS diseases (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                category VARCHAR(100),
                severity VARCHAR(20),
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS symptoms (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                body_part VARCHAR(100),
                intensity VARCHAR(20),
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS medicines (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                drug_class VARCHAR(100),
                strength VARCHAR(50),
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS disease_symptom_relations (
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
            )''',
            '''CREATE TABLE IF NOT EXISTS disease_medicine_relations (
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
            )'''
        ]
        
        for table in tables:
            cursor.execute(table)
    
    def _insert_historical_data(self, cursor):
        """插入历史医疗数据"""
        two_months_ago = datetime.now() - timedelta(days=60)
        one_week_ago = datetime.now() - timedelta(days=7)
        
        # 疾病实体
        diseases = [
            ("disease_cold_001", "感冒", "呼吸系统疾病", "mild", two_months_ago.isoformat()),
            ("disease_hypertension_001", "高血压", "心血管疾病", "moderate", one_week_ago.isoformat()),
            # 添加糖尿病实体供测试更新逻辑
            (f"disease_diabetes_{self.user_id}", "糖尿病", "内分泌系统疾病", "potential", two_months_ago.isoformat()),
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
                (id, name, drug_class, strength, created_time, updated_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', medicine + (medicine[4],))
        
        # 疾病-症状关系
        ds_relations = [
            ("rel_cold_dizzy_001", "disease_cold_001", "symptom_dizzy_001", "CONSULT", "online_consult", 0.8, 
             "用户咨询头晕症状，医生诊断为感冒", self.user_id, two_months_ago.isoformat()),
            ("rel_cold_fever_001", "disease_cold_001", "symptom_fever_001", "CONSULT", "online_consult", 0.9, 
             "感冒伴有发热症状", self.user_id, two_months_ago.isoformat()),
        ]
        
        for relation in ds_relations:
            cursor.execute('''
                INSERT OR REPLACE INTO disease_symptom_relations 
                (id, disease_id, symptom_id, relation_type, source, confidence, context, user_id, created_time, updated_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', relation + (relation[8],))
    
    def _insert_memory_data(self):
        """插入记忆数据"""
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
            self.memory_manager.add_conversation(
                conv["message"],
                conv["response"],
                conv["entities"],
                conv["intent"],
                conv["importance"]
            )
    
    def query_all_memories(self, query: str = None, limit: int = 10) -> Dict[str, Any]:
        """查询所有记忆数据"""
        print(f"🔍 查询所有记忆数据...")
        
        results = {
            "short_term_memories": [],
            "long_term_memories": [],
            "graph_relations": {
                "disease_symptom": [],
                "disease_medicine": [],
                "symptoms": [],
                "diseases": [],
                "medicines": []
            },
            "memory_stats": {},
            "query_summary": {
                "total_memories": 0,
                "relevant_memories": 0,
                "query_used": query or "所有记忆"
            }
        }
        
        # 查询短期记忆
        short_term_data = list(self.memory_manager.short_term_memory)
        results["short_term_memories"] = [
            {
                "content": item.get("user_message", str(item)),
                "response": item.get("ai_response", ""),
                "timestamp": item.get("timestamp", datetime.now()).isoformat() if hasattr(item.get("timestamp", datetime.now()), 'isoformat') else str(item.get("timestamp", "")),
                "entities": item.get("entities", {}),
                "intent": item.get("intent", ""),
                "importance": item.get("importance", 1)
            } for item in short_term_data
        ]
        
        # 查询长期记忆
        if query:
            long_term_results = self.memory_manager.retrieve_memories(query, limit)
        else:
            long_term_results = self.memory_manager.store.search_memories(self.user_id, "", limit * 2)
        
        results["long_term_memories"] = long_term_results
        
        # 查询图谱关系
        results["graph_relations"]["disease_symptom"] = self.graph_manager.get_disease_symptom_relations(user_id=self.user_id)
        results["graph_relations"]["disease_medicine"] = self.graph_manager.get_disease_medicine_relations(user_id=self.user_id)
        
        # 查询实体数据
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for entity_type in ["diseases", "symptoms", "medicines"]:
            cursor.execute(f"SELECT * FROM {entity_type} ORDER BY created_time DESC LIMIT ?", (limit,))
            results["graph_relations"][entity_type] = [
                dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()
            ]
        
        conn.close()
        
        # 记忆统计
        results["memory_stats"] = self.memory_manager.get_memory_stats()
        
        # 查询统计
        results["query_summary"]["total_memories"] = len(results["short_term_memories"]) + len(results["long_term_memories"])
        if query:
            results["query_summary"]["relevant_memories"] = len([m for m in results["long_term_memories"] if m.get("score", 0) > 0.5])
        else:
            results["query_summary"]["relevant_memories"] = results["query_summary"]["total_memories"]
        
        return results
    
    def analyze_query_with_graph_update(self, query: str, context: str = "") -> Dict[str, Any]:
        """分析问题并输出图谱更新逻辑"""
        print(f"🤖 分析问题: {query}")
        print("=" * 60)
        
        analysis_result = {
            "query": query,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "extracted_info": {
                "symptoms": [],
                "diseases": [],
                "medicines": []
            },
            "memory_retrieval": {},
            "graph_analysis": {},
            "qwen_decision": {},
            "update_recommendations": [],
            "analysis_flow": []
        }
        
        # 步骤1: 信息提取
        analysis_result["analysis_flow"].append("步骤1: 从问题中提取医疗信息")
        extracted_symptoms = self._extract_symptoms_from_query(query)
        analysis_result["extracted_info"]["symptoms"] = extracted_symptoms
        
        print(f"🔍 提取信息:")
        print(f"  症状: {extracted_symptoms}")
        
        # 步骤2: 记忆检索
        analysis_result["analysis_flow"].append("步骤2: 检索相关记忆")
        memory_results = self.query_all_memories(query, limit=5)
        analysis_result["memory_retrieval"] = memory_results
        
        print(f"\n📚 记忆检索结果:")
        print(f"  短期记忆: {len(memory_results['short_term_memories'])}条")
        print(f"  长期记忆: {len(memory_results['long_term_memories'])}条")
        print(f"  图谱关系: {len(memory_results['graph_relations']['disease_symptom'])}条")
        
        # 显示详细的记忆内容
        if memory_results['short_term_memories']:
            print(f"\n  🔍 短期记忆详情:")
            for i, mem in enumerate(memory_results['short_term_memories'], 1):
                print(f"    {i}. {mem['content'][:50]}...")
                print(f"       回复: {mem['response'][:50]}...")
                print(f"       时间: {mem['timestamp']}")
                if mem.get('entities'):
                    print(f"       实体: {mem['entities']}")
        
        if memory_results['long_term_memories']:
            print(f"\n  🔍 长期记忆详情:")
            for i, mem in enumerate(memory_results['long_term_memories'], 1):
                print(f"    {i}. {mem.get('content', str(mem))[:50]}...")
        
        if memory_results['graph_relations']['disease_symptom']:
            print(f"\n  🔍 图谱关系详情:")
            for i, rel in enumerate(memory_results['graph_relations']['disease_symptom'], 1):
                print(f"    {i}. {rel['disease_name']} → {rel['symptom_name']}")
                print(f"       置信度: {rel['confidence']}, 来源: {rel['source']}")
                print(f"       创建时间: {rel['created_time']}")
                if rel.get('context'):
                    print(f"       上下文: {rel['context'][:50]}...")
        
        # 步骤3: Qwen AI分析
        analysis_result["analysis_flow"].append("步骤3: Qwen AI智能分析")
        if extracted_symptoms:
            qwen_decision = self.qwen_engine.analyze_update_scenario(
                current_symptoms=extracted_symptoms,
                user_id=self.user_id,
                context=f"{context}\n用户问题: {query}"
            )
            analysis_result["qwen_decision"] = {
                "action": qwen_decision.action.value,
                "confidence": qwen_decision.confidence,
                "reasoning": qwen_decision.reasoning,
                "recommendations": qwen_decision.recommendations,
                "risk_factors": qwen_decision.risk_factors,
                "medical_advice": qwen_decision.medical_advice,
                "diabetes_risk_assessment": qwen_decision.diabetes_risk_assessment
            }
            
            print(f"\n🤖 Qwen AI分析:")
            print(f"  推荐动作: {qwen_decision.action.value}")
            print(f"  置信度: {qwen_decision.confidence:.2f}")
            print(f"  分析理由: {qwen_decision.reasoning[:100]}...")
            
            if qwen_decision.diabetes_risk_assessment:
                print(f"  糖尿病风险评估: {qwen_decision.diabetes_risk_assessment}")
            
            # 如果是糖尿病关系创建，执行实际的图谱更新
            if qwen_decision.action.value == "create_diabetes_relation":
                print(f"\n🌱 执行糖尿病关系创建...")
                execution_result = self.qwen_engine.execute_diabetes_relation_creation(
                    symptoms=extracted_symptoms,
                    user_id=self.user_id,
                    diabetes_risk_assessment=qwen_decision.diabetes_risk_assessment or "高风险"
                )
                
                if execution_result["success"]:
                    total_operations = (len(execution_result.get('created_entities', [])) + 
                                      len(execution_result.get('updated_entities', [])) + 
                                      len(execution_result.get('created_relations', [])) + 
                                      len(execution_result.get('updated_relations', [])))
                    print(f"  ✅ 成功完成 {total_operations} 个操作")
                    
                    # 显示创建的实体
                    for entity in execution_result.get("created_entities", []):
                        print(f"    ➕ 创建{entity['type']}: {entity['name']}")
                    
                    # 显示更新的实体
                    for entity in execution_result.get("updated_entities", []):
                        print(f"    🔄 更新{entity['type']}: {entity['name']}")
                    
                    # 显示创建的关系
                    for relation in execution_result.get("created_relations", []):
                        print(f"    ➕ 创建关系: {relation['disease']} → {relation['symptom']} (置信度: {relation['confidence']})")
                    
                    # 显示更新的关系
                    for relation in execution_result.get("updated_relations", []):
                        print(f"    🔄 更新关系: {relation['disease']} → {relation['symptom']} (置信度: {relation['confidence']})")
                else:
                    print(f"  ❌ 操作失败: {execution_result['errors']}")
        
        # 步骤4: 生成更新建议
        analysis_result["analysis_flow"].append("步骤4: 生成图谱更新建议")
        update_recommendations = self._generate_update_recommendations(analysis_result)
        analysis_result["update_recommendations"] = update_recommendations
        
        print(f"\n📝 更新建议:")
        for i, rec in enumerate(update_recommendations, 1):
            print(f"  {i}. {rec['type']}: {rec['description']}")
        
        return analysis_result
    
    def _extract_symptoms_from_query(self, query: str) -> List[str]:
        """从问题中提取症状"""
        # 扩展症状关键词，特别加强糖尿病相关症状
        symptom_keywords = {
            # 神经系统症状
            "头痛": ["头痛", "头疼"],
            "头晕": ["头晕", "眩晕", "头昏"],
            "乏力": ["乏力", "疲劳", "无力", "没力气"],
            
            # 糖尿病经典症状（三多一少）
            "多尿": ["多尿", "尿多", "小便多", "尿频"],
            "多饮": ["多饮", "口渴", "想喝水", "总是渴"],
            "多食": ["多食", "饿得快", "总是饿", "食量大"],
            "体重下降": ["体重下降", "消瘦", "瘦了", "体重减轻"],
            
            # 糖尿病早期症状
            "视力模糊": ["视力模糊", "眼花", "看不清", "视力下降"],
            "皮肤瘙痒": ["皮肤瘙痒", "皮肤痒", "身上痒"],
            "伤口愈合慢": ["伤口愈合慢", "伤口不愈合", "切口感染"],
            
            # 其他常见症状
            "发热": ["发热", "发烧", "体温高"],
            "咳嗽": ["咳嗽", "咳"],
            "胸痛": ["胸痛", "胸疼", "胸闷"],
            "腹痛": ["腹痛", "肚子疼", "胃痛"],
            "腹泻": ["腹泻", "拉肚子"],
            "便秘": ["便秘", "大便困难"],
            "失眠": ["失眠", "睡不着", "睡眠不好"],
            "焦虑": ["焦虑", "紧张", "心慌"]
        }
        
        found_symptoms = []
        query_lower = query.lower()
        
        for symptom_name, keywords in symptom_keywords.items():
            for keyword in keywords:
                if keyword in query_lower or keyword in query:
                    found_symptoms.append(symptom_name)
                    break  # 避免重复添加
        
        return list(set(found_symptoms))  # 去重
    
    def _generate_update_recommendations(self, analysis_result: Dict) -> List[Dict]:
        """生成更新建议"""
        recommendations = []
        
        # 基于Qwen分析结果
        qwen_decision = analysis_result.get("qwen_decision", {})
        if qwen_decision:
            action = qwen_decision.get("action")
            if action == "create_new":
                recommendations.append({
                    "type": "创建新关系",
                    "description": "建议创建新的疾病-症状关系，不要与历史记录关联",
                    "confidence": qwen_decision.get("confidence", 0.5),
                    "reasoning": qwen_decision.get("reasoning", "")
                })
            elif action == "update_existing":
                recommendations.append({
                    "type": "更新现有关系",
                    "description": "建议更新现有的医疗关系，可能是疾病进展或相关症状",
                    "confidence": qwen_decision.get("confidence", 0.5),
                    "reasoning": qwen_decision.get("reasoning", "")
                })
            elif action == "create_diabetes_relation":
                recommendations.append({
                    "type": "创建糖尿病关系",
                    "description": f"已根据糖尿病风险评估创建相关医疗关系，包括症状与糖尿病风险的关联",
                    "confidence": qwen_decision.get("confidence", 0.9),
                    "reasoning": qwen_decision.get("reasoning", ""),
                    "diabetes_assessment": qwen_decision.get("diabetes_risk_assessment", "")
                })
        
        # 如果没有Qwen分析结果，提供默认建议
        if not recommendations:
            recommendations.append({
                "type": "基础分析",
                "description": "建议进行进一步的医疗评估和记录",
                "confidence": 0.6,
                "reasoning": "系统分析结果不完整，需要人工审核"
            })
        
        return recommendations
        
    def extract_current_memories(self) -> Dict[str, Any]:
        """直接提取目前所有记忆数据，包括用户个人信息"""
        print(f"📊 提取目前所有记忆数据...")
        
        extracted_memories = {
            "user_profile": {
                "name": "柳阳",
                "age": 40,
                "allergies": ["青霉素过敏"],
                "family_history": ["糖尿病遗传病史"],
                "user_id": self.user_id
            },
            "memory_snapshot": {
                "extraction_time": datetime.now().isoformat(),
                "short_term_memories": [],
                "long_term_memories": [],
                "working_memory": {},
                "graph_entities": {
                    "diseases": [],
                    "symptoms": [],
                    "medicines": []
                },
                "graph_relations": {
                    "disease_symptom": [],
                    "disease_medicine": []
                }
            },
            "memory_analysis": {
                "total_memories": 0,
                "memory_distribution": {},
                "key_medical_events": [],
                "recent_symptoms": [],
                "medication_history": [],
                "risk_factors": []
            },
            "summary": {
                "patient_status": "",
                "key_concerns": [],
                "recommendations": []
            }
        }
        
        # 1. 提取短期记忆
        short_term_data = list(self.memory_manager.short_term_memory)
        extracted_memories["memory_snapshot"]["short_term_memories"] = [
            {
                "content": item.get("user_message", str(item)),
                "response": item.get("ai_response", ""),
                "timestamp": item.get("timestamp", datetime.now()).isoformat() if hasattr(item.get("timestamp", datetime.now()), 'isoformat') else str(item.get("timestamp", "")),
                "entities": item.get("entities", {}),
                "intent": item.get("intent", ""),
                "importance": item.get("importance", 1)
            } for item in short_term_data
        ]
        
        # 2. 提取长期记忆
        try:
            long_term_results = self.memory_manager.store.search_memories(self.user_id, "", 50)  # 获取最多50条
            extracted_memories["memory_snapshot"]["long_term_memories"] = long_term_results
        except Exception as e:
            print(f"⚠️ 长期记忆提取失败: {e}")
            extracted_memories["memory_snapshot"]["long_term_memories"] = []
        
        # 3. 提取工作记忆（转换set为list以支持JSON序列化）
        working_memory_dict = {}
        for key, value in self.memory_manager.working_memory.items():
            if isinstance(value, set):
                working_memory_dict[key] = list(value)
            else:
                working_memory_dict[key] = value
        extracted_memories["memory_snapshot"]["working_memory"] = working_memory_dict
        
        # 4. 提取图谱实体和关系
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 提取疑病实体
            cursor.execute("SELECT * FROM diseases ORDER BY created_time DESC")
            diseases = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            extracted_memories["memory_snapshot"]["graph_entities"]["diseases"] = diseases
            
            # 提取症状实体
            cursor.execute("SELECT * FROM symptoms ORDER BY created_time DESC")
            symptoms = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            extracted_memories["memory_snapshot"]["graph_entities"]["symptoms"] = symptoms
            
            # 提取药物实体
            cursor.execute("SELECT * FROM medicines ORDER BY created_time DESC")
            medicines = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            extracted_memories["memory_snapshot"]["graph_entities"]["medicines"] = medicines
            
            # 提取病症关系
            extracted_memories["memory_snapshot"]["graph_relations"]["disease_symptom"] = self.graph_manager.get_disease_symptom_relations(user_id=self.user_id)
            
            # 提取病药关系
            extracted_memories["memory_snapshot"]["graph_relations"]["disease_medicine"] = self.graph_manager.get_disease_medicine_relations(user_id=self.user_id)
            
        except Exception as e:
            print(f"⚠️ 图谱数据提取失败: {e}")
        finally:
            conn.close()
        
        # 5. 分析记忆数据
        extracted_memories["memory_analysis"] = self._analyze_extracted_memories(extracted_memories["memory_snapshot"])
        
        # 6. 生成总结
        extracted_memories["summary"] = self._generate_memory_summary(extracted_memories["memory_snapshot"], extracted_memories["memory_analysis"])
        
        return extracted_memories
    
    def _analyze_extracted_memories(self, memory_snapshot: Dict) -> Dict:
        """分析提取的记忆数据"""
        analysis = {
            "total_memories": 0,
            "memory_distribution": {
                "short_term": len(memory_snapshot["short_term_memories"]),
                "long_term": len(memory_snapshot["long_term_memories"]),
                "diseases": len(memory_snapshot["graph_entities"]["diseases"]),
                "symptoms": len(memory_snapshot["graph_entities"]["symptoms"]),
                "medicines": len(memory_snapshot["graph_entities"]["medicines"]),
                "disease_symptom_relations": len(memory_snapshot["graph_relations"]["disease_symptom"]),
                "disease_medicine_relations": len(memory_snapshot["graph_relations"]["disease_medicine"])
            },
            "key_medical_events": [],
            "recent_symptoms": [],
            "medication_history": [],
            "risk_factors": []
        }
        
        # 计算总记忆数
        analysis["total_memories"] = (
            analysis["memory_distribution"]["short_term"] + 
            analysis["memory_distribution"]["long_term"] +
            analysis["memory_distribution"]["diseases"] +
            analysis["memory_distribution"]["symptoms"] +
            analysis["memory_distribution"]["medicines"]
        )
        
        # 提取关键医疗事件
        for memory in memory_snapshot["short_term_memories"] + memory_snapshot["long_term_memories"]:
            if memory.get("intent") == "medical_consultation":
                analysis["key_medical_events"].append({
                    "content": memory["content"],
                    "timestamp": memory["timestamp"],
                    "entities": memory.get("entities", {})
                })
        
        # 提取最近症状
        for symptom in memory_snapshot["graph_entities"]["symptoms"]:
            try:
                created_time = datetime.fromisoformat(symptom["created_time"])
                days_ago = (datetime.now() - created_time).days
                if days_ago <= 30:  # 最近30天的症状
                    analysis["recent_symptoms"].append({
                        "name": symptom["name"],
                        "body_part": symptom.get("body_part", ""),
                        "intensity": symptom.get("intensity", ""),
                        "days_ago": days_ago
                    })
            except:
                pass
        
        # 提取用药历史
        for medicine in memory_snapshot["graph_entities"]["medicines"]:
            analysis["medication_history"].append({
                "name": medicine["name"],
                "drug_class": medicine.get("drug_class", ""),
                "strength": medicine.get("strength", "")
            })
        
        # 根据用户信息识别风険因素
        analysis["risk_factors"] = [
            "青霉素过敏 - 需要避免使用青霉素类抗生素",
            "糖尿病家族史 - 需要定期监测血糖水平",
            "40岁中年 - 需要关注心血管和代谢疾病风険"
        ]
        
        return analysis
    
    def _generate_memory_summary(self, memory_snapshot: Dict, analysis: Dict) -> Dict:
        """生成记忆总结"""
        summary = {
            "patient_status": "",
            "key_concerns": [],
            "recommendations": []
        }
        
        # 生成患者状态描述
        recent_symptoms_count = len(analysis["recent_symptoms"])
        total_relations = len(memory_snapshot["graph_relations"]["disease_symptom"])
        
        if recent_symptoms_count > 0:
            summary["patient_status"] = f"柳阳（40岁）近期有{recent_symptoms_count}个症状记录，共{total_relations}条病症关系。"
        else:
            summary["patient_status"] = f"柳阳（40岁）目前无最近症状记录，共{total_relations}条历史病症关系。"
        
        # 识别关键关注点
        if analysis["recent_symptoms"]:
            symptom_names = [s["name"] for s in analysis["recent_symptoms"]]
            summary["key_concerns"].append(f"最近症状: {', '.join(symptom_names)}")
        
        if analysis["medication_history"]:
            medicine_names = [m["name"] for m in analysis["medication_history"]]
            summary["key_concerns"].append(f"用药历史: {', '.join(medicine_names)}")
        
        # 生成建议
        summary["recommendations"] = [
            "定期监测血糖水平（家族糖尿病史）",
            "避免使用青霉素类药物（过敏史）",
            "保持记忆系统更新，定期备份医疗数据"
        ]
        
        if recent_symptoms_count > 2:
            summary["recommendations"].append("建议就近症状进行专业医疗评估")
        
        return summary
    
    def display_extracted_memories(self, extracted_memories: Dict):
        """显示提取的记忆数据"""
        print(f"\n📄 记忆提取报告")
        print("=" * 60)
        
        # 用户信息
        user_profile = extracted_memories["user_profile"]
        print(f"👤 患者信息:")
        print(f"  姓名: {user_profile['name']}")
        print(f"  年龄: {user_profile['age']}岁")
        print(f"  过敏史: {', '.join(user_profile['allergies'])}")
        print(f"  家族史: {', '.join(user_profile['family_history'])}")
        
        # 记忆统计
        analysis = extracted_memories["memory_analysis"]
        print(f"\n📊 记忆统计:")
        print(f"  总记忆数: {analysis['total_memories']}条")
        print(f"  短期记忆: {analysis['memory_distribution']['short_term']}条")
        print(f"  长期记忆: {analysis['memory_distribution']['long_term']}条")
        print(f"  病症关系: {analysis['memory_distribution']['disease_symptom_relations']}条")
        print(f"  病药关系: {analysis['memory_distribution']['disease_medicine_relations']}条")
        
        # 最近症状
        if analysis["recent_symptoms"]:
            print(f"\n⚠️ 最近症状 (近30天):")
            for symptom in analysis["recent_symptoms"]:
                print(f"  - {symptom['name']} ({symptom['body_part']}, {symptom['days_ago']}天前)")
        
        # 用药历史
        if analysis["medication_history"]:
            print(f"\n💊 用药历史:")
            for medicine in analysis["medication_history"]:
                print(f"  - {medicine['name']} ({medicine['drug_class']}, {medicine['strength']})")
        
        # 风険因素
        print(f"\n⚠️ 风険因素:")
        for risk in analysis["risk_factors"]:
            print(f"  - {risk}")
        
        # 总结和建议
        summary = extracted_memories["summary"]
        print(f"\n📝 患者状态:")
        print(f"  {summary['patient_status']}")
        
        if summary["key_concerns"]:
            print(f"\n🔴 关键关注点:")
            for concern in summary["key_concerns"]:
                print(f"  - {concern}")
        
        print(f"\n📝 建议:")
        for recommendation in summary["recommendations"]:
            print(f"  - {recommendation}")
        
        print(f"\n📅 提取时间: {extracted_memories['memory_snapshot']['extraction_time']}")
    
    def run_interactive_demo(self):
        """运行交互式演示"""
        print("🚀 增强版Qwen图谱演示系统启动")
        print("=" * 60)
        print("支持的命令:")
        print("  1. query [问题] - 分析问题并输出图谱更新逻辑")
        print("  2. memories [查询词] - 查询所有记忆")
        print("  3. extract - 直接提取目前所有记忆数据")
        print("  4. stats - 显示系统统计")
        print("  5. clear_diabetes - 删除短期记忆中关于糖尿病的全部内容")
        print("  6. clear_graph_diabetes - 删除图谱中关于糖尿病的全部数据")
        print("  7. preview_diabetes - 预览图谱中的糖尿病相关数据")
        print("  8. exit - 退出系统")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n请输入命令: ").strip()
                
                if user_input.lower() in ['exit', 'quit', '退出']:
                    print("👋 再见！")
                    break
                
                elif user_input.startswith('query '):
                    query = user_input[6:].strip()
                    if query:
                        result = self.analyze_query_with_graph_update(query)
                        print(f"\n✅ 分析完成，共{len(result['analysis_flow'])}个步骤")
                    else:
                        print("❌ 请提供要分析的问题")
                
                elif user_input.startswith('memories'):
                    search_term = user_input[8:].strip() if len(user_input) > 8 else None
                    result = self.query_all_memories(search_term)
                    print(f"\n📊 记忆查询结果:")
                    print(f"  总计: {result['query_summary']['total_memories']}条记忆")
                    print(f"  相关: {result['query_summary']['relevant_memories']}条记忆")
                
                elif user_input.lower() == 'extract':
                    print(f"\n📊 开始提取目前所有记忆数据...")
                    extracted_memories = self.extract_current_memories()
                    self.display_extracted_memories(extracted_memories)
                    
                    # 询问是否保存到文件
                    save_choice = input("\n💾 是否保存记忆数据到文件? (y/n): ").strip().lower()
                    if save_choice in ['y', 'yes', '是']:
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"memory_extract_{timestamp}.json"
                        filepath = os.path.join(os.path.dirname(self.db_path), filename)
                        
                        try:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                json.dump(extracted_memories, f, ensure_ascii=False, indent=2)
                            print(f"✅ 记忆数据已保存到: {filepath}")
                        except Exception as e:
                            print(f"❌ 保存失败: {e}")
                
                elif user_input.lower() == 'stats':
                    stats = self.memory_manager.get_memory_stats()
                    print(f"\n📈 系统统计:")
                    print(f"  用户ID: {stats['user_id']}")
                    print(f"  短期记忆: {stats['short_term_count']}条")
                    print(f"  长期记忆: {stats['total_long_term']}条")
                    print(f"  工作记忆: {stats['working_memory_size']}项")
                
                elif user_input.lower() == 'clear_diabetes':
                    print(f"\n🧡 删除短期记忆中关于糖尿病的全部内容...")
                    
                    # 先显示删除前的统计
                    before_stats = self.memory_manager.get_memory_stats()
                    print(f"  删除前: 短期记忆 {before_stats['short_term_count']}条, 工作记忆 {before_stats['working_memory_size']}项")
                    
                    # 执行删除
                    removal_result = self.memory_manager.remove_diabetes_related_memories()
                    
                    # 显示结果
                    print(f"  ✅ 删除完成:")
                    print(f"    - 删除短期记忆: {removal_result['removed_short_term']}条")
                    print(f"    - 删除工作记忆键: {removal_result['removed_working_keys']}个")
                    print(f"    - 剩余短期记忆: {removal_result['remaining_short_term']}条")
                    print(f"    - 剩余工作记忆: {removal_result['remaining_working_memory']}项")
                    
                    if removal_result['removed_short_term'] > 0 or removal_result['removed_working_keys'] > 0:
                        print(f"  🎉 成功清理糖尿病相关记忆！")
                    else:
                        print(f"  💭 未找到糖尿病相关记忆")
                
                elif user_input.lower() == 'clear_graph_diabetes':
                    print(f"\n🗂️ 删除图谱中关于糖尿病的全部数据...")
                    
                    # 先预览要删除的数据
                    diabetes_data = self.graph_manager.get_diabetes_related_data(user_id=self.user_id)
                    total_items = (len(diabetes_data['diseases']) + 
                                  len(diabetes_data['symptoms']) + 
                                  len(diabetes_data['medicines']) +
                                  len(diabetes_data['disease_symptom_relations']) +
                                  len(diabetes_data['disease_medicine_relations']))
                    
                    print(f"  📊 预览要删除的数据:")
                    print(f"    - 疾病实体: {len(diabetes_data['diseases'])}个")
                    print(f"    - 症状实体: {len(diabetes_data['symptoms'])}个")
                    print(f"    - 药物实体: {len(diabetes_data['medicines'])}个")
                    print(f"    - 疾病-症状关系: {len(diabetes_data['disease_symptom_relations'])}条")
                    print(f"    - 疾病-药物关系: {len(diabetes_data['disease_medicine_relations'])}条")
                    print(f"    总计: {total_items}项")
                    
                    if total_items > 0:
                        # 确认删除
                        confirm = input(f"\n⚠️ 确认删除这些糖尿病相关数据吗? (y/n): ").strip().lower()
                        if confirm in ['y', 'yes', '是']:
                            # 执行删除
                            removal_result = self.graph_manager.remove_diabetes_related_graph_data(user_id=self.user_id)
                            
                            if removal_result['success']:
                                print(f"  ✅ 图谱数据删除完成:")
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
                                print(f"  🎉 成功删除 {total_removed} 项糖尿病相关数据！")
                            else:
                                print(f"  ❌ 删除失败: {removal_result['errors']}")
                        else:
                            print(f"  ⏹️ 取消删除操作")
                    else:
                        print(f"  💭 未找到糖尿病相关的图谱数据")
                
                elif user_input.lower() == 'preview_diabetes':
                    print(f"\n🔍 预览图谱中的糖尿病相关数据...")
                    
                    diabetes_data = self.graph_manager.get_diabetes_related_data(user_id=self.user_id)
                    
                    print(f"\n📋 糖尿病相关疾病实体 ({len(diabetes_data['diseases'])}个):")
                    for disease in diabetes_data['diseases']:
                        print(f"  - {disease['name']} (ID: {disease['id']})")
                    
                    print(f"\n📋 糖尿病相关症状实体 ({len(diabetes_data['symptoms'])}个):")
                    for symptom in diabetes_data['symptoms']:
                        print(f"  - {symptom['name']} (ID: {symptom['id']})")
                    
                    print(f"\n📋 糖尿病相关药物实体 ({len(diabetes_data['medicines'])}个):")
                    for medicine in diabetes_data['medicines']:
                        print(f"  - {medicine['name']} (ID: {medicine['id']})")
                    
                    print(f"\n📋 糖尿病相关疾病-症状关系 ({len(diabetes_data['disease_symptom_relations'])}条):")
                    for rel in diabetes_data['disease_symptom_relations']:
                        print(f"  - {rel['disease_name']} → {rel['symptom_name']} (置信度: {rel['confidence']})")
                    
                    print(f"\n📋 糖尿病相关疾病-药物关系 ({len(diabetes_data['disease_medicine_relations'])}条):")
                    for rel in diabetes_data['disease_medicine_relations']:
                        print(f"  - {rel['disease_name']} → {rel['medicine_name']} (疗效: {rel.get('effectiveness', '未知')})")
                    
                    total_items = (len(diabetes_data['diseases']) + 
                                  len(diabetes_data['symptoms']) + 
                                  len(diabetes_data['medicines']) +
                                  len(diabetes_data['disease_symptom_relations']) +
                                  len(diabetes_data['disease_medicine_relations']))
                    print(f"\n📊 总计: {total_items}项糖尿病相关数据")
                
                else:
                    print("❌ 未知命令，请输入:")
                    print("  - 'query 问题' 分析问题")
                    print("  - 'memories 查询词' 查询记忆")
                    print("  - 'extract' 提取所有记忆")
                    print("  - 'stats' 显示统计")
                    print("  - 'clear_diabetes' 删除糖尿病相关记忆")
                    print("  - 'clear_graph_diabetes' 删除图谱中糖尿病数据")
                    print("  - 'preview_diabetes' 预览糖尿病相关数据")
                    print("  - 'exit' 退出系统")
                    
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 处理命令时出错: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="增强版Qwen图谱演示")
    parser.add_argument("--api-key", default=os.getenv('DASHSCOPE_API_KEY'), 
                       help="DashScope API密钥")
    parser.add_argument("--db-path", help="数据库路径")
    parser.add_argument("--query", help="直接分析的问题")
    parser.add_argument("--extract", action="store_true", help="直接提取所有记忆数据")
    parser.add_argument("--interactive", action="store_true", help="启动交互模式")
    parser.add_argument("--save-extract", help="保存提取数据到指定文件")
    
    args = parser.parse_args()
    
    # 初始化演示系统
    demo = EnhancedQwenGraphDemo(args.api_key, args.db_path)
    
    if args.extract:
        # 直接提取记忆数据
        print("📊 直接提取模式启动...")
        extracted_memories = demo.extract_current_memories()
        demo.display_extracted_memories(extracted_memories)
        
        # 如果指定了保存文件
        if args.save_extract:
            try:
                with open(args.save_extract, 'w', encoding='utf-8') as f:
                    json.dump(extracted_memories, f, ensure_ascii=False, indent=2)
                print(f"\n✅ 记忆数据已保存到: {args.save_extract}")
            except Exception as e:
                print(f"\n❌ 保存失败: {e}")
    elif args.query:
        # 直接分析问题
        result = demo.analyze_query_with_graph_update(args.query)
        print(f"\n✅ 分析完成")
    elif args.interactive:
        # 交互模式
        demo.run_interactive_demo()
    else:
        # 默认演示
        print("🎯 运行默认演示...")
        demo.analyze_query_with_graph_update("我现在头痛，和之前的头晕不一样")
        print("\n" + "="*60)
        print("提示：")
        print("  --interactive     启动交互模式")
        print("  --query '问题'   直接分析问题")
        print("  --extract         直接提取所有记忆")
        print("  --save-extract '文件' 提取并保存记忆数据")


if __name__ == "__main__":
    main()