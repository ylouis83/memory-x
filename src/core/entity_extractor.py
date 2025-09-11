#!/usr/bin/env python3
"""
医疗实体抽取器
Medical Entity Extractor

从用户在线问答中提取疾病、症状、药品实体信息
并构建知识图谱关系
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime
from dataclasses import dataclass

from .medical_graph_manager import (
    MedicalGraphManager, DiseaseEntity, SymptomEntity, MedicineEntity,
    DiseaseSymptomRelation, DiseaseMedicineRelation, SourceType, RelationType
)

@dataclass
class ExtractedEntity:
    """抽取的实体"""
    name: str
    entity_type: str  # disease/symptom/medicine
    confidence: float
    position: Tuple[int, int]  # 在文本中的位置
    context: str  # 上下文

@dataclass
class ExtractedRelation:
    """抽取的关系"""
    entity1: str
    entity2: str
    relation_type: str
    confidence: float
    context: str

class MedicalEntityExtractor:
    """医疗实体抽取器"""
    
    def __init__(self, graph_manager: MedicalGraphManager):
        self.graph_manager = graph_manager
        self._init_medical_dictionaries()
    
    def _init_medical_dictionaries(self):
        """初始化医疗词典"""
        # 疾病词典 - 基于您的糖尿病遗传病史
        self.disease_dict = {
            # 内分泌疾病
            '糖尿病': {'category': '内分泌疾病', 'severity': 'moderate', 'code': 'E11'},
            '1型糖尿病': {'category': '内分泌疾病', 'severity': 'severe', 'code': 'E10'},
            '2型糖尿病': {'category': '内分泌疾病', 'severity': 'moderate', 'code': 'E11'},
            '妊娠糖尿病': {'category': '内分泌疾病', 'severity': 'moderate', 'code': 'O24'},
            
            # 心血管疾病
            '高血压': {'category': '心血管疾病', 'severity': 'moderate', 'code': 'I10'},
            '冠心病': {'category': '心血管疾病', 'severity': 'severe', 'code': 'I25'},
            '心律不齐': {'category': '心血管疾病', 'severity': 'mild', 'code': 'I49'},
            
            # 呼吸系统疾病
            '感冒': {'category': '呼吸系统疾病', 'severity': 'mild', 'code': 'J00'},
            '肺炎': {'category': '呼吸系统疾病', 'severity': 'severe', 'code': 'J18'},
            '哮喘': {'category': '呼吸系统疾病', 'severity': 'moderate', 'code': 'J45'},
            
            # 消化系统疾病
            '胃炎': {'category': '消化系统疾病', 'severity': 'mild', 'code': 'K29'},
            '胃溃疡': {'category': '消化系统疾病', 'severity': 'moderate', 'code': 'K25'},
            '肝炎': {'category': '消化系统疾病', 'severity': 'severe', 'code': 'K75'},
        }
        
        # 症状词典
        self.symptom_dict = {
            # 全身症状
            '发热': {'body_part': '全身', 'intensity': 'moderate'},
            '乏力': {'body_part': '全身', 'intensity': 'mild'},
            '疲劳': {'body_part': '全身', 'intensity': 'mild'},
            '体重下降': {'body_part': '全身', 'intensity': 'moderate'},
            
            # 头部症状
            '头痛': {'body_part': '头部', 'intensity': 'moderate'},
            '头晕': {'body_part': '头部', 'intensity': 'mild'},
            '眼花': {'body_part': '头部', 'intensity': 'mild'},
            
            # 呼吸系统症状
            '咳嗽': {'body_part': '呼吸系统', 'intensity': 'mild'},
            '气短': {'body_part': '呼吸系统', 'intensity': 'moderate'},
            '胸闷': {'body_part': '胸部', 'intensity': 'moderate'},
            
            # 消化系统症状
            '恶心': {'body_part': '消化系统', 'intensity': 'mild'},
            '呕吐': {'body_part': '消化系统', 'intensity': 'moderate'},
            '腹痛': {'body_part': '腹部', 'intensity': 'moderate'},
            '腹泻': {'body_part': '消化系统', 'intensity': 'mild'},
            
            # 糖尿病相关症状
            '多饮': {'body_part': '全身', 'intensity': 'moderate'},
            '多尿': {'body_part': '泌尿系统', 'intensity': 'moderate'},
            '多食': {'body_part': '消化系统', 'intensity': 'moderate'},
            '口干': {'body_part': '口腔', 'intensity': 'mild'},
            '视力模糊': {'body_part': '眼部', 'intensity': 'moderate'},
        }
        
        # 药品词典 - 基于您的青霉素过敏史
        self.medicine_dict = {
            # 抗生素类 - 特别标注青霉素过敏风险
            '青霉素': {'generic_name': '青霉素', 'drug_class': '抗生素', 'prescription_required': True, 'allergy_risk': 'high'},
            '阿莫西林': {'generic_name': '阿莫西林', 'drug_class': '抗生素', 'prescription_required': True, 'allergy_risk': 'medium'},
            '头孢菌素': {'generic_name': '头孢菌素', 'drug_class': '抗生素', 'prescription_required': True, 'allergy_risk': 'medium'},
            '红霉素': {'generic_name': '红霉素', 'drug_class': '抗生素', 'prescription_required': True, 'allergy_risk': 'low'},
            
            # 糖尿病药物
            '二甲双胍': {'generic_name': '二甲双胍', 'drug_class': '降糖药', 'prescription_required': True},
            '胰岛素': {'generic_name': '胰岛素', 'drug_class': '降糖药', 'prescription_required': True},
            '格列齐特': {'generic_name': '格列齐特', 'drug_class': '降糖药', 'prescription_required': True},
            
            # 心血管药物
            '氨氯地平': {'generic_name': '氨氯地平', 'drug_class': '降压药', 'prescription_required': True},
            '硝苯地平': {'generic_name': '硝苯地平', 'drug_class': '降压药', 'prescription_required': True},
            '阿司匹林': {'generic_name': '阿司匹林', 'drug_class': '抗血小板药', 'prescription_required': False},
            
            # 常用药物
            '布洛芬': {'generic_name': '布洛芬', 'drug_class': '解热镇痛药', 'prescription_required': False},
            '对乙酰氨基酚': {'generic_name': '对乙酰氨基酚', 'drug_class': '解热镇痛药', 'prescription_required': False},
            '感冒药': {'generic_name': '复方感冒药', 'drug_class': '感冒药', 'prescription_required': False},
        }
        
        # 关系触发词
        self.consult_keywords = ['有', '出现', '症状', '感觉', '不舒服', '疼痛', '难受']
        self.treatment_keywords = ['吃', '服用', '用药', '治疗', '开药', '处方', '医生建议']
        
        # 源头识别关键词
        self.source_keywords = {
            SourceType.ONLINE_CONSULT: ['在线咨询', '网上问诊', '线上问医生', '咨询医生'],
            SourceType.PHYSICAL_EXAM: ['体检', '检查', '医院检查', '体检报告'],
            SourceType.MEDICAL_RECORD: ['病历', '就诊记录', '医疗记录', '诊断书'],
            SourceType.PRESCRIPTION: ['处方', '开药', '医生开的药', '药方'],
        }

    def extract_entities_from_text(self, text: str, user_id: str, session_id: str = None) -> Dict[str, List]:
        """从文本中抽取实体和关系"""
        result = {
            'diseases': [],
            'symptoms': [],
            'medicines': [],
            'disease_symptom_relations': [],
            'disease_medicine_relations': [],
            'source': self._detect_source(text)
        }
        
        # 抽取疾病实体
        diseases = self._extract_diseases(text)
        result['diseases'] = diseases
        
        # 抽取症状实体
        symptoms = self._extract_symptoms(text)
        result['symptoms'] = symptoms
        
        # 抽取药品实体
        medicines = self._extract_medicines(text)
        result['medicines'] = medicines
        
        # 抽取关系
        ds_relations = self._extract_disease_symptom_relations(text, diseases, symptoms, user_id, session_id, result['source'])
        result['disease_symptom_relations'] = ds_relations
        
        dm_relations = self._extract_disease_medicine_relations(text, diseases, medicines, user_id, session_id, result['source'])
        result['disease_medicine_relations'] = dm_relations
        
        return result

    def _extract_diseases(self, text: str) -> List[ExtractedEntity]:
        """抽取疾病实体"""
        diseases = []
        for disease_name, disease_info in self.disease_dict.items():
            pattern = re.compile(f'({re.escape(disease_name)})', re.IGNORECASE)
            matches = pattern.finditer(text)
            
            for match in matches:
                start, end = match.span()
                context = text[max(0, start-10):min(len(text), end+10)]
                
                diseases.append(ExtractedEntity(
                    name=disease_name,
                    entity_type='disease',
                    confidence=0.9,  # 字典匹配高置信度
                    position=(start, end),
                    context=context.strip()
                ))
        
        return diseases

    def _extract_symptoms(self, text: str) -> List[ExtractedEntity]:
        """抽取症状实体"""
        symptoms = []
        for symptom_name, symptom_info in self.symptom_dict.items():
            pattern = re.compile(f'({re.escape(symptom_name)})', re.IGNORECASE)
            matches = pattern.finditer(text)
            
            for match in matches:
                start, end = match.span()
                context = text[max(0, start-10):min(len(text), end+10)]
                
                symptoms.append(ExtractedEntity(
                    name=symptom_name,
                    entity_type='symptom',
                    confidence=0.9,
                    position=(start, end),
                    context=context.strip()
                ))
        
        return symptoms

    def _extract_medicines(self, text: str) -> List[ExtractedEntity]:
        """抽取药品实体"""
        medicines = []
        for medicine_name, medicine_info in self.medicine_dict.items():
            pattern = re.compile(f'({re.escape(medicine_name)})', re.IGNORECASE)
            matches = pattern.finditer(text)
            
            for match in matches:
                start, end = match.span()
                context = text[max(0, start-10):min(len(text), end+10)]
                
                # 特别注意青霉素过敏风险
                confidence = 0.9
                if medicine_name == '青霉素' and '过敏' in text:
                    confidence = 0.95  # 过敏相关的青霉素提及更高置信度
                
                medicines.append(ExtractedEntity(
                    name=medicine_name,
                    entity_type='medicine',
                    confidence=confidence,
                    position=(start, end),
                    context=context.strip()
                ))
        
        return medicines

    def _extract_disease_symptom_relations(self, text: str, diseases: List[ExtractedEntity], 
                                         symptoms: List[ExtractedEntity], user_id: str, 
                                         session_id: str, source: SourceType) -> List[Dict]:
        """抽取疾病-症状关系"""
        relations = []
        
        for disease in diseases:
            for symptom in symptoms:
                # 检查是否有咨询关系的触发词
                has_consult_keyword = any(keyword in text for keyword in self.consult_keywords)
                
                if has_consult_keyword:
                    # 计算位置距离，距离越近关系越可能
                    distance = abs(disease.position[0] - symptom.position[0])
                    confidence = max(0.3, 1.0 - distance / len(text))
                    
                    relations.append({
                        'disease_name': disease.name,
                        'symptom_name': symptom.name,
                        'confidence': confidence,
                        'context': text,
                        'user_id': user_id,
                        'session_id': session_id,
                        'source': source.value
                    })
        
        return relations

    def _extract_disease_medicine_relations(self, text: str, diseases: List[ExtractedEntity], 
                                          medicines: List[ExtractedEntity], user_id: str, 
                                          session_id: str, source: SourceType) -> List[Dict]:
        """抽取疾病-药品关系"""
        relations = []
        
        for disease in diseases:
            for medicine in medicines:
                # 检查是否有治疗关系的触发词
                has_treatment_keyword = any(keyword in text for keyword in self.treatment_keywords)
                
                if has_treatment_keyword:
                    # 计算位置距离
                    distance = abs(disease.position[0] - medicine.position[0])
                    confidence = max(0.3, 1.0 - distance / len(text))
                    
                    # 特别处理过敏情况
                    effectiveness = 'unknown'
                    if '过敏' in text and medicine.name in ['青霉素', '阿莫西林']:
                        effectiveness = 'contraindicated'  # 禁忌
                        confidence = 0.95
                    
                    relations.append({
                        'disease_name': disease.name,
                        'medicine_name': medicine.name,
                        'confidence': confidence,
                        'effectiveness': effectiveness,
                        'context': text,
                        'user_id': user_id,
                        'session_id': session_id,
                        'source': source.value
                    })
        
        return relations

    def _detect_source(self, text: str) -> SourceType:
        """检测数据源类型"""
        for source_type, keywords in self.source_keywords.items():
            if any(keyword in text for keyword in keywords):
                return source_type
        
        # 默认为在线咨询
        return SourceType.ONLINE_CONSULT

    def process_user_message(self, message: str, user_id: str, session_id: str = None) -> Dict:
        """处理用户消息并构建图谱"""
        # 抽取实体和关系
        extracted = self.extract_entities_from_text(message, user_id, session_id)
        
        # 存储到图谱
        stored_entities = {
            'diseases': 0,
            'symptoms': 0, 
            'medicines': 0,
            'disease_symptom_relations': 0,
            'disease_medicine_relations': 0
        }
        
        # 存储疾病实体
        for disease_entity in extracted['diseases']:
            disease_id = self.graph_manager.generate_entity_id('disease', disease_entity.name)
            disease_info = self.disease_dict.get(disease_entity.name, {})
            
            disease = DiseaseEntity(
                id=disease_id,
                name=disease_entity.name,
                code=disease_info.get('code'),
                category=disease_info.get('category'),
                severity=disease_info.get('severity')
            )
            
            if self.graph_manager.add_disease(disease):
                stored_entities['diseases'] += 1
        
        # 存储症状实体
        for symptom_entity in extracted['symptoms']:
            symptom_id = self.graph_manager.generate_entity_id('symptom', symptom_entity.name)
            symptom_info = self.symptom_dict.get(symptom_entity.name, {})
            
            symptom = SymptomEntity(
                id=symptom_id,
                name=symptom_entity.name,
                body_part=symptom_info.get('body_part'),
                intensity=symptom_info.get('intensity')
            )
            
            if self.graph_manager.add_symptom(symptom):
                stored_entities['symptoms'] += 1
        
        # 存储药品实体
        for medicine_entity in extracted['medicines']:
            medicine_id = self.graph_manager.generate_entity_id('medicine', medicine_entity.name)
            medicine_info = self.medicine_dict.get(medicine_entity.name, {})
            
            medicine = MedicineEntity(
                id=medicine_id,
                name=medicine_entity.name,
                generic_name=medicine_info.get('generic_name'),
                drug_class=medicine_info.get('drug_class'),
                prescription_required=medicine_info.get('prescription_required', False)
            )
            
            if self.graph_manager.add_medicine(medicine):
                stored_entities['medicines'] += 1
        
        # 存储疾病-症状关系
        for relation_data in extracted['disease_symptom_relations']:
            disease_id = self.graph_manager.generate_entity_id('disease', relation_data['disease_name'])
            symptom_id = self.graph_manager.generate_entity_id('symptom', relation_data['symptom_name'])
            relation_id = self.graph_manager.generate_relation_id(disease_id, symptom_id, 'CONSULT')
            
            relation = DiseaseSymptomRelation(
                id=relation_id,
                disease_id=disease_id,
                symptom_id=symptom_id,
                source=relation_data['source'],
                confidence=relation_data['confidence'],
                context=relation_data['context'],
                user_id=user_id,
                session_id=session_id
            )
            
            if self.graph_manager.add_disease_symptom_relation(relation):
                stored_entities['disease_symptom_relations'] += 1
        
        # 存储疾病-药品关系
        for relation_data in extracted['disease_medicine_relations']:
            disease_id = self.graph_manager.generate_entity_id('disease', relation_data['disease_name'])
            medicine_id = self.graph_manager.generate_entity_id('medicine', relation_data['medicine_name'])
            relation_id = self.graph_manager.generate_relation_id(disease_id, medicine_id, 'TREATMENT')
            
            relation = DiseaseMedicineRelation(
                id=relation_id,
                disease_id=disease_id,
                medicine_id=medicine_id,
                source=relation_data['source'],
                effectiveness=relation_data.get('effectiveness'),
                user_id=user_id
            )
            
            if self.graph_manager.add_disease_medicine_relation(relation):
                stored_entities['disease_medicine_relations'] += 1
        
        return {
            'success': True,
            'message': f"成功处理用户消息，提取并存储了 {sum(stored_entities.values())} 个图谱元素",
            'extracted_summary': extracted,
            'stored_counts': stored_entities,
            'user_id': user_id,
            'session_id': session_id
        }