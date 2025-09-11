#!/usr/bin/env python3
"""
医疗知识图谱API路由
Medical Knowledge Graph API Routes

提供图谱构建、查询、分析的RESTful API接口
"""

import os
from flask import Blueprint, request, jsonify
from typing import Dict, List
import json

from ..core.medical_graph_manager import MedicalGraphManager
from ..core.entity_extractor import MedicalEntityExtractor
from ..core.graph_update_engine import GraphUpdateEngine
from ..core.qwen_update_engine import QwenGraphUpdateEngine

# 创建蓝图
graph_bp = Blueprint('graph', __name__, url_prefix='/api/graph')

# 初始化图谱管理器和实体抽取器
graph_manager = MedicalGraphManager()
entity_extractor = MedicalEntityExtractor(graph_manager)
update_engine = GraphUpdateEngine(graph_manager)

# 初始化Qwen3增强更新引擎（如果有API密钥）
qwen_engine = None
try:
    # 这里应该从环境变量或配置文件读取API密钥
    qwen_api_key = os.getenv('DASHSCOPE_API_KEY')
    if not qwen_api_key:
        return jsonify({"error": "未设置DASHSCOPE_API_KEY环境变量"}), 500
    qwen_engine = QwenGraphUpdateEngine(graph_manager, qwen_api_key)
except Exception as e:
    print(f"⚠️ Qwen3引擎初始化失败: {e}")

@graph_bp.route('/health', methods=['GET'])
def health_check():
    """图谱服务健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': 'Medical Knowledge Graph',
        'version': '1.0.0'
    })

@graph_bp.route('/extract', methods=['POST'])
def extract_entities():
    """从文本中抽取医疗实体和关系"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': '缺少必需的text参数'}), 400
        
        text = data.get('text', '')
        user_id = data.get('user_id', 'demo_user')
        session_id = data.get('session_id')
        
        if not text.strip():
            return jsonify({'error': '文本内容不能为空'}), 400
        
        # 处理用户消息并构建图谱
        result = entity_extractor.process_user_message(text, user_id, session_id)
        
        return jsonify({
            'success': True,
            'result': result,
            'message': '实体抽取和图谱构建完成'
        })
        
    except Exception as e:
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

@graph_bp.route('/entities/<entity_type>', methods=['GET'])
def get_entities(entity_type):
    """获取指定类型的实体列表"""
    try:
        # 参数验证
        if entity_type not in ['disease', 'symptom', 'medicine']:
            return jsonify({'error': '无效的实体类型，支持: disease, symptom, medicine'}), 400
        
        name_filter = request.args.get('name', '')
        limit = int(request.args.get('limit', 50))
        
        # 搜索实体
        entities = graph_manager.search_entities_by_name(entity_type, name_filter)
        
        # 应用限制
        if limit > 0:
            entities = entities[:limit]
        
        return jsonify({
            'success': True,
            'entity_type': entity_type,
            'count': len(entities),
            'entities': entities
        })
        
    except Exception as e:
        return jsonify({'error': f'查询失败: {str(e)}'}), 500

@graph_bp.route('/relations/disease-symptom', methods=['GET'])
def get_disease_symptom_relations():
    """获取疾病-症状关系"""
    try:
        user_id = request.args.get('user_id')
        source = request.args.get('source')
        limit = int(request.args.get('limit', 100))
        
        relations = graph_manager.get_disease_symptom_relations(user_id, source)
        
        if limit > 0:
            relations = relations[:limit]
        
        return jsonify({
            'success': True,
            'relation_type': 'disease-symptom',
            'count': len(relations),
            'relations': relations,
            'filters': {
                'user_id': user_id,
                'source': source
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'查询失败: {str(e)}'}), 500

@graph_bp.route('/relations/disease-medicine', methods=['GET'])
def get_disease_medicine_relations():
    """获取疾病-药品关系"""
    try:
        user_id = request.args.get('user_id')
        source = request.args.get('source')
        limit = int(request.args.get('limit', 100))
        
        relations = graph_manager.get_disease_medicine_relations(user_id, source)
        
        if limit > 0:
            relations = relations[:limit]
        
        return jsonify({
            'success': True,
            'relation_type': 'disease-medicine',
            'count': len(relations),
            'relations': relations,
            'filters': {
                'user_id': user_id,
                'source': source
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'查询失败: {str(e)}'}), 500

@graph_bp.route('/user/<user_id>/summary', methods=['GET'])
def get_user_graph_summary(user_id):
    """获取用户个人图谱摘要"""
    try:
        summary = graph_manager.get_user_graph_summary(user_id)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({'error': f'查询失败: {str(e)}'}), 500

@graph_bp.route('/user/<user_id>/graph', methods=['GET'])
def get_user_personal_graph(user_id):
    """获取用户个人完整图谱数据"""
    try:
        # 获取用户的疾病-症状关系
        ds_relations = graph_manager.get_disease_symptom_relations(user_id=user_id)
        
        # 获取用户的疾病-药品关系
        dm_relations = graph_manager.get_disease_medicine_relations(user_id=user_id)
        
        # 提取涉及的实体
        involved_diseases = set()
        involved_symptoms = set()
        involved_medicines = set()
        
        for rel in ds_relations:
            involved_diseases.add((rel['disease_id'], rel['disease_name']))
            involved_symptoms.add((rel['symptom_id'], rel['symptom_name']))
        
        for rel in dm_relations:
            involved_diseases.add((rel['disease_id'], rel['disease_name']))
            involved_medicines.add((rel['medicine_id'], rel['medicine_name']))
        
        # 构建图谱数据结构
        graph_data = {
            'nodes': [],
            'edges': []
        }
        
        # 添加疾病节点
        for disease_id, disease_name in involved_diseases:
            graph_data['nodes'].append({
                'id': disease_id,
                'name': disease_name,
                'type': 'disease',
                'category': 'disease'
            })
        
        # 添加症状节点
        for symptom_id, symptom_name in involved_symptoms:
            graph_data['nodes'].append({
                'id': symptom_id,
                'name': symptom_name,
                'type': 'symptom',
                'category': 'symptom'
            })
        
        # 添加药品节点
        for medicine_id, medicine_name in involved_medicines:
            graph_data['nodes'].append({
                'id': medicine_id,
                'name': medicine_name,
                'type': 'medicine',
                'category': 'medicine'
            })
        
        # 添加疾病-症状边
        for rel in ds_relations:
            graph_data['edges'].append({
                'id': rel['id'],
                'source': rel['disease_id'],
                'target': rel['symptom_id'], 
                'type': 'consult',
                'confidence': rel['confidence'],
                'source_type': rel['source'],
                'frequency': rel['frequency']
            })
        
        # 添加疾病-药品边
        for rel in dm_relations:
            graph_data['edges'].append({
                'id': rel['id'],
                'source': rel['disease_id'],
                'target': rel['medicine_id'],
                'type': 'treatment',
                'effectiveness': rel.get('effectiveness'),
                'source_type': rel['source']
            })
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'graph': graph_data,
            'statistics': {
                'total_nodes': len(graph_data['nodes']),
                'total_edges': len(graph_data['edges']),
                'disease_count': len(involved_diseases),
                'symptom_count': len(involved_symptoms),
                'medicine_count': len(involved_medicines)
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'查询失败: {str(e)}'}), 500

@graph_bp.route('/search', methods=['POST'])
def search_graph():
    """图谱搜索接口"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '缺少搜索参数'}), 400
        
        query = data.get('query', '')
        entity_types = data.get('entity_types', ['disease', 'symptom', 'medicine'])
        user_id = data.get('user_id')
        limit = data.get('limit', 20)
        
        if not query.strip():
            return jsonify({'error': '搜索关键词不能为空'}), 400
        
        results = {
            'query': query,
            'results': {}
        }
        
        # 搜索各类实体
        for entity_type in entity_types:
            if entity_type in ['disease', 'symptom', 'medicine']:
                entities = graph_manager.search_entities_by_name(entity_type, query)
                results['results'][entity_type] = entities[:limit] if limit > 0 else entities
        
        # 如果指定了用户ID，还要搜索相关关系
        if user_id:
            ds_relations = graph_manager.get_disease_symptom_relations(user_id=user_id)
            dm_relations = graph_manager.get_disease_medicine_relations(user_id=user_id)
            
            # 过滤包含查询关键词的关系
            relevant_ds = [rel for rel in ds_relations 
                          if query.lower() in rel['disease_name'].lower() or 
                             query.lower() in rel['symptom_name'].lower()]
            relevant_dm = [rel for rel in dm_relations 
                          if query.lower() in rel['disease_name'].lower() or 
                             query.lower() in rel['medicine_name'].lower()]
            
            results['results']['disease_symptom_relations'] = relevant_ds[:limit] if limit > 0 else relevant_ds
            results['results']['disease_medicine_relations'] = relevant_dm[:limit] if limit > 0 else relevant_dm
        
        return jsonify({
            'success': True,
            'search_results': results
        })
        
    except Exception as e:
        return jsonify({'error': f'搜索失败: {str(e)}'}), 500

@graph_bp.route('/analyze/allergies/<user_id>', methods=['GET'])
def analyze_user_allergies(user_id):
    """分析用户过敏史 - 专门针对您的青霉素过敏"""
    try:
        # 搜索用户的药品相关关系
        dm_relations = graph_manager.get_disease_medicine_relations(user_id=user_id)
        
        # 分析过敏风险
        allergy_analysis = {
            'user_id': user_id,
            'known_allergies': [],
            'high_risk_medicines': [],
            'safe_alternatives': [],
            'recommendations': []
        }
        
        # 检查已知过敏
        for rel in dm_relations:
            if rel.get('effectiveness') == 'contraindicated' or '过敏' in (rel.get('context', '') or ''):
                allergy_analysis['known_allergies'].append({
                    'medicine': rel['medicine_name'],
                    'source': rel['source'],
                    'severity': 'high',
                    'context': rel.get('context')
                })
        
        # 基于您的青霉素过敏史，添加高风险药物
        penicillin_allergic = any('青霉素' in allergy['medicine'] for allergy in allergy_analysis['known_allergies'])
        
        if penicillin_allergic:
            allergy_analysis['high_risk_medicines'] = [
                {'medicine': '阿莫西林', 'risk_level': 'high', 'reason': '青霉素类抗生素交叉过敏'},
                {'medicine': '氨苄西林', 'risk_level': 'high', 'reason': '青霉素类抗生素交叉过敏'},
                {'medicine': '头孢菌素', 'risk_level': 'medium', 'reason': '可能存在交叉过敏反应'}
            ]
            
            allergy_analysis['safe_alternatives'] = [
                {'medicine': '红霉素', 'drug_class': '大环内酯类抗生素'},
                {'medicine': '阿奇霉素', 'drug_class': '大环内酯类抗生素'},
                {'medicine': '左氧氟沙星', 'drug_class': '喹诺酮类抗生素'}
            ]
            
            allergy_analysis['recommendations'] = [
                '在就医时主动告知青霉素过敏史',
                '避免使用青霉素类抗生素',
                '使用头孢类抗生素前需要过敏测试',
                '随身携带过敏史卡片或医疗手环',
                '紧急情况下使用肾上腺素自动注射器'
            ]
        
        return jsonify({
            'success': True,
            'allergy_analysis': allergy_analysis
        })
        
    except Exception as e:
        return jsonify({'error': f'分析失败: {str(e)}'}), 500

@graph_bp.route('/analyze/diabetes-risk/<user_id>', methods=['GET'])
def analyze_diabetes_risk(user_id):
    """分析糖尿病风险 - 专门针对您的家族糖尿病史"""
    try:
        # 获取用户的疾病-症状关系
        ds_relations = graph_manager.get_disease_symptom_relations(user_id=user_id)
        dm_relations = graph_manager.get_disease_medicine_relations(user_id=user_id)
        
        diabetes_analysis = {
            'user_id': user_id,
            'family_history': False,
            'current_symptoms': [],
            'risk_factors': [],
            'preventive_measures': [],
            'monitoring_recommendations': []
        }
        
        # 检查是否有糖尿病相关记录
        diabetes_related = [rel for rel in ds_relations if '糖尿病' in rel['disease_name']]
        diabetes_medicines = [rel for rel in dm_relations if rel['medicine_name'] in ['二甲双胍', '胰岛素', '格列齐特']]
        
        if diabetes_related or '遗传病史' in str(ds_relations):
            diabetes_analysis['family_history'] = True
        
        # 分析当前症状
        diabetes_symptoms = ['多饮', '多尿', '多食', '体重下降', '视力模糊', '乏力']
        for rel in ds_relations:
            if rel['symptom_name'] in diabetes_symptoms:
                diabetes_analysis['current_symptoms'].append({
                    'symptom': rel['symptom_name'],
                    'confidence': rel['confidence'],
                    'source': rel['source']
                })
        
        # 风险因素评估
        if diabetes_analysis['family_history']:
            diabetes_analysis['risk_factors'].append('家族糖尿病遗传史')
        
        if len(diabetes_analysis['current_symptoms']) > 0:
            diabetes_analysis['risk_factors'].append('出现糖尿病相关症状')
        
        # 年龄因素（成年人风险评估）
        diabetes_analysis['risk_factors'].append('成年人，属于需要关注的年龄段')
        
        # 预防措施建议
        diabetes_analysis['preventive_measures'] = [
            '控制体重，维持健康BMI',
            '规律运动，每周至少150分钟中等强度运动',
            '健康饮食，限制高糖高脂食物',
            '定期监测血糖水平',
            '控制血压和血脂',
            '戒烟限酒'
        ]
        
        # 监测建议
        diabetes_analysis['monitoring_recommendations'] = [
            '每年进行糖尿病筛查（空腹血糖、糖化血红蛋白）',
            '关注典型症状：多饮、多尿、多食、体重下降',
            '定期测量血压和血脂',
            '年度眼底检查',
            '足部护理和检查'
        ]
        
        return jsonify({
            'success': True,
            'diabetes_analysis': diabetes_analysis
        })
        
    except Exception as e:
        return jsonify({'error': f'分析失败: {str(e)}'}), 500

@graph_bp.route('/smart-update', methods=['POST'])
def smart_update_graph():
    """智能图谱更新分析"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '缺少请求数据'}), 400
        
        user_id = data.get('user_id')
        current_symptoms = data.get('current_symptoms', [])
        context = data.get('context', '')
        
        if not user_id:
            return jsonify({'error': '缺少user_id参数'}), 400
        
        if not current_symptoms:
            return jsonify({'error': '缺少current_symptoms参数'}), 400
        
        # 进行智能更新分析
        decision = update_engine.analyze_update_scenario(
            current_symptoms=current_symptoms,
            user_id=user_id,
            context=context
        )
        
        return jsonify({
            'success': True,
            'update_decision': {
                'action': decision.action.value,
                'confidence': decision.confidence,
                'reasoning': decision.reasoning,
                'recommendations': decision.recommendations,
                'risk_factors': decision.risk_factors
            },
            'input': {
                'user_id': user_id,
                'current_symptoms': current_symptoms,
                'context': context
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'分析失败: {str(e)}'}), 500

@graph_bp.route('/smart-update-ai', methods=['POST'])
def smart_update_graph_ai():
    """AI增强的智能图谱更新分析（使用Qwen3模型）"""
    try:
        if not qwen_engine:
            return jsonify({
                'error': 'Qwen3引擎未初始化，使用基础规则分析',
                'fallback_available': True
            }), 503
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '缺少请求数据'}), 400
        
        user_id = data.get('user_id')
        current_symptoms = data.get('current_symptoms', [])
        context = data.get('context', '')
        
        if not user_id:
            return jsonify({'error': '缺少user_id参数'}), 400
        
        if not current_symptoms:
            return jsonify({'error': '缺少current_symptoms参数'}), 400
        
        # 使用Qwen3进行AI增强分析
        ai_decision = qwen_engine.analyze_with_ai(
            current_symptoms=current_symptoms,
            user_id=user_id,
            context=context
        )
        
        # 同时进行基础规则分析以作对比
        base_decision = update_engine.analyze_update_scenario(
            current_symptoms=current_symptoms,
            user_id=user_id,
            context=context
        )
        
        return jsonify({
            'success': True,
            'ai_enhanced_decision': {
                'action': ai_decision.action.value,
                'confidence': ai_decision.confidence,
                'reasoning': ai_decision.reasoning,
                'recommendations': ai_decision.recommendations,
                'risk_factors': ai_decision.risk_factors
            },
            'base_decision': {
                'action': base_decision.action.value,
                'confidence': base_decision.confidence,
                'reasoning': base_decision.reasoning,
                'recommendations': base_decision.recommendations,
                'risk_factors': base_decision.risk_factors
            },
            'comparison': {
                'confidence_improvement': ai_decision.confidence - base_decision.confidence,
                'action_changed': ai_decision.action != base_decision.action,
                'enhancement_type': 'qwen3_ai_model'
            },
            'input': {
                'user_id': user_id,
                'current_symptoms': current_symptoms,
                'context': context
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'AI分析失败: {str(e)}'}), 500

@graph_bp.route('/generate-report', methods=['POST'])
def generate_medical_report():
    """生成AI驱动的医疗分析报告"""
    try:
        if not qwen_engine:
            return jsonify({
                'error': 'Qwen3引擎未初始化，无法生成AI报告'
            }), 503
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '缺少请求数据'}), 400
        
        user_id = data.get('user_id')
        analysis_results = data.get('analysis_results', [])
        
        if not user_id:
            return jsonify({'error': '缺少user_id参数'}), 400
        
        # 如果没有提供分析结果，使用用户最近的医疗数据
        if not analysis_results:
            # 获取用户最近的症状咨询
            recent_relations = graph_manager.get_disease_symptom_relations(user_id=user_id)
            if recent_relations:
                # 模拟分析结果
                for rel in recent_relations[-3:]:  # 最近3条记录
                    mock_decision = update_engine.analyze_update_scenario(
                        current_symptoms=[rel['symptom_name']],
                        user_id=user_id,
                        context=f"历史记录分析：{rel['disease_name']}相关症状"
                    )
                    analysis_results.append(mock_decision)
        
        if not analysis_results:
            return jsonify({'error': '无可用的分析数据生成报告'}), 400
        
        # 生成AI医疗报告
        report = qwen_engine.generate_medical_report(user_id, analysis_results)
        
        return jsonify({
            'success': True,
            'report': report,
            'user_id': user_id,
            'analysis_count': len(analysis_results),
            'generated_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'报告生成失败: {str(e)}'}), 500

@graph_bp.route('/batch-analyze', methods=['POST'])
def batch_analyze_cases():
    """批量分析多个医疗案例"""
    try:
        if not qwen_engine:
            return jsonify({
                'error': 'Qwen3引擎未初始化，无法进行批量AI分析'
            }), 503
        
        data = request.get_json()
        
        if not data or 'cases' not in data:
            return jsonify({'error': '缺少cases参数'}), 400
        
        cases = data.get('cases', [])
        
        if not cases:
            return jsonify({'error': 'cases不能为空'}), 400
        
        if len(cases) > 10:  # 限制批量处理数量
            return jsonify({'error': '批量处理最多支持10个案例'}), 400
        
        # 进行批量分析
        results = qwen_engine.batch_analyze_cases(cases)
        
        # 统计结果
        success_count = sum(1 for r in results if r['status'] == 'success')
        
        return jsonify({
            'success': True,
            'batch_results': results,
            'statistics': {
                'total_cases': len(cases),
                'success_count': success_count,
                'failure_count': len(cases) - success_count,
                'success_rate': success_count / len(cases) if cases else 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'批量分析失败: {str(e)}'}), 500

@graph_bp.route('/update-scenarios/demo', methods=['GET'])
def demo_update_scenarios():
    """演示不同更新场景"""
    try:
        # 模拟不同的更新场景
        scenarios = [
            {
                'name': '急性疾病超时更新',
                'description': '两个月前感冒（头晕），现在头疼',
                'user_id': 'demo_acute_disease',
                'historical_disease': '感冒',
                'historical_symptom': '头晕',
                'historical_time': '60天前',
                'current_symptoms': ['头疼'],
                'expected_action': 'create_new',
                'reasoning': '感冒为急性疾病，时间间隔超出典型病程'
            },
            {
                'name': '慢性疾病症状演变',
                'description': '三个月前糖尿病（多尿），现在视力模糊',
                'user_id': 'demo_chronic_disease',
                'historical_disease': '糖尿病',
                'historical_symptom': '多尿',
                'historical_time': '90天前',
                'current_symptoms': ['视力模糊'],
                'expected_action': 'update_existing',
                'reasoning': '糖尿病为慢性疾病，新症状可能是病情进展'
            },
            {
                'name': '发作性疾病复发',
                'description': '一个月前偏头痛（头疼），现在再次头疼',
                'user_id': 'demo_episodic_disease',
                'historical_disease': '偏头痛',
                'historical_symptom': '头疼',
                'historical_time': '30天前',
                'current_symptoms': ['头疼'],
                'expected_action': 'create_new',
                'reasoning': '偏头痛为发作性疾病，此次可能是新的发作'
            }
        ]
        
        # 添加API使用说明
        api_usage = {
            'basic_analysis': 'POST /api/graph/smart-update',
            'ai_enhanced_analysis': 'POST /api/graph/smart-update-ai',
            'generate_report': 'POST /api/graph/generate-report',
            'batch_analysis': 'POST /api/graph/batch-analyze',
            'qwen3_available': qwen_engine is not None
        }
        
        return jsonify({
            'success': True,
            'scenarios': scenarios,
            'api_usage': api_usage
        })
        
    except Exception as e:
        return jsonify({'error': f'获取演示失败: {str(e)}'}), 500