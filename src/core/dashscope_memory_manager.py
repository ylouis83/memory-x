#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DashScope集成的记忆管理器
使用DashScope API进行AI对话和记忆管理
"""

import os
import json
import requests
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import deque
import logging

class DashScopeMemoryManager:
    """DashScope集成的记忆管理器"""
    
    def __init__(self, user_id: str, db_path: str = "data/dashscope_memory.db"):
        self.user_id = user_id
        self.db_path = db_path
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 短期记忆
        self.short_term_memory = deque(maxlen=10)
        self.working_memory = {}
        
        # DashScope配置
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY环境变量未设置")
        
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model = "qwen-turbo"
        
        # 初始化数据库
        self._init_database()
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dashscope_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                entities TEXT,
                intent TEXT,
                importance INTEGER NOT NULL,
                embedding TEXT,
                timestamp TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _call_dashscope_api(self, messages: List[Dict], max_tokens: int = 1000) -> str:
        """调用DashScope API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                self.logger.error(f"DashScope API错误: {response.status_code} - {response.text}")
                return "抱歉，我现在无法回答您的问题。"
                
        except Exception as e:
            self.logger.error(f"DashScope API调用异常: {e}")
            return "抱歉，服务暂时不可用。"
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """获取文本嵌入向量"""
        try:
            embedding_url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            embedding_data = {
                "model": "text-embedding-v1",
                "input": {
                    "texts": [text]
                }
            }
            
            response = requests.post(
                embedding_url,
                headers=headers,
                json=embedding_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['output']['embeddings'][0]['embedding']
            else:
                self.logger.error(f"嵌入API错误: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"嵌入API调用异常: {e}")
            return None
    
    def _detect_intent(self, message: str) -> str:
        """检测用户意图"""
        messages = [
            {"role": "system", "content": "你是一个意图检测专家。请分析用户消息的意图，只返回以下之一：INTRODUCE（自我介绍）、MEDICAL_INFO（医疗信息）、REQUEST_MEDICINE（请求开药）、PRESCRIPTION_INQUIRY（用药咨询）、EMERGENCY（紧急情况）、NORMAL_CONSULTATION（普通咨询）"},
            {"role": "user", "content": message}
        ]
        
        intent = self._call_dashscope_api(messages, max_tokens=50)
        return intent.strip()
    
    def _extract_entities(self, message: str) -> Dict:
        """提取实体信息"""
        messages = [
            {"role": "system", "content": "你是一个实体识别专家。请从用户消息中提取实体信息，以JSON格式返回，包含PERSON（人名）、AGE（年龄）、DISEASE（疾病）、MEDICINE（药品）、ALLERGY（过敏）等字段。"},
            {"role": "user", "content": message}
        ]
        
        try:
            entities_text = self._call_dashscope_api(messages, max_tokens=200)
            # 尝试解析JSON
            entities = json.loads(entities_text)
            return entities
        except:
            return {}
    
    def _evaluate_importance(self, intent: str, entities: Dict) -> int:
        """评估重要性"""
        importance = 1
        
        if intent == "EMERGENCY":
            importance = 4
        elif intent in ["REQUEST_MEDICINE", "MEDICAL_INFO"]:
            importance = 3
        elif intent == "PRESCRIPTION_INQUIRY":
            importance = 2
        
        # 根据实体调整重要性
        if entities.get("DISEASE") or entities.get("ALLERGY"):
            importance = min(4, importance + 1)
        
        return importance
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """处理用户消息"""
        try:
            # 检测意图
            intent = self._detect_intent(message)
            
            # 提取实体
            entities = self._extract_entities(message)
            
            # 评估重要性
            importance = self._evaluate_importance(intent, entities)
            
            # 构建上下文
            context_messages = [
                {"role": "system", "content": "你是一个专业的医疗助手，请根据用户的医疗信息和历史记录提供专业的建议。注意用户可能有过敏史和慢性病。"}
            ]
            
            # 添加历史记忆作为上下文
            for memory in list(self.short_term_memory)[-3:]:  # 最近3轮对话
                context_messages.append({"role": "user", "content": memory['user_message']})
                context_messages.append({"role": "assistant", "content": memory['ai_response']})
            
            # 添加当前消息
            context_messages.append({"role": "user", "content": message})
            
            # 生成AI回复
            ai_response = self._call_dashscope_api(context_messages)
            
            # 获取嵌入向量
            embedding = self._get_embedding(message)
            
            # 存储记忆
            self._store_memory(message, ai_response, entities, intent, importance, embedding)
            
            return {
                'success': True,
                'response': ai_response,
                'intent': intent,
                'entities': entities,
                'importance': importance,
                'embedding': embedding is not None
            }
            
        except Exception as e:
            self.logger.error(f"消息处理失败: {e}")
            return {
                'success': False,
                'response': '抱歉，处理您的消息时出现了问题。',
                'error': str(e)
            }
    
    def _store_memory(self, user_message: str, ai_response: str, 
                     entities: Dict, intent: str, importance: int, 
                     embedding: Optional[List[float]]):
        """存储记忆"""
        # 添加到短期记忆
        memory = {
            'user_message': user_message,
            'ai_response': ai_response,
            'entities': entities,
            'intent': intent,
            'importance': importance,
            'timestamp': datetime.now(),
            'embedding': embedding
        }
        
        self.short_term_memory.append(memory)
        
        # 更新工作记忆
        if entities:
            for entity_type, entity_list in entities.items():
                if entity_type not in self.working_memory:
                    self.working_memory[entity_type] = set()
                
                if isinstance(entity_list, list):
                    for entity in entity_list:
                        self.working_memory[entity_type].add(str(entity))
        
        # 存储到数据库
        if importance >= 2:
            self._store_to_database(user_message, ai_response, entities, intent, importance, embedding)
    
    def _store_to_database(self, user_message: str, ai_response: str,
                          entities: Dict, intent: str, importance: int,
                          embedding: Optional[List[float]]):
        """存储到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO dashscope_memories 
                (user_id, user_message, ai_response, entities, intent, importance, embedding, timestamp, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.user_id, user_message, ai_response, 
                json.dumps(entities), intent, importance,
                json.dumps(embedding) if embedding else None,
                datetime.now().isoformat(), datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"数据库存储失败: {e}")
    
    def search_memories(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索相关记忆"""
        try:
            # 获取查询的嵌入向量
            query_embedding = self._get_embedding(query)
            if not query_embedding:
                return []
            
            # 从数据库搜索
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_message, ai_response, entities, intent, importance, embedding
                FROM dashscope_memories 
                WHERE user_id = ? AND embedding IS NOT NULL
                ORDER BY importance DESC, created_at DESC
                LIMIT ?
            ''', (self.user_id, top_k * 2))  # 获取更多结果用于相似度计算
            
            results = cursor.fetchall()
            conn.close()
            
            # 计算相似度并排序
            memory_scores = []
            for result in results:
                user_msg, ai_resp, entities, intent, importance, embedding_str = result
                
                if embedding_str:
                    try:
                        embedding = json.loads(embedding_str)
                        # 简单的余弦相似度计算
                        similarity = self._cosine_similarity(query_embedding, embedding)
                        memory_scores.append({
                            'user_message': user_msg,
                            'ai_response': ai_resp,
                            'entities': json.loads(entities) if entities else {},
                            'intent': intent,
                            'importance': importance,
                            'similarity': similarity
                        })
                    except:
                        continue
            
            # 按相似度排序
            memory_scores.sort(key=lambda x: x['similarity'], reverse=True)
            
            return memory_scores[:top_k]
            
        except Exception as e:
            self.logger.error(f"记忆搜索失败: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM dashscope_memories WHERE user_id = ?', (self.user_id,))
            total_memories = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM dashscope_memories WHERE user_id = ? AND importance >= 3', (self.user_id,))
            important_memories = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'user_id': self.user_id,
                'short_term_count': len(self.short_term_memory),
                'working_memory_size': len(self.working_memory),
                'total_memories': total_memories,
                'important_memories': important_memories,
                'session_id': f"session_{datetime.now().strftime('%Y%m%d')}"
            }
            
        except Exception as e:
            self.logger.error(f"获取统计失败: {e}")
            return {
                'user_id': self.user_id,
                'short_term_count': len(self.short_term_memory),
                'working_memory_size': len(self.working_memory),
                'total_memories': 0,
                'important_memories': 0,
                'session_id': f"session_{datetime.now().strftime('%Y%m%d')}"
            }
    
    def clear_session(self):
        """清空会话"""
        self.short_term_memory.clear()
        self.working_memory.clear()
