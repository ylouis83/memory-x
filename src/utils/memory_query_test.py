#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
import os
from datetime import datetime, timedelta

# 创建SQLite双时态数据库
def create_spanner_db():
    db_path = 'memory_db/spanner_memory.db'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 启用外键
    cursor.execute('PRAGMA foreign_keys = ON')
    
    # 创建fact_memory表（双时态）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            predicate TEXT NOT NULL,
            object TEXT NOT NULL,
            valid_from DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
            valid_to DATETIME,
            commit_ts DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
            version INTEGER NOT NULL DEFAULT 1,
            importance REAL NOT NULL DEFAULT 0.5,
            confidence REAL NOT NULL DEFAULT 0.8,
            provenance TEXT,
            tombstone INTEGER NOT NULL DEFAULT 0,
            expire_at DATETIME
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fact_user_key ON fact_memory(user_id, subject, predicate)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fact_current ON fact_memory(user_id, subject, predicate, valid_to)')
    
    # 创建当前事实视图
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS v_fact_current AS
        SELECT id, user_id, subject, predicate, object, 
               valid_from, valid_to, commit_ts, version, 
               importance, confidence, provenance
        FROM fact_memory
        WHERE tombstone = 0 AND valid_to IS NULL
    ''')
    
    # 创建版本化触发器
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_fact_close_old
        AFTER INSERT ON fact_memory
        BEGIN
            UPDATE fact_memory
            SET valid_to = strftime('%Y-%m-%dT%H:%M:%fZ','now')
            WHERE user_id = new.user_id
              AND subject = new.subject
              AND predicate = new.predicate
              AND valid_to IS NULL
              AND tombstone = 0
              AND id <> new.id;
        END
    ''')
    
    conn.commit()
    conn.close()
    print('✅ SQLite双时态数据库创建完成')

# 测试功能
def test_spanner_memory():
    create_spanner_db()
    
    db_path = 'memory_db/spanner_memory.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print('\n🧪 测试SQLite双时态记忆系统:')
    print('=' * 50)
    
    # 测试1: 保存名字（短期记忆）
    print('📝 测试1: 保存用户名字（24小时TTL）')
    expire_time = (datetime.now() + timedelta(hours=24)).isoformat()
    cursor.execute('''
        INSERT INTO fact_memory (user_id, subject, predicate, object, importance, expire_at, provenance)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('test_user', 'user_profile', 'name', '柳阳', 0.3, expire_time, '{"type": "short_term"}'))
    
    # 测试2: 保存慢性疾病（长期记忆）
    print('📝 测试2: 保存慢性疾病（永久保存）')
    cursor.execute('''
        INSERT INTO fact_memory (user_id, subject, predicate, object, importance, provenance)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('test_user', 'medical_history', 'chronic_disease', '高血压', 0.9, '{"type": "long_term"}'))
    
    # 测试3: 保存过敏史（长期记忆）
    print('📝 测试3: 保存过敏史（永久保存）')
    cursor.execute('''
        INSERT INTO fact_memory (user_id, subject, predicate, object, importance, provenance)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('test_user', 'allergy_info', 'allergic_to', '阿司匹林', 0.95, '{"type": "long_term"}'))
    
    conn.commit()
    
    # 查询当前事实
    print('\n📊 查询当前事实:')
    cursor.execute('SELECT * FROM v_fact_current WHERE user_id = ?', ('test_user',))
    facts = cursor.fetchall()
    
    for fact in facts:
        id, user_id, subject, predicate, object_val, valid_from, valid_to, commit_ts, version, importance, confidence, provenance = fact
        ttl_status = '短期记忆' if 'short_term' in (provenance or '') else '长期记忆'
        print(f'   {subject}.{predicate} = {object_val} | 重要性: {importance} | {ttl_status}')
    
    # 测试版本化：更新名字
    print('\n📝 测试4: 更新名字（版本化）')
    cursor.execute('''
        INSERT INTO fact_memory (user_id, subject, predicate, object, importance, expire_at, provenance)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('test_user', 'user_profile', 'name', '柳阳（更新）', 0.3, expire_time, '{"type": "short_term", "version": 2}'))
    
    conn.commit()
    
    # 查询版本历史
    print('\n📊 查询名字版本历史:')
    cursor.execute('''
        SELECT id, object, valid_from, valid_to, version, commit_ts
        FROM fact_memory
        WHERE user_id = ? AND subject = 'user_profile' AND predicate = 'name'
        ORDER BY commit_ts
    ''', ('test_user',))
    
    name_versions = cursor.fetchall()
    for version in name_versions:
        id, object_val, valid_from, valid_to, ver, commit_ts = version
        status = '当前有效' if valid_to is None else f'已关闭于{valid_to}'
        print(f'   版本{ver}: {object_val} | {status} | 提交时间: {commit_ts}')
    
    # 查询变更日志
    print('\n📊 查询变更日志:')
    cursor.execute('SELECT table_name, op, keys, commit_ts FROM change_log ORDER BY commit_ts')
    changes = cursor.fetchall()
    for change in changes:
        table, op, keys, commit_ts = change
        print(f'   {commit_ts}: {table} {op} - {keys}')
    
    conn.close()
    print('\n✅ Spanner风格记忆系统测试完成！')

if __name__ == '__main__':
    test_spanner_memory()
