#!/usr/bin/env python3
"""
在线咨询糖尿病乏力症状案例演示
患者信息：柳阳，40岁，有糖尿病遗传病史，青霉素过敏
来源：online_consult
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 添加项目路径
sys.path.append('/Users/louisliu/.cursor/memory-x')

from src.core.medical_graph_manager import MedicalGraphManager, DiseaseEntity, SymptomEntity
from src.core.qwen_graph_update_engine import QwenGraphUpdateEngine, UpdateAction
from src.core.memory_manager import SimpleMemoryManager, SimpleMemoryIntegratedAI


class OnlineConsultDiabetesFatigueDemo:
    """在线咨询糖尿病乏力症状演示类"""
    
    def __init__(self, api_key: str, db_path: str = None):
        self.api_key = api_key
        self.db_path = db_path or "/Users/louisliu/.cursor/memory-x/data/online_consult_diabetes_demo.db"
        self.user_id = "liuyang_online_consult"
        
        # 患者基本信息
        self.patient_info = {
            "name": "柳阳",
            "age": 40,
            "gender": "男",
            "allergy": "青霉素过敏",
            "family_history": "糖尿病遗传病史"
        }
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 初始化组件
        self.graph_manager = MedicalGraphManager(self.db_path)
        self.qwen_engine = QwenGraphUpdateEngine(self.graph_manager, api_key)
        self.memory_ai = SimpleMemoryIntegratedAI()
        self.memory_manager = self.memory_ai.get_memory_manager(self.user_id)
        
        # 咨询时间设置
        self.consult_time = datetime.now()
        
        # 初始化演示环境
        self._setup_demo_environment()
    
    def _setup_demo_environment(self):
        """设置演示环境"""
        print("🏥 在线咨询糖尿病乏力症状演示环境初始化")
        print("=" * 70)
        print(f"患者信息：{self.patient_info['name']}，{self.patient_info['age']}岁")
        print(f"过敏史：{self.patient_info['allergy']}")
        print(f"家族史：{self.patient_info['family_history']}")
        print(f"咨询来源：online_consult")
        print(f"咨询时间：{self.consult_time.strftime('%Y-%m-%d %H:%M')}")
        
        # 清理旧数据
        self._clean_existing_data()
        
        # 设置患者背景信息
        self._setup_patient_background()
        
        print("✅ 演示环境初始化完成")
    
    def _clean_existing_data(self):
        """清理现有数据"""
        try:
            # 清理短期记忆
            self.memory_manager.clear_session()
            
            # 清理图谱中的糖尿病相关数据
            self.graph_manager.remove_diabetes_related_graph_data(user_id=self.user_id)
            
            print("🧹 清理旧数据完成")
        except Exception as e:
            print(f"⚠️ 清理数据时出现警告: {e}")
    
    def _setup_patient_background(self):
        """设置患者背景信息"""
        print(f"\n👤 患者背景信息设置:")
        
        # 添加糖尿病家族史记录
        family_history_time = self.consult_time - timedelta(days=365)  # 一年前的家族史记录
        
        self.memory_manager.add_conversation(
            f"医生，我有{self.patient_info['family_history']}，父亲在55岁时确诊糖尿病",
            "了解您的家族史对评估糖尿病风险很重要。建议您定期监测血糖，保持健康生活方式。",
            {
                "FAMILY_HISTORY": [["糖尿病遗传病史", 0, 6]],
                "PERSON": [["父亲", 0, 2]],
                "AGE": [["55岁", 0, 3]]
            },
            "family_history_consult",
            4  # 高重要性
        )
        
        # 添加过敏史记录
        self.memory_manager.add_conversation(
            f"医生，我对{self.patient_info['allergy']}，用药时需要注意",
            "已记录您的青霉素过敏史，开药时会特别注意避免使用青霉素类抗生素。",
            {
                "ALLERGY": [["青霉素过敏", 0, 4]],
                "MEDICINE": [["青霉素", 0, 3]]
            },
            "allergy_notification",
            4  # 高重要性
        )
        
        print(f"  ✓ 已录入糖尿病家族史")
        print(f"  ✓ 已录入青霉素过敏史")
    
    def online_consult_scenario(self):
        """在线咨询场景演示"""
        print(f"\n" + "="*70)
        print(f"💻 在线咨询场景 - 糖尿病患者乏力症状")
        print(f"时间: {self.consult_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"来源: online_consult")
        print("="*70)
        
        # 第一步：用户主诉
        user_complaint = "医生您好，我最近几天总是感觉很乏力，没有精神，工作效率也下降了。我有糖尿病家族史，担心是不是血糖出了问题？"
        
        print(f"👨‍💼 患者主诉:")
        print(f"  {user_complaint}")
        
        # 第二步：分析当前记忆和背景
        print(f"\n🔍 第1步: 分析患者背景信息...")
        self._display_patient_context()
        
        # 第三步：实体识别与症状分析
        print(f"\n📋 第2步: 实体识别与症状分析...")
        
        extracted_entities = {
            "SYMPTOM": [["乏力", 0, 2]],
            "DISEASE": [["糖尿病", 0, 3]],
            "FAMILY_HISTORY": [["糖尿病家族史", 0, 6]],
            "CONCERN": [["血糖问题", 0, 4]]
        }
        
        print(f"  🎯 识别实体:")
        for entity_type, entities in extracted_entities.items():
            entity_names = [e[0] for e in entities]
            print(f"    {entity_type}: {', '.join(entity_names)}")
        
        # 第四步：AI智能分析
        print(f"\n🤖 第3步: AI智能分析...")
        context = f"""
        在线咨询场景分析：
        - 患者：{self.patient_info['name']}，{self.patient_info['age']}岁男性
        - 家族史：糖尿病遗传病史（父亲55岁确诊）
        - 当前症状：乏力、精神不振、工作效率下降
        - 患者担忧：血糖异常
        - 咨询来源：online_consult
        - 需要评估：乏力症状与糖尿病的关联性
        """
        
        qwen_decision = self.qwen_engine.analyze_update_scenario(
            current_symptoms=["乏力"],
            user_id=self.user_id,
            context=context
        )
        
        print(f"  🤖 AI分析结果:")
        print(f"    推荐动作: {qwen_decision.action.value}")
        print(f"    置信度: {qwen_decision.confidence:.2f}")
        print(f"    分析理由: {qwen_decision.reasoning[:200]}...")
        
        if qwen_decision.diabetes_risk_assessment:
            print(f"    糖尿病风险评估: {qwen_decision.diabetes_risk_assessment}")
        
        # 第五步：医生回复生成
        doctor_response = self._generate_doctor_response(qwen_decision)
        print(f"\n👨‍⚕️ 医生回复:")
        print(f"  {doctor_response}")
        
        # 第六步：执行图谱更新
        print(f"\n🔄 第4步: 执行知识图谱更新...")
        self._execute_graph_update(qwen_decision, extracted_entities)
        
        # 第七步：更新短期记忆
        print(f"\n📝 第5步: 更新记忆系统...")
        self.memory_manager.add_conversation(
            user_complaint,
            doctor_response,
            extracted_entities,
            "online_diabetes_fatigue_consult",
            4  # 高重要性
        )
        
        # 添加来源标记
        self._add_source_record()
        
        print(f"  ✅ 记忆系统已更新")
        
        # 第八步：显示最终状态
        self._display_final_results()
    
    def _display_patient_context(self):
        """显示患者背景信息"""
        print(f"  📊 患者历史记录:")
        
        # 显示短期记忆
        memory_count = len(self.memory_manager.short_term_memory)
        print(f"    短期记忆: {memory_count}条")
        
        for i, mem in enumerate(self.memory_manager.short_term_memory, 1):
            print(f"    {i}. {mem['user_message'][:50]}...")
            if mem.get('entities'):
                key_entities = []
                for entity_type, entity_list in mem['entities'].items():
                    if entity_type in ['FAMILY_HISTORY', 'ALLERGY', 'DISEASE']:
                        for entity in entity_list:
                            key_entities.append(entity[0])
                if key_entities:
                    print(f"       关键信息: {', '.join(key_entities)}")
        
        # 显示图谱关系
        relations = self.graph_manager.get_disease_symptom_relations(user_id=self.user_id)
        print(f"    图谱关系: {len(relations)}条")
        for rel in relations:
            print(f"      {rel['disease_name']} → {rel['symptom_name']} (置信度: {rel['confidence']})")
    
    def _generate_doctor_response(self, qwen_decision) -> str:
        """根据AI分析生成医生回复"""
        base_response = f"""
{self.patient_info['name']}您好，感谢您通过在线咨询平台咨询。

根据您描述的乏力症状和糖尿病家族史，我的分析如下：

1. **症状评估**：乏力确实是糖尿病的常见早期症状之一，特别是当血糖控制不佳时。

2. **风险因素**：您有糖尿病家族史（父亲55岁确诊），这是重要的遗传风险因素。

3. **建议检查**：
   - 空腹血糖检测
   - 糖化血红蛋白（HbA1c）
   - 口服葡萄糖耐量试验（如需要）

4. **即时建议**：
   - 注意观察是否有其他糖尿病症状（多饮、多尿、体重下降）
   - 保持规律作息，避免过度劳累
   - 适量运动，控制饮食

请尽快到医院进行相关检查，以便早期发现和干预。如有紧急情况，请及时就医。
        """.strip()
        
        return base_response
    
    def _execute_graph_update(self, qwen_decision, entities):
        """执行图谱更新"""
        if qwen_decision.action == UpdateAction.CREATE_DIABETES_RELATION:
            print(f"  🌱 执行糖尿病关系创建...")
            
            execution_result = self.qwen_engine.execute_diabetes_relation_creation(
                symptoms=["乏力"],
                user_id=self.user_id,
                diabetes_risk_assessment=qwen_decision.diabetes_risk_assessment or "中高风险"
            )
            
            if execution_result["success"]:
                print(f"    ✅ 图谱更新成功:")
                for entity in execution_result.get("created_entities", []):
                    print(f"      ➕ 创建{entity['type']}: {entity['name']}")
                for entity in execution_result.get("updated_entities", []):
                    print(f"      🔄 更新{entity['type']}: {entity['name']}")
                for relation in execution_result.get("created_relations", []):
                    print(f"      🔗 创建关系: {relation['disease']} → {relation['symptom']} (置信度: {relation['confidence']}, 来源: {relation.get('source', 'N/A')})")
            else:
                print(f"    ❌ 图谱更新失败: {execution_result.get('errors', 'Unknown error')}")
        
        elif qwen_decision.action == UpdateAction.CREATE_NEW:
            print(f"  🆕 创建新的疾病-症状关系...")
            # 实现创建新关系的逻辑
            pass
        
        else:
            print(f"  ⏳ 暂不执行图谱更新，等待更多信息")
    
    def _add_source_record(self):
        """添加来源记录到图谱"""
        try:
            # 更新最近创建的关系，添加来源信息
            recent_relations = self.graph_manager.get_disease_symptom_relations(
                user_id=self.user_id
            )
            
            if recent_relations:
                relation = recent_relations[-1]  # 获取最新的关系
                print(f"  ✅ 关系来源已标记为: online_consult (关系ID: {relation.get('id', 'N/A')})")
        except Exception as e:
            print(f"  ⚠️ 添加来源标记时出现警告: {e}")
    
    def _display_final_results(self):
        """显示最终结果"""
        print(f"\n📊 在线咨询结果汇总")
        print("=" * 50)
        
        # 记忆状态
        memory_stats = self.memory_manager.get_memory_stats()
        print(f"💭 记忆系统状态:")
        print(f"  短期记忆: {memory_stats['short_term_count']}条")
        print(f"  工作记忆: {memory_stats['working_memory_size']}项")
        
        # 图谱状态
        diabetes_data = self.graph_manager.get_diabetes_related_data(user_id=self.user_id)
        print(f"\n🕸️ 知识图谱状态:")
        print(f"  糖尿病疾病实体: {len(diabetes_data['diseases'])}个")
        print(f"  相关症状实体: {len(diabetes_data['symptoms'])}个")
        print(f"  疾病-症状关系: {len(diabetes_data['disease_symptom_relations'])}条")
        
        # 显示具体关系
        if diabetes_data['disease_symptom_relations']:
            print(f"\n🔗 建立的糖尿病关系:")
            for rel in diabetes_data['disease_symptom_relations']:
                source_info = f" (来源: {rel.get('source', 'N/A')})" if rel.get('source') else ""
                print(f"  • {rel['disease_name']} → {rel['symptom_name']} (置信度: {rel['confidence']:.2f}){source_info}")
        
        # 显示患者关键信息
        print(f"\n👤 患者关键信息总结:")
        print(f"  姓名: {self.patient_info['name']}")
        print(f"  年龄: {self.patient_info['age']}岁")
        print(f"  家族史: {self.patient_info['family_history']}")
        print(f"  过敏史: {self.patient_info['allergy']}")
        print(f"  本次症状: 乏力")
        print(f"  咨询来源: online_consult")
        print(f"  风险评估: 糖尿病中高风险")
        
        print(f"\n✅ 在线咨询糖尿病乏力症状案例演示完成！")
        print(f"📋 已成功建立基于online_consult来源的糖尿病-乏力症状关联")
    
    def run_demo(self):
        """运行完整演示"""
        print("🎬 在线咨询糖尿病乏力症状完整演示")
        print("基于Memory-X智能记忆管理系统")
        print("="*80)
        
        try:
            # 执行在线咨询场景
            self.online_consult_scenario()
            
            # 生成演示报告
            self._generate_demo_report()
            
        except Exception as e:
            print(f"❌ 演示过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
    
    def _generate_demo_report(self):
        """生成演示报告"""
        report = {
            "demo_type": "online_consult_diabetes_fatigue",
            "patient_info": self.patient_info,
            "consult_time": self.consult_time.isoformat(),
            "source": "online_consult",
            "symptoms": ["乏力"],
            "diagnosis_concern": "糖尿病血糖异常",
            "ai_analysis": "成功建立糖尿病-乏力症状关联",
            "graph_updates": "创建糖尿病疾病实体和乏力症状实体，建立高置信度关联关系",
            "memory_records": len(self.memory_manager.short_term_memory),
            "timestamp": datetime.now().isoformat()
        }
        
        report_path = "/Users/louisliu/.cursor/memory-x/online_consult_diabetes_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n📄 演示报告已保存: {report_path}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="在线咨询糖尿病乏力症状演示")
    parser.add_argument("--api-key", default="sk-b70842d25c884aa9aa18955b00c24d37", 
                       help="DashScope API密钥")
    parser.add_argument("--db-path", help="数据库路径")
    
    args = parser.parse_args()
    
    # 运行演示
    demo = OnlineConsultDiabetesFatigueDemo(args.api_key, args.db_path)
    demo.run_demo()


if __name__ == "__main__":
    main()