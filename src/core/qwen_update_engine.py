#!/usr/bin/env python3
"""
基于Qwen3模型的智能医疗知识图谱更新引擎
Enhanced Medical Knowledge Graph Update Engine with Qwen3 Model

使用统一的百炼API客户端配置，为患者医疗场景优化
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import time

# 导入统一的百炼API客户端
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys_path not in sys.path:
    import sys
    sys.path.insert(0, sys_path)

from configs.dashscope_client import DashScopeClientFactory, BaseDashScopeClient

from .graph_update_engine import (
    GraphUpdateEngine, DiseaseProfile, UpdateDecision, UpdateAction, DiseaseType
)
from .medical_graph_manager import MedicalGraphManager


class QwenGraphUpdateEngine(GraphUpdateEngine):
    """基于Qwen3的增强图谱更新引擎（使用统一客户端配置）"""
    
    def __init__(self, graph_manager: MedicalGraphManager, api_key: str = None):
        super().__init__(graph_manager)
        
        # 使用统一的客户端工厂创建医疗专用客户端
        try:
            self.qwen_client = DashScopeClientFactory.create_medical_client(
                api_key=api_key,
                max_tokens=2000,
                temperature=0.1
            )
            print("✅ Qwen3增强图谱更新引擎初始化完成（使用统一医疗客户端）")
        except Exception as e:
            print(f"❌ 客户端初始化失败: {e}")
            raise
    
    def analyze_with_ai(self, current_symptoms: List[str], user_id: str, 
                       context: str = "") -> UpdateDecision:
        """使用AI增强的场景分析"""
        print(f"🤖 使用Qwen3模型分析更新场景...")
        
        # 1. 先使用基础规则分析
        base_decision = super().analyze_update_scenario(current_symptoms, user_id, context)
        
        # 2. 收集历史信息
        historical_relations = self.graph_manager.get_disease_symptom_relations(user_id=user_id)
        
        # 3. 构建AI分析提示
        ai_prompt = self._build_ai_prompt(
            current_symptoms, historical_relations, base_decision, context
        )
        
        try:
            # 4. 调用Qwen3分析
            ai_response = self.qwen_client.generate_response(ai_prompt)
            
            # 5. 整合AI分析结果
            enhanced_decision = self._integrate_ai_analysis(base_decision, ai_response)
            
            print(f"✅ Qwen3分析完成，置信度: {enhanced_decision.confidence:.2f}")
            return enhanced_decision
            
        except Exception as e:
            print(f"⚠️ AI分析失败，使用基础规则: {e}")
            return base_decision
    
    def _build_ai_prompt(self, current_symptoms: List[str], 
                        historical_relations: List[Dict], 
                        base_decision: UpdateDecision,
                        context: str) -> str:
        """构建AI分析提示"""
        
        recent_diagnoses = self._get_recent_diagnoses(historical_relations, days_threshold=180)
        
        prompt = f"""
分析以下医疗知识图谱更新场景：

**当前症状：**
{', '.join(current_symptoms)}

**病史信息：**
"""
        
        if recent_diagnoses:
            for i, diagnosis in enumerate(recent_diagnoses, 1):
                diagnosis_date = diagnosis.get('created_time', 'Unknown')
                try:
                    date_obj = datetime.fromisoformat(diagnosis_date)
                    days_ago = (datetime.now() - date_obj).days
                    formatted_date = f"{days_ago}天前"
                except:
                    formatted_date = diagnosis_date
                
                prompt += f"""
{i}. {formatted_date}: {diagnosis.get('disease_name', 'Unknown')} → {diagnosis.get('symptom_name', 'Unknown')}
"""
        else:
            prompt += "\n无相关病史"
        
        prompt += f"""

**上下文：**
{context if context else '无'}

**基础分析：**
- 动作: {base_decision.action.value}
- 置信度: {base_decision.confidence:.2f}
- 原因: {base_decision.reasoning}

请分析：
1. 医学关联性
2. 时间因素影响
3. 诊断风险评估

以JSON格式返回：
```json
{{
    "medical_analysis": "医学分析",
    "recommended_action": "CREATE_NEW/UPDATE_EXISTING/IGNORE/MERGE/SPLIT",
    "confidence_score": 0.85,
    "key_reasoning": "核心原因",
    "clinical_recommendations": ["建议1", "建议2"],
    "risk_factors": ["风险1", "风险2"]
}}
```
"""
        
        return prompt
    
    def _integrate_ai_analysis(self, base_decision: UpdateDecision, 
                             ai_response: str) -> UpdateDecision:
        """整合AI分析结果"""
        try:
            # 提取JSON
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("未找到JSON响应")
            
            json_str = ai_response[json_start:json_end]
            ai_analysis = json.loads(json_str)
            
            # 映射动作
            action_mapping = {
                "CREATE_NEW": UpdateAction.CREATE_NEW,
                "UPDATE_EXISTING": UpdateAction.UPDATE_EXISTING,
                "IGNORE": UpdateAction.IGNORE,
                "MERGE": UpdateAction.MERGE,
                "SPLIT": UpdateAction.SPLIT
            }
            
            ai_action = action_mapping.get(
                ai_analysis.get("recommended_action", "CREATE_NEW"),
                UpdateAction.CREATE_NEW
            )
            
            # 计算综合置信度
            ai_confidence = float(ai_analysis.get("confidence_score", 0.5))
            combined_confidence = 0.3 * base_decision.confidence + 0.7 * ai_confidence
            
            # 整合信息
            combined_reasoning = f"AI分析: {ai_analysis.get('key_reasoning', '')} | 规则分析: {base_decision.reasoning}"
            
            combined_recommendations = list(base_decision.recommendations)
            combined_recommendations.extend(ai_analysis.get("clinical_recommendations", []))
            
            combined_risk_factors = list(base_decision.risk_factors)
            combined_risk_factors.extend(ai_analysis.get("risk_factors", []))
            
            return UpdateDecision(
                action=ai_action,
                confidence=min(combined_confidence, 1.0),
                reasoning=combined_reasoning[:500],
                recommendations=combined_recommendations[:8],
                risk_factors=combined_risk_factors[:6]
            )
            
        except Exception as e:
            print(f"⚠️ 整合AI分析失败: {e}")
            return UpdateDecision(
                action=base_decision.action,
                confidence=base_decision.confidence * 0.9,
                reasoning=f"AI分析异常，使用规则分析: {base_decision.reasoning}",
                recommendations=base_decision.recommendations + ["建议人工复核"],
                risk_factors=base_decision.risk_factors + ["AI分析不可用"]
            )
    
    def generate_medical_report(self, user_id: str, decisions: List[UpdateDecision]) -> str:
        """生成医疗分析报告"""
        print(f"📊 生成医疗分析报告...")
        
        prompt = f"""
基于以下分析结果，生成医疗报告：

**患者：** {user_id}

**分析结果：**
"""
        
        for i, decision in enumerate(decisions, 1):
            prompt += f"""
{i}. 动作: {decision.action.value}, 置信度: {decision.confidence:.2f}
   原因: {decision.reasoning}
"""
        
        prompt += """

生成包含以下内容的报告：
1. 总体评估
2. 关键发现
3. 医疗建议
4. 风险管理
5. 随访重点
"""
        
        try:
            return self.qwen_client.generate_response(prompt, max_tokens=1000)
        except Exception as e:
            return f"报告生成失败: {e}"