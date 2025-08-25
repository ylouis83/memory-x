#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DashScope集成的API路由
提供基于DashScope的记忆管理和AI对话API
"""

from flask import Blueprint, request, jsonify
from src.core.dashscope_memory_manager import DashScopeMemoryManager
import logging

# 创建蓝图
dashscope_bp = Blueprint('dashscope', __name__, url_prefix='/api/dashscope')

# 设置日志
logger = logging.getLogger(__name__)

# 全局记忆管理器字典，按用户ID存储
memory_managers = {}

def get_memory_manager(user_id: str) -> DashScopeMemoryManager:
    """获取或创建用户的记忆管理器"""
    if user_id not in memory_managers:
        try:
            memory_managers[user_id] = DashScopeMemoryManager(user_id)
            logger.info(f"为用户 {user_id} 创建了新的记忆管理器")
        except Exception as e:
            logger.error(f"为用户 {user_id} 创建记忆管理器失败: {e}")
            raise
    
    return memory_managers[user_id]

@dashscope_bp.route('/chat', methods=['POST'])
def chat():
    """处理用户聊天消息"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要参数: message'
            }), 400
        
        message = data['message']
        user_id = data.get('user_id', 'default_user')
        
        # 获取记忆管理器
        memory_manager = get_memory_manager(user_id)
        
        # 处理消息
        result = memory_manager.process_message(message)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"聊天API错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashscope_bp.route('/search', methods=['POST'])
def search_memories():
    """搜索相关记忆"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要参数: query'
            }), 400
        
        query = data['query']
        user_id = data.get('user_id', 'default_user')
        top_k = data.get('top_k', 5)
        
        # 获取记忆管理器
        memory_manager = get_memory_manager(user_id)
        
        # 搜索记忆
        results = memory_manager.search_memories(query, top_k=top_k)
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'results': results,
                'count': len(results)
            }
        })
        
    except Exception as e:
        logger.error(f"记忆搜索API错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashscope_bp.route('/stats/<user_id>', methods=['GET'])
def get_user_stats(user_id):
    """获取用户统计信息"""
    try:
        # 获取记忆管理器
        memory_manager = get_memory_manager(user_id)
        
        # 获取统计信息
        stats = memory_manager.get_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"获取用户统计API错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashscope_bp.route('/working-memory/<user_id>', methods=['GET'])
def get_working_memory(user_id):
    """获取用户工作记忆"""
    try:
        # 获取记忆管理器
        memory_manager = get_memory_manager(user_id)
        
        # 转换set为list以便JSON序列化
        working_memory = {}
        for entity_type, entities in memory_manager.working_memory.items():
            working_memory[entity_type] = list(entities)
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': user_id,
                'working_memory': working_memory,
                'short_term_count': len(memory_manager.short_term_memory)
            }
        })
        
    except Exception as e:
        logger.error(f"获取工作记忆API错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashscope_bp.route('/clear-session/<user_id>', methods=['POST'])
def clear_session(user_id):
    """清空用户会话"""
    try:
        # 获取记忆管理器
        memory_manager = get_memory_manager(user_id)
        
        # 清空会话
        memory_manager.clear_session()
        
        return jsonify({
            'success': True,
            'message': f'用户 {user_id} 的会话已清空'
        })
        
    except Exception as e:
        logger.error(f"清空会话API错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashscope_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        # 检查API密钥是否设置
        import os
        api_key = os.getenv('DASHSCOPE_API_KEY')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'DASHSCOPE_API_KEY未设置'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'DashScope API服务正常',
            'api_key_configured': True,
            'active_users': len(memory_managers)
        })
        
    except Exception as e:
        logger.error(f"健康检查API错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashscope_bp.route('/test-connection', methods=['POST'])
def test_connection():
    """测试DashScope API连接"""
    try:
        import requests
        import os
        
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'DASHSCOPE_API_KEY未设置'
            }), 500
        
        # 测试API连接
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        headers = {
            "Authorization": f"Bearer {api_key}",
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
            return jsonify({
                'success': True,
                'message': 'DashScope API连接正常',
                'response': result['choices'][0]['message']['content']
            })
        else:
            return jsonify({
                'success': False,
                'error': f'API连接失败: {response.status_code}',
                'details': response.text
            }), 500
            
    except Exception as e:
        logger.error(f"测试连接API错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
