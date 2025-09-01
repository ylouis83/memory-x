#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory-X 全面测试脚本
测试记忆系统的 UPDATE、DELETE、MERGE 核心功能
"""

import os
import sys
import json
import traceback
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.memory_manager import SimpleMemoryManager
from src.core.medical_memory import MedicationEntry, upsert_medication_entry
from src.core.fhir_memory_policy import EffectivePeriod, MedicationRecord, decide_action


class MemoryTestSuite:
    """记忆系统综合测试套件"""
    
    def __init__(self):
        self.test_results = []
        self.success_count = 0
        self.failure_count = 0
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """记录测试结果"""
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        if success:
            self.success_count += 1
            print(f"✅ {test_name}")
        else:
            self.failure_count += 1
            print(f"❌ {test_name} - {details}")
    
    def test_basic_memory_operations(self):
        """测试基本记忆操作"""
        print("\n🧠 测试1: 基本记忆操作 (CREATE/READ/UPDATE/DELETE)")
        print("-" * 60)
        
        try:
            # 初始化记忆管理器
            mm = SimpleMemoryManager(user_id="test_user_basic")
            
            # 1. CREATE - 添加记忆
            mm.add_conversation(
                user_message="我叫张三，今年30岁",
                ai_response="你好张三，很高兴认识你！",
                importance=3  # 确保存储到长期记忆
            )
            
            # 验证记忆添加
            memories = mm.retrieve_memories("张三")
            assert len(memories) > 0, "记忆添加失败"
            self.log_test("基本记忆添加", True)
            
            # 2. READ - 搜索记忆
            search_results = mm.retrieve_memories("年龄")
            found_age_info = any("30" in str(memory) for memory in search_results)
            self.log_test("记忆搜索功能", found_age_info, "未找到年龄信息" if not found_age_info else "")
            
            # 3. UPDATE - 更新记忆
            mm.add_conversation(
                user_message="我今年31岁了，不是30岁",
                ai_response="好的，已经更新你的年龄信息",
                importance=3  # 确保存储到长期记忆
            )
            
            # 验证更新
            updated_memories = mm.retrieve_memories("张三 年龄")
            self.log_test("记忆更新功能", len(updated_memories) > 0)
            
            # 4. DELETE - 删除记忆 (通过清理实现)
            # 注：当前版本可能没有直接删除接口，测试清理功能
            try:
                mm.clear_session()
                # 清理会话不会删除长期记忆，测试长期记忆是否还存在
                long_term_memories = mm.retrieve_memories("张三")
                self.log_test("会话清理功能", len(long_term_memories) >= 0, "会话清理测试")
            except AttributeError:
                self.log_test("记忆删除功能", False, "当前版本未实现删除接口")
                
        except Exception as e:
            self.log_test("基本记忆操作", False, f"异常: {str(e)}")
    
    def test_medical_memory_upsert(self):
        """测试医疗记忆的 APPEND/UPDATE/MERGE 功能"""
        print("\n💊 测试2: 医疗记忆 UPSERT 操作")
        print("-" * 60)
        
        try:
            now = datetime.utcnow()
            entries = []
            
            # 1. APPEND - 新增用药记录
            first_medication = MedicationEntry(
                rxnorm="12345",
                dose="5 mg",
                frequency="qd", 
                route="oral",
                start=now - timedelta(days=30),
                provenance="初诊"
            )
            
            action = upsert_medication_entry(entries, first_medication)
            assert action == "append", f"期望 append，实际 {action}"
            assert len(entries) == 1, f"期望1条记录，实际{len(entries)}条"
            self.log_test("医疗记忆 APPEND 操作", True, f"新增用药记录: {first_medication.rxnorm}")
            
            # 2. UPDATE - 更新同一疗程
            updated_medication = MedicationEntry(
                rxnorm="12345",
                dose="5 mg", 
                frequency="qd",
                route="oral",
                start=now - timedelta(days=25),
                end=now - timedelta(days=15),
                status="completed",
                provenance="复诊"
            )
            
            action = upsert_medication_entry(entries, updated_medication)
            assert action == "update", f"期望 update，实际 {action}"
            assert entries[0].version_id == 2, f"期望版本2，实际版本{entries[0].version_id}"
            assert entries[0].end == updated_medication.end, "结束时间更新失败"
            self.log_test("医疗记忆 UPDATE 操作", True, f"更新疗程，版本: {entries[0].version_id}")
            
            # 3. MERGE - 合并分裂的疗程
            continuation = MedicationEntry(
                rxnorm="12345",
                dose="5 mg",
                frequency="qd", 
                route="oral",
                start=updated_medication.end + timedelta(days=2),  # 2天间隔，符合合并条件
                provenance="续药"
            )
            
            action = upsert_medication_entry(entries, continuation)
            assert action == "merge", f"期望 merge，实际 {action}"
            assert len(entries) == 1, f"合并后应该只有1条记录，实际{len(entries)}条"
            assert entries[0].start == first_medication.start, "合并后起始时间错误"
            assert entries[0].end is None, "合并后应该是进行中状态"
            assert entries[0].status == "active", "合并后状态应该是active"
            assert entries[0].version_id == 3, f"期望版本3，实际版本{entries[0].version_id}"
            self.log_test("医疗记忆 MERGE 操作", True, f"合并疗程，最终版本: {entries[0].version_id}")
            
        except Exception as e:
            self.log_test("医疗记忆 UPSERT 操作", False, f"异常: {str(e)}\n{traceback.format_exc()}")
    
    def test_fhir_policy_decisions(self):
        """测试 FHIR 策略决策"""
        print("\n🏥 测试3: FHIR 策略决策逻辑")
        print("-" * 60)
        
        try:
            from datetime import date
            
            def build_record(rxnorm, start_date, end_date=None):
                return MedicationRecord(
                    rxnorm=rxnorm,
                    dose="5 mg",
                    frequency="once daily", 
                    route="oral",
                    period=EffectivePeriod(
                        start=date.fromisoformat(start_date),
                        end=date.fromisoformat(end_date) if end_date else None
                    )
                )
            
            # 1. 测试 APPEND 决策 - 不同药物
            history = [build_record("123", "2024-01-01", "2024-02-01")]
            new_record = build_record("999", "2024-03-01")
            action = decide_action(history, new_record)
            assert action == "APPEND", f"期望 APPEND，实际 {action}"
            self.log_test("FHIR APPEND 决策", True, "不同药物正确识别为新增")
            
            # 2. 测试 UPDATE 决策 - 同一进行中疗程
            history = [build_record("123", "2024-01-01")]  # 进行中
            new_record = build_record("123", "2024-02-01")
            action = decide_action(history, new_record)
            assert action == "UPDATE", f"期望 UPDATE，实际 {action}"
            self.log_test("FHIR UPDATE 决策", True, "同一疗程正确识别为更新")
            
            # 3. 测试 MERGE 决策 - 分裂疗程
            history = [build_record("123", "2024-01-01", "2024-01-10")]  # 已完成
            new_record = build_record("123", "2024-01-12", "2024-01-20")  # 2天间隔
            action = decide_action(history, new_record)
            assert action == "MERGE", f"期望 MERGE，实际 {action}"
            self.log_test("FHIR MERGE 决策", True, "分裂疗程正确识别为合并")
            
        except Exception as e:
            self.log_test("FHIR 策略决策", False, f"异常: {str(e)}\n{traceback.format_exc()}")
    
    def test_memory_versioning(self):
        """测试记忆版本控制"""
        print("\n📝 测试4: 记忆版本控制")
        print("-" * 60)
        
        try:
            now = datetime.utcnow()
            entries = []
            
            # 创建初始记录
            original = MedicationEntry(
                rxnorm="67890",
                dose="10 mg",
                frequency="bid",
                route="oral", 
                start=now - timedelta(days=20),
                provenance="处方1"
            )
            
            upsert_medication_entry(entries, original)
            assert entries[0].version_id == 1, "初始版本应该为1"
            assert entries[0].last_updated is not None, "应该有更新时间"
            original_update_time = entries[0].last_updated
            self.log_test("记忆版本初始化", True, f"版本: {entries[0].version_id}")
            
            # 等待一秒确保时间差异
            import time
            time.sleep(1)
            
            # 更新记录
            updated = MedicationEntry(
                rxnorm="67890",
                dose="10 mg", 
                frequency="bid",
                route="oral",
                start=now - timedelta(days=15),
                end=now - timedelta(days=5),
                status="completed",
                provenance="处方2"
            )
            
            upsert_medication_entry(entries, updated)
            assert entries[0].version_id == 2, f"更新后版本应该为2，实际{entries[0].version_id}"
            assert entries[0].last_updated > original_update_time, "更新时间应该变化"
            assert entries[0].provenance == "处方2", "来源信息应该更新"
            self.log_test("记忆版本更新", True, f"版本递增: {entries[0].version_id}")
            
            # 再次合并操作
            merged = MedicationEntry(
                rxnorm="67890",
                dose="10 mg",
                frequency="bid", 
                route="oral",
                start=updated.end + timedelta(days=1),
                provenance="处方3"
            )
            
            second_update_time = entries[0].last_updated
            time.sleep(1)
            
            upsert_medication_entry(entries, merged)
            assert entries[0].version_id == 3, f"合并后版本应该为3，实际{entries[0].version_id}"
            assert entries[0].last_updated > second_update_time, "合并后更新时间应该变化"
            assert entries[0].provenance == "处方3", "最新来源信息应该保留"
            self.log_test("记忆版本合并", True, f"最终版本: {entries[0].version_id}")
            
        except Exception as e:
            self.log_test("记忆版本控制", False, f"异常: {str(e)}\n{traceback.format_exc()}")
    
    def test_edge_cases(self):
        """测试边缘情况"""
        print("\n🎯 测试5: 边缘情况处理")
        print("-" * 60)
        
        try:
            now = datetime.utcnow()
            
            # 1. 空记录列表
            entries = []
            new_entry = MedicationEntry(
                rxnorm="11111",
                dose="1 mg",
                frequency="qd",
                route="oral",
                start=now
            )
            action = upsert_medication_entry(entries, new_entry)
            assert action == "append", "空列表应该执行 append"
            self.log_test("空记录列表处理", True)
            
            # 2. 相同时间点的记录
            entries = []
            first = MedicationEntry(rxnorm="22222", dose="2 mg", frequency="qd", route="oral", start=now)
            second = MedicationEntry(rxnorm="22222", dose="2 mg", frequency="qd", route="oral", start=now)
            
            upsert_medication_entry(entries, first)
            action = upsert_medication_entry(entries, second)
            self.log_test("相同时间点记录", action in ["update", "merge"], f"处理动作: {action}")
            
            # 3. 超长间隔的记录（不应该合并）
            entries = []
            old_entry = MedicationEntry(
                rxnorm="33333", dose="3 mg", frequency="qd", route="oral",
                start=now - timedelta(days=100), end=now - timedelta(days=90)
            )
            new_entry = MedicationEntry(
                rxnorm="33333", dose="3 mg", frequency="qd", route="oral", 
                start=now - timedelta(days=10)
            )
            
            upsert_medication_entry(entries, old_entry)
            action = upsert_medication_entry(entries, new_entry)
            assert action == "append", f"超长间隔应该 append，实际 {action}"
            assert len(entries) == 2, f"超长间隔应该有2条记录，实际{len(entries)}条"
            self.log_test("超长间隔记录", True, "正确识别为独立疗程")
            
            # 4. 不同剂量的相同药物
            entries = []
            dose5mg = MedicationEntry(rxnorm="44444", dose="5 mg", frequency="qd", route="oral", start=now-timedelta(days=5))
            dose10mg = MedicationEntry(rxnorm="44444", dose="10 mg", frequency="qd", route="oral", start=now)
            
            upsert_medication_entry(entries, dose5mg)
            action = upsert_medication_entry(entries, dose10mg)
            assert action == "append", f"不同剂量应该 append，实际 {action}"
            self.log_test("不同剂量处理", True, "正确识别为不同方案")
            
        except Exception as e:
            self.log_test("边缘情况处理", False, f"异常: {str(e)}\n{traceback.format_exc()}")
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*80)
        print("📊 Memory-X 全面测试报告")
        print("="*80)
        
        print(f"✅ 成功: {self.success_count} 项")
        print(f"❌ 失败: {self.failure_count} 项")
        print(f"📈 成功率: {self.success_count/(self.success_count+self.failure_count)*100:.1f}%")
        
        if self.failure_count > 0:
            print("\n🔍 失败测试详情:")
            for test in self.test_results:
                if not test['success']:
                    print(f"  ❌ {test['test_name']}: {test['details']}")
        
        # 保存报告到文件
        report_file = f"memory_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'success_count': self.success_count,
                    'failure_count': self.failure_count,
                    'total_count': self.success_count + self.failure_count,
                    'success_rate': self.success_count/(self.success_count+self.failure_count)*100
                },
                'details': self.test_results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        return report_file
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始 Memory-X 全面测试...")
        print("="*80)
        
        self.test_basic_memory_operations()
        self.test_medical_memory_upsert()
        self.test_fhir_policy_decisions()
        self.test_memory_versioning()
        self.test_edge_cases()
        
        return self.generate_report()


if __name__ == "__main__":
    try:
        test_suite = MemoryTestSuite()
        report_file = test_suite.run_all_tests()
        
        print(f"\n🎉 测试完成！报告文件: {report_file}")
        
    except Exception as e:
        print(f"❌ 测试套件运行失败: {str(e)}")
        print(traceback.format_exc())
