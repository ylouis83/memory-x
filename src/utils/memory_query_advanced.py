#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高级记忆查询工具
支持多种查询模式和数据分析
"""

import sqlite3
import os
import sys
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any


class AdvancedMemoryQuery:
    """高级记忆查询类"""
    
    def __init__(self, db_path: str = 'memory_db/user_memories.db'):
        self.db_path = db_path
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """确保数据库存在"""
        if not os.path.exists(self.db_path):
            print(f"❌ 数据库不存在: {self.db_path}")
            sys.exit(1)
    
    def query_by_user(self, user_id: str) -> List[Dict]:
        """查询指定用户的所有记忆"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, content, memory_type, importance, created_at
                FROM user_memories
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            
            records = cursor.fetchall()
            memories = []
            
            for record in records:
                memories.append({
                    'id': record[0],
                    'content': record[1],
                    'memory_type': record[2],
                    'importance': record[3],
                    'created_at': record[4]
                })
            
            conn.close()
            return memories
            
        except Exception as e:
            print(f"❌ 查询用户记忆失败: {e}")
            return []
    
    def search_by_keyword(self, keyword: str) -> List[Dict]:
        """按关键词搜索记忆"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user_id, content, memory_type, importance, created_at
                FROM user_memories
                WHERE content LIKE ?
                ORDER BY created_at DESC
            ''', (f'%{keyword}%',))
            
            records = cursor.fetchall()
            memories = []
            
            for record in records:
                memories.append({
                    'id': record[0],
                    'user_id': record[1],
                    'content': record[2],
                    'memory_type': record[3],
                    'importance': record[4],
                    'created_at': record[5]
                })
            
            conn.close()
            return memories
            
        except Exception as e:
            print(f"❌ 关键词搜索失败: {e}")
            return []
    
    def get_health_profiles(self) -> List[Dict]:
        """获取所有健康档案"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user_id, content, importance, created_at
                FROM user_memories
                WHERE memory_type = 'health_profile'
                ORDER BY importance DESC, created_at DESC
            ''')
            
            records = cursor.fetchall()
            profiles = []
            
            for record in records:
                profiles.append({
                    'id': record[0],
                    'user_id': record[1],
                    'content': record[2],
                    'importance': record[3],
                    'created_at': record[4]
                })
            
            conn.close()
            return profiles
            
        except Exception as e:
            print(f"❌ 获取健康档案失败: {e}")
            return []
    
    def analyze_user_health(self, user_id: str) -> Dict[str, Any]:
        """分析用户健康档案"""
        memories = self.query_by_user(user_id)
        
        analysis = {
            'user_id': user_id,
            'total_memories': len(memories),
            'health_records': [],
            'allergies': [],
            'chronic_conditions': [],
            'medications': []
        }
        
        for memory in memories:
            content = memory['content']
            
            # 分析健康档案
            if memory['memory_type'] == 'health_profile':
                analysis['health_records'].append(memory)
                
                # 分析过敏信息
                if '过敏' in content:
                    if '阿司匹林' in content:
                        analysis['allergies'].append('阿司匹林')
                    if '青霉素' in content:
                        analysis['allergies'].append('青霉素')
                
                # 分析慢性疾病
                chronic_diseases = ['高血压', '糖尿病', '心脏病', '哮喘', '癌症']
                for disease in chronic_diseases:
                    if disease in content and disease not in analysis['chronic_conditions']:
                        analysis['chronic_conditions'].append(disease)
        
        # 去重
        analysis['allergies'] = list(set(analysis['allergies']))
        analysis['chronic_conditions'] = list(set(analysis['chronic_conditions']))
        
        return analysis


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI-安主任高级记忆查询工具')
    parser.add_argument('--user', help='查询指定用户的记忆')
    parser.add_argument('--search', help='按关键词搜索记忆')
    parser.add_argument('--health-only', action='store_true', help='只显示健康档案')
    parser.add_argument('--analyze', help='分析指定用户的健康档案')
    parser.add_argument('--export', help='导出数据到JSON文件')
    
    args = parser.parse_args()
    
    # 创建查询工具
    query_tool = AdvancedMemoryQuery()
    
    print("�� AI-安主任 高级记忆查询工具")
    print("=" * 80)
    
    if args.user:
        memories = query_tool.query_by_user(args.user)
        print(f"\n👤 用户 '{args.user}' 的记忆记录 ({len(memories)} 条):")
        for memory in memories:
            print(f"\n🔸 记录 #{memory['id']}:")
            print(f"   内容: {memory['content']}")
            print(f"   类型: {memory['memory_type']}")
            print(f"   重要性: {memory['importance']}/3")
            print(f"   时间: {memory['created_at']}")
    
    elif args.search:
        memories = query_tool.search_by_keyword(args.search)
        print(f"\n🔍 搜索 '{args.search}' 的结果 ({len(memories)} 条):")
        for memory in memories:
            print(f"\n🔸 记录 #{memory['id']} (用户: {memory['user_id']}):")
            print(f"   内容: {memory['content']}")
            print(f"   类型: {memory['memory_type']}")
            print(f"   重要性: {memory['importance']}/3")
    
    elif args.health_only:
        profiles = query_tool.get_health_profiles()
        print(f"\n🏥 健康档案记录 ({len(profiles)} 条):")
        for profile in profiles:
            print(f"\n💊 健康档案 #{profile['id']} (用户: {profile['user_id']}):")
            print(f"   内容: {profile['content']}")
            print(f"   重要性: {profile['importance']}/3")
            print(f"   时间: {profile['created_at']}")
    
    elif args.analyze:
        analysis = query_tool.analyze_user_health(args.analyze)
        print(f"\n🏥 用户 '{args.analyze}' 健康档案分析:")
        print(f"   总记忆数: {analysis['total_memories']}")
        print(f"   健康记录: {len(analysis['health_records'])} 条")
        print(f"   过敏药物: {analysis['allergies'] if analysis['allergies'] else '无'}")
        print(f"   慢性疾病: {analysis['chronic_conditions'] if analysis['chronic_conditions'] else '无'}")
    
    else:
        # 默认显示概览
        print("\n📊 数据库概览:")
        query_tool = AdvancedMemoryQuery()
        
        # 显示统计信息
        conn = sqlite3.connect(query_tool.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM user_memories')
        total = cursor.fetchone()[0]
        print(f"   总记录数: {total}")
        
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_memories')
        users = cursor.fetchone()[0]
        print(f"   用户数: {users}")
        
        cursor.execute('SELECT COUNT(*) FROM user_memories WHERE memory_type = "health_profile"')
        health_count = cursor.fetchone()[0]
        print(f"   健康档案: {health_count}")
        
        conn.close()
        
        print(f"\n💡 使用示例:")
        print(f"   python3 advanced_memory_query.py --user test_user_001")
        print(f"   python3 advanced_memory_query.py --search 阿司匹林")
        print(f"   python3 advanced_memory_query.py --health-only")
        print(f"   python3 advanced_memory_query.py --analyze test_user_001")


if __name__ == "__main__":
    main()
