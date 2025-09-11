#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
演示统一百炼API客户端配置的使用
Demo for Unified DashScope API Client Configuration

展示如何在各种场景中使用统一的客户端配置
专为柳阳（40岁，糖尿病遗传病史，青霉素过敏）设计
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs.dashscope_client import (
    DashScopeClientFactory,
    get_global_client,
    quick_ask,
    medical_consultation,
    check_medication_safety
)


def demo_basic_client_usage():
    """演示基础客户端使用"""
    print("🔬 基础客户端使用演示")
    print("=" * 50)
    
    try:
        # 创建标准客户端
        client = DashScopeClientFactory.create_client(
            client_type="standard",
            medical_mode=True
        )
        
        # 基础对话
        response = client.generate_response("你好，我是柳阳，想了解一下糖尿病的预防知识。")
        print("AI回答:")
        print(response)
        print()
        
    except Exception as e:
        print(f"❌ 基础客户端演示失败: {e}")


def demo_medical_client_usage():
    """演示医疗专用客户端使用"""
    print("🏥 医疗专用客户端使用演示")
    print("=" * 50)
    
    try:
        # 创建医疗专用客户端
        medical_client = DashScopeClientFactory.create_medical_client()
        
        # 症状诊断
        symptoms = ["头晕", "乏力", "口渴"]
        diagnosis = medical_client.diagnose_symptoms(symptoms)
        print("症状诊断分析:")
        print(diagnosis)
        print()
        
        # 药物安全检查
        safety_check = medical_client.medication_safety_check("二甲双胍")
        print("药物安全检查:")
        print(safety_check)
        print()
        
    except Exception as e:
        print(f"❌ 医疗客户端演示失败: {e}")


def demo_global_client_usage():
    """演示全局客户端使用"""
    print("🌐 全局客户端使用演示")
    print("=" * 50)
    
    try:
        # 使用全局客户端进行快速提问
        answer1 = quick_ask("糖尿病的早期症状有哪些？")
        print("快速提问 - 糖尿病早期症状:")
        print(answer1)
        print()
        
        # 医疗咨询便捷函数
        consultation = medical_consultation(["多尿", "多饮", "体重下降"])
        print("医疗咨询分析:")
        print(consultation)
        print()
        
        # 药物安全检查便捷函数
        drug_safety = check_medication_safety("阿莫西林")
        print("药物安全检查 - 阿莫西林:")
        print(drug_safety)
        print()
        
    except Exception as e:
        print(f"❌ 全局客户端演示失败: {e}")


def demo_configuration_options():
    """演示不同配置选项"""
    print("⚙️ 配置选项演示")
    print("=" * 50)
    
    try:
        # 自定义配置的客户端
        custom_client = DashScopeClientFactory.create_client(
            client_type="medical",
            model="qwen-plus",
            max_tokens=1000,
            temperature=0.2,
            medical_mode=True
        )
        
        # 使用自定义配置
        response = custom_client.generate_response(
            "请简要介绍糖尿病的分类和特点。",
            max_tokens=500
        )
        print("自定义配置客户端回答:")
        print(response)
        print()
        
    except Exception as e:
        print(f"❌ 配置选项演示失败: {e}")


def demo_integration_with_existing_code():
    """演示与现有代码的集成"""
    print("🔗 现有代码集成演示")
    print("=" * 50)
    
    try:
        # 模拟现有的医疗分析流程
        def analyze_patient_symptoms(patient_info, symptoms):
            """模拟现有的患者症状分析函数"""
            client = get_global_client(client_type="medical")
            
            prompt = f"""
患者信息：
- 姓名：{patient_info.get('name', '未知')}
- 年龄：{patient_info.get('age', '未知')}
- 过敏史：{', '.join(patient_info.get('allergies', []))}
- 家族史：{', '.join(patient_info.get('family_history', []))}

当前症状：{', '.join(symptoms)}

请进行专业的医疗分析。
"""
            
            return client.generate_response(prompt)
        
        # 使用统一客户端
        patient_info = {
            "name": "柳阳",
            "age": 40,
            "allergies": ["青霉素"],
            "family_history": ["糖尿病遗传病史"]
        }
        
        symptoms = ["头晕", "疲劳"]
        
        analysis = analyze_patient_symptoms(patient_info, symptoms)
        print("患者症状分析:")
        print(analysis)
        print()
        
    except Exception as e:
        print(f"❌ 现有代码集成演示失败: {e}")


def demo_error_handling():
    """演示错误处理"""
    print("🛡️ 错误处理演示")
    print("=" * 50)
    
    try:
        # 故意使用无效的API key来演示错误处理
        print("测试无效API key的错误处理...")
        
        try:
            invalid_client = DashScopeClientFactory.create_client(
                client_type="standard",
                api_key="invalid-key-for-demo"
            )
            response = invalid_client.generate_response("测试消息")
            print("这不应该被执行到")
        except Exception as e:
            print(f"✅ 正确捕获错误: {str(e)[:100]}...")
        
        # 演示降级处理
        print("\n演示正常客户端操作...")
        normal_client = get_global_client()
        response = normal_client.generate_response("糖尿病患者应该注意什么？")
        print("正常客户端回答:")
        print(response[:200] + "..." if len(response) > 200 else response)
        
    except Exception as e:
        print(f"❌ 错误处理演示失败: {e}")


def main():
    """主函数"""
    print("🎯 Memory-X 统一百炼API客户端配置演示")
    print("专为柳阳（40岁，糖尿病遗传病史，青霉素过敏）优化")
    print("=" * 80)
    print()
    
    # 检查环境变量
    if not os.getenv('DASHSCOPE_API_KEY'):
        print("⚠️ 警告：未设置DASHSCOPE_API_KEY环境变量")
        print("请设置环境变量：export DASHSCOPE_API_KEY='your-api-key'")
        print("或创建.env文件并添加DASHSCOPE_API_KEY=your-api-key")
        print()
        return
    
    # 运行各种演示
    demos = [
        demo_basic_client_usage,
        demo_medical_client_usage,
        demo_global_client_usage,
        demo_configuration_options,
        demo_integration_with_existing_code,
        demo_error_handling
    ]
    
    for i, demo_func in enumerate(demos, 1):
        try:
            demo_func()
            if i < len(demos):
                print("─" * 80)
                print()
        except Exception as e:
            print(f"❌ 演示 {demo_func.__name__} 失败: {e}")
            print()
    
    print("🎉 所有演示完成！")
    print()
    print("📋 使用总结：")
    print("1. 使用 DashScopeClientFactory.create_client() 创建不同类型的客户端")
    print("2. 使用 get_global_client() 获取全局单例客户端")
    print("3. 使用便捷函数 quick_ask(), medical_consultation(), check_medication_safety()")
    print("4. 医疗专用客户端自动考虑患者过敏史和家族病史")
    print("5. 所有客户端都支持统一的错误处理和重试机制")


if __name__ == "__main__":
    main()