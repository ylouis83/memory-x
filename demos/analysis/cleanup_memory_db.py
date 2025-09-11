#!/usr/bin/env python3
"""
Memory-X 数据库清理脚本
保留必要的数据库，清理测试和演示用的临时数据库
"""

import os
import shutil
import sqlite3
from datetime import datetime
from typing import List, Dict, Any

def get_db_info(db_path: str) -> Dict[str, Any]:
    """获取数据库信息"""
    if not os.path.exists(db_path):
        return {"exists": False}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表信息
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # 获取数据统计
        stats = {}
        total_records = 0
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
                total_records += count
            except:
                stats[table] = 0
        
        # 获取文件大小
        file_size = os.path.getsize(db_path)
        
        conn.close()
        
        return {
            "exists": True,
            "tables": tables,
            "stats": stats,
            "total_records": total_records,
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2)
        }
    except Exception as e:
        return {"exists": True, "error": str(e)}

def analyze_databases():
    """分析所有数据库"""
    print("🔍 Memory-X 数据库清理分析")
    print("=" * 60)
    
    # 所有数据库文件
    db_files = [
        "/Users/louisliu/.cursor/memory-x/memory_db/spanner_memory.db",
        "/Users/louisliu/.cursor/memory-x/memory_db/user_memories.db", 
        "/Users/louisliu/.cursor/memory-x/examples/data/demo_medical_graph.db",
        "/Users/louisliu/.cursor/memory-x/examples/data/simple_memory.db",
        "/Users/louisliu/.cursor/memory-x/data/demo_medical_graph.db",
        "/Users/louisliu/.cursor/memory-x/data/diabetes_test.db",
        "/Users/louisliu/.cursor/memory-x/data/qwen_update_demo.db",
        "/Users/louisliu/.cursor/memory-x/data/qwen_demo.db",
        "/Users/louisliu/.cursor/memory-x/data/simple_memory.db",
        "/Users/louisliu/.cursor/memory-x/data/diabetes_scenario_demo.db",
        "/Users/louisliu/.cursor/memory-x/data/update_demo.db",
        "/Users/louisliu/.cursor/memory-x/data/online_consult_diabetes_demo.db",
        "/Users/louisliu/.cursor/memory-x/data/enhanced_qwen_demo.db",
        "/Users/louisliu/.cursor/memory-x/data/dashscope_memory.db",
        "/Users/louisliu/.cursor/memory-x/data/test.db",
        "/Users/louisliu/.cursor/memory-x/data/qwen_multi_demo.db"
    ]
    
    # 分类数据库
    essential_dbs = []  # 核心必要数据库
    demo_dbs = []       # 演示数据库
    test_dbs = []       # 测试数据库
    empty_dbs = []      # 空数据库
    
    total_size = 0
    
    for db_path in db_files:
        db_name = os.path.basename(db_path)
        db_info = get_db_info(db_path)
        
        if not db_info["exists"]:
            continue
            
        if "error" in db_info:
            print(f"❌ {db_name}: 读取错误 - {db_info['error']}")
            continue
        
        total_size += db_info.get("size_bytes", 0)
        
        print(f"\n📊 {db_name}")
        print(f"   路径: {db_path}")
        print(f"   大小: {db_info.get('size_mb', 0)} MB")
        print(f"   表数: {len(db_info.get('tables', []))}")
        print(f"   记录数: {db_info.get('total_records', 0)}")
        
        if db_info.get('tables'):
            print(f"   表结构: {', '.join(db_info['tables'])}")
            if db_info.get('stats'):
                for table, count in db_info['stats'].items():
                    if count > 0:
                        print(f"     - {table}: {count}条")
        
        # 分类判断
        if db_info.get('total_records', 0) == 0:
            empty_dbs.append((db_path, db_info))
            print("   🔴 类型: 空数据库 (建议删除)")
        elif "memory_db" in db_path:
            essential_dbs.append((db_path, db_info))
            print("   🟢 类型: 核心数据库 (保留)")
        elif any(keyword in db_name for keyword in ["demo", "test", "scenario"]):
            demo_dbs.append((db_path, db_info))
            print("   🟡 类型: 演示/测试数据库 (可选清理)")
        elif db_info.get('total_records', 0) > 0:
            # 有数据的生产数据库
            essential_dbs.append((db_path, db_info))
            print("   🟢 类型: 有数据库 (建议保留)")
        else:
            test_dbs.append((db_path, db_info))
            print("   🟡 类型: 其他数据库 (可选清理)")
    
    # 汇总分析
    print(f"\n📈 数据库分析汇总")
    print("=" * 60)
    print(f"📁 总数据库文件: {len([f for f in db_files if os.path.exists(f)])}")
    print(f"💾 总占用空间: {round(total_size / (1024 * 1024), 2)} MB")
    print(f"🟢 核心必要数据库: {len(essential_dbs)}个")
    print(f"🟡 演示/测试数据库: {len(demo_dbs)}个") 
    print(f"🔴 空数据库: {len(empty_dbs)}个")
    
    return {
        "essential": essential_dbs,
        "demo": demo_dbs,
        "test": test_dbs,
        "empty": empty_dbs,
        "total_size_mb": round(total_size / (1024 * 1024), 2)
    }

def create_cleanup_plan(analysis_result):
    """创建清理计划"""
    print(f"\n📋 数据库清理计划")
    print("=" * 60)
    
    # 保留的数据库
    print(f"🟢 保留数据库 ({len(analysis_result['essential'])}个):")
    for db_path, db_info in analysis_result['essential']:
        db_name = os.path.basename(db_path)
        print(f"   ✅ {db_name} ({db_info.get('size_mb', 0)} MB, {db_info.get('total_records', 0)}条记录)")
    
    # 建议清理的数据库
    cleanup_candidates = analysis_result['demo'] + analysis_result['test'] + analysis_result['empty']
    
    if cleanup_candidates:
        print(f"\n🗑️ 建议清理 ({len(cleanup_candidates)}个):")
        cleanup_size = 0
        for db_path, db_info in cleanup_candidates:
            db_name = os.path.basename(db_path)
            size_mb = db_info.get('size_mb', 0)
            cleanup_size += size_mb
            records = db_info.get('total_records', 0)
            
            if records == 0:
                reason = "空数据库"
            elif any(keyword in db_name for keyword in ["demo", "test", "scenario"]):
                reason = "演示/测试数据库"
            else:
                reason = "临时数据库"
                
            print(f"   🗑️ {db_name} ({size_mb} MB, {records}条记录) - {reason}")
        
        print(f"\n💾 清理后节省空间: {round(cleanup_size, 2)} MB")
        
        return cleanup_candidates
    else:
        print(f"\n✅ 无需清理，所有数据库都是必要的")
        return []

def execute_cleanup(cleanup_list, dry_run=True):
    """执行清理操作"""
    if not cleanup_list:
        print("✅ 无文件需要清理")
        return
    
    backup_dir = "/Users/louisliu/.cursor/memory-x/backup/db_cleanup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if dry_run:
        print(f"\n🔍 预演清理操作 (dry run):")
        print(f"📁 备份目录: {backup_dir}")
        for db_path, db_info in cleanup_list:
            print(f"   🗑️ 将删除: {os.path.basename(db_path)}")
        print(f"\n💡 如需执行实际清理，请运行: python cleanup_memory_db.py --execute")
    else:
        print(f"\n🗑️ 执行清理操作:")
        
        # 创建备份目录
        os.makedirs(backup_dir, exist_ok=True)
        
        deleted_count = 0
        saved_space = 0
        
        for db_path, db_info in cleanup_list:
            try:
                db_name = os.path.basename(db_path)
                
                # 备份文件
                backup_path = os.path.join(backup_dir, db_name)
                shutil.copy2(db_path, backup_path)
                print(f"   📦 备份: {db_name}")
                
                # 删除原文件
                os.remove(db_path)
                print(f"   ✅ 删除: {db_name}")
                
                deleted_count += 1
                saved_space += db_info.get('size_mb', 0)
                
            except Exception as e:
                print(f"   ❌ 删除失败 {db_name}: {e}")
        
        print(f"\n🎉 清理完成:")
        print(f"   📁 备份位置: {backup_dir}")
        print(f"   🗑️ 删除文件: {deleted_count}个")
        print(f"   💾 节省空间: {round(saved_space, 2)} MB")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Memory-X 数据库清理工具")
    parser.add_argument("--execute", action="store_true", help="执行实际清理操作")
    parser.add_argument("--force", action="store_true", help="强制清理，不询问确认")
    
    args = parser.parse_args()
    
    # 分析数据库
    analysis = analyze_databases()
    
    # 创建清理计划
    cleanup_list = create_cleanup_plan(analysis)
    
    if not cleanup_list:
        return
    
    # 执行清理
    if args.execute:
        if not args.force:
            confirm = input(f"\n❓ 确认清理 {len(cleanup_list)} 个数据库文件吗? (y/N): ")
            if confirm.lower() != 'y':
                print("❌ 用户取消操作")
                return
        
        execute_cleanup(cleanup_list, dry_run=False)
    else:
        execute_cleanup(cleanup_list, dry_run=True)

if __name__ == "__main__":
    main()
