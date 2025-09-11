#!/usr/bin/env python3
"""
医疗知识图谱智能更新引擎
Medical Knowledge Graph Intelligent Update Engine

处理复杂的时间序列医疗数据更新场景
考虑疾病特性、时间间隔、症状关联等因素
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from .medical_graph_manager import MedicalGraphManager
from .entity_extractor import MedicalEntityExtractor

class DiseaseType(Enum):
    """疾病类型分类"""
    ACUTE = "acute"           # 急性疾病 (感冒、急性胃炎等)
    CHRONIC = "chronic"       # 慢性疾病 (糖尿病、高血压等)
    EPISODIC = "episodic"     # 发作性疾病 (偏头痛、哮喘等)
    UNKNOWN = "unknown"       # 未知类型

class UpdateAction(Enum):
    """更新动作类型"""
    CREATE_NEW = "create_new"           # 创建新关系
    UPDATE_EXISTING = "update_existing" # 更新现有关系
    IGNORE = "ignore"                   # 忽略（不更新）
    MERGE = "merge"                     # 合并关系
    SPLIT = "split"                     # 分离关系

@dataclass
class DiseaseProfile:
    """疾病特征档案"""
    name: str
    disease_type: DiseaseType
    typical_duration_days: Tuple[int, int]  # (最短, 最长) 天数
    recurrence_likelihood: float  # 复发可能性 0-1
    symptom_evolution: bool       # 症状是否会演变
    chronic_risk: float          # 慢性化风险 0-1

@dataclass
class UpdateDecision:
    """更新决策结果"""
    action: UpdateAction
    confidence: float
    reasoning: str
    recommendations: List[str]
    risk_factors: List[str]

class GraphUpdateEngine:
    """图谱智能更新引擎"""
    
    def __init__(self, graph_manager: MedicalGraphManager):
        self.graph_manager = graph_manager
        self.entity_extractor = MedicalEntityExtractor(graph_manager)
        self._init_disease_profiles()
        self._init_symptom_compatibility()
    
    def _init_disease_profiles(self):
        """初始化疾病特征档案"""
        self.disease_profiles = {
            # 急性疾病
            '感冒': DiseaseProfile(
                name='感冒',
                disease_type=DiseaseType.ACUTE,
                typical_duration_days=(3, 14),
                recurrence_likelihood=0.8,  # 感冒容易反复发作
                symptom_evolution=True,     # 症状会演变
                chronic_risk=0.1           # 很少慢性化
            ),
            '急性胃炎': DiseaseProfile(
                name='急性胃炎',
                disease_type=DiseaseType.ACUTE,
                typical_duration_days=(1, 7),
                recurrence_likelihood=0.6,
                symptom_evolution=False,
                chronic_risk=0.3
            ),
            
            # 慢性疾病
            '糖尿病': DiseaseProfile(
                name='糖尿病',
                disease_type=DiseaseType.CHRONIC,
                typical_duration_days=(365*10, 365*50),  # 终身性
                recurrence_likelihood=0.0,  # 不存在复发，是持续性的
                symptom_evolution=True,
                chronic_risk=1.0
            ),
            '高血压': DiseaseProfile(
                name='高血压',
                disease_type=DiseaseType.CHRONIC,
                typical_duration_days=(365*5, 365*50),
                recurrence_likelihood=0.0,
                symptom_evolution=True,
                chronic_risk=1.0
            ),
            
            # 发作性疾病
            '偏头痛': DiseaseProfile(
                name='偏头痛',
                disease_type=DiseaseType.EPISODIC,
                typical_duration_days=(1, 3),
                recurrence_likelihood=0.9,  # 高复发性
                symptom_evolution=False,
                chronic_risk=0.2
            ),
            '哮喘': DiseaseProfile(
                name='哮喘',
                disease_type=DiseaseType.EPISODIC,
                typical_duration_days=(1, 7),
                recurrence_likelihood=0.8,
                symptom_evolution=True,
                chronic_risk=0.7
            )
        }
    
    def _init_symptom_compatibility(self):
        """初始化症状兼容性映射"""
        # 症状相似度和关联性
        self.symptom_similarity = {
            ('头晕', '头疼'): 0.7,      # 都是头部症状，有一定关联
            ('头疼', '头痛'): 0.95,     # 基本是同一症状
            ('发热', '发烧'): 0.98,     # 同一症状的不同表达
            ('咳嗽', '咳痰'): 0.8,      # 相关症状
            ('乏力', '疲劳'): 0.9,      # 相似症状
            ('多尿', '尿频'): 0.8,      # 相关症状
            ('胸痛', '胸闷'): 0.6,      # 相关但有区别
        }
        
        # 症状演变路径（疾病发展过程中症状的变化）
        self.symptom_evolution_paths = {
            '感冒': {
                'early': ['发热', '头晕', '乏力'],
                'middle': ['咳嗽', '流鼻涕', '头疼'],
                'late': ['咳嗽', '咳痰']
            },
            '糖尿病': {
                'early': ['多尿', '多饮'],
                'middle': ['多食', '体重下降'],
                'late': ['视力模糊', '乏力']
            }
        }
    
    def analyze_update_scenario(self, current_symptoms: List[str], user_id: str, 
                              context: str = "") -> UpdateDecision:
        """分析更新场景并做出决策"""
        
        # 1. 获取用户的历史疾病-症状关系
        historical_relations = self.graph_manager.get_disease_symptom_relations(user_id=user_id)
        
        if not historical_relations:
            return UpdateDecision(
                action=UpdateAction.CREATE_NEW,
                confidence=0.9,
                reasoning="用户无历史记录，创建新的疾病-症状关系",
                recommendations=["建议医生进行详细问诊和体检"],
                risk_factors=[]
            )
        
        # 2. 分析最近的疾病诊断
        recent_diagnoses = self._get_recent_diagnoses(historical_relations)
        
        if not recent_diagnoses:
            return UpdateDecision(
                action=UpdateAction.CREATE_NEW,
                confidence=0.8,
                reasoning="无近期诊断记录，建议创建新关系",
                recommendations=["进行全面的医疗评估"],
                risk_factors=[]
            )
        
        # 3. 对每个近期诊断进行分析
        best_decision = None
        highest_confidence = 0.0
        
        for diagnosis in recent_diagnoses:
            decision = self._analyze_single_diagnosis(diagnosis, current_symptoms, user_id)
            if decision.confidence > highest_confidence:
                highest_confidence = decision.confidence
                best_decision = decision
        
        return best_decision or UpdateDecision(
            action=UpdateAction.CREATE_NEW,
            confidence=0.5,
            reasoning="无法确定最佳更新策略，建议创建新关系",
            recommendations=["需要医生进一步评估"],
            risk_factors=["诊断不确定性"]
        )
    
    def _get_recent_diagnoses(self, relations: List[Dict], days_threshold: int = 90) -> List[Dict]:
        """获取近期诊断（默认90天内）"""
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        recent = []
        
        for rel in relations:
            try:
                rel_date = datetime.fromisoformat(rel['created_time'])
                if rel_date >= cutoff_date:
                    recent.append(rel)
            except:
                continue
        
        # 按疾病分组，保留最新的记录
        disease_latest = {}
        for rel in recent:
            disease = rel['disease_name']
            if disease not in disease_latest or rel['created_time'] > disease_latest[disease]['created_time']:
                disease_latest[disease] = rel
        
        return list(disease_latest.values())
    
    def _analyze_single_diagnosis(self, diagnosis: Dict, current_symptoms: List[str], 
                                user_id: str) -> UpdateDecision:
        """分析单个诊断的更新策略"""
        disease_name = diagnosis['disease_name']
        diagnosis_time = datetime.fromisoformat(diagnosis['created_time'])
        time_elapsed = (datetime.now() - diagnosis_time).days
        
        # 获取疾病特征
        disease_profile = self.disease_profiles.get(disease_name)
        if not disease_profile:
            disease_profile = DiseaseProfile(
                name=disease_name,
                disease_type=DiseaseType.UNKNOWN,
                typical_duration_days=(1, 30),
                recurrence_likelihood=0.5,
                symptom_evolution=True,
                chronic_risk=0.3
            )
        
        # 计算症状兼容性
        historical_symptom = diagnosis['symptom_name']
        symptom_compatibility = self._calculate_symptom_compatibility(
            historical_symptom, current_symptoms, disease_name
        )
        
        # 分析时间因素
        time_analysis = self._analyze_time_factor(time_elapsed, disease_profile)
        
        # 综合决策
        return self._make_update_decision(
            disease_profile, symptom_compatibility, time_analysis, 
            current_symptoms, time_elapsed, user_id
        )
    
    def _calculate_symptom_compatibility(self, historical_symptom: str, 
                                       current_symptoms: List[str], 
                                       disease_name: str) -> Dict:
        """计算症状兼容性"""
        compatibility_scores = []
        
        for current_symptom in current_symptoms:
            # 直接相似度
            similarity_key = tuple(sorted([historical_symptom, current_symptom]))
            direct_similarity = self.symptom_similarity.get(similarity_key, 0.0)
            
            # 疾病演变路径相似度
            evolution_similarity = self._get_evolution_similarity(
                historical_symptom, current_symptom, disease_name
            )
            
            # 综合评分
            total_score = max(direct_similarity, evolution_similarity)
            compatibility_scores.append({
                'symptom': current_symptom,
                'score': total_score,
                'direct_similarity': direct_similarity,
                'evolution_similarity': evolution_similarity
            })
        
        return {
            'scores': compatibility_scores,
            'max_score': max([s['score'] for s in compatibility_scores]) if compatibility_scores else 0.0,
            'avg_score': sum([s['score'] for s in compatibility_scores]) / len(compatibility_scores) if compatibility_scores else 0.0
        }
    
    def _get_evolution_similarity(self, historical_symptom: str, current_symptom: str, 
                                disease_name: str) -> float:
        """获取疾病演变路径中的症状相似度"""
        evolution_path = self.symptom_evolution_paths.get(disease_name, {})
        
        # 检查是否在同一演变阶段或相邻阶段
        historical_stage = None
        current_stage = None
        
        for stage, symptoms in evolution_path.items():
            if historical_symptom in symptoms:
                historical_stage = stage
            if current_symptom in symptoms:
                current_stage = stage
        
        if historical_stage and current_stage:
            if historical_stage == current_stage:
                return 0.8  # 同一阶段，高相似度
            elif self._are_adjacent_stages(historical_stage, current_stage):
                return 0.6  # 相邻阶段，中等相似度
        
        return 0.0
    
    def _are_adjacent_stages(self, stage1: str, stage2: str) -> bool:
        """判断是否是相邻的疾病发展阶段"""
        stage_order = ['early', 'middle', 'late']
        try:
            idx1 = stage_order.index(stage1)
            idx2 = stage_order.index(stage2)
            return abs(idx1 - idx2) == 1
        except:
            return False
    
    def _analyze_time_factor(self, time_elapsed: int, disease_profile: DiseaseProfile) -> Dict:
        """分析时间因素"""
        min_duration, max_duration = disease_profile.typical_duration_days
        
        analysis = {
            'time_elapsed': time_elapsed,
            'within_typical_duration': min_duration <= time_elapsed <= max_duration,
            'beyond_typical_duration': time_elapsed > max_duration,
            'recurrence_possible': time_elapsed > max_duration and disease_profile.recurrence_likelihood > 0.5,
            'chronic_development_risk': time_elapsed > max_duration and disease_profile.chronic_risk > 0.3
        }
        
        return analysis
    
    def _make_update_decision(self, disease_profile: DiseaseProfile, 
                            symptom_compatibility: Dict, time_analysis: Dict,
                            current_symptoms: List[str], time_elapsed: int, 
                            user_id: str) -> UpdateDecision:
        """综合各因素做出更新决策"""
        
        max_compatibility = symptom_compatibility['max_score']
        disease_type = disease_profile.disease_type
        
        # 决策逻辑
        if disease_type == DiseaseType.ACUTE:
            return self._decide_for_acute_disease(
                disease_profile, symptom_compatibility, time_analysis, current_symptoms
            )
        elif disease_type == DiseaseType.CHRONIC:
            return self._decide_for_chronic_disease(
                disease_profile, symptom_compatibility, time_analysis, current_symptoms
            )
        elif disease_type == DiseaseType.EPISODIC:
            return self._decide_for_episodic_disease(
                disease_profile, symptom_compatibility, time_analysis, current_symptoms
            )
        else:
            return self._decide_for_unknown_disease(
                disease_profile, symptom_compatibility, time_analysis, current_symptoms
            )
    
    def _decide_for_acute_disease(self, disease_profile: DiseaseProfile,
                                symptom_compatibility: Dict, time_analysis: Dict,
                                current_symptoms: List[str]) -> UpdateDecision:
        """为急性疾病做决策"""
        max_compatibility = symptom_compatibility['max_score']
        time_elapsed = time_analysis['time_elapsed']
        
        # 如果在典型病程内且症状高度相似，更新现有关系
        if time_analysis['within_typical_duration'] and max_compatibility > 0.7:
            return UpdateDecision(
                action=UpdateAction.UPDATE_EXISTING,
                confidence=0.8,
                reasoning=f"在{disease_profile.name}典型病程内({time_elapsed}天)，症状相似度高({max_compatibility:.2f})",
                recommendations=[f"继续观察{disease_profile.name}的症状发展", "如症状加重请及时就医"],
                risk_factors=[]
            )
        
        # 如果超出典型病程但有复发可能性
        elif time_analysis['beyond_typical_duration'] and disease_profile.recurrence_likelihood > 0.5:
            if max_compatibility > 0.5:
                return UpdateDecision(
                    action=UpdateAction.CREATE_NEW,
                    confidence=0.7,
                    reasoning=f"{disease_profile.name}可能复发，但时间间隔较长({time_elapsed}天)，建议创建新记录",
                    recommendations=[f"评估{disease_profile.name}复发原因", "检查是否有并发症或其他疾病"],
                    risk_factors=[f"{disease_profile.name}反复发作", "可能存在其他潜在疾病"]
                )
            else:
                return UpdateDecision(
                    action=UpdateAction.CREATE_NEW,
                    confidence=0.8,
                    reasoning=f"症状与历史{disease_profile.name}关联性低，且时间间隔长，可能是新疾病",
                    recommendations=["进行全面诊断评估", "排除其他疾病可能性"],
                    risk_factors=["新发疾病风险"]
                )
        
        # 时间过长，症状相似度低
        else:
            return UpdateDecision(
                action=UpdateAction.CREATE_NEW,
                confidence=0.9,
                reasoning=f"时间间隔过长({time_elapsed}天)，超出{disease_profile.name}典型病程，应视为新的医疗事件",
                recommendations=["重新进行诊断评估", "不要受历史诊断影响"],
                risk_factors=[]
            )
    
    def _decide_for_chronic_disease(self, disease_profile: DiseaseProfile,
                                  symptom_compatibility: Dict, time_analysis: Dict,
                                  current_symptoms: List[str]) -> UpdateDecision:
        """为慢性疾病做决策"""
        max_compatibility = symptom_compatibility['max_score']
        
        # 慢性疾病通常更新现有关系
        if max_compatibility > 0.6:
            return UpdateDecision(
                action=UpdateAction.UPDATE_EXISTING,
                confidence=0.9,
                reasoning=f"{disease_profile.name}为慢性疾病，新症状可能是疾病进展的表现",
                recommendations=[f"监测{disease_profile.name}病情变化", "调整治疗方案", "定期复查"],
                risk_factors=[f"{disease_profile.name}病情进展", "并发症风险"]
            )
        else:
            return UpdateDecision(
                action=UpdateAction.CREATE_NEW,
                confidence=0.7,
                reasoning=f"新症状与{disease_profile.name}关联性低，可能是并发疾病或新发疾病",
                recommendations=["评估是否为并发症", "排查其他疾病可能性"],
                risk_factors=[f"{disease_profile.name}并发症", "多重疾病风险"]
            )
    
    def _decide_for_episodic_disease(self, disease_profile: DiseaseProfile,
                                   symptom_compatibility: Dict, time_analysis: Dict,
                                   current_symptoms: List[str]) -> UpdateDecision:
        """为发作性疾病做决策"""
        max_compatibility = symptom_compatibility['max_score']
        
        # 发作性疾病容易复发
        if max_compatibility > 0.7:
            return UpdateDecision(
                action=UpdateAction.CREATE_NEW,
                confidence=0.8,
                reasoning=f"{disease_profile.name}为发作性疾病，此次可能是新的发作",
                recommendations=[f"记录{disease_profile.name}发作模式", "寻找发作诱因", "预防性治疗"],
                risk_factors=[f"{disease_profile.name}反复发作"]
            )
        else:
            return UpdateDecision(
                action=UpdateAction.CREATE_NEW,
                confidence=0.8,
                reasoning=f"症状与历史{disease_profile.name}不匹配，可能是其他疾病",
                recommendations=["鉴别诊断", "排除其他疾病"],
                risk_factors=["新发疾病风险"]
            )
    
    def _decide_for_unknown_disease(self, disease_profile: DiseaseProfile,
                                  symptom_compatibility: Dict, time_analysis: Dict,
                                  current_symptoms: List[str]) -> UpdateDecision:
        """为未知类型疾病做决策"""
        return UpdateDecision(
            action=UpdateAction.CREATE_NEW,
            confidence=0.6,
            reasoning="疾病特征不明确，建议创建新记录以避免错误关联",
            recommendations=["详细病史询问", "全面体格检查", "必要的辅助检查"],
            risk_factors=["诊断不确定性"]
        )

def demonstrate_update_scenario():
    """演示更新场景"""
    print("🏥 医疗知识图谱智能更新演示")
    print("=" * 60)
    
    # 初始化组件
    graph_manager = MedicalGraphManager("data/update_demo.db")
    update_engine = GraphUpdateEngine(graph_manager)
    
    # 模拟用户ID（柳阳，40岁）
    user_id = "liuyang_40_update_demo"
    
    # 场景1：模拟两个月前的感冒诊断
    print("\n📅 场景设置：两个月前的感冒诊断")
    print("-" * 40)
    
    # 创建历史记录（两个月前）
    two_months_ago = datetime.now() - timedelta(days=60)
    
    # 手动插入历史数据
    conn = sqlite3.connect("data/update_demo.db")
    cursor = conn.cursor()
    
    # 插入疾病实体
    disease_id = "disease_cold_001"
    cursor.execute('''
        INSERT OR REPLACE INTO diseases 
        (id, name, category, severity, created_time, updated_time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (disease_id, "感冒", "呼吸系统疾病", "mild", 
          two_months_ago.isoformat(), two_months_ago.isoformat()))
    
    # 插入症状实体
    symptom_id = "symptom_dizzy_001"
    cursor.execute('''
        INSERT OR REPLACE INTO symptoms 
        (id, name, body_part, intensity, created_time, updated_time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (symptom_id, "头晕", "头部", "mild", 
          two_months_ago.isoformat(), two_months_ago.isoformat()))
    
    # 插入疾病-症状关系
    relation_id = "rel_cold_dizzy_001"
    cursor.execute('''
        INSERT OR REPLACE INTO disease_symptom_relations 
        (id, disease_id, symptom_id, source, confidence, context, user_id, created_time, updated_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (relation_id, disease_id, symptom_id, "online_consult", 0.8, 
          "用户咨询头晕症状，医生诊断为感冒", user_id, 
          two_months_ago.isoformat(), two_months_ago.isoformat()))
    
    conn.commit()
    conn.close()
    
    print(f"✅ 已创建历史记录：{two_months_ago.strftime('%Y-%m-%d')} - 感冒 → 头晕")
    
    # 场景2：现在的新症状咨询
    print(f"\n📅 当前咨询：{datetime.now().strftime('%Y-%m-%d')} - 新症状：头疼")
    print("-" * 40)
    
    current_symptoms = ["头疼"]
    
    # 分析更新策略
    decision = update_engine.analyze_update_scenario(
        current_symptoms=current_symptoms,
        user_id=user_id,
        context="用户再次咨询，主诉头疼症状"
    )
    
    print(f"🤖 智能分析结果:")
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
    
    # 场景3：演示不同的时间间隔对决策的影响
    print(f"\n🔬 对比分析：不同时间间隔的决策差异")
    print("-" * 50)
    
    time_scenarios = [
        (3, "3天前（感冒病程内）"),
        (14, "14天前（感冒末期）"),
        (30, "30天前（超出感冒病程）"),
        (60, "60天前（当前场景）")
    ]
    
    for days, description in time_scenarios:
        # 创建临时的历史记录
        test_date = datetime.now() - timedelta(days=days)
        
        # 临时修改数据库记录的时间
        conn = sqlite3.connect("data/update_demo.db")
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE disease_symptom_relations 
            SET created_time = ?, updated_time = ?
            WHERE user_id = ?
        ''', (test_date.isoformat(), test_date.isoformat(), user_id))
        conn.commit()
        conn.close()
        
        # 分析决策
        test_decision = update_engine.analyze_update_scenario(
            current_symptoms=["头疼"],
            user_id=user_id
        )
        
        print(f"   {description}:")
        print(f"     动作: {test_decision.action.value}, 置信度: {test_decision.confidence:.2f}")
        print(f"     原因: {test_decision.reasoning[:60]}...")
    
    # 恢复原始时间
    conn = sqlite3.connect("data/update_demo.db")
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE disease_symptom_relations 
        SET created_time = ?, updated_time = ?
        WHERE user_id = ?
    ''', (two_months_ago.isoformat(), two_months_ago.isoformat(), user_id))
    conn.commit()
    conn.close()
    
    print(f"\n🎯 核心结论:")
    print(f"   对于感冒这种急性疾病，两个月的时间间隔已超出其典型病程")
    print(f"   应该创建新的医疗记录，而不是更新原有的感冒诊断")
    print(f"   这样可以避免错误的医疗推断，保证诊断的准确性")

if __name__ == "__main__":
    demonstrate_update_scenario()