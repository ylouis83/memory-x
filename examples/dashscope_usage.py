#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DashScope集成使用示例
演示如何使用DashScope API进行记忆管理和AI对话
"""

import os
import sys
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """主函数"""
    print("🚀 Memory-X DashScope集成示例")
    print("=" * 50)
    
    # 检查API密钥
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ 未设置DASHSCOPE_API_KEY环境变量")
        print("请设置环境变量：export DASHSCOPE_API_KEY='your-api-key'")
        return False
    
    print(f"✅ API密钥已设置: {api_key[:10]}...")
    
    try:
        from src.core.dashscope_memory_manager import DashScopeMemoryManager
        
        # 创建记忆管理器
        user_id = "demo_user"
        memory_manager = DashScopeMemoryManager(user_id)
        print("✅ DashScope记忆管理器创建成功")
        
        # 测试对话
        test_conversations = [
            "你好，我叫张三，今年30岁",
            "我对青霉素过敏，请记住这一点",
            "我有高血压，正在服用氨氯地平",
            "我最近头痛，能吃什么药？",
            "我想了解一下我的过敏史",
            "我的血压控制得怎么样？"
        ]
        
        print("\n💬 开始测试对话...")
        
        for i, message in enumerate(test_conversations, 1):
            print(f"\n--- 对话 {i} ---")
            print(f"用户: {message}")
            
            # 处理消息
            start_time = time.time()
            result = memory_manager.process_message(message)
            end_time = time.time()
            
            print(f"AI: {result['response']}")
            print(f"意图: {result['intent']}")
            print(f"重要性: {result['importance']}")
            print(f"处理时间: {end_time - start_time:.2f}秒")
            
            # 显示实体信息
            if result['entities']:
                print("实体信息:")
                for entity_type, entities in result['entities'].items():
                    print(f"  {entity_type}: {entities}")
        
        # 测试记忆搜索
        print("\n🔍 测试记忆搜索...")
        search_queries = ["过敏", "高血压", "头痛", "张三"]
        
        for query in search_queries:
            print(f"\n搜索: '{query}'")
            results = memory_manager.search_memories(query, top_k=3)
            
            if results:
                for i, memory in enumerate(results, 1):
                    print(f"  {i}. 相似度: {memory['similarity']:.3f}")
                    print(f"     用户: {memory['user_message']}")
                    print(f"     AI: {memory['ai_response'][:50]}...")
            else:
                print("  未找到相关记忆")
        
        # 获取统计信息
        print("\n📊 统计信息:")
        stats = memory_manager.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # 显示工作记忆
        print("\n🧠 工作记忆:")
        for entity_type, entities in memory_manager.working_memory.items():
            print(f"  {entity_type}: {list(entities)}")
        
        print("\n✅ DashScope集成测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
