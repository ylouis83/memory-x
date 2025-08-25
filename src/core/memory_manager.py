#!/usr/bin/env python3
"""
简化版记忆管理系统
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List
from collections import deque
import logging

class SimpleMemoryManager:
    """简化版记忆管理器"""
    
    def __init__(self, user_id: str, db_path: str = "data/simple_memory.db"):
        self.user_id = user_id
        self.db_path = db_path
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 短期记忆
        self.short_term_memory = deque(maxlen=10)
        self.working_memory = {}
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                message_type TEXT NOT NULL,
                importance INTEGER NOT NULL,
                entities TEXT,
                intent TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_conversation(self, user_message: str, ai_response: str, 
                        entities: Dict = None, intent: str = None,
                        importance: int = 2) -> bool:
        """添加对话"""
        try:
            conversation = {
                'user_message': user_message,
                'ai_response': ai_response,
                'timestamp': datetime.now(),
                'entities': entities or {},
                'intent': intent,
                'importance': importance
            }
            
            self.short_term_memory.append(conversation)
            self._update_working_memory(entities, intent)
            
            if importance >= 3:
                self._store_to_long_term(user_message, ai_response, entities, intent, importance)
            
            return True
        except Exception as e:
            return False
    
    def _update_working_memory(self, entities: Dict, intent: str):
        """更新工作记忆"""
        if entities:
            for entity_type, entity_list in entities.items():
                if entity_type not in self.working_memory:
                    self.working_memory[entity_type] = set()
                
                for entity_info in entity_list:
                    if isinstance(entity_info, tuple):
                        self.working_memory[entity_type].add(entity_info[0])
                    else:
                        self.working_memory[entity_type].add(entity_info)
        
        if intent:
            self.working_memory['current_intent'] = intent
    
    def _store_to_long_term(self, user_message: str, ai_response: str,
                           entities: Dict, intent: str, importance: int):
        """存储到长期记忆"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO memories 
                (user_id, content, message_type, importance, entities, intent, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.user_id, user_message, 'user', importance,
                json.dumps(entities), intent, datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            pass
    
    def get_memory_stats(self) -> Dict:
        """获取记忆统计"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM memories WHERE user_id = ?', (self.user_id,))
            long_term_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'user_id': self.user_id,
                'short_term_count': len(self.short_term_memory),
                'working_memory_size': len(self.working_memory),
                'total_long_term': long_term_count,
                'session_id': f"session_{datetime.now().strftime('%Y%m%d')}"
            }
        except:
            return {
                'user_id': self.user_id,
                'short_term_count': 0,
                'working_memory_size': 0,
                'total_long_term': 0
            }
    
    def clear_session(self):
        """清空会话"""
        self.short_term_memory.clear()
        self.working_memory.clear()

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
            
            # 生成回复
            ai_response = self._generate_response(user_message, intent, entities)
            
            # 存储对话
            memory_manager.add_conversation(user_message, ai_response, entities, intent, importance)
            
            return {
                'success': True,
                'response': ai_response,
                'intent': {'detected': intent, 'confidence': 80},
                'memory_info': {
                    'importance': importance,
                    'used_long_term': importance >= 3,
                    'context_continuity': 0.7
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
        """简化实体识别"""
        entities = {}
        
        medicines = ['布洛芬', '阿司匹林', '感冒药']
        symptoms = ['头痛', '发热', '咳嗽']
        
        found_medicines = [m for m in medicines if m in message]
        found_symptoms = [s for s in symptoms if s in message]
        
        if found_medicines:
            entities['MEDICINE'] = [(m, 0, len(m)) for m in found_medicines]
        if found_symptoms:
            entities['SYMPTOM'] = [(s, 0, len(s)) for s in found_symptoms]
        
        return entities
    
    def _evaluate_importance(self, intent: str, entities: Dict) -> int:
        """评估重要性"""
        importance = 1
        
        if intent == 'EMERGENCY':
            importance = 4
        elif intent in ['REQUEST_MEDICINE', 'REQUEST_REAL_DOCTOR']:
            importance = 3
        elif intent == 'PRESCRIPTION_INQUIRY':
            importance = 2
        
        if entities:
            importance += 1
        
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
