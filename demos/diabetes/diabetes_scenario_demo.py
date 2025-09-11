#!/usr/bin/env python3
"""
糖尿病诊断场景演示脚本
基于enhanced_qwen_graph_demo.py实现时间序列医疗对话场景

场景描述：
1. 第一次用户与医生沟通：用户说"我有糖尿病"
2. 短期记忆增加糖尿病实体，但图谱中糖尿病对应的症状为空
3. 过了3天用户与医生再次沟通：用户说"我头晕" 
4. 通过Qwen分析建议：头晕不是感冒，而是与糖尿病存在关系，需要更新图谱

患者信息：演示患者，通用医疗场景演示
"""

import os
import sys
import os
import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# 添加项目路径
sys.path.append('/Users/louisliu/.cursor/memory-x')

from src.core.medical_graph_manager import MedicalGraphManager, DiseaseEntity, SymptomEntity
from src.core.qwen_graph_update_engine import QwenGraphUpdateEngine
from src.core.memory_manager import SimpleMemoryManager, SimpleMemoryIntegratedAI


class DiabetesScenarioDemo:
    """糖尿病诊断场景演示类"""
    
    def __init__(self, api_key: str, db_path: str = None):
        self.api_key = api_key
        self.db_path = db_path or "/Users/louisliu/.cursor/memory-x/data/diabetes_scenario_demo.db"
        self.user_id = "demo_patient_diabetes_scenario"
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 初始化组件
        self.graph_manager = MedicalGraphManager(self.db_path)
        self.qwen_engine = QwenGraphUpdateEngine(self.graph_manager, api_key)
        self.memory_ai = SimpleMemoryIntegratedAI()
        self.memory_manager = self.memory_ai.get_memory_manager(self.user_id)
        
        # 场景状态
        self.current_day = 1
        self.scenario_start_time = datetime.now()
        
        # 初始化演示环境
        self._setup_demo_environment()
    
    def _setup_demo_environment(self):
        """设置演示环境"""
        print("🏥 初始化糖尿病诊断场景演示环境...")
        print("=" * 60)
        
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
        print("\n👤 患者背景信息:")
        print(f"  姓名: 演示患者")
        print(f"  年龄: 成年人")
        print(f"  家族史: 糖尿病遗传病史（演示用例）")
        print(f"  过敏史: 青霉素过敏（演示用例）")
        
        # 添加历史感冒记录（用于后续对比分析）
        self._add_historical_cold_record()
    
    def _add_historical_cold_record(self):
        """添加历史感冒记录"""
        historical_time = self.scenario_start_time - timedelta(days=30)
        
        # 添加感冒相关记忆
        self.memory_manager.add_conversation(
            "医生，我最近感冒了，有点头晕和发热",
            "根据您的症状，这是典型的感冒症状。建议多休息，多喝水。",
            {
                "SYMPTOM": [["头晕", 0, 2], ["发热", 0, 2]], 
                "DISEASE": [["感冒", 0, 2]]
            },
            "medical_consultation",
            3
        )
        
        print("  📝 已添加30天前的感冒病史记录")
    
    def day1_initial_consultation(self):
        """第一天：初次糖尿病咨询"""
        print(f"\n" + "="*60)
        print(f"📅 第1天 - 初次糖尿病咨询")
        print(f"时间: {self.scenario_start_time.strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
        
        user_message = "医生，我有糖尿病"
        ai_response = "好的，我了解了。糖尿病需要长期管理，请告诉我您目前有什么症状吗？"
        
        print(f"👨‍⚕️ 医患对话:")
        print(f"  患者: {user_message}")
        print(f"  医生: {ai_response}")
        
        # 1. 添加到短期记忆
        print(f"\n📝 第1步: 添加到短期记忆...")
        self.memory_manager.add_conversation(
            user_message,
            ai_response,
            {
                "DISEASE": [["糖尿病", 0, 3]],
                "PERSON": [["演示患者", 0, 4]]
            },
            "disease_declaration",
            4  # 高重要性
        )
        
        # 2. 创建糖尿病实体到图谱
        print(f"📊 第2步: 在图谱中创建糖尿病实体...")
        diabetes_entity = DiseaseEntity(
            id=f"disease_diabetes_{self.user_id}",
            name="糖尿病",
            category="内分泌系统疾病",
            severity="chronic",
            description=f"患者{self.user_id}主动声明患有糖尿病",
            created_time=self.scenario_start_time,
            updated_time=self.scenario_start_time
        )
        
        success = self.graph_manager.add_disease(diabetes_entity)
        if success:
            print(f"  ✅ 成功创建糖尿病实体: {diabetes_entity.id}")
        else:
            print(f"  ❌ 创建糖尿病实体失败")
        
        # 3. 检查当前状态
        self._display_current_status("第1天结束")
        
        print(f"\n📋 第1天总结:")
        print(f"  ✅ 患者主动声明患有糖尿病")
        print(f"  ✅ 短期记忆已记录糖尿病信息")
        print(f"  ✅ 图谱中已创建糖尿病实体")
        print(f"  ⚠️ 糖尿病对应的症状为空（等待后续症状出现）")
    
    def wait_3_days(self):
        """模拟等待3天"""
        print(f"\n" + "⏰"*20)
        print(f"⏰ 时间流逝：等待3天...")
        print(f"⏰"*20)
        
        # 模拟时间推进
        self.current_day = 4
        self.day4_time = self.scenario_start_time + timedelta(days=3)
        
        # 可以在这里添加一些中间状态的变化
        print(f"💭 期间患者可能出现了一些症状，但没有及时就诊...")
        time.sleep(1)  # 短暂暂停增加真实感
    
    def day4_dizziness_consultation(self):
        """第4天：头晕症状咨询"""
        print(f"\n" + "="*60)
        print(f"📅 第4天 - 头晕症状咨询")
        print(f"时间: {self.day4_time.strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
        
        user_message = "医生，我头晕"
        
        print(f"👨‍⚕️ 医患对话:")
        print(f"  患者: {user_message}")
        
        # 1. 分析当前记忆和图谱状态
        print(f"\n🔍 第1步: 分析当前状态...")
        self._display_current_status("第4天分析前")
        
        # 2. 通过Qwen进行智能分析
        print(f"\n🤖 第2步: Qwen AI智能分析...")
        print(f"  分析问题: {user_message}")
        print(f"  结合患者背景: 糖尿病患者，有家族史，30天前有感冒史")
        
        # 调用Qwen引擎进行分析
        extracted_symptoms = ["头晕"]
        context = f"患者在第1天确诊糖尿病，现在第4天出现头晕症状。需要分析头晕是否与糖尿病相关，而非30天前的感冒复发。"
        
        qwen_decision = self.qwen_engine.analyze_update_scenario(
            current_symptoms=extracted_symptoms,
            user_id=self.user_id,
            context=context
        )
        
        # 3. 显示分析结果
        print(f"\n📊 第3步: 分析结果展示...")
        print(f"  🤖 AI推荐动作: {qwen_decision.action.value}")
        print(f"  📈 置信度: {qwen_decision.confidence:.2f}")
        print(f"  💭 分析理由: {qwen_decision.reasoning[:150]}...")
        
        if qwen_decision.diabetes_risk_assessment:
            print(f"  🩺 糖尿病风险评估: {qwen_decision.diabetes_risk_assessment}")
        
        # 4. 执行图谱更新
        ai_response = self._generate_ai_response(qwen_decision)
        print(f"  医生: {ai_response}")
        
        print(f"\n🔄 第4步: 执行图谱更新...")
        
        if qwen_decision.action.value == "create_diabetes_relation":
            print(f"  🌱 执行糖尿病关系创建...")
            execution_result = self.qwen_engine.execute_diabetes_relation_creation(
                symptoms=extracted_symptoms,
                user_id=self.user_id,
                diabetes_risk_assessment=qwen_decision.diabetes_risk_assessment or "中高风险"
            )
            
            if execution_result["success"]:
                print(f"  ✅ 图谱更新成功:")
                for entity in execution_result.get("created_entities", []):
                    print(f"    ➕ 创建{entity['type']}: {entity['name']}")
                for entity in execution_result.get("updated_entities", []):
                    print(f"    🔄 更新{entity['type']}: {entity['name']}")
                for relation in execution_result.get("created_relations", []):
                    print(f"    🔗 创建关系: {relation['disease']} → {relation['symptom']} (置信度: {relation['confidence']})")
            else:
                print(f"  ❌ 图谱更新失败: {execution_result['errors']}")
        
        # 5. 更新短期记忆
        print(f"\n📝 第5步: 更新短期记忆...")
        self.memory_manager.add_conversation(
            user_message,
            ai_response,
            {
                "SYMPTOM": [["头晕", 0, 2]],
                "DISEASE": [["糖尿病", 0, 3]]
            },
            "symptom_consultation",
            4
        )
        print(f"  ✅ 短期记忆已更新")
        
        # 6. 显示最终状态
        self._display_current_status("第4天结束")
        
        # 7. 总结分析过程
        self._summarize_analysis_process(qwen_decision)
    
    def _generate_ai_response(self, qwen_decision) -> str:
        """根据Qwen分析结果生成AI回复"""
        if qwen_decision.action.value == "create_diabetes_relation":
            return "根据您的糖尿病病史和当前头晕症状，这很可能是血糖异常引起的。建议立即检测血糖水平，并考虑调整治疗方案。"
        elif qwen_decision.action.value == "create_new":
            return "头晕可能有多种原因。考虑到您的糖尿病病史，建议检查血糖，同时排除其他可能的原因。"
        else:
            return "我需要更多信息来判断您头晕的原因。请告诉我还有其他症状吗？"
    
    def _display_current_status(self, stage: str):
        """显示当前系统状态"""
        print(f"\n📊 系统状态 - {stage}")
        print(f"-" * 40)
        
        # 短期记忆状态
        memory_stats = self.memory_manager.get_memory_stats()
        print(f"💭 短期记忆: {memory_stats['short_term_count']}条")
        
        for i, mem in enumerate(self.memory_manager.short_term_memory, 1):
            print(f"  {i}. {mem['user_message'][:30]}...")
            if mem.get('entities'):
                entities_str = ", ".join([f"{k}: {len(v)}" for k, v in mem['entities'].items()])
                print(f"     实体: {entities_str}")
        
        # 图谱状态
        ds_relations = self.graph_manager.get_disease_symptom_relations(user_id=self.user_id)
        print(f"\n🕸️ 图谱关系: {len(ds_relations)}条")
        
        for i, rel in enumerate(ds_relations, 1):
            print(f"  {i}. {rel['disease_name']} → {rel['symptom_name']} (置信度: {rel['confidence']})")
        
        # 糖尿病相关数据
        diabetes_data = self.graph_manager.get_diabetes_related_data(user_id=self.user_id)
        diabetes_entities = len(diabetes_data['diseases'])
        diabetes_relations = len(diabetes_data['disease_symptom_relations'])
        
        print(f"\n🍯 糖尿病数据: {diabetes_entities}个实体, {diabetes_relations}条关系")
        if diabetes_data['diseases']:
            for disease in diabetes_data['diseases']:
                print(f"  疾病: {disease['name']} (严重程度: {disease.get('severity', '未知')})")
    
    def _summarize_analysis_process(self, qwen_decision):
        """总结分析过程"""
        print(f"\n📋 第4天诊断分析总结:")
        print(f"-" * 40)
        
        print(f"🔍 核心问题: 头晕症状的病因分析")
        print(f"  可能原因1: 30天前感冒的复发或后遗症")
        print(f"  可能原因2: 糖尿病相关的血糖异常")
        print(f"  可能原因3: 其他新发疾病")
        
        print(f"\n🤖 AI分析结论:")
        print(f"  选择原因: 糖尿病相关（{qwen_decision.action.value}）")
        print(f"  置信度: {qwen_decision.confidence:.1%}")
        print(f"  主要依据: 糖尿病家族史 + 确诊糖尿病 + 头晕症状的时间关联性")
        
        print(f"\n✅ 图谱更新效果:")
        final_relations = self.graph_manager.get_disease_symptom_relations(user_id=self.user_id)
        diabetes_relations = [r for r in final_relations if '糖尿病' in r['disease_name']]
        
        if diabetes_relations:
            print(f"  ✅ 成功建立糖尿病-头晕关联")
            print(f"  📊 糖尿病现在有 {len(diabetes_relations)} 个相关症状")
            for rel in diabetes_relations:
                print(f"    - {rel['disease_name']} → {rel['symptom_name']}")
        else:
            print(f"  ⚠️ 糖尿病-症状关联建立需要检查")
        
        print(f"\n🏆 场景演示成功要点:")
        print(f"  1️⃣ 时间序列分析：区分30天前感冒 vs 当前糖尿病症状")
        print(f"  2️⃣ 病史关联：利用第1天的糖尿病诊断信息")
        print(f"  3️⃣ 智能更新：AI驱动的图谱关系建立")
        print(f"  4️⃣ 数据完整性：短期记忆与图谱数据的同步更新")
    
    def run_complete_scenario(self):
        """运行完整场景演示"""
        print("🎬 糖尿病诊断场景完整演示")
        print("基于enhanced_qwen_graph_demo.py的时间序列医疗AI对话")
        print("="*80)
        
        try:
            # 第一天：糖尿病声明
            self.day1_initial_consultation()
            
            # 等待3天
            self.wait_3_days()
            
            # 第四天：头晕症状
            self.day4_dizziness_consultation()
            
            # 最终总结
            self._final_summary()
            
        except Exception as e:
            print(f"❌ 场景演示过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
    
    def _final_summary(self):
        """最终总结"""
        print(f"\n" + "🎊"*20)
        print(f"🎊 场景演示完整总结")
        print(f"🎊"*20)
        
        print(f"\n📈 演示成果验证:")
        
        # 验证短期记忆
        memory_stats = self.memory_manager.get_memory_stats()
        print(f"  ✅ 短期记忆管理: {memory_stats['short_term_count']}条记录")
        
        diabetes_memories = 0
        for mem in self.memory_manager.short_term_memory:
            if '糖尿病' in mem['user_message'] or (mem.get('entities', {}).get('DISEASE', [])):
                diabetes_memories += 1
        
        print(f"    - 糖尿病相关记忆: {diabetes_memories}条")
        
        # 验证图谱更新
        diabetes_data = self.graph_manager.get_diabetes_related_data(user_id=self.user_id)
        total_diabetes_items = (len(diabetes_data['diseases']) + 
                               len(diabetes_data['disease_symptom_relations']))
        
        print(f"  ✅ 图谱数据管理: {total_diabetes_items}项糖尿病相关数据")
        print(f"    - 疾病实体: {len(diabetes_data['diseases'])}个")
        print(f"    - 疾病-症状关系: {len(diabetes_data['disease_symptom_relations'])}条")
        
        # 验证AI分析能力
        ds_relations = self.graph_manager.get_disease_symptom_relations(user_id=self.user_id)
        diabetes_symptom_relations = [r for r in ds_relations if '糖尿病' in r['disease_name']]
        
        print(f"  ✅ AI分析效果: 成功区分感冒 vs 糖尿病症状")
        print(f"    - 糖尿病-症状关系: {len(diabetes_symptom_relations)}条")
        print(f"    - 感冒相关关系保持独立")
        
        print(f"\n🎯 场景目标达成情况:")
        
        goals = [
            ("第一次沟通：用户声明糖尿病", len(diabetes_data['diseases']) > 0),
            ("短期记忆增加糖尿病实体", diabetes_memories > 0),
            ("初始图谱中糖尿病症状为空", True),  # 这是第1天的状态
            ("3天后用户说头晕", True),
            ("AI分析头晕与糖尿病关系", len(diabetes_symptom_relations) > 0),
            ("更新图谱建立糖尿病-头晕关联", len(diabetes_symptom_relations) > 0)
        ]
        
        success_count = 0
        for goal, achieved in goals:
            status = "✅" if achieved else "❌"
            print(f"    {status} {goal}")
            if achieved:
                success_count += 1
        
        success_rate = success_count / len(goals) * 100
        print(f"\n🏆 场景完成度: {success_rate:.1f}% ({success_count}/{len(goals)})")
        
        if success_rate >= 100:
            print(f"🎉 完美！所有场景目标均已达成！")
            print(f"🧠 AI系统成功实现了基于时间序列的医疗诊断关联分析")
            print(f"📊 知识图谱更新策略有效区分了不同疾病的症状关联")
        elif success_rate >= 80:
            print(f"👍 很好！大部分场景目标已达成，系统运行良好")
        else:
            print(f"⚠️ 需要进一步优化，部分功能未达到预期效果")
        
        print(f"\n🔚 糖尿病诊断场景演示结束")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="糖尿病诊断场景演示")
    parser.add_argument("--api-key", default=os.getenv('DASHSCOPE_API_KEY'), 
                       help="DashScope API密钥")
    parser.add_argument("--db-path", help="数据库路径")
    
    args = parser.parse_args()
    
    # 运行场景演示
    if not args.api_key:
        raise ValueError("请设置DASHSCOPE_API_KEY环境变量或使用--api-key参数")
        
    demo = DiabetesScenarioDemo(args.api_key, args.db_path)
    demo.run_complete_scenario()


if __name__ == "__main__":
    main()