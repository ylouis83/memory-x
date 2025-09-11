#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通用医疗AI演示
General Medical AI Demo

展示Memory-X系统如何处理不同患者的医疗信息
Demonstrates how Memory-X system handles medical information for different patients
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs.dashscope_client import (
    DashScopeClientFactory,
    DashScopeConfig,
    MedicalDashScopeClient
)


class GeneralMedicalDemo:
    """通用医疗AI演示类"""
    
    def __init__(self, api_key: str = None):
        """初始化演示系统"""
        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY')
        if not self.api_key:
            raise ValueError("请设置DASHSCOPE_API_KEY环境变量")
        
        print("🏥 Memory-X 通用医疗AI演示系统")
        print("=" * 60)
    
    def demo_patient_specific_analysis(self):
        """演示针对特定患者的医疗分析"""
        print("\n👤 患者特定医疗分析演示")
        print("-" * 40)
        
        # 定义不同类型的患者
        patients = [
            {
                "name": "张先生",
                "age": 35,
                "allergies": ["磺胺类药物"],
                "family_history": ["高血压家族史"],
                "symptoms": ["头痛", "眩晕"],
                "scenario": "年轻男性，有高血压家族史，出现头痛眩晕症状"
            },
            {
                "name": "李女士", 
                "age": 50,
                "allergies": ["青霉素"],
                "family_history": ["糖尿病遗传病史"],
                "symptoms": ["口渴", "多尿", "乏力"],
                "scenario": "中年女性，有糖尿病家族史，出现典型糖尿病症状"
            },
            {
                "name": "王老师",
                "age": 28,
                "allergies": [],
                "family_history": ["哮喘家族史"],
                "symptoms": ["咳嗽", "气喘"],
                "scenario": "年轻教师，有哮喘家族史，出现呼吸道症状"
            }
        ]
        
        for i, patient in enumerate(patients, 1):
            print(f"\n📋 患者 {i}: {patient['name']}")
            print(f"   年龄: {patient['age']}岁")
            print(f"   过敏史: {', '.join(patient['allergies']) if patient['allergies'] else '无'}")
            print(f"   家族史: {', '.join(patient['family_history']) if patient['family_history'] else '无'}")
            print(f"   症状: {', '.join(patient['symptoms'])}")
            print(f"   场景: {patient['scenario']}")
            
            # 创建患者特定的客户端配置
            patient_config = DashScopeConfig(
                api_key=self.api_key,
                medical_mode=True,
                patient_context={
                    "patient_name": patient['name'],
                    "age": patient['age'],
                    "allergies": patient['allergies'],
                    "family_history": patient['family_history'],
                    "medical_focus": ["症状分析", "风险评估", "药物安全"]
                }
            )
            
            try:
                # 创建医疗客户端
                client = MedicalDashScopeClient(patient_config)
                
                # 进行症状诊断
                diagnosis = client.diagnose_symptoms(
                    patient['symptoms'],
                    patient_context=patient_config.patient_context
                )
                
                print(f"   🔍 AI诊断分析:")
                print(f"   {diagnosis[:200]}..." if len(diagnosis) > 200 else f"   {diagnosis}")
                
            except Exception as e:
                print(f"   ❌ 分析失败: {e}")
            
            if i < len(patients):
                print()
    
    def demo_medication_safety_analysis(self):
        """演示药物安全性分析"""
        print("\n💊 药物安全性分析演示")
        print("-" * 40)
        
        # 定义药物和患者场景
        medication_scenarios = [
            {
                "medication": "阿莫西林",
                "patient_profile": "青霉素过敏患者",
                "expected_risk": "高风险（交叉过敏）"
            },
            {
                "medication": "二甲双胍",
                "patient_profile": "糖尿病高风险患者",
                "expected_risk": "适用（一线治疗药物）"
            },
            {
                "medication": "阿司匹林",
                "patient_profile": "哮喘患者",
                "expected_risk": "中等风险（可能诱发哮喘）"
            },
            {
                "medication": "红霉素",
                "patient_profile": "青霉素过敏患者",
                "expected_risk": "低风险（可作为替代选择）"
            }
        ]
        
        # 创建通用医疗客户端
        client = DashScopeClientFactory.create_medical_client(api_key=self.api_key)
        
        for scenario in medication_scenarios:
            print(f"\n🔬 药物: {scenario['medication']}")
            print(f"   患者类型: {scenario['patient_profile']}")
            print(f"   预期风险: {scenario['expected_risk']}")
            
            try:
                # 药物安全检查
                if isinstance(client, MedicalDashScopeClient):
                    safety_analysis = client.medication_safety_check(scenario['medication'])
                else:
                    safety_analysis = client.generate_response(
                        f"请分析药物{scenario['medication']}对于{scenario['patient_profile']}的安全性"
                    )
                
                print(f"   🛡️ 安全性分析:")
                print(f"   {safety_analysis[:150]}..." if len(safety_analysis) > 150 else f"   {safety_analysis}")
                
            except Exception as e:
                print(f"   ❌ 分析失败: {e}")
    
    def demo_general_medical_consultation(self):
        """演示通用医疗咨询"""
        print("\n🩺 通用医疗咨询演示")
        print("-" * 40)
        
        # 通用医疗问题
        medical_questions = [
            "糖尿病的早期症状有哪些？如何预防？",
            "高血压患者在日常生活中需要注意什么？",
            "哮喘发作时的应急处理方法是什么？",
            "青霉素过敏患者可以使用哪些替代抗生素？",
            "老年人用药安全需要注意哪些问题？"
        ]
        
        client = DashScopeClientFactory.create_client(
            client_type="medical",
            api_key=self.api_key
        )
        
        for i, question in enumerate(medical_questions, 1):
            print(f"\n❓ 问题 {i}: {question}")
            
            try:
                answer = client.generate_response(question)
                print(f"🤖 AI回答: {answer[:200]}..." if len(answer) > 200 else f"🤖 AI回答: {answer}")
                
            except Exception as e:
                print(f"❌ 回答失败: {e}")
    
    def demo_family_history_risk_assessment(self):
        """演示家族史风险评估"""
        print("\n🧬 家族史风险评估演示")
        print("-" * 40)
        
        family_history_cases = [
            {
                "family_history": ["糖尿病", "高血压"],
                "patient_age": 45,
                "symptoms": ["头晕", "口渴"],
                "focus": "代谢性疾病风险"
            },
            {
                "family_history": ["心脏病", "高血脂"],
                "patient_age": 38,
                "symptoms": ["胸闷", "气短"],
                "focus": "心血管疾病风险"
            },
            {
                "family_history": ["肿瘤家族史"],
                "patient_age": 55,
                "symptoms": ["体重下降", "乏力"],
                "focus": "肿瘤筛查建议"
            }
        ]
        
        for i, case in enumerate(family_history_cases, 1):
            print(f"\n🔍 案例 {i}:")
            print(f"   家族史: {', '.join(case['family_history'])}")
            print(f"   患者年龄: {case['patient_age']}岁")
            print(f"   现有症状: {', '.join(case['symptoms'])}")
            print(f"   评估重点: {case['focus']}")
            
            # 创建特定的客户端配置
            specific_config = DashScopeConfig(
                api_key=self.api_key,
                medical_mode=True,
                patient_context={
                    "age": case['patient_age'],
                    "family_history": case['family_history'],
                    "current_symptoms": case['symptoms']
                }
            )
            
            try:
                client = MedicalDashScopeClient(specific_config)
                
                risk_assessment = client.generate_response(
                    f"基于家族史{', '.join(case['family_history'])}和当前症状{', '.join(case['symptoms'])}，"
                    f"请为{case['patient_age']}岁患者进行风险评估和预防建议。"
                )
                
                print(f"   📊 风险评估:")
                print(f"   {risk_assessment[:250]}..." if len(risk_assessment) > 250 else f"   {risk_assessment}")
                
            except Exception as e:
                print(f"   ❌ 评估失败: {e}")
    
    def run_all_demos(self):
        """运行所有演示"""
        print("🎯 开始运行全部医疗AI演示...")
        
        try:
            self.demo_patient_specific_analysis()
            self.demo_medication_safety_analysis()
            self.demo_general_medical_consultation()
            self.demo_family_history_risk_assessment()
            
            print("\n" + "=" * 60)
            print("🎉 所有演示完成！")
            print("\n📋 系统特点总结:")
            print("✅ 支持多患者个性化医疗分析")
            print("✅ 智能药物安全性评估")
            print("✅ 全面的家族史风险评估")
            print("✅ 通用医疗知识咨询")
            print("✅ 可配置的患者信息管理")
            print("✅ 统一的AI客户端接口")
            
        except Exception as e:
            print(f"\n❌ 演示运行失败: {e}")


def main():
    """主函数"""
    try:
        # 检查环境变量
        if not os.getenv('DASHSCOPE_API_KEY'):
            print("⚠️ 警告：未设置DASHSCOPE_API_KEY环境变量")
            print("请设置环境变量：export DASHSCOPE_API_KEY='your-api-key'")
            print("或创建.env文件并添加DASHSCOPE_API_KEY=your-api-key")
            return
        
        # 创建并运行演示
        demo = GeneralMedicalDemo()
        demo.run_all_demos()
        
    except Exception as e:
        print(f"❌ 程序运行失败: {e}")


if __name__ == "__main__":
    main()