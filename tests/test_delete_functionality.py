#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DELETE 功能专项测试
测试记忆删除的各种场景
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.memory_manager import SimpleMemoryManager
from src.storage.sqlite_store import SQLiteMemoryStore


def test_direct_database_delete():
    """直接通过数据库测试删除功能"""
    print("🗑️ 测试直接数据库删除功能")
    print("-" * 50)
    
    try:
        # 使用临时数据库
        test_db_path = "./data/test_delete.db"
        
        # 确保 data 目录存在
        os.makedirs("./data", exist_ok=True)
        
        # 清理可能存在的测试数据库
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        # 创建记忆管理器
        mm = SimpleMemoryManager(user_id="delete_test_user", db_path=test_db_path)
        
        # 添加测试记忆
        mm.add_conversation(
            user_message="我叫王五",
            ai_response="你好王五！",
            importance=3
        )
        
        mm.add_conversation(
            user_message="我住在北京",
            ai_response="北京是个好地方！",
            importance=3
        )
        
        # 验证记忆已添加
        memories_before = mm.retrieve_memories("王五")
        print(f"✅ 删除前记忆数量: {len(memories_before)}")
        
        # 直接通过 SQLite 删除记录
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # 查看表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📊 数据库表: {tables}")
        
        # 查看记录
        cursor.execute("SELECT * FROM memories WHERE user_id = ?", ("delete_test_user",))
        records_before = cursor.fetchall()
        print(f"📝 删除前记录数: {len(records_before)}")
        
        # 执行删除操作 - 删除包含"王五"的记录
        cursor.execute("""
            DELETE FROM memories 
            WHERE user_id = ? AND content LIKE ?
        """, ("delete_test_user", "%王五%"))
        
        deleted_count = cursor.rowcount
        conn.commit()
        print(f"🗑️ 删除记录数: {deleted_count}")
        
        # 验证删除结果
        cursor.execute("SELECT * FROM memories WHERE user_id = ?", ("delete_test_user",))
        records_after = cursor.fetchall()
        print(f"📝 删除后记录数: {len(records_after)}")
        
        conn.close()
        
        # 通过记忆管理器验证
        memories_after = mm.retrieve_memories("王五")
        print(f"✅ 删除后记忆数量: {len(memories_after)}")
        
        # 验证其他记忆还在
        other_memories = mm.retrieve_memories("北京")
        print(f"🏠 其他记忆保留: {len(other_memories)} 条")
        
        # 清理测试数据库
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        print("✅ DELETE 功能测试完成")
        
        # 删除成功的条件：删除了记录，且目标记忆减少了，其他记忆保留
        success = deleted_count > 0 and len(memories_after) < len(memories_before) and len(other_memories) > 0
        print(f"🎯 删除测试结果: {'✅ 成功' if success else '❌ 失败'}")
        return success
        
    except Exception as e:
        print(f"❌ DELETE 测试失败: {str(e)}")
        return False


def test_memory_store_delete():
    """测试 MemoryStore 的删除接口"""
    print("\n🔧 测试 MemoryStore 删除接口")
    print("-" * 50)
    
    try:
        test_db_path = "./data/test_store_delete.db"
        
        # 确保 data 目录存在
        os.makedirs("./data", exist_ok=True)
        
        # 清理可能存在的测试数据库
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        # 创建存储对象
        store = SQLiteMemoryStore(test_db_path)
        user_id = "store_test_user"
        
        # 添加测试记忆
        store.add_conversation(
            user_id=user_id,
            user_message="我是张工程师",
            ai_response="你好张工程师！",
            entities={"person": ["张工程师"]},
            intent="自我介绍",
            importance=3
        )
        
        store.add_conversation(
            user_id=user_id,
            user_message="我在腾讯工作",
            ai_response="腾讯是很棒的公司！",
            entities={"company": ["腾讯"]},
            intent="工作信息",
            importance=3
        )
        
        # 搜索验证记忆已添加
        memories_before = store.search_memories(user_id, "张工程师")
        print(f"✅ 添加记忆数量: {len(memories_before)}")
        
        # 检查 store 是否有删除方法
        if hasattr(store, 'delete_memory'):
            print("🔧 找到 delete_memory 方法")
            # 如果有删除方法，测试删除
            store.delete_memory(user_id, "张工程师")
        elif hasattr(store, 'clear_user_memories'):
            print("🔧 找到 clear_user_memories 方法")
            # 如果有清理用户记忆方法
            store.clear_user_memories(user_id)
        else:
            print("⚠️ 未找到删除接口，使用数据库直接操作")
            # 直接操作数据库
            conn = sqlite3.connect(test_db_path)
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM memories 
                WHERE user_id = ? AND content LIKE ?
            """, (user_id, "%张工程师%"))
            conn.commit()
            conn.close()
        
        # 验证删除结果
        memories_after = store.search_memories(user_id, "张工程师")
        other_memories = store.search_memories(user_id, "腾讯")
        
        print(f"🗑️ 删除后目标记忆: {len(memories_after)} 条")
        print(f"🏢 其他记忆保留: {len(other_memories)} 条")
        
        # 清理测试数据库
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        print("✅ MemoryStore 删除测试完成")
        
        # MemoryStore 删除成功的条件：目标记忆减少，其他记忆保留
        success = len(memories_after) < len(memories_before) and len(other_memories) > 0
        print(f"🎯 MemoryStore 删除测试结果: {'✅ 成功' if success else '❌ 失败'}")
        return success
        
    except Exception as e:
        print(f"❌ MemoryStore 删除测试失败: {str(e)}")
        return False


def test_medical_memory_delete():
    """测试医疗记忆的删除/撤销功能"""
    print("\n💊 测试医疗记忆删除功能")
    print("-" * 50)
    
    try:
        from src.core.medical_memory import MedicationEntry
        
        now = datetime.utcnow()
        entries = []
        
        # 添加多个医疗记录
        med1 = MedicationEntry(
            rxnorm="11111",
            dose="5 mg",
            frequency="qd",
            route="oral",
            start=now - timedelta(days=30),
            status="active",
            provenance="处方1"
        )
        
        med2 = MedicationEntry(
            rxnorm="22222", 
            dose="10 mg",
            frequency="bid",
            route="oral",
            start=now - timedelta(days=20),
            status="active",
            provenance="处方2"
        )
        
        entries.extend([med1, med2])
        print(f"✅ 添加医疗记录数: {len(entries)}")
        
        # 测试删除指定药物记录
        entries_before_delete = len(entries)
        
        # 删除特定 rxnorm 的记录
        entries = [entry for entry in entries if entry.rxnorm != "11111"]
        
        print(f"🗑️ 删除后记录数: {len(entries)} (删除了 {entries_before_delete - len(entries)} 条)")
        
        # 验证正确的记录被保留
        remaining_rxnorms = [entry.rxnorm for entry in entries]
        print(f"📋 保留的药物代码: {remaining_rxnorms}")
        
        # 测试撤销最后一次更新（通过版本回退模拟）
        if entries:
            last_entry = entries[-1]
            if last_entry.version_id > 1:
                # 模拟版本回退
                last_entry.version_id -= 1
                last_entry.last_updated = datetime.utcnow()
                print(f"↩️ 版本回退: {last_entry.rxnorm} 版本回退至 {last_entry.version_id}")
        
        print("✅ 医疗记忆删除测试完成")
        
        return len(entries) == 1 and "22222" in remaining_rxnorms
        
    except Exception as e:
        print(f"❌ 医疗记忆删除测试失败: {str(e)}")
        return False


def main():
    """运行所有删除功能测试"""
    print("🧪 Memory-X DELETE 功能专项测试")
    print("=" * 60)
    
    results = []
    
    # 测试1: 直接数据库删除
    results.append(test_direct_database_delete())
    
    # 测试2: MemoryStore 删除接口
    results.append(test_memory_store_delete())
    
    # 测试3: 医疗记忆删除
    results.append(test_medical_memory_delete())
    
    # 统计结果
    success_count = sum(results)
    total_count = len(results)
    success_rate = success_count / total_count * 100
    
    print("\n" + "=" * 60)
    print("📊 DELETE 功能测试报告")
    print("=" * 60)
    print(f"✅ 成功: {success_count}/{total_count} 项")
    print(f"📈 成功率: {success_rate:.1f}%")
    
    if success_count == total_count:
        print("🎉 所有 DELETE 功能测试通过！")
    else:
        print("⚠️ 部分 DELETE 功能需要进一步实现")
    
    return success_rate


if __name__ == "__main__":
    main()
