#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI-安主任 记忆数据库查询工具
用于查询和分析用户长期记忆数据
"""

import sqlite3
import os
import json
from datetime import datetime


def query_memory_database():
    """查询记忆数据库的完整信息"""
    
    db_path = 'memory_db/user_memories.db'
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🧠 AI-安主任 记忆数据库查询工具")
        print("=" * 80)
        
        # 1. 表结构信息
        print("\n📋 数据库表结构:")
        print("-" * 60)
        cursor.execute('PRAGMA table_info(user_memories)')
        columns = cursor.fetchall()
        
        print(f"{'字段名':<15} {'数据类型':<12} {'约束':<20} {'默认值':<15}")
        print("-" * 65)
        
        for col in columns:
            cid, name, data_type, not_null, default_value, pk = col
            
            constraints = []
            if pk:
                constraints.append('主键')
            if not_null:
                constraints.append('非空')
            
            constraint_str = ', '.join(constraints) if constraints else '无'
            default_str = str(default_value) if default_value else '无'
            
            print(f"{name:<15} {data_type:<12} {constraint_str:<20} {default_str:<15}")
        
        # 2. 统计信息
        print(f"\n📊 数据库统计:")
        print("-" * 40)
        
        cursor.execute('SELECT COUNT(*) FROM user_memories')
        total_count = cursor.fetchone()[0]
        print(f"📈 总记录数: {total_count}")
        
        # 按类型统计
        cursor.execute('''
            SELECT memory_type, COUNT(*) as count
            FROM user_memories
            GROUP BY memory_type
            ORDER BY count DESC
        ''')
        type_stats = cursor.fetchall()
        
        print(f"\n🏷️ 记忆类型分布:")
        for memory_type, count in type_stats:
            percentage = (count / total_count) * 100 if total_count > 0 else 0
            print(f"   {memory_type}: {count} 条 ({percentage:.1f}%)")
        
        # 3. 长期记忆详情
        print(f"\n🏥 长期记忆（健康档案）:")
        print("-" * 60)
        
        cursor.execute('''
            SELECT id, user_id, content, importance, created_at
            FROM user_memories
            WHERE memory_type = 'health_profile'
            ORDER BY created_at DESC
        ''')
        health_records = cursor.fetchall()
        
        if health_records:
            for record in health_records:
                id, user_id, content, importance, created_at = record
                print(f"\n💊 健康档案 #{id}:")
                print(f"   👤 用户: {user_id}")
                print(f"   💬 内容: {content}")
                print(f"   ⭐ 重要性: {importance}/3")
                print(f"   ⏰ 时间: {created_at}")
        else:
            print("   暂无健康档案记录")
        
        # 4. 过敏记忆专项查询
        print(f"\n🚨 过敏相关记忆:")
        print("-" * 60)
        
        cursor.execute('''
            SELECT id, user_id, content, memory_type, importance, created_at
            FROM user_memories
            WHERE content LIKE '%过敏%' OR content LIKE '%阿司匹林%' OR content LIKE '%青霉素%'
            ORDER BY created_at DESC
        ''')
        allergy_records = cursor.fetchall()
        
        if allergy_records:
            for record in allergy_records:
                id, user_id, content, memory_type, importance, created_at = record
                print(f"\n🔸 过敏记录 #{id}:")
                print(f"   👤 用户: {user_id}")
                print(f"   💬 内容: {content}")
                print(f"   🏷️ 类型: {memory_type}")
                print(f"   ⭐ 重要性: {importance}/3")
                print(f"   ⏰ 时间: {created_at}")
                
                # 分析过敏类型
                if '阿司匹林' in content:
                    print(f"   💊 过敏药物: 阿司匹林")
                if '青霉素' in content:
                    print(f"   �� 过敏药物: 青霉素")
        else:
            print("   暂无过敏相关记录")
        
        # 5. 最新记忆活动
        print(f"\n⏰ 最近记忆活动 (最新5条):")
        print("-" * 60)
        
        cursor.execute('''
            SELECT id, user_id, content, memory_type, created_at
            FROM user_memories
            ORDER BY created_at DESC
            LIMIT 5
        ''')
        recent_records = cursor.fetchall()
        
        for i, record in enumerate(recent_records, 1):
            id, user_id, content, memory_type, created_at = record
            content_preview = content[:50] + "..." if len(content) > 50 else content
            print(f"   {i}. [{created_at}] {user_id} | {memory_type} | {content_preview}")
        
        conn.close()
        print(f"\n✅ 查询完成")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    query_memory_database()
