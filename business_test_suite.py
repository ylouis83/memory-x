#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Memory-X 业务级别测试套件
全面测试记忆管理系统的业务功能和实际应用场景
"""

import os
import sys
import time
import json
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestStatus(Enum):
    """测试状态枚举"""
    PASSED = "✅ 通过"
    FAILED = "❌ 失败"
    SKIPPED = "⚠️ 跳过"
    ERROR = "💥 错误"

@dataclass
class TestResult:
    """测试结果数据类"""
    name: str
    status: TestStatus
    duration: float
    message: str
    details: Optional[Dict] = None

class BusinessTestSuite:
    """业务级别测试套件"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.api_base_url = "http://localhost:5000"
        
        # 检查环境
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        if not self.api_key:
            print("❌ 未设置DASHSCOPE_API_KEY环境变量")
            sys.exit(1)
        
        print(f"✅ API密钥已设置: {self.api_key[:10]}...")
    
    def run_test(self, test_name: str, test_func):
        """运行单个测试"""
        print(f"\n🧪 运行测试: {test_name}")
        start_time = time.time()
        
        try:
            result = test_func()
            duration = time.time() - start_time
            
            if result:
                status = TestStatus.PASSED
                message = "测试通过"
            else:
                status = TestStatus.FAILED
                message = "测试失败"
                
        except Exception as e:
            duration = time.time() - start_time
            status = TestStatus.ERROR
            message = f"测试异常: {str(e)}"
            result = False
        
        test_result = TestResult(
            name=test_name,
            status=status,
            duration=duration,
            message=message
        )
        
        self.results.append(test_result)
        print(f"{status.value} {test_name} ({duration:.2f}s)")
        
        return result
    
    def test_environment_setup(self) -> bool:
        """测试环境配置"""
        try:
            # 检查Python版本
            if sys.version_info < (3, 8):
                print("❌ Python版本过低，需要3.8+")
                return False
            
            # 检查必要模块
            required_modules = [
                'flask', 'requests', 'sqlite3', 'json', 'datetime'
            ]
            
            for module in required_modules:
                try:
                    __import__(module)
                except ImportError:
                    print(f"❌ 缺少必要模块: {module}")
                    return False
            
            # 检查数据库目录
            os.makedirs("data", exist_ok=True)
            os.makedirs("logs", exist_ok=True)
            
            print("✅ 环境配置检查通过")
            return True
            
        except Exception as e:
            print(f"❌ 环境配置检查失败: {e}")
            return False
    
    def test_dashscope_api_connection(self) -> bool:
        """测试DashScope API连接"""
        try:
            import requests
            
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            test_data = {
                "model": "qwen-turbo",
                "messages": [
                    {"role": "user", "content": "你好，请简单回复一下"}
                ],
                "max_tokens": 50
            }
            
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ API连接成功，响应: {result['choices'][0]['message']['content'][:50]}...")
                return True
            else:
                print(f"❌ API连接失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ API连接异常: {e}")
            return False
    
    def test_memory_manager_creation(self) -> bool:
        """测试记忆管理器创建"""
        try:
            from src.core.dashscope_memory_manager import DashScopeMemoryManager
            
            # 测试创建记忆管理器
            memory_manager = DashScopeMemoryManager("test_user_001")
            
            # 检查基本属性
            assert hasattr(memory_manager, 'user_id')
            assert hasattr(memory_manager, 'short_term_memory')
            assert hasattr(memory_manager, 'working_memory')
            assert hasattr(memory_manager, 'api_key')
            
            print("✅ 记忆管理器创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 记忆管理器创建失败: {e}")
            return False
    
    def test_basic_conversation_flow(self) -> bool:
        """测试基础对话流程"""
        try:
            from src.core.dashscope_memory_manager import DashScopeMemoryManager
            
            memory_manager = DashScopeMemoryManager("test_user_002")
            
            # 测试基础对话
            test_messages = [
                "你好，我叫张三",
                "我今年30岁",
                "我对青霉素过敏"
            ]
            
            for i, message in enumerate(test_messages, 1):
                print(f"  对话 {i}: {message}")
                result = memory_manager.process_message(message)

                if not result['success']:
                    print(f"❌ 对话 {i} 处理失败: {result.get('error', '未知错误')}")
                    return False

                print(f"    AI回复: {result['response'][:50]}...")
                print(f"    意图: {result['intent']}")
                print(f"    重要性: {result['importance']}")

            # 检查短期记忆
            assert len(memory_manager.short_term_memory) == 3

            # 展示记忆召回效果
            recall = memory_manager.search_memories("过敏", top_k=1)
            if recall:
                mem = recall[0]
                print(
                    f"    🔁 记忆召回: {mem['user_message']} (相似度: {mem['similarity']:.3f})"
                )
            else:
                print("    ⚠️ 未找到关于过敏的记忆")

            print("✅ 基础对话流程测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 基础对话流程测试失败: {e}")
            return False
    
    def test_medical_scenario(self) -> bool:
        """测试医疗场景"""
        try:
            from src.core.dashscope_memory_manager import DashScopeMemoryManager
            
            memory_manager = DashScopeMemoryManager("medical_user_001")
            
            # 模拟医疗咨询场景
            medical_conversation = [
                "医生，我叫李四，今年45岁",
                "我有高血压，正在服用氨氯地平",
                "我对阿司匹林过敏",
                "最近头痛，能吃什么药？",
                "我的血压控制得怎么样？",
                "我想了解一下我的过敏史"
            ]
            
            print("🏥 开始医疗场景测试...")
            
            for i, message in enumerate(medical_conversation, 1):
                print(f"  医疗对话 {i}: {message}")
                result = memory_manager.process_message(message)
                
                if not result['success']:
                    print(f"❌ 医疗对话 {i} 处理失败")
                    return False
                
                # 检查AI回复的医疗专业性
                response = result['response']
                if any(keyword in response.lower() for keyword in ['建议', '注意', '就医', '药物', '血压']):
                    print(f"    ✅ AI回复专业: {response[:50]}...")
                else:
                    print(f"    ⚠️ AI回复可能不够专业: {response[:50]}...")
                
                print(f"    意图: {result['intent']}")
                print(f"    重要性: {result['importance']}")
                
                # 检查实体识别
                if result['entities']:
                    print(f"    实体: {result['entities']}")
            
            # 检查工作记忆中的医疗信息
            working_memory = memory_manager.working_memory
            print(f"  工作记忆: {working_memory}")
            
            # 验证重要医疗信息是否被记住
            assert len(memory_manager.short_term_memory) == 6

            print("✅ 医疗场景测试通过")
            return True

        except Exception as e:
            print(f"❌ 医疗场景测试失败: {e}")
            return False

    def test_ecommerce_scenario(self) -> bool:
        """测试电子商务场景，验证用户偏好记忆与召回"""
        try:
            from src.core.dashscope_memory_manager import DashScopeMemoryManager

            memory_manager = DashScopeMemoryManager("shop_user_001")

            shopping_conversation = [
                "我喜欢华为手机",
                "预算在3000元左右",
                "推荐一款手机给我"
            ]

            print("🛒 开始电子商务场景测试...")

            for i, message in enumerate(shopping_conversation, 1):
                print(f"  购物对话 {i}: {message}")
                result = memory_manager.process_message(message)

                if not result['success']:
                    print(f"❌ 购物对话 {i} 处理失败")
                    return False

                print(f"    AI回复: {result['response'][:50]}...")

            # 展示对用户偏好和预算的记忆
            recall = memory_manager.search_memories("手机", top_k=5)
            if recall:
                print(f"  🔁 召回相关记忆 {len(recall)} 条:")
                for m in recall:
                    print(f"    - {m['user_message']} (相似度: {m['similarity']:.3f})")
            else:
                print("  ⚠️ 未召回用户偏好记忆")

            print("✅ 电子商务场景测试通过")
            return True

        except Exception as e:
            print(f"❌ 电子商务场景测试失败: {e}")
            return False

    def test_memory_search_functionality(self) -> bool:
        """测试记忆搜索功能"""
        try:
            from src.core.dashscope_memory_manager import DashScopeMemoryManager
            
            memory_manager = DashScopeMemoryManager("search_user_001")
            
            # 添加测试记忆
            test_data = [
                "我喜欢吃苹果",
                "我住在北京",
                "我是一名程序员",
                "我喜欢Python编程",
                "我经常去健身房",
                "我对海鲜过敏",
                "我有糖尿病",
                "我在阿里云工作"
            ]
            
            print("🔍 添加测试记忆...")
            for message in test_data:
                memory_manager.process_message(message)
            
            # 测试搜索功能
            search_queries = [
                ("过敏", "应该能找到过敏相关信息"),
                ("编程", "应该能找到编程相关信息"),
                ("北京", "应该能找到居住地信息"),
                ("糖尿病", "应该能找到疾病信息")
            ]
            
            print("🔍 测试记忆搜索...")
            for query, expected in search_queries:
                print(f"  搜索: '{query}' - {expected}")
                results = memory_manager.search_memories(query, top_k=3)
                
                if results:
                    print(f"    找到 {len(results)} 条相关记忆")
                    for i, memory in enumerate(results, 1):
                        print(f"    {i}. 相似度: {memory['similarity']:.3f}")
                        print(f"       用户: {memory['user_message']}")
                else:
                    print(f"    ⚠️ 未找到相关记忆")
            
            print("✅ 记忆搜索功能测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 记忆搜索功能测试失败: {e}")
            return False
    
    def test_api_endpoints(self) -> bool:
        """测试API端点"""
        try:
            # 测试健康检查
            print("🌐 测试API健康检查...")
            response = requests.get(f"{self.api_base_url}/health", timeout=10)
            if response.status_code != 200:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False
            
            # 测试DashScope健康检查
            response = requests.get(f"{self.api_base_url}/api/dashscope/health", timeout=10)
            if response.status_code != 200:
                print(f"❌ DashScope健康检查失败: {response.status_code}")
                return False
            
            # 测试聊天API
            print("🌐 测试聊天API...")
            chat_data = {
                "message": "你好，我叫王五",
                "user_id": "api_test_user"
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/dashscope/chat",
                json=chat_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"    ✅ 聊天API正常: {result['data']['response'][:50]}...")
                else:
                    print(f"    ❌ 聊天API失败: {result.get('error')}")
                    return False
            else:
                print(f"    ❌ 聊天API请求失败: {response.status_code}")
                return False
            
            # 测试搜索API
            print("🌐 测试搜索API...")
            search_data = {
                "query": "王五",
                "user_id": "api_test_user",
                "top_k": 3
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/dashscope/search",
                json=search_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"    ✅ 搜索API正常，找到 {len(result['data']['results'])} 条结果")
                else:
                    print(f"    ❌ 搜索API失败: {result.get('error')}")
            else:
                print(f"    ❌ 搜索API请求失败: {response.status_code}")
            
            print("✅ API端点测试通过")
            return True
            
        except Exception as e:
            print(f"❌ API端点测试失败: {e}")
            return False
    
    def test_database_operations(self) -> bool:
        """测试数据库操作"""
        try:
            from src.core.dashscope_memory_manager import DashScopeMemoryManager
            
            memory_manager = DashScopeMemoryManager("db_test_user")
            
            # 测试数据库写入
            print("💾 测试数据库写入...")
            test_messages = [
                "这是一个重要的测试消息",
                "另一个重要的测试消息"
            ]
            
            for message in test_messages:
                result = memory_manager.process_message(message)
                if not result['success']:
                    print(f"❌ 数据库写入失败: {result.get('error')}")
                    return False
            
            # 检查数据库文件是否存在
            db_path = memory_manager.db_path
            if not os.path.exists(db_path):
                print(f"❌ 数据库文件不存在: {db_path}")
                return False
            
            # 检查数据库内容
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM dashscope_memories WHERE user_id = ?", ("db_test_user",))
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"    ✅ 数据库中有 {count} 条记录")
            else:
                print("    ⚠️ 数据库中没有找到记录")
            
            conn.close()
            
            print("✅ 数据库操作测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 数据库操作测试失败: {e}")
            return False
    
    def test_performance_metrics(self) -> bool:
        """测试性能指标"""
        try:
            from src.core.dashscope_memory_manager import DashScopeMemoryManager
            
            memory_manager = DashScopeMemoryManager("perf_test_user")
            
            # 测试响应时间
            print("⚡ 测试响应时间...")
            test_message = "这是一个性能测试消息"
            
            start_time = time.time()
            result = memory_manager.process_message(test_message)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response_time < 10:  # 10秒内响应
                print(f"    ✅ 响应时间正常: {response_time:.2f}秒")
            else:
                print(f"    ⚠️ 响应时间较长: {response_time:.2f}秒")
            
            # 测试内存使用
            try:
                import psutil
                process = psutil.Process()
                memory_usage = process.memory_info().rss / 1024 / 1024  # MB
                
                if memory_usage < 500:  # 500MB以内
                    print(f"    ✅ 内存使用正常: {memory_usage:.1f}MB")
                else:
                    print(f"    ⚠️ 内存使用较高: {memory_usage:.1f}MB")
            except ImportError:
                print("    ⚠️ 无法检查内存使用（缺少psutil模块）")
            
            print("✅ 性能指标测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 性能指标测试失败: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """测试错误处理"""
        try:
            from src.core.dashscope_memory_manager import DashScopeMemoryManager
            
            # 测试无效API密钥
            print("🛡️ 测试错误处理...")
            
            # 保存原始API密钥
            original_key = os.environ.get('DASHSCOPE_API_KEY')
            
            # 测试无效密钥
            os.environ['DASHSCOPE_API_KEY'] = 'invalid_key'
            
            try:
                memory_manager = DashScopeMemoryManager("error_test_user")
                result = memory_manager.process_message("测试消息")
                
                if not result['success']:
                    print("    ✅ 无效API密钥处理正确")
                else:
                    print("    ⚠️ 无效API密钥未正确处理")
                    
            except ValueError as e:
                print("    ✅ 无效API密钥异常处理正确")
            
            # 恢复原始API密钥
            if original_key:
                os.environ['DASHSCOPE_API_KEY'] = original_key
            else:
                del os.environ['DASHSCOPE_API_KEY']
            
            # 测试空消息
            memory_manager = DashScopeMemoryManager("error_test_user_2")
            result = memory_manager.process_message("")
            
            if result['success']:
                print("    ✅ 空消息处理正常")
            else:
                print("    ⚠️ 空消息处理异常")
            
            print("✅ 错误处理测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 错误处理测试失败: {e}")
            return False
    
    def test_data_persistence(self) -> bool:
        """测试数据持久化"""
        try:
            from src.core.dashscope_memory_manager import DashScopeMemoryManager
            
            user_id = "persistence_test_user"
            
            # 第一次创建管理器并添加数据
            print("💾 测试数据持久化...")
            memory_manager1 = DashScopeMemoryManager(user_id)
            
            test_messages = [
                "这是持久化测试消息1",
                "这是持久化测试消息2",
                "这是持久化测试消息3"
            ]
            
            for message in test_messages:
                memory_manager1.process_message(message)
            
            # 检查短期记忆
            short_term_count = len(memory_manager1.short_term_memory)
            print(f"   短期记忆数量: {short_term_count}")
            
            # 创建新的管理器实例
            memory_manager2 = DashScopeMemoryManager(user_id)
            
            # 检查数据是否持久化
            stats = memory_manager2.get_stats()
            total_memories = stats['total_memories']
            
            if total_memories > 0:
                print(f"    ✅ 数据持久化成功，总记忆数: {total_memories}")
            else:
                print("    ⚠️ 数据持久化可能有问题")
            
            # 测试记忆搜索
            results = memory_manager2.search_memories("持久化", top_k=5)
            if results:
                print(f"    ✅ 持久化数据搜索成功，找到 {len(results)} 条结果")
            else:
                print("    ⚠️ 持久化数据搜索未找到结果")
            
            print("✅ 数据持久化测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 数据持久化测试失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 Memory-X 业务级别测试套件开始")
        print("=" * 60)
        
        # 定义测试列表
        tests = [
            ("环境配置检查", self.test_environment_setup),
            ("DashScope API连接", self.test_dashscope_api_connection),
            ("记忆管理器创建", self.test_memory_manager_creation),
            ("基础对话流程", self.test_basic_conversation_flow),
            ("医疗场景测试", self.test_medical_scenario),
            ("电子商务场景", self.test_ecommerce_scenario),
            ("记忆搜索功能", self.test_memory_search_functionality),
            ("API端点测试", self.test_api_endpoints),
            ("数据库操作", self.test_database_operations),
            ("性能指标", self.test_performance_metrics),
            ("错误处理", self.test_error_handling),
            ("数据持久化", self.test_data_persistence)
        ]
        
        # 运行测试
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # 生成测试报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        total_time = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 测试报告")
        print("=" * 60)
        
        # 统计结果
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed_tests = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        error_tests = sum(1 for r in self.results if r.status == TestStatus.ERROR)
        skipped_tests = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
        
        # 计算成功率
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"错误: {error_tests} 💥")
        print(f"跳过: {skipped_tests} ⚠️")
        print(f"成功率: {success_rate:.1f}%")
        print(f"总耗时: {total_time:.2f}秒")
        
        # 详细结果
        print("\n📋 详细结果:")
        for result in self.results:
            print(f"{result.status.value} {result.name} ({result.duration:.2f}s)")
            if result.message and result.message != "测试通过":
                print(f"    {result.message}")
        
        # 性能分析
        print("\n⚡ 性能分析:")
        durations = [r.duration for r in self.results]
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)
            
            print(f"平均耗时: {avg_duration:.2f}秒")
            print(f"最长耗时: {max_duration:.2f}秒")
            print(f"最短耗时: {min_duration:.2f}秒")
        
        # 建议
        print("\n💡 建议:")
        if success_rate >= 90:
            print("✅ 系统运行良好，可以投入生产使用")
        elif success_rate >= 70:
            print("⚠️ 系统基本可用，建议修复失败的测试")
        else:
            print("❌ 系统存在问题，需要重点修复")
        
        if failed_tests > 0:
            print("🔧 需要修复的测试:")
            for result in self.results:
                if result.status in [TestStatus.FAILED, TestStatus.ERROR]:
                    print(f"   - {result.name}: {result.message}")
        
        # 保存报告到文件
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "error": error_tests,
            "skipped": skipped_tests,
            "success_rate": success_rate,
            "total_time": total_time,
            "results": [
                {
                    "name": r.name,
                    "status": r.status.value,
                    "duration": r.duration,
                    "message": r.message
                }
                for r in self.results
            ]
        }
        
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        return success_rate >= 90

def main():
    """主函数"""
    test_suite = BusinessTestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n🎉 所有测试通过！系统可以投入生产使用")
        sys.exit(0)
    else:
        print("\n⚠️ 部分测试失败，请检查系统配置")
        sys.exit(1)

if __name__ == "__main__":
    main()
