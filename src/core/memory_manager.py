#!/usr/bin/env python3
"""Simplified memory management system.

The original implementation stored long‑term memory directly in a local
SQLite database. To better mirror Google Vertex AI's architecture, the
manager now delegates persistence to pluggable ``MemoryStore`` backends.
This allows using Cloud Spanner for scalable deployments while keeping the
lightweight SQLite store for tests and local development.
"""

from datetime import datetime, date
from typing import Dict, List, Optional
from collections import deque

import os

from src.storage import (
    MemoryStore,
    SQLiteMemoryStore,
    SpannerMemoryStore,
    Mem0MemoryStore,
)
from src.modules.medical_validator import (
    assess_statement,
    parse_time_phrase,
    TimeWindow,
    update_time_window,
    Precision,
)

class SimpleMemoryManager:
    """简化版记忆管理器"""

    def __init__(
        self,
        user_id: str,
        db_path: str = "data/simple_memory.db",
        store: Optional[MemoryStore] = None,
    ):
        self.user_id = user_id
        # 仍然保留 ``db_path`` 参数以兼容现有代码；当未提供
        # ``store`` 时使用本地 SQLite 实现。
        if store is not None:
            self.store = store
        else:
            backend = os.getenv("MEMORY_DB_TYPE", "sqlite").lower()
            if backend == "spanner":
                self.store = SpannerMemoryStore()
            elif backend == "mem0" and Mem0MemoryStore is not None:
                self.store = Mem0MemoryStore()
            else:
                self.store = SQLiteMemoryStore(db_path)

        # 短期记忆
        self.short_term_memory = deque(maxlen=10)
        self.working_memory = {}
        # 症状时间窗（仅在运行期维护，用于时间精度提升；键：症状名）
        self.symptom_windows: Dict[str, TimeWindow] = {}
    
    def add_conversation(
        self,
        user_message: str,
        ai_response: str,
        entities: Dict = None,
        intent: str = None,
        importance: int = 2,
    ) -> bool:
        """添加对话"""
        try:
            # 1) 基础有效性校验（拦截明显造假/矛盾信息）
            validation = assess_statement(user_message)
            if not validation.is_valid:
                # 允许进入短期记忆用于上下文，但拒绝合入长期（importance 强制视为 <3）
                importance_for_persist = 0
            else:
                importance_for_persist = importance

            # 2) 解析时间短语，并与既有症状时间窗合并（不降级精度）
            time_payloads: List[Dict] = []
            parsed = parse_time_phrase(user_message)
            # 统一实体结构
            entities = entities or {}
            # 提取症状名列表
            symptom_names: List[str] = []
            if 'SYMPTOM' in entities:
                for e in entities['SYMPTOM']:
                    name = e[0] if isinstance(e, (list, tuple)) and e else str(e)
                    symptom_names.append(name)
            # 如果没有显性症状，但存在时间短语，也记录为通用时间（symptom=None）
            if parsed:
                new_tw = TimeWindow(start=parsed.start, end=parsed.end, precision=parsed.precision, approximate=parsed.approximate)
                targets = symptom_names if symptom_names else [None]
                for sym in targets:
                    key = sym or "__general__"
                    if key in self.symptom_windows:
                        action, updated_tw = update_time_window(self.symptom_windows[key], new_tw)
                        # 对于 append（非同一发作），保持原窗口不变
                        if action != 'append':
                            self.symptom_windows[key] = updated_tw
                    else:
                        self.symptom_windows[key] = new_tw
                    tw = self.symptom_windows[key]
                    time_payloads.append({
                        'symptom': sym,
                        'start': tw.start.isoformat(),
                        'end': tw.end.isoformat() if tw.end else None,
                        'precision': Precision(tw.precision).name,
                        'approximate': tw.approximate,
                        'phrase': parsed.phrase,
                    })

            conversation = {
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": datetime.now(),
                "entities": entities,
                "intent": intent,
                "importance": importance,
            }

            # 将时间归一化结果写入实体（不破坏原结构）
            if time_payloads:
                entities.setdefault('TIME', [])
                entities['TIME'].extend(time_payloads)

            self.short_term_memory.append(conversation)
            self._update_working_memory(entities, intent)

            if importance_for_persist >= 3:
                self.store.add_conversation(
                    self.user_id,
                    user_message,
                    ai_response,
                    entities,
                    intent,
                    importance,
                )

            return True
        except Exception:
            return False
    
    def _update_working_memory(self, entities: Dict, intent: str):
        """更新工作记忆"""
        if entities:
            for entity_type, entity_list in entities.items():
                # 跳过时间结构（包含字典对象，不适合作为集合项）
                if entity_type == 'TIME':
                    continue
                if entity_type not in self.working_memory:
                    self.working_memory[entity_type] = set()
                
                for entity_info in entity_list:
                    if isinstance(entity_info, tuple):
                        self.working_memory[entity_type].add(entity_info[0])
                    else:
                        self.working_memory[entity_type].add(entity_info)
        
        if intent:
            self.working_memory['current_intent'] = intent
    
    def get_memory_stats(self) -> Dict:
        """获取记忆统计"""
        stats = self.store.get_stats(self.user_id)
        return {
            "user_id": self.user_id,
            "short_term_count": len(self.short_term_memory),
            "working_memory_size": len(self.working_memory),
            "total_long_term": stats.get("total_long_term", 0),
            "session_id": f"session_{datetime.now().strftime('%Y%m%d')}",
        }

    def retrieve_memories(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve memories relevant to ``query`` using the configured store."""
        return self.store.search_memories(self.user_id, query, top_k)

    def search_long_term_memory(self, query: str, limit: int = 5) -> List[Dict]:
        """Alias for :meth:`retrieve_memories` for backward compatibility."""
        return self.retrieve_memories(query, limit)
    
    def clear_session(self):
        """清空会话"""
        self.short_term_memory.clear()
        self.working_memory.clear()
    
    def remove_diabetes_related_memories(self):
        """删除短期记忆中关于糖尿病的全部内容"""
        diabetes_keywords = ['糖尿病', '血糖', '胰岛素', '家族史', '糖尿病风险', 'diabetes']
        
        # 过滤短期记忆
        filtered_memories = []
        removed_count = 0
        
        for memory_item in self.short_term_memory:
            is_diabetes_related = False
            
            # 检查用户消息
            user_message = memory_item.get('user_message', '')
            ai_response = memory_item.get('ai_response', '')
            entities = memory_item.get('entities', {})
            
            # 检查消息内容是否包含糖尿病关键词
            for keyword in diabetes_keywords:
                if (keyword in user_message or 
                    keyword in ai_response):
                    is_diabetes_related = True
                    break
            
            # 检查实体是否包含糖尿病相关内容
            if not is_diabetes_related and entities:
                for entity_type, entity_list in entities.items():
                    if isinstance(entity_list, list):
                        for entity_info in entity_list:
                            entity_text = entity_info[0] if isinstance(entity_info, (list, tuple)) else str(entity_info)
                            for keyword in diabetes_keywords:
                                if keyword in entity_text:
                                    is_diabetes_related = True
                                    break
                            if is_diabetes_related:
                                break
                    if is_diabetes_related:
                        break
            
            if not is_diabetes_related:
                filtered_memories.append(memory_item)
            else:
                removed_count += 1
        
        # 更新短期记忆
        self.short_term_memory.clear()
        for memory in filtered_memories:
            self.short_term_memory.append(memory)
        
        # 清理工作记忆中的糖尿病相关内容
        diabetes_working_keys = []
        for key, value in self.working_memory.items():
            if isinstance(value, set):
                # 检查set中的元素
                filtered_set = set()
                for item in value:
                    is_diabetes_item = False
                    for keyword in diabetes_keywords:
                        if keyword in str(item):
                            is_diabetes_item = True
                            break
                    if not is_diabetes_item:
                        filtered_set.add(item)
                
                if len(filtered_set) != len(value):
                    self.working_memory[key] = filtered_set
            elif isinstance(value, str):
                # 检查字符串值
                for keyword in diabetes_keywords:
                    if keyword in value:
                        diabetes_working_keys.append(key)
                        break
        
        # 删除糖尿病相关的工作记忆键
        for key in diabetes_working_keys:
            del self.working_memory[key]
        
        return {
            'removed_short_term': removed_count,
            'removed_working_keys': len(diabetes_working_keys),
            'remaining_short_term': len(self.short_term_memory),
            'remaining_working_memory': len(self.working_memory)
        }

class SimpleMemoryIntegratedAI:
    """简化版记忆集成AI"""
    
    def __init__(self):
        self.user_memories = {}
    
    def get_memory_manager(self, user_id: str) -> SimpleMemoryManager:
        """获取记忆管理器"""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = SimpleMemoryManager(user_id)
        return self.user_memories[user_id]
    
    def process_message(self, user_message: str, user_id: str = "default") -> Dict:
        """处理消息"""
        try:
            memory_manager = self.get_memory_manager(user_id)
            
            # 简化意图检测
            intent = self._detect_intent(user_message)
            
            # 简化实体识别
            entities = self._recognize_entities(user_message)
            
            # 评估重要性
            importance = self._evaluate_importance(intent, entities)
            
            # 在长期记忆中检索相关内容
            retrieved = memory_manager.search_long_term_memory(user_message)

            # 生成回复
            ai_response = self._generate_response(user_message, intent, entities)
            if retrieved:
                ai_response = f"我记得你提到过：{retrieved[0]['user_message']}。" + ai_response

            # 存储对话
            memory_manager.add_conversation(
                user_message, ai_response, entities, intent, importance
            )

            return {
                'success': True,
                'response': ai_response,
                'intent': {'detected': intent, 'confidence': 80},
                'memory_info': {
                    'importance': importance,
                    'used_long_term': importance >= 3,
                    'context_continuity': 0.7,
                    'retrieved': len(retrieved),
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': '处理失败'
            }
    
    def _detect_intent(self, message: str) -> str:
        """简化意图检测"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['开药', '配药', '买药']):
            return 'REQUEST_MEDICINE'
        elif any(word in message_lower for word in ['怎么吃', '用法', '副作用']):
            return 'PRESCRIPTION_INQUIRY'
        elif any(word in message_lower for word in ['救命', '紧急', '胸痛']):
            return 'EMERGENCY'
        else:
            return 'NORMAL_CONSULTATION'
    
    def _recognize_entities(self, message: str) -> Dict:
        """增强实体识别"""
        entities = {}
        
        # 药物实体
        medicines = ['布洛芬', '阿司匹林', '感冒药', '青霉素', '氨氯地平', '胰岛素']
        
        # 症状实体
        symptoms = ['头痛', '发热', '咳嗽', '高血压', '糖尿病', '过敏']
        
        # 疾病实体
        diseases = ['糖尿病', '高血压', '心脏病', '哮喘', '肝病', '肾病']
        
        # 过敏相关
        allergies = ['过敏', '青霉素过敏', '花粉过敏', '食物过敏']
        
        # 年龄相关（简单匹配）
        import re
        age_pattern = r'(\d+)岁|今年(\d+)'
        age_match = re.search(age_pattern, message)
        if age_match:
            age = age_match.group(1) or age_match.group(2)
            entities['AGE'] = [(f"{age}岁", age_match.start(), age_match.end())]
        
        # 姓名相关（简单识别）
        name_patterns = ['我叫', '我是', '我的名字是']
        for pattern in name_patterns:
            if pattern in message:
                start_idx = message.find(pattern) + len(pattern)
                # 查找后面的中文字符作为姓名
                name_match = re.search(r'[\u4e00-\u9fff]+', message[start_idx:start_idx+10])
                if name_match:
                    name = name_match.group()
                    entities['PERSON'] = [(name, start_idx + name_match.start(), start_idx + name_match.end())]
                    break
        
        # 遗传病史
        if '遗传病史' in message or '家族史' in message:
            entities['FAMILY_HISTORY'] = [('遗传病史', message.find('遗传病史'), message.find('遗传病史') + 4)]
        
        # 检查各类实体
        found_medicines = [m for m in medicines if m in message]
        found_symptoms = [s for s in symptoms if s in message]
        found_diseases = [d for d in diseases if d in message]
        found_allergies = [a for a in allergies if a in message]
        
        if found_medicines:
            entities['MEDICINE'] = [(m, message.find(m), message.find(m) + len(m)) for m in found_medicines]
        if found_symptoms:
            entities['SYMPTOM'] = [(s, message.find(s), message.find(s) + len(s)) for s in found_symptoms]
        if found_diseases:
            entities['DISEASE'] = [(d, message.find(d), message.find(d) + len(d)) for d in found_diseases]
        if found_allergies:
            entities['ALLERGY'] = [(a, message.find(a), message.find(a) + len(a)) for a in found_allergies]
        
        return entities
    
    def _evaluate_importance(self, intent: str, entities: Dict) -> int:
        """增强重要性评估"""
        importance = 1
        
        # 根据意图评估
        if intent == 'EMERGENCY':
            importance = 4
        elif intent in ['REQUEST_MEDICINE', 'REQUEST_REAL_DOCTOR']:
            importance = 3
        elif intent == 'PRESCRIPTION_INQUIRY':
            importance = 2
        
        # 根据实体类型调整重要性
        if entities:
            # 个人信息相关（高重要性）
            if 'PERSON' in entities or 'AGE' in entities:
                importance = max(importance, 3)
            
            # 医疗相关信息（高重要性）
            if any(key in entities for key in ['DISEASE', 'ALLERGY', 'FAMILY_HISTORY']):
                importance = max(importance, 4)
            
            # 药物和症状（中等重要性）
            if any(key in entities for key in ['MEDICINE', 'SYMPTOM']):
                importance = max(importance, 2)
        
        return min(4, importance)
    
    def _generate_response(self, message: str, intent: str, entities: Dict) -> str:
        """生成回复"""
        if intent == 'EMERGENCY':
            return "紧急情况请立即就医或拨打120！"
        elif intent == 'REQUEST_MEDICINE':
            return "我无法开具处方药，建议您前往医院就诊。"
        elif intent == 'PRESCRIPTION_INQUIRY':
            if 'MEDICINE' in entities:
                medicine_names = [e[0] for e in entities['MEDICINE']]
                return f"关于{', '.join(medicine_names)}的用药问题，建议咨询医生或药师。"
            return "关于用药问题，建议咨询专业医生。"
        else:
            return "我理解您的情况，建议注意观察并及时就医。"
    
    def get_stats(self, user_id: str) -> Dict:
        """获取统计"""
        memory_manager = self.get_memory_manager(user_id)
        return memory_manager.get_memory_stats()
    
    def clear_user_session(self, user_id: str):
        """清空用户会话"""
        if user_id in self.user_memories:
            self.user_memories[user_id].clear_session()
