#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spanner风格记忆查询工具
支持时间旅行查询、版本历史、变更日志等高级功能
"""

import sqlite3
import json
import argparse
from datetime import datetime, timedelta


def display_table_structure():
    """显示表结构"""
    db_path = 'memory_db/spanner_memory.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("📋 SQLite双时态数据库表结构")
    print("=" * 80)
    
    # fact_memory表结构
    print("\n🏛️ fact_memory (事实记忆表 - 双时态架构):")
    cursor.execute('PRAGMA table_info(fact_memory)')
    columns = cursor.fetchall()
    
    print(f"{'字段名':<15} {'类型':<12} {'约束':<15} {'默认值':<20}")
    print("-" * 70)
    
    for col in columns:
        cid, name, data_type, not_null, default_value, pk = col
        constraints = []
        if pk: constraints.append('主键')
        if not_null: constraints.append('非空')
        constraint_str = ', '.join(constraints) if constraints else '无'
        default_str = str(default_value) if default_value else '无'
        print(f"{name:<15} {data_type:<12} {constraint_str:<15} {default_str:<20}")
    
    # 索引信息
    cursor.execute('PRAGMA index_list(fact_memory)')
    indexes = cursor.fetchall()
    print(f"\n🔗 索引数量: {len(indexes)}")
    
    # 视图信息
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
    views = cursor.fetchall()
    print(f"👁️ 视图: {[v[0] for v in views]}")
    
    # 触发器信息
    cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
    triggers = cursor.fetchall()
    print(f"⚡ 触发器: {[t[0] for t in triggers]}")
    
    conn.close()


def query_current_facts(user_id):
    """查询当前事实"""
    db_path = 'memory_db/spanner_memory.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"\n📊 用户 {user_id} 的当前事实:")
    print("-" * 60)
    
    cursor.execute('''
        SELECT subject, predicate, object, importance, confidence, 
               valid_from, commit_ts, provenance
        FROM v_fact_current
        WHERE user_id = ?
        ORDER BY importance DESC, commit_ts DESC
    ''', (user_id,))
    
    facts = cursor.fetchall()
    
    if facts:
        for fact in facts:
            subject, predicate, object_val, importance, confidence, valid_from, commit_ts, provenance = fact
            
            # 解析provenance
            prov_info = ""
            if provenance:
                try:
                    prov_data = json.loads(provenance)
                    prov_info = f" | 来源: {prov_data.get('type', '未知')}"
                except:
                    pass
            
            # TTL信息 (当前视图不包含expire_at，显示为永久保存)
            ttl_info = " | 永久保存"
            
            print(f"🔸 {subject}.{predicate} = {object_val}")
            print(f"   重要性: {importance} | 置信度: {confidence}")
            print(f"   生效时间: {valid_from[:19]} | 提交时间: {commit_ts[:19]}")
            print(f"   {ttl_info}{prov_info}")
            print()
    else:
        print("   暂无当前事实")
    
    conn.close()


def query_version_history(user_id, subject, predicate):
    """查询特定事实的版本历史"""
    db_path = 'memory_db/spanner_memory.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"\n📈 {subject}.{predicate} 的版本历史:")
    print("-" * 60)
    
    cursor.execute('''
        SELECT id, object, version, valid_from, valid_to, commit_ts, importance
        FROM fact_memory
        WHERE user_id = ? AND subject = ? AND predicate = ?
        ORDER BY commit_ts
    ''', (user_id, subject, predicate))
    
    versions = cursor.fetchall()
    
    if versions:
        for i, version in enumerate(versions, 1):
            id, object_val, ver, valid_from, valid_to, commit_ts, importance = version
            
            if valid_to:
                status = f"失效于 {valid_to[:19]}"
                duration = "已关闭"
            else:
                status = "当前有效"
                duration = "活跃中"
            
            print(f"📌 版本 {i} (ID: {id}):")
            print(f"   值: {object_val}")
            print(f"   生效: {valid_from[:19]} | 状态: {status}")
            print(f"   提交: {commit_ts[:19]} | 重要性: {importance}")
            print(f"   {duration}")
            print()
    else:
        print("   无版本历史")
    
    conn.close()


def query_change_log(user_id, limit=10, order_by='desc'):
    """查询变更日志"""
    db_path = 'memory_db/spanner_memory.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 确定排序方式 - 使用id字段确保正确顺序
    order_clause = "ORDER BY id DESC" if order_by.lower() == 'desc' else "ORDER BY id ASC"
    order_text = "倒序" if order_by.lower() == 'desc' else "正序"
    
    print(f"\n📝 用户 {user_id} 的变更日志 (最近{limit}条, {order_text}):")
    print("-" * 60)
    
    cursor.execute(f'''
        SELECT table_name, op, keys, new_snapshot, commit_ts
        FROM change_log
        WHERE user_id = ?
        {order_clause}
        LIMIT ?
    ''', (user_id, limit))
    
    changes = cursor.fetchall()
    
    if changes:
        for i, change in enumerate(changes, 1):
            table_name, op, keys, snapshot, commit_ts = change
            
            keys_data = json.loads(keys) if keys else {}
            snapshot_data = json.loads(snapshot) if snapshot else {}
            
            print(f"🔸 变更 {i} ({commit_ts[:19]}):")
            print(f"   表: {table_name} | 操作: {op}")
            print(f"   键: {keys_data}")
            if 'object' in snapshot_data:
                print(f"   值: {snapshot_data.get('object', 'N/A')}")
            print()
    else:
        print("   无变更记录")
    
    conn.close()


def main():
    parser = argparse.ArgumentParser(description='SQLite双时态记忆查询工具')
    parser.add_argument('--user', help='用户ID')
    parser.add_argument('--structure', action='store_true', help='显示表结构')
    parser.add_argument('--history', nargs=2, help='查询版本历史: subject predicate')
    parser.add_argument('--changes', action='store_true', help='显示变更日志')
    parser.add_argument('--limit', type=int, default=10, help='变更日志显示条数 (默认: 10)')
    parser.add_argument('--order', choices=['asc', 'desc'], default='desc', help='变更日志排序方式 (默认: desc倒序)')
    
    args = parser.parse_args()
    
    print("🧠 SQLite双时态记忆查询工具")
    print("=" * 80)
    
    if args.structure:
        display_table_structure()
    
    if args.user:
        query_current_facts(args.user)
        
        if args.history:
            subject, predicate = args.history
            query_version_history(args.user, subject, predicate)
        
        if args.changes:
            query_change_log(args.user, args.limit, args.order)
    
    if not any([args.structure, args.user]):
        print("💡 使用示例:")
        print("   python3 memory_query_spanner.py --structure")
        print("   python3 memory_query_spanner.py --user test_user")
        print("   python3 memory_query_spanner.py --user test_user --history user_profile name")
        print("   python3 memory_query_spanner.py --user test_user --changes")
        print("   python3 memory_query_spanner.py --user test_user --changes --limit 20 --order desc")
        print("   python3 memory_query_spanner.py --user test_user --changes --order asc")


if __name__ == "__main__":
    main()
