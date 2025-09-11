#!/usr/bin/env python3
"""
直接测试Qwen3医疗分析功能
"""

import sys
import os
sys.path.append('/Users/louisliu/.cursor/memory-x')

from src.core.qwen_update_engine import QwenAPIClient


def direct_qwen_test():
    """直接测试Qwen3医疗分析"""
    print("🤖 直接测试Qwen3医疗分析功能")
    print("=" * 50)
    
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        raise ValueError("请设置DASHSCOPE_API_KEY环境变量")
    client = QwenAPIClient(api_key)
    
    # 构建医疗场景分析提示
    prompt = """
作为医疗AI专家，请分析以下医疗知识图谱更新场景：

**患者当前症状：**
头疼

**病史信息：**
1. 60天前 (2025-07-13): 感冒 → 头晕
   来源: online_consult
   置信度: 0.8

**上下文信息：**
患者柳阳，40岁，再次咨询头疼症状，两个月前曾因头晕诊断为感冒

**基础规则分析结果：**
- 推荐动作: create_new
- 置信度: 0.70
- 分析原因: 感冒为急性疾病，时间间隔较长，建议创建新记录

**请你从以下角度进行深入分析：**

1. **医学合理性分析**：
   - 当前症状与历史诊断的医学关联性
   - 疾病的自然病程和可能的并发症
   - 症状的鉴别诊断要点

2. **时间因素评估**：
   - 感冒的典型病程和复发特点
   - 时间间隔对诊断的影响
   - 是否存在慢性化或并发症的可能

3. **风险评估**：
   - 错误关联的医疗风险
   - 漏诊或误诊的可能性
   - 需要特别关注的危险信号

请以JSON格式返回你的分析结果：
```json
{
    "medical_analysis": "医学角度的深入分析",
    "recommended_action": "CREATE_NEW/UPDATE_EXISTING/IGNORE/MERGE/SPLIT之一",
    "confidence_score": 0.85,
    "key_reasoning": "核心推理逻辑",
    "clinical_recommendations": ["临床建议1", "临床建议2"],
    "risk_factors": ["风险因素1", "风险因素2"],
    "differential_diagnosis": ["鉴别诊断1", "鉴别诊断2"]
}
```
"""
    
    try:
        print("🔍 发送医疗分析请求...")
        response = client.generate_response(prompt)
        
        print("✅ Qwen3分析完成！")
        print("📋 分析结果：")
        print("-" * 30)
        print(response)
        
        # 尝试提取JSON部分
        import json
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start != -1 and json_end > 0:
            json_str = response[json_start:json_end]
            try:
                analysis = json.loads(json_str)
                print("\n📊 结构化分析结果：")
                print(f"推荐动作: {analysis.get('recommended_action', 'N/A')}")
                print(f"置信度: {analysis.get('confidence_score', 'N/A')}")
                print(f"核心推理: {analysis.get('key_reasoning', 'N/A')}")
                
                if analysis.get('clinical_recommendations'):
                    print("💡 临床建议:")
                    for i, rec in enumerate(analysis['clinical_recommendations'], 1):
                        print(f"  {i}. {rec}")
                
                if analysis.get('risk_factors'):
                    print("⚠️ 风险因素:")
                    for i, risk in enumerate(analysis['risk_factors'], 1):
                        print(f"  {i}. {risk}")
                
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON解析失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return False


def test_batch_scenarios():
    """测试多种场景"""
    print("\n🔬 测试多种医疗场景")
    print("=" * 40)
    
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        raise ValueError("请设置DASHSCOPE_API_KEY环境变量")
    client = QwenAPIClient(api_key)
    
    scenarios = [
        {
            "name": "急性疾病复发判断",
            "prompt": "患者一周前感冒已愈，现在又出现发热咳嗽，请分析是否为感冒复发？"
        },
        {
            "name": "慢性疾病进展",
            "prompt": "糖尿病患者出现视力模糊新症状，请分析是否为糖尿病并发症？"
        },
        {
            "name": "症状演变分析", 
            "prompt": "患者从胸闷发展为胸痛，请分析这种症状演变的临床意义？"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 场景 {i}: {scenario['name']}")
        try:
            response = client.generate_response(scenario['prompt'])
            print(f"AI分析: {response[:200]}...")
        except Exception as e:
            print(f"❌ 分析失败: {e}")


if __name__ == "__main__":
    # 主要测试
    success = direct_qwen_test()
    
    if success:
        # 额外场景测试
        test_batch_scenarios()
        
    print(f"\n🎉 Qwen3医疗分析测试完成！")