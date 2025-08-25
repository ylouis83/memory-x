#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI-安主任记忆查询工具套件主入口
统一管理所有记忆查询功能
"""

import argparse
import os
import sys
import subprocess


def show_tool_menu():
    """显示工具菜单"""
    print("🧠 AI-安主任记忆查询工具套件")
    print("=" * 80)
    print("\n🛠️ 可用工具:")
    print("1. memory_query_basic      - 基础记忆查询（原始架构）")
    print("2. memory_query_advanced   - 高级记忆查询（原始架构）")
    print("3. memory_query_spanner    - SQLite双时态查询（双时态架构）")
    print("4. memory_query_migration  - 数据迁移工具")
    print("5. memory_query_test       - 记忆系统测试")
    
    print("\n💡 使用示例:")
    print("python3 memory_query_main.py --tool sqlite --user test_user")
    print("python3 memory_query_main.py --tool migration")
    print("python3 memory_query_main.py --tool basic")
    print("python3 memory_query_main.py --list-tools")


def run_tool(tool_name, args):
    """运行指定的工具"""
    tool_mapping = {
        'basic': 'memory_query_basic.py',
        'advanced': 'memory_query_advanced.py', 
        'sqlite': 'memory_query_spanner.py',  # SQLite双时态查询
        'migration': 'memory_query_migration.py',
        'test': 'memory_query_test.py'
    }
    
    if tool_name not in tool_mapping:
        print(f"❌ 未知工具: {tool_name}")
        print(f"可用工具: {list(tool_mapping.keys())}")
        return
    
    tool_file = tool_mapping[tool_name]
    
    if not os.path.exists(tool_file):
        print(f"❌ 工具文件不存在: {tool_file}")
        return
    
    # 构建命令
    cmd = ['python3', tool_file] + args
    
    print(f"🚀 运行工具: {tool_name}")
    print(f"📋 命令: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 工具执行失败: {e}")
    except KeyboardInterrupt:
        print("\\n⚠️ 用户中断执行")


def main():
    parser = argparse.ArgumentParser(description='AI-安主任记忆查询工具套件')
    parser.add_argument('--tool', choices=['basic', 'advanced', 'sqlite', 'migration', 'test'], 
                       help='选择要使用的工具')
    parser.add_argument('--list-tools', action='store_true', help='列出所有可用工具')
    parser.add_argument('--user', help='用户ID（传递给子工具）')
    parser.add_argument('--search', help='搜索关键词（传递给子工具）')
    parser.add_argument('--structure', action='store_true', help='显示表结构（传递给子工具）')
    parser.add_argument('--history', nargs=2, help='查询版本历史: subject predicate（传递给子工具）')
    parser.add_argument('--changes', action='store_true', help='显示变更日志（传递给子工具）')
    parser.add_argument('--limit', type=int, help='变更日志显示条数（传递给子工具）')
    parser.add_argument('--order', choices=['asc', 'desc'], help='变更日志排序方式（传递给子工具）')
    
    args, unknown_args = parser.parse_known_args()
    
    if args.list_tools or not args.tool:
        show_tool_menu()
        return
    
    # 构建传递给子工具的参数
    sub_args = unknown_args.copy()
    
    if args.user:
        sub_args.extend(['--user', args.user])
    if args.search:
        sub_args.extend(['--search', args.search])
    if args.structure:
        sub_args.append('--structure')
    if args.history:
        sub_args.extend(['--history'] + args.history)
    if args.changes:
        sub_args.append('--changes')
    if args.limit:
        sub_args.extend(['--limit', str(args.limit)])
    if args.order:
        sub_args.extend(['--order', args.order])
    
    # 运行指定工具
    run_tool(args.tool, sub_args)


if __name__ == "__main__":
    main()
