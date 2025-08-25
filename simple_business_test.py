#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Memory-X 简化业务测试
专注于核心功能测试，不依赖服务器
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_core_functionality():
    """测试核心功能"""
    print("🚀 Memory-X 核心功能测试")
    print("=" * 50)
    
    # 检查API密钥
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ 未设置DASHSCOPE_API_KEY环境变量")
        return False
    
    print(f"✅ API密钥已设置: {api_key[:10]}...")
    
    try:
        from src.core.dashscope_memory_manager import DashScopeMemoryManager
        
        # 创建记忆管理器
        memory_manager = DashScopeMemoryManager("business_test_user")
        print("✅ 记忆管理器创建成功")
        
        # 测试基础对话
        print("\n💬 测试基础对话...")
        test_messages = [
            "你好，我叫张三，今年30岁",
            "我对青霉素过敏",
            "我有高血压，在吃氨氯地平",
            "我最近头痛，能吃什么药？"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n--- 对话 {i} ---")
            print(f"用户: {message}")
            
            start_time = time.time()
            result = memory_manager.process_message(message)
            end_time = time.time()
            
            print(f"AI: {result['response'][:100]}...")
            print(f"意图: {result['intent']}")
            print(f"重要性: {result['importance']}")
            print(f"处理时间: {end_time - start_time:.2f}秒")
            
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
        
        print("\n✅ 核心功能测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance():
    """测试性能"""
    print("\n⚡ 性能测试")
    print("=" * 30)
    
    try:
        from src.core.dashscope_memory_manager import DashScopeMemoryManager
        
        memory_manager = DashScopeMemoryManager("perf_test_user")
        
        # 测试响应时间
        test_message = "这是一个性能测试消息"
        
        start_time = time.time()
        result = memory_manager.process_message(test_message)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        print(f"响应时间: {response_time:.2f}秒")
        
        if response_time < 10:
            print("✅ 响应时间正常")
        else:
            print("⚠️ 响应时间较长")
        
        # 测试内存使用
        try:
            import psutil
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            print(f"内存使用: {memory_usage:.1f}MB")
            
            if memory_usage < 500:
                print("✅ 内存使用正常")
            else:
                print("⚠️ 内存使用较高")
        except ImportError:
            print("⚠️ 无法检查内存使用（缺少psutil模块）")
        
        return True
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        return False

def test_error_handling():
    """测试错误处理"""
    print("\n🛡️ 错误处理测试")
    print("=" * 30)
    
    try:
        from src.core.dashscope_memory_manager import DashScopeMemoryManager
        
        # 测试空消息
        memory_manager = DashScopeMemoryManager("error_test_user")
        result = memory_manager.process_message("")
        
        if result['success']:
            print("✅ 空消息处理正常")
        else:
            print("⚠️ 空消息处理异常")
        
        # 测试特殊字符
        result = memory_manager.process_message("测试特殊字符：@#$%^&*()")
        
        if result['success']:
            print("✅ 特殊字符处理正常")
        else:
            print("⚠️ 特殊字符处理异常")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False

def generate_test_report(results):
    """生成测试报告"""
    print("\n" + "=" * 50)
    print("📊 测试报告")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"总测试数: {total_tests}")
    print(f"通过: {passed_tests} ✅")
    print(f"失败: {failed_tests} ❌")
    print(f"成功率: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n🎉 系统运行良好，可以投入生产使用")
    elif success_rate >= 70:
        print("\n⚠️ 系统基本可用，建议修复失败的测试")
    else:
        print("\n❌ 系统存在问题，需要重点修复")
    
    # 保存报告
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "success_rate": success_rate,
        "results": results
    }
    
    report_file = f"simple_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存到: {report_file}")
    
    return success_rate >= 90

def main():
    """主函数"""
    print("🚀 Memory-X 简化业务测试开始")
    
    results = []
    
    # 运行测试
    results.append(test_core_functionality())
    results.append(test_performance())
    results.append(test_error_handling())
    
    # 生成报告
    success = generate_test_report(results)
    
    if success:
        print("\n✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("\n⚠️ 部分测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
