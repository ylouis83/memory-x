#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Memory-X 数据库初始化脚本
创建和初始化数据库表结构
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any

# 添加项目根目录到Python路径
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from configs.settings import get_config


class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.db_path = self.config.DATABASE['path']
        
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def init_sqlite_database(self):
        """初始化SQLite数据库"""
        print(f"🔧 初始化SQLite数据库: {self.db_path}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 1. 创建事实记忆表 (双时态架构)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fact_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    predicate TEXT NOT NULL,
                    object TEXT NOT NULL,
                    importance INTEGER DEFAULT 2,
                    confidence REAL DEFAULT 0.8,
                    valid_from TEXT NOT NULL,
                    valid_to TEXT,
                    commit_ts TEXT NOT NULL,
                    expire_at TEXT,
                    provenance TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(user_id, subject, predicate, valid_from)
                )
            ''')
            
            # 2. 创建对话记忆表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    entities TEXT,
                    intent TEXT,
                    importance INTEGER DEFAULT 2,
                    timestamp TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # 3. 创建实体记忆表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entity_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_value TEXT NOT NULL,
                    entity_metadata TEXT,
                    frequency INTEGER DEFAULT 1,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    confidence REAL DEFAULT 0.8,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(user_id, entity_type, entity_value)
                )
            ''')
            
            # 4. 创建用户画像表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profile (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    name TEXT,
                    age INTEGER,
                    gender TEXT,
                    preferences TEXT,
                    medical_history TEXT,
                    allergies TEXT,
                    medications TEXT,
                    risk_level TEXT DEFAULT 'low',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # 5. 创建记忆索引表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    memory_id INTEGER NOT NULL,
                    index_key TEXT NOT NULL,
                    index_value TEXT NOT NULL,
                    importance INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    UNIQUE(user_id, memory_type, memory_id, index_key)
                )
            ''')
            
            # 6. 创建系统配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_key TEXT UNIQUE NOT NULL,
                    config_value TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # 创建索引
            self._create_indexes(cursor)
            
            # 创建视图
            self._create_views(cursor)
            
            # 创建触发器
            self._create_triggers(cursor)
            
            # 插入初始数据
            self._insert_initial_data(cursor)
            
            conn.commit()
            print("✅ SQLite数据库初始化完成")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ 数据库初始化失败: {e}")
            raise
        finally:
            conn.close()
    
    def _create_indexes(self, cursor):
        """创建索引"""
        print("📊 创建数据库索引...")
        
        # 事实记忆表索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_fact_memory_user_id 
            ON fact_memory(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_fact_memory_subject 
            ON fact_memory(subject)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_fact_memory_valid_from 
            ON fact_memory(valid_from)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_fact_memory_commit_ts 
            ON fact_memory(commit_ts)
        ''')
        
        # 对话记忆表索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_conversation_user_id 
            ON conversation_memory(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_conversation_timestamp 
            ON conversation_memory(timestamp)
        ''')
        
        # 实体记忆表索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_entity_user_id 
            ON entity_memory(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_entity_type_value 
            ON entity_memory(entity_type, entity_value)
        ''')
        
        # 记忆索引表索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_memory_index_user_key 
            ON memory_index(user_id, index_key)
        ''')
        
        print("✅ 索引创建完成")
    
    def _create_views(self, cursor):
        """创建视图"""
        print("👁️ 创建数据库视图...")
        
        # 当前事实视图 (双时态查询)
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS v_fact_current AS
            SELECT 
                user_id, subject, predicate, object, importance, confidence,
                valid_from, commit_ts, provenance, metadata, created_at, updated_at
            FROM fact_memory 
            WHERE (valid_to IS NULL OR valid_to > datetime('now'))
            AND (expire_at IS NULL OR expire_at > datetime('now'))
        ''')
        
        # 用户记忆统计视图
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS v_user_memory_stats AS
            SELECT 
                user_id,
                COUNT(DISTINCT subject) as fact_count,
                COUNT(DISTINCT entity_type) as entity_count,
                COUNT(DISTINCT session_id) as session_count,
                MAX(created_at) as last_activity
            FROM (
                SELECT user_id, subject, created_at FROM fact_memory
                UNION ALL
                SELECT user_id, entity_type, created_at FROM entity_memory
                UNION ALL
                SELECT user_id, session_id, created_at FROM conversation_memory
            ) combined
            GROUP BY user_id
        ''')
        
        print("✅ 视图创建完成")
    
    def _create_triggers(self, cursor):
        """创建触发器"""
        print("⚡ 创建数据库触发器...")
        
        # 事实记忆更新时间触发器
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS tr_fact_memory_update
            AFTER UPDATE ON fact_memory
            FOR EACH ROW
            BEGIN
                UPDATE fact_memory SET updated_at = datetime('now') 
                WHERE id = NEW.id;
            END
        ''')
        
        # 实体记忆更新时间触发器
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS tr_entity_memory_update
            AFTER UPDATE ON entity_memory
            FOR EACH ROW
            BEGIN
                UPDATE entity_memory SET updated_at = datetime('now') 
                WHERE id = NEW.id;
            END
        ''')
        
        # 用户画像更新时间触发器
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS tr_user_profile_update
            AFTER UPDATE ON user_profile
            FOR EACH ROW
            BEGIN
                UPDATE user_profile SET updated_at = datetime('now') 
                WHERE id = NEW.id;
            END
        ''')
        
        print("✅ 触发器创建完成")
    
    def _insert_initial_data(self, cursor):
        """插入初始数据"""
        print("📝 插入初始数据...")
        
        now = datetime.now().isoformat()
        
        # 插入系统配置
        initial_configs = [
            ('system_version', '1.0.0', '系统版本'),
            ('database_version', '1.0.0', '数据库版本'),
            ('max_memory_age_days', '365', '记忆最大保存天数'),
            ('importance_threshold', '3', '重要性阈值'),
            ('entity_confidence_threshold', '0.7', '实体识别置信度阈值'),
            ('intent_confidence_threshold', '0.6', '意图识别置信度阈值')
        ]
        
        for config_key, config_value, description in initial_configs:
            cursor.execute('''
                INSERT OR IGNORE INTO system_config 
                (config_key, config_value, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (config_key, config_value, description, now, now))
        
        print("✅ 初始数据插入完成")
    
    def verify_database(self):
        """验证数据库结构"""
        print("🔍 验证数据库结构...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查表是否存在
            tables = ['fact_memory', 'conversation_memory', 'entity_memory', 
                     'user_profile', 'memory_index', 'system_config']
            
            for table in tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if cursor.fetchone():
                    print(f"✅ 表 {table} 存在")
                else:
                    print(f"❌ 表 {table} 不存在")
            
            # 检查视图是否存在
            views = ['v_fact_current', 'v_user_memory_stats']
            
            for view in views:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='view' AND name='{view}'")
                if cursor.fetchone():
                    print(f"✅ 视图 {view} 存在")
                else:
                    print(f"❌ 视图 {view} 不存在")
            
            # 检查系统配置
            cursor.execute("SELECT COUNT(*) FROM system_config")
            config_count = cursor.fetchone()[0]
            print(f"✅ 系统配置项数量: {config_count}")
            
        finally:
            conn.close()
    
    def reset_database(self):
        """重置数据库"""
        print("⚠️ 重置数据库...")
        
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            print(f"🗑️ 删除数据库文件: {self.db_path}")
        
        self.init_sqlite_database()


def main():
    """主函数"""
    print("🧠 Memory-X 数据库初始化工具")
    print("=" * 50)
    
    config = get_config()
    initializer = DatabaseInitializer(config)
    
    try:
        # 初始化数据库
        initializer.init_sqlite_database()
        
        # 验证数据库
        initializer.verify_database()
        
        print("\n🎉 数据库初始化完成！")
        print(f"📁 数据库文件: {config.DATABASE['path']}")
        print(f"🔧 配置环境: {os.getenv('MEMORY_ENV', 'default')}")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
