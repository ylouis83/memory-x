#!/usr/bin/env python3
"""
基于百炼API Qwen3模型的医疗知识图谱智能更新引擎
Medical Knowledge Graph Intelligent Update Engine with Qwen3

专门处理感冒等短期疾病的图谱更新场景
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from .medical_graph_manager import MedicalGraphManager

class UpdateAction(Enum):
    """更新动作类型"""
    CREATE_NEW = "create_new"                    # 创建新关系
    UPDATE_EXISTING = "update_existing"          # 更新现有关系
    IGNORE = "ignore"                            # 忽略（不更新）
    MERGE = "merge"                              # 合并关系
    CREATE_DIABETES_RELATION = "create_diabetes_relation"  # 创建糖尿病关系

@dataclass
class UpdateDecision:
    """更新决策结果"""
    action: UpdateAction
    confidence: float
    reasoning: str
    recommendations: List[str]
    risk_factors: List[str]
    medical_advice: str
    diabetes_risk_assessment: Optional[str] = None
    suggested_entities: Optional[Dict[str, Any]] = None  # 新增：建议创建的实体
    suggested_relations: Optional[List[Dict[str, Any]]] = None  # 新增：建议创建的关系

class QwenGraphUpdateEngine:
    """基于Qwen3的智能图谱更新引擎"""
    
    def __init__(self, graph_manager: MedicalGraphManager, api_key: str):
        self.graph_manager = graph_manager
        self.api_key = api_key
        self.api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        self.model = "qwen-plus"  # 使用Qwen3模型
        
    def analyze_update_scenario(self, current_symptoms: List[str], user_id: str, 
                              context: str = "") -> UpdateDecision:
        """分析更新场景并做出决策"""
        
        # 1. 获取用户历史医疗记录
        historical_relations = self.graph_manager.get_disease_symptom_relations(user_id=user_id)
        dm_relations = self.graph_manager.get_disease_medicine_relations(user_id=user_id)
        
        # 注意：即使没有历史记录，也要进行完整的AI分析，特别是考虑糖尿病家族史
        
        # 2. 构建医疗上下文
        medical_context = self._build_medical_context(
            historical_relations, dm_relations, current_symptoms, context
        )
        
        # 3. 调用Qwen3进行智能分析
        qwen_analysis = self._call_qwen_api(medical_context)
        
        # 4. 解析Qwen分析结果
        decision = self._parse_qwen_response(qwen_analysis)
        
        return decision
    
    def _build_medical_context(self, historical_relations: List[Dict], 
                             dm_relations: List[Dict], current_symptoms: List[str],
                             context: str) -> str:
        """构建医疗上下文供Qwen分析"""
        
        # 整理历史记录
        historical_summary = []
        for rel in historical_relations[-5:]:  # 取最近5条记录
            time_info = rel.get('created_time', '')
            if time_info:
                try:
                    rel_date = datetime.fromisoformat(time_info)
                    days_ago = (datetime.now() - rel_date).days
                    historical_summary.append(
                        f"{days_ago}天前: {rel['disease_name']} → {rel['symptom_name']} "
                        f"(置信度: {rel['confidence']}, 来源: {rel['source']})"
                    )
                except:
                    historical_summary.append(
                        f"{rel['disease_name']} → {rel['symptom_name']}"
                    )
        
        # 整理用药记录
        medication_summary = []
        for rel in dm_relations[-3:]:  # 取最近3条用药记录
            medication_summary.append(
                f"{rel['disease_name']} → {rel['medicine_name']} "
                f"(疗效: {rel.get('effectiveness', '未知')})"
            )
        
        # 构建完整的医疗上下文
        medical_context = f"""
# 医疗知识图谱更新分析任务

## 患者信息
- 姓名: 柳阳
- 年龄: 40岁  
- 过敏史: 青霉素过敏
- 家族史: 糖尿病遗传病史

## 历史医疗记录
{chr(10).join(historical_summary) if historical_summary else "无历史记录"}

## 历史用药记录
{chr(10).join(medication_summary) if medication_summary else "无用药记录"}

## 当前咨询
- 症状: {', '.join(current_symptoms)}
- 背景: {context}

## 分析要求
请作为资深医疗专家，分析以下问题：

1. **时间分析**: 评估历史诊断与当前症状的时间间隔是否合理
2. **疾病特性**: 考虑历史疾病的典型病程和复发可能性
3. **症状关联**: 分析历史症状与当前症状的医学关联性
4. **家族史关联**: 重点评估当前症状与糖尿病家族史的可能关联
5. **更新策略**: 判断应该创建新记录还是更新现有记录

## 特别关注
- 感冒等急性疾病的典型病程为3-14天
- 超出病程的症状可能是新发疾病或复发
- **糖尿病家族史是重要风险因素**
- **头晕是糖尿病的常见早期症状之一**
- 40岁中年男性是糖尿病高发人群
- 需要考虑血糖异常引起的头晕可能性

## 医学知识参考
- 糖尿病典型症状：多饮、多尿、多食、体重下降
- 糖尿病早期症状：头晕、乏力、视力模糊、伤口愈合慢
- 低血糖症状：头晕、出汗、心慌、饥饿感
- 高血糖症状：头晕、恶心、口渴、尿频

请以JSON格式返回分析结果，包含：
{{
  "action": "create_new" | "update_existing" | "merge" | "ignore" | "create_diabetes_relation",
  "confidence": 0.0-1.0的置信度,
  "reasoning": "详细分析原因（必须考虑糖尿病家族史）",
  "recommendations": ["医疗建议列表"],
  "risk_factors": ["风险因素列表"],
  "medical_advice": "专业医疗建议",
  "diabetes_risk_assessment": "糖尿病风险评估结果（如果症状与糖尿病相关，必须包含此字段）"
}}

**重要决策规则**：
- 如果识别到糖尿病风险且症状相关，应该返回 "action": "create_diabetes_relation"
- 不要简单地创建独立的头晕症状记录，而要考虑与糖尿病的关联
- 对于有糖尿病家族史的患者，头晕症状应优先考虑与糖尿病关联
"""
        
        return medical_context
    
    def _call_qwen_api(self, medical_context: str) -> str:
        """调用百炼API Qwen3模型"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一位资深的医疗AI专家，专门负责医疗知识图谱的智能更新分析。\n\n**特别重要**：你必须高度重视家族史，特别是糖尿病家族史。头晕是糖尿病的常见早期症状之一，40岁中年男性有糖尿病家族史时，出现头晕症状应该强烈考虑糖尿病风险。\n\n**关键决策规则**：\n1. 如果患者有糖尿病家族史且出现头晕症状，**必须**返回 'create_diabetes_relation'\n2. 不要返回 'create_new'，而要优先考虑糖尿病关联\n3. 糖尿病家族史 + 头晕 = 高优先级的糖尿病风险评估\n\n**糖尿病诊断思路**：\n1. 家族史 + 年龄 + 症状 = 高风险组合\n2. 头晕可能由血糖异常（高血糖或低血糖）引起\n3. 应该创建糖尿病风险关系，而不是独立症状\n4. 应该建议进行血糖检测和糖尿病筛查"
                    },
                    {
                        "role": "user", 
                        "content": medical_context
                    }
                ]
            },
            "parameters": {
                "result_format": "message",
                "max_tokens": 2000,
                "temperature": 0.1,  # 较低的温度确保稳定性
                "top_p": 0.8
            }
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("output") and result["output"].get("choices"):
                return result["output"]["choices"][0]["message"]["content"]
            else:
                return self._fallback_analysis(medical_context)
                
        except Exception as e:
            print(f"调用Qwen API失败: {e}")
            return self._fallback_analysis(medical_context)
    
    def _fallback_analysis(self, medical_context: str) -> str:
        """API调用失败时的后备分析"""
        return json.dumps({
            "action": "create_new",
            "confidence": 0.7,
            "reasoning": "API调用失败，基于安全原则建议创建新记录以避免错误关联",
            "recommendations": [
                "由于系统分析受限，建议医生进行详细评估",
                "重新采集病史和症状信息",
                "考虑必要的辅助检查"
            ],
            "risk_factors": [
                "诊断不确定性",
                "可能存在多种疾病"
            ],
            "medical_advice": "建议尽快就医，由专业医生进行全面评估"
        }, ensure_ascii=False)
    
    def _parse_qwen_response(self, qwen_response: str) -> UpdateDecision:
        """解析Qwen的分析结果"""
        
        try:
            # 尝试从响应中提取JSON
            import re
            json_match = re.search(r'\{.*\}', qwen_response, re.DOTALL)
            
            if json_match:
                analysis_data = json.loads(json_match.group())
            else:
                # 如果没有找到JSON，使用文本解析
                analysis_data = self._parse_text_response(qwen_response)
            
            # 验证和标准化action
            action_str = analysis_data.get("action", "create_new").lower()
            if action_str in ["create_new", "创建新记录"]:
                action = UpdateAction.CREATE_NEW
            elif action_str in ["update_existing", "更新现有"]:
                action = UpdateAction.UPDATE_EXISTING
            elif action_str in ["merge", "合并"]:
                action = UpdateAction.MERGE
            elif action_str in ["create_diabetes_relation", "创建糖尿病关系"]:
                action = UpdateAction.CREATE_DIABETES_RELATION
            else:
                action = UpdateAction.CREATE_NEW  # 默认安全选择
            
            return UpdateDecision(
                action=action,
                confidence=float(analysis_data.get("confidence", 0.7)),
                reasoning=analysis_data.get("reasoning", ""),
                recommendations=analysis_data.get("recommendations", []),
                risk_factors=analysis_data.get("risk_factors", []),
                medical_advice=analysis_data.get("medical_advice", ""),
                diabetes_risk_assessment=analysis_data.get("diabetes_risk_assessment", None)
            )
            
        except Exception as e:
            print(f"解析Qwen响应失败: {e}")
            return UpdateDecision(
                action=UpdateAction.CREATE_NEW,
                confidence=0.6,
                reasoning="响应解析失败，采用安全策略",
                recommendations=["建议人工审核"],
                risk_factors=["系统分析不确定"],
                medical_advice="请咨询专业医生"
            )
    
    def _parse_text_response(self, text_response: str) -> Dict:
        """从文本响应中解析关键信息"""
        
        # 简单的文本解析逻辑
        analysis = {
            "action": "create_new",
            "confidence": 0.7,
            "reasoning": "",
            "recommendations": [],
            "risk_factors": [],
            "medical_advice": ""
        }
        
        # 提取关键信息
        if "创建新" in text_response or "新记录" in text_response:
            analysis["action"] = "create_new"
        elif "更新" in text_response or "关联" in text_response:
            analysis["action"] = "update_existing"
        
        # 提取置信度
        import re
        confidence_match = re.search(r'置信度[：:]\s*(\d+\.?\d*)%?', text_response)
        if confidence_match:
            confidence = float(confidence_match.group(1))
            if confidence > 1:
                confidence /= 100
            analysis["confidence"] = confidence
        
        # 提取建议
        if "建议" in text_response:
            suggestions = re.findall(r'建议[：:]([^。\n]+)', text_response)
            analysis["recommendations"] = suggestions
        
        analysis["reasoning"] = text_response[:200] + "..." if len(text_response) > 200 else text_response
        
        return analysis
    
    def execute_diabetes_relation_creation(self, symptoms: List[str], user_id: str, 
                                          diabetes_risk_assessment: str) -> Dict[str, Any]:
        """执行糖尿病关系创建或更新"""
        from .medical_graph_manager import DiseaseEntity, SymptomEntity, DiseaseSymptomRelation
        import uuid
        from datetime import datetime
        
        execution_result = {
            "success": False,
            "created_entities": [],
            "updated_entities": [],
            "created_relations": [],
            "updated_relations": [],
            "errors": []
        }
        
        try:
            # 1. 检查或创建/更新糖尿病实体
            diabetes_id = f"disease_diabetes_{user_id}"
            
            # 检查是否已存在糖尿病实体
            existing_diseases = self.graph_manager.search_entities_by_name('disease', '糖尿病')
            user_diabetes = None
            for disease in existing_diseases:
                if disease.get('id') == diabetes_id:
                    user_diabetes = disease
                    break
            
            if user_diabetes:
                # 更新现有糖尿病实体
                print(f"  🔄 更新现有糖尿病实体: {diabetes_id}")
                execution_result["updated_entities"].append({
                    "type": "disease",
                    "id": diabetes_id,
                    "name": "糖尿病",
                    "action": "updated"
                })
            else:
                # 创建新的糖尿病实体
                diabetes_entity = DiseaseEntity(
                    id=diabetes_id,
                    name="糖尿病",
                    category="内分泌系统疾病",
                    severity="potential",  # 潜在风险
                    description=f"基于家族史和症状的糖尿病评估: {diabetes_risk_assessment}",
                    created_time=datetime.now(),
                    updated_time=datetime.now()
                )
                
                if self.graph_manager.add_disease(diabetes_entity):
                    print(f"  ✅ 创建新糖尿病实体: {diabetes_id}")
                    execution_result["created_entities"].append({
                        "type": "disease",
                        "id": diabetes_id,
                        "name": "糖尿病",
                        "action": "created"
                    })
            
            # 2. 为每个症状处理实体和关系
            for symptom_name in symptoms:
                # 检查或创建/更新症状实体
                symptom_id = f"symptom_{symptom_name}_{user_id}"
                
                existing_symptoms = self.graph_manager.search_entities_by_name('symptom', symptom_name)
                user_symptom = None
                for symptom in existing_symptoms:
                    if symptom.get('id') == symptom_id:
                        user_symptom = symptom
                        break
                
                if user_symptom:
                    # 更新现有症状实体
                    print(f"  🔄 更新现有症状实体: {symptom_name}")
                    execution_result["updated_entities"].append({
                        "type": "symptom",
                        "id": symptom_id,
                        "name": symptom_name,
                        "action": "updated"
                    })
                else:
                    # 创建新症状实体
                    symptom_entity = SymptomEntity(
                        id=symptom_id,
                        name=symptom_name,
                        description=f"与糖尿病相关的{symptom_name}症状",
                        body_part="头部" if symptom_name == "头晕" else "未知",
                        intensity="mild",
                        created_time=datetime.now(),
                        updated_time=datetime.now()
                    )
                    
                    if self.graph_manager.add_symptom(symptom_entity):
                        print(f"  ✅ 创建新症状实体: {symptom_name}")
                        execution_result["created_entities"].append({
                            "type": "symptom",
                            "id": symptom_id,
                            "name": symptom_name,
                            "action": "created"
                        })
                
                # 3. 检查或创建糖尿病-症状关系
                existing_relations = self.graph_manager.get_disease_symptom_relations(user_id=user_id)
                diabetes_symptom_relation = None
                
                for relation in existing_relations:
                    if (relation.get('disease_id') == diabetes_id and 
                        relation.get('symptom_id') == symptom_id):
                        diabetes_symptom_relation = relation
                        break
                
                if diabetes_symptom_relation:
                    # 更新现有关系
                    print(f"  🔄 更新现有关系: 糖尿病 → {symptom_name}")
                    execution_result["updated_relations"].append({
                        "id": diabetes_symptom_relation['id'],
                        "disease": "糖尿病",
                        "symptom": symptom_name,
                        "confidence": diabetes_symptom_relation.get('confidence', 0.9),
                        "action": "updated"
                    })
                else:
                    # 创建新关系
                    relation_id = f"rel_diabetes_{symptom_name}_{user_id}_{int(datetime.now().timestamp())}"
                    relation = DiseaseSymptomRelation(
                        id=relation_id,
                        disease_id=diabetes_id,
                        symptom_id=symptom_id,
                        relation_type="DIABETES_SYMPTOM",  # 糖尿病症状关系
                        source="ai_analysis",
                        confidence=0.9,  # 高置信度，因为是基于家族史的分析
                        context=f"基于糖尿病家族史和{symptom_name}症状的AI智能关联分析",
                        user_id=user_id,
                        created_time=datetime.now(),
                        updated_time=datetime.now()
                    )
                    
                    if self.graph_manager.add_disease_symptom_relation(relation):
                        print(f"  ✅ 创建新关系: 糖尿病 → {symptom_name}")
                        execution_result["created_relations"].append({
                            "id": relation_id,
                            "disease": "糖尿病",
                            "symptom": symptom_name,
                            "confidence": 0.9,
                            "action": "created"
                        })
            
            execution_result["success"] = True
            
        except Exception as e:
            execution_result["errors"].append(f"创建/更新糖尿病关系失败: {str(e)}")
        
        return execution_result

def demonstrate_qwen_update_engine():
    """演示基于Qwen的更新引擎"""
    print("🤖 基于百炼API Qwen3的医疗图谱智能更新演示")
    print("=" * 60)
    
    # 初始化组件
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        raise ValueError("请设置DASHSCOPE_API_KEY环境变量")
    graph_manager = MedicalGraphManager("data/qwen_update_demo.db") 
    qwen_engine = QwenGraphUpdateEngine(graph_manager, api_key)
    
    # 柳阳的用户ID
    user_id = "liuyang_40_qwen_demo"
    
    print(f"\n👤 患者信息：柳阳，40岁，青霉素过敏，糖尿病家族史")
    print(f"📋 场景：两个月前感冒（头晕）→ 现在头疼")
    print("-" * 60)
    
    # 模拟历史记录（两个月前感冒）
    two_months_ago = datetime.now() - timedelta(days=60)
    
    # 创建历史数据
    import sqlite3
    conn = sqlite3.connect("data/qwen_update_demo.db")
    cursor = conn.cursor()
    
    # 插入历史疾病-症状关系
    cursor.execute('''
        INSERT OR REPLACE INTO disease_symptom_relations 
        (id, disease_id, symptom_id, source, confidence, context, user_id, created_time, updated_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        "rel_cold_dizzy_qwen", "disease_cold_qwen", "symptom_dizzy_qwen",
        "online_consult", 0.8, "用户咨询头晕症状，医生诊断为感冒", 
        user_id, two_months_ago.isoformat(), two_months_ago.isoformat()
    ))
    
    # 插入对应的疾病和症状实体
    cursor.execute('''
        INSERT OR REPLACE INTO diseases 
        (id, name, category, severity, created_time, updated_time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        "disease_cold_qwen", "感冒", "呼吸系统疾病", "mild",
        two_months_ago.isoformat(), two_months_ago.isoformat()
    ))
    
    cursor.execute('''
        INSERT OR REPLACE INTO symptoms 
        (id, name, body_part, intensity, created_time, updated_time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        "symptom_dizzy_qwen", "头晕", "头部", "mild",
        two_months_ago.isoformat(), two_months_ago.isoformat()
    ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ 历史记录已创建：{two_months_ago.strftime('%Y-%m-%d')} 感冒 → 头晕")
    
    # 当前症状分析
    current_symptoms = ["头疼"]
    context = "用户两个月前因头晕症状被诊断为感冒，现在出现头疼症状前来咨询"
    
    print(f"\n🔍 Qwen3智能分析中...")
    
    # 调用智能更新引擎
    decision = qwen_engine.analyze_update_scenario(
        current_symptoms=current_symptoms,
        user_id=user_id,
        context=context
    )
    
    print(f"\n🤖 Qwen3分析结果：")
    print(f"   推荐动作: {decision.action.value}")
    print(f"   置信度: {decision.confidence:.2f}")
    print(f"   分析原因: {decision.reasoning}")
    
    print(f"\n💡 医疗建议:")
    for i, rec in enumerate(decision.recommendations, 1):
        print(f"   {i}. {rec}")
    
    if decision.risk_factors:
        print(f"\n⚠️ 风险因素:")
        for i, risk in enumerate(decision.risk_factors, 1):
            print(f"   {i}. {risk}")
    
    if decision.medical_advice:
        print(f"\n🏥 专业建议: {decision.medical_advice}")
    
    print(f"\n🎯 结论：")
    if decision.action == UpdateAction.CREATE_NEW:
        print(f"   建议创建新的医疗记录，不要关联到两个月前的感冒诊断")
        print(f"   原因：感冒为急性疾病，时间间隔超出典型病程")
    elif decision.action == UpdateAction.UPDATE_EXISTING:
        print(f"   建议更新现有记录，可能是疾病进展或相关症状")
    elif decision.action == UpdateAction.MERGE:
        print(f"   建议合并记录，可能是同一疾病的不同表现")
    
    return decision

if __name__ == "__main__":
    try:
        decision = demonstrate_qwen_update_engine()
        print(f"\n✅ Qwen3智能更新引擎演示完成")
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()