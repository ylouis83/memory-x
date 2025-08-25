#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
记忆数据迁移工具
将现有的user_memories数据迁移到Spanner风格双时态架构
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta


class MemoryMigrationTool:
    """记忆数据迁移工具"""
    
    def __init__(self):
        self.old_db = 'memory_db/user_memories.db'
        self.new_db = 'memory_db/spanner_memory.db'
        self.migration_log = []
    
    def check_databases(self):
        """检查数据库状态"""
        print("🔍 检查数据库状态...")
        
        old_exists = os.path.exists(self.old_db)
        new_exists = os.path.exists(self.new_db)
        
        print(f"📊 旧数据库 ({self.old_db}): {'存在' if old_exists else '不存在'}")
        print(f"📊 新数据库 ({self.new_db}): {'存在' if new_exists else '不存在'}")
        
        if old_exists:
            # 统计旧数据库记录数
            conn = sqlite3.connect(self.old_db)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM user_memories')
            old_count = cursor.fetchone()[0]
            print(f"📈 旧数据库记录数: {old_count}")
            
            # 按类型统计
            cursor.execute('SELECT memory_type, COUNT(*) FROM user_memories GROUP BY memory_type')
            type_stats = cursor.fetchall()
            print(f"📊 类型分布: {dict(type_stats)}")
            conn.close()
        
        if new_exists:
            # 统计新数据库记录数
            conn = sqlite3.connect(self.new_db)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM fact_memory')
            new_count = cursor.fetchone()[0]
            print(f"📈 新数据库记录数: {new_count}")
            conn.close()
        
        return old_exists, new_exists
    
    def migrate_data(self):
        """执行数据迁移"""
        old_exists, new_exists = self.check_databases()
        
        if not old_exists:
            print("❌ 旧数据库不存在，无法迁移")
            return False
        
        if not new_exists:
            print("❌ 新数据库不存在，请先创建Spanner架构")
            return False
        
        try:
            print("\n🔄 开始数据迁移...")
            
            # 连接两个数据库
            old_conn = sqlite3.connect(self.old_db)
            new_conn = sqlite3.connect(self.new_db)
            
            old_cursor = old_conn.cursor()
            new_cursor = new_conn.cursor()
            
            # 查询所有旧记录
            old_cursor.execute('''
                SELECT id, user_id, content, memory_type, importance, created_at
                FROM user_memories
                ORDER BY created_at
            ''')
            
            old_records = old_cursor.fetchall()
            
            print(f"📊 找到 {len(old_records)} 条记录需要迁移")
            
            migrated_count = 0
            
            for record in old_records:
                old_id, user_id, content, memory_type, importance, created_at = record
                
                # 分析内容并提取结构化信息
                facts = self._extract_facts_from_content(content, user_id, memory_type, importance, created_at)
                
                # 插入到新架构
                for fact in facts:
                    try:
                        # 计算TTL
                        expire_at = None
                        if fact['is_short_term']:
                            expire_time = datetime.fromisoformat(created_at.replace('Z', '+00:00')) + timedelta(hours=24)
                            expire_at = expire_time.isoformat()
                        
                        new_cursor.execute('''
                            INSERT INTO fact_memory 
                            (user_id, subject, predicate, object, valid_from, importance, confidence, provenance, expire_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            user_id, fact['subject'], fact['predicate'], fact['object'],
                            created_at, fact['importance'], fact['confidence'],
                            json.dumps({
                                'source': 'migration',
                                'original_id': old_id,
                                'original_type': memory_type,
                                'migration_time': datetime.now().isoformat()
                            }),
                            expire_at
                        ))
                        
                        migrated_count += 1
                        
                    except Exception as e:
                        print(f"⚠️ 迁移记录失败 (ID: {old_id}): {e}")
                        continue
                
                # 同时保存到情节记忆
                try:
                    new_cursor.execute('''
                        INSERT INTO episode_memory 
                        (user_id, event_type, title, content, occurred_at, importance, provenance)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        user_id, 
                        self._map_event_type(memory_type),
                        f"历史记录 - {memory_type}",
                        content,
                        created_at,
                        importance / 3.0,  # 转换重要性范围
                        json.dumps({
                            'source': 'migration',
                            'original_id': old_id,
                            'original_type': memory_type
                        })
                    ))
                    
                except Exception as e:
                    print(f"⚠️ 保存情节记忆失败: {e}")
            
            new_conn.commit()
            
            old_conn.close()
            new_conn.close()
            
            print(f"✅ 迁移完成！成功迁移 {migrated_count} 条事实记录")
            return True
            
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            return False
    
    def _extract_facts_from_content(self, content: str, user_id: str, memory_type: str, importance: int, created_at: str) -> list:
        """从内容中提取结构化事实"""
        facts = []
        
        # 分析内容类型
        content_lower = content.lower()
        
        # 提取名字
        if '我叫' in content or '我的名字' in content or '名字叫' in content:
            import re
            name_patterns = [r'我叫([^\s，。！？]+)', r'我的名字[是叫]([^\s，。！？]+)', r'名字叫([^\s，。！？]+)']
            for pattern in name_patterns:
                matches = re.findall(pattern, content)
                for name in matches:
                    if name not in ['啥', '什么', '谁']:
                        facts.append({
                            'subject': 'user_profile',
                            'predicate': 'name',
                            'object': name,
                            'importance': 0.3,
                            'confidence': 0.9,
                            'is_short_term': True  # 名字是短期记忆
                        })
        
        # 提取慢性疾病
        chronic_diseases = ['高血压', '糖尿病', '心脏病', '哮喘', '癌症', '肾病', '肝病']
        for disease in chronic_diseases:
            if disease in content:
                facts.append({
                    'subject': 'medical_history',
                    'predicate': 'chronic_disease',
                    'object': disease,
                    'importance': 0.9,
                    'confidence': 0.95,
                    'is_short_term': False  # 慢性疾病是长期记忆
                })
        
        # 提取过敏信息
        if '过敏' in content:
            allergy_medicines = ['阿司匹林', '青霉素', '头孢', '布洛芬', '药物']
            for medicine in allergy_medicines:
                if medicine in content:
                    facts.append({
                        'subject': 'allergy_info',
                        'predicate': 'allergic_to',
                        'object': medicine,
                        'importance': 0.95,
                        'confidence': 0.98,
                        'is_short_term': False  # 过敏史是长期记忆
                    })
        
        # 如果没有提取到具体事实，创建一个通用记录
        if not facts:
            is_short_term = memory_type in ['short_term', 'important'] and not any(
                keyword in content for keyword in chronic_diseases + ['过敏', '阿司匹林', '青霉素']
            )
            
            facts.append({
                'subject': 'general_info',
                'predicate': 'content',
                'object': content,
                'importance': min(1.0, importance / 3.0),
                'confidence': 0.7,
                'is_short_term': is_short_term
            })
        
        return facts
    
    def _map_event_type(self, memory_type: str) -> str:
        """映射事件类型"""
        mapping = {
            'health_profile': 'health_consultation',
            'important': 'important_conversation',
            'short_term': 'casual_conversation'
        }
        return mapping.get(memory_type, 'general_conversation')
    
    def verify_migration(self):
        """验证迁移结果"""
        print("\n🔍 验证迁移结果...")
        
        try:
            # 连接新数据库
            conn = sqlite3.connect(self.new_db)
            cursor = conn.cursor()
            
            # 统计迁移后的数据
            cursor.execute('SELECT COUNT(*) FROM fact_memory')
            fact_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM episode_memory')
            episode_count = cursor.fetchone()[0]
            
            print(f"📊 迁移后统计:")
            print(f"   事实记忆: {fact_count} 条")
            print(f"   情节记忆: {episode_count} 条")
            
            # 按主题统计事实
            cursor.execute('SELECT subject, COUNT(*) FROM fact_memory GROUP BY subject')
            subject_stats = cursor.fetchall()
            
            print(f"\\n📋 事实主题分布:")
            for subject, count in subject_stats:
                cursor.execute('SELECT COUNT(*) FROM fact_memory WHERE subject = ? AND expire_at IS NOT NULL', (subject,))
                short_term_count = cursor.fetchone()[0]
                long_term_count = count - short_term_count
                print(f"   {subject}: {count} 条 (长期: {long_term_count}, 短期: {short_term_count})")
            
            # 显示过敏信息迁移结果
            print(f"\\n🚨 过敏信息迁移验证:")
            cursor.execute('''
                SELECT user_id, object, importance, expire_at
                FROM fact_memory
                WHERE subject = 'allergy_info' AND predicate = 'allergic_to'
            ''')
            allergies = cursor.fetchall()
            
            for allergy in allergies:
                user_id, medicine, importance, expire_at = allergy
                ttl_status = '永久保存' if expire_at is None else f'过期时间: {expire_at}'
                print(f"   {user_id}: 对{medicine}过敏 | 重要性: {importance} | {ttl_status}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ 验证失败: {e}")
            return False


def main():
    print("🔄 AI-安主任记忆数据迁移工具")
    print("=" * 60)
    
    migration_tool = MemoryMigrationTool()
    
    # 执行迁移
    success = migration_tool.migrate_data()
    
    if success:
        # 验证迁移结果
        migration_tool.verify_migration()
        
        print(f"\\n🎉 数据迁移完成！")
        print(f"✅ 旧数据已成功迁移到Spanner风格架构")
        print(f"✅ 短期记忆设置了24小时TTL")
        print(f"✅ 长期记忆（疾病、过敏）永久保存")
        print(f"✅ 支持时间旅行查询和版本历史")
    else:
        print("❌ 数据迁移失败")


if __name__ == "__main__":
    main()
