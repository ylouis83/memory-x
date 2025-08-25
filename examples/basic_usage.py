#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Memory-X 基础使用示例
演示如何使用Memory-X进行基本的记忆管理
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.core.memory_manager import SimpleMemoryManager, SimpleMemoryIntegratedAI


def basic_memory_example():
    """基础记忆使用示例"""
    print("🧠 Memory-X 基础使用示例")
    print("=" * 50)
    
    # 创建记忆管理器
    memory_manager = SimpleMemoryManager(user_id="user_001")
    
    # 示例1: 添加用户基本信息
    print("\n📝 示例1: 添加用户基本信息")
    print("-" * 30)
    
    result = memory_manager.add_conversation(
        user_message="我叫张三，今年30岁",
        ai_response="你好张三，很高兴认识你！我会记住你的基本信息。",
        entities={"PERSON": [("张三", 0, 2)], "AGE": [("30", 5, 7)]},
        intent="INTRODUCE",
        importance=3
    )
    
    print(f"添加结果: {result}")
    
    # 示例2: 添加医疗信息
    print("\n📝 示例2: 添加医疗信息")
    print("-" * 30)
    
    result = memory_manager.add_conversation(
        user_message="我对青霉素过敏",
        ai_response="好的，我会记住你对青霉素过敏，以后开药时会注意避开。",
        entities={"ALLERGY": [("青霉素", 2, 4)]},
        intent="MEDICAL_INFO",
        importance=4
    )
    
    print(f"添加结果: {result}")
    
    # 示例3: 查询记忆
    print("\n📝 示例3: 查询记忆")
    print("-" * 30)
    
    # 查询短期记忆
    short_term_count = len(memory_manager.short_term_memory)
    print(f"短期记忆数量: {short_term_count} 条")
    
    # 查询工作记忆
    working_memory_size = len(memory_manager.working_memory)
    print(f"工作记忆大小: {working_memory_size}")
    
    # 示例4: 获取记忆统计
    print("\n📝 示例4: 获取记忆统计")
    print("-" * 30)
    
    stats = memory_manager.get_memory_stats()
    print(f"记忆统计: {stats}")


def integrated_ai_example():
    """集成AI示例"""
    print("\n🤖 Memory-X 集成AI示例")
    print("=" * 50)
    
    # 创建集成AI实例
    memory_ai = SimpleMemoryIntegratedAI()
    
    # 示例对话
    conversations = [
        "我叫李四",
        "我头痛",
        "我对阿司匹林过敏",
        "我的血压有点高",
        "我今年45岁"
    ]
    
    for i, message in enumerate(conversations, 1):
        print(f"\n💬 对话 {i}: {message}")
        print("-" * 30)
        
        # 处理消息
        result = memory_ai.process_message(message, "user_002")
        
        print(f"AI回复: {result['response']}")
        print(f"检测意图: {result['intent']['detected']}")
        print(f"重要性: {result['memory_info']['importance']}")
        print(f"使用长期记忆: {result['memory_info']['used_long_term']}")
    
    # 查询用户信息
    print("\n📊 查询用户信息")
    print("-" * 30)
    
    # 询问用户名字
    result = memory_ai.process_message("我的名字叫什么？", "user_002")
    print(f"AI回复: {result['response']}")
    
    # 询问过敏史
    result = memory_ai.process_message("我有什么过敏史吗？", "user_002")
    print(f"AI回复: {result['response']}")
    
    # 获取统计信息
    stats = memory_ai.get_stats("user_002")
    print(f"\n用户统计: {stats}")


def memory_operations_example():
    """记忆操作示例"""
    print("\n🔧 Memory-X 记忆操作示例")
    print("=" * 50)
    
    memory_manager = SimpleMemoryManager(user_id="user_003")
    
    # 添加不同类型的记忆
    print("\n📝 添加不同类型的记忆")
    print("-" * 30)
    
    # 低重要性记忆
    memory_manager.add_conversation(
        user_message="今天天气不错",
        ai_response="是的，天气确实很好。",
        importance=1
    )
    
    # 中等重要性记忆
    memory_manager.add_conversation(
        user_message="我喜欢吃苹果",
        ai_response="苹果是很好的水果，富含维生素。",
        entities={"FOOD": [("苹果", 3, 5)]},
        importance=2
    )
    
    # 高重要性记忆
    memory_manager.add_conversation(
        user_message="我有糖尿病",
        ai_response="糖尿病需要特别注意饮食和血糖控制。",
        entities={"DISEASE": [("糖尿病", 2, 4)]},
        importance=4
    )
    
    # 查看记忆统计
    stats = memory_manager.get_memory_stats()
    print(f"记忆统计: {stats}")
    
    # 清空会话
    print("\n🗑️ 清空会话")
    print("-" * 30)
    
    memory_manager.clear_session()
    stats = memory_manager.get_memory_stats()
    print(f"清空后统计: {stats}")


def main():
    """主函数"""
    print("🚀 Memory-X 使用示例")
    print("=" * 60)
    
    try:
        # 基础记忆示例
        basic_memory_example()
        
        # 集成AI示例
        integrated_ai_example()
        
        # 记忆操作示例
        memory_operations_example()
        
        print("\n🎉 所有示例执行完成！")
        
    except Exception as e:
        print(f"❌ 示例执行失败: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
