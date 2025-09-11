#!/usr/bin/env python3
"""
简化版Qwen3图谱更新演示
"""

import os
import sys
import os
import sqlite3
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append('/Users/louisliu/.cursor/memory-x')

from src.core.medical_graph_manager import MedicalGraphManager
from src.core.qwen_update_engine import QwenGraphUpdateEngine


def create_simple_demo():
    """创建简化演示"""
    print("🤖 Qwen3医疗图谱更新简化演示")
    print("=" * 50)
    
    # 使用简单的内存数据库
    db_path = ":memory:"
    
    try:
        # 初始化组件
        graph_manager = MedicalGraphManager(db_path)
        qwen_engine = QwenGraphUpdateEngine(graph_manager, os.getenv('DASHSCOPE_API_KEY') or "请设置DASHSCOPE_API_KEY环境变量")
        
        # 手动创建简单的测试数据
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建基本表结构
        cursor.execute('''
            CREATE TABLE diseases (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                category VARCHAR(100),
                severity VARCHAR(20),
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE symptoms (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                body_part VARCHAR(100),
                intensity VARCHAR(20),
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE disease_symptom_relations (
                id VARCHAR(50) PRIMARY KEY,
                disease_id VARCHAR(50) NOT NULL,
                symptom_id VARCHAR(50) NOT NULL,
                source VARCHAR(50) NOT NULL,
                confidence DECIMAL(3,2) DEFAULT 0.50,
                user_id VARCHAR(50),
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 添加测试数据
        two_months_ago = datetime.now() - timedelta(days=60)
        
        # 插入疾病
        cursor.execute('''
            INSERT INTO diseases (id, name, category, severity)
            VALUES (?, ?, ?, ?)
        ''', ("disease_001", "感冒", "呼吸系统疾病", "mild"))
        
        # 插入症状
        cursor.execute('''
            INSERT INTO symptoms (id, name, body_part, intensity)
            VALUES (?, ?, ?, ?)
        ''', ("symptom_001", "头晕", "头部", "mild"))
        
        # 插入关系
        cursor.execute('''
            INSERT INTO disease_symptom_relations 
            (id, disease_id, symptom_id, source, confidence, user_id, created_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ("rel_001", "disease_001", "symptom_001", "online_consult", 0.8, 
              "demo_user", two_months_ago.isoformat()))
        
        conn.commit()
        
        print(f"✅ 测试数据创建完成")
        print(f"历史记录：{two_months_ago.strftime('%Y-%m-%d')} - 感冒 → 头晕")
        
        # 进行AI分析
        print(f"\n🤖 Qwen3智能分析...")
        
        current_symptoms = ["头疼"]
        context = "患者再次咨询，现在出现头疼症状"
        
        # 使用基础规则分析
        print("📊 基础规则分析...")
        base_decision = qwen_engine.analyze_update_scenario(
            current_symptoms=current_symptoms,
            user_id="demo_user",
            context=context
        )
        
        print(f"基础分析结果：")
        print(f"  动作: {base_decision.action.value}")
        print(f"  置信度: {base_decision.confidence:.2f}")
        print(f"  原因: {base_decision.reasoning}")
        
        # 使用AI增强分析
        print(f"\n🧠 Qwen3增强分析...")
        ai_decision = qwen_engine.analyze_with_ai(
            current_symptoms=current_symptoms,
            user_id="demo_user",
            context=context
        )
        
        print(f"AI增强分析结果：")
        print(f"  推荐动作: {ai_decision.action.value}")
        print(f"  置信度: {ai_decision.confidence:.2f}")
        print(f"  分析原因: {ai_decision.reasoning[:200]}...")
        
        if ai_decision.recommendations:
            print(f"\n💡 医疗建议：")
            for i, rec in enumerate(ai_decision.recommendations[:3], 1):
                print(f"  {i}. {rec}")
        
        # 对比分析
        print(f"\n📈 分析对比：")
        print(f"  置信度提升: {ai_decision.confidence - base_decision.confidence:+.2f}")
        print(f"  动作是否改变: {'是' if ai_decision.action != base_decision.action else '否'}")
        
        conn.close()
        print(f"\n🎉 演示完成！")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    create_simple_demo()