#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Memory-X API 应用主文件
提供RESTful API接口服务
"""

import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from loguru import logger

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from configs.settings import get_config
from src.core.memory_manager import SimpleMemoryManager, SimpleMemoryIntegratedAI

# 导入DashScope路由
try:
    from src.api.dashscope_routes import dashscope_bp
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False


def create_app(config_name: str = None):
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 加载配置
    config = get_config(config_name)
    app.config.from_object(config)
    
    # 配置CORS
    CORS(app, origins=config.API['cors_origins'])
    
    # 配置日志
    logger.add(
        config.LOGGING['file'],
        level=config.LOGGING['level'],
        rotation=config.LOGGING['max_bytes'],
        retention=config.LOGGING['backup_count'],
        format=config.LOGGING['format']
    )
    
    # 初始化记忆管理器
    memory_ai = SimpleMemoryIntegratedAI()
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查接口"""
        return jsonify({
            'status': 'healthy',
            'service': 'Memory-X',
            'version': config.VERSION
        })
    
    @app.route('/api/memory', methods=['POST'])
    def add_memory():
        """添加记忆"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            user_id = data.get('user_id', 'default')
            message = data.get('message', '')
            response = data.get('response', '')
            entities = data.get('entities', {})
            intent = data.get('intent', '')
            importance = data.get('importance', 2)
            
            if not message:
                return jsonify({'error': 'Message is required'}), 400
            
            # 处理消息
            result = memory_ai.process_message(message, user_id)
            
            return jsonify({
                'success': True,
                'result': result,
                'memory_id': f"memory_{user_id}_{hash(message)}"
            })
            
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/memory/<user_id>', methods=['GET'])
    def get_memory(user_id):
        """查询记忆"""
        try:
            query = request.args.get('query', '')
            limit = int(request.args.get('limit', 10))
            
            memory_manager = memory_ai.get_memory_manager(user_id)
            
            if query:
                # 搜索相关记忆（长程检索）
                memories = memory_manager.retrieve_memories(query, top_k=limit)
            else:
                # 获取最近记忆
                memories = list(memory_manager.short_term_memory)[-limit:]
            
            return jsonify({
                'success': True,
                'user_id': user_id,
                'memories': memories,
                'count': len(memories)
            })
            
        except Exception as e:
            logger.error(f"Error getting memory: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/memory/<user_id>/stats', methods=['GET'])
    def get_memory_stats(user_id):
        """获取记忆统计"""
        try:
            stats = memory_ai.get_stats(user_id)
            
            return jsonify({
                'success': True,
                'user_id': user_id,
                'stats': stats
            })
            
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/memory/<user_id>/clear', methods=['POST'])
    def clear_memory(user_id):
        """清空用户记忆"""
        try:
            memory_ai.clear_user_session(user_id)
            
            return jsonify({
                'success': True,
                'message': f'Memory cleared for user {user_id}'
            })
            
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/memory/chat', methods=['POST'])
    def memory_chat():
        """记忆聊天接口"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            user_id = data.get('user_id', 'default')
            message = data.get('message', '')
            
            if not message:
                return jsonify({'error': 'Message is required'}), 400
            
            # 处理消息并获取记忆信息
            result = memory_ai.process_message(message, user_id)
            
            # 构建响应
            response_data = {
                'success': result['success'],
                'response': result['response'],
                'user_id': user_id,
                'memory_operations': []
            }
            
            if result['success']:
                # 添加记忆操作信息
                memory_manager = memory_ai.get_memory_manager(user_id)
                stats = memory_manager.get_memory_stats()
                
                response_data['memory_operations'] = [
                    {
                        'type': 'intent_detection',
                        'operation': 'detected',
                        'details': f"Intent: {result['intent']['detected']} (confidence: {result['intent']['confidence']}%)"
                    },
                    {
                        'type': 'memory_storage',
                        'operation': 'stored',
                        'details': f"Importance: {result['memory_info']['importance']}, Used long-term: {result['memory_info']['used_long_term']}"
                    },
                    {
                        'type': 'context_analysis',
                        'operation': 'analyzed',
                        'details': f"Context continuity: {result['memory_info']['context_continuity']}"
                    }
                ]
                
                response_data['memory_stats'] = stats
            
            return jsonify(response_data)
            
        except Exception as e:
            logger.error(f"Error in memory chat: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/memory/query', methods=['POST'])
    def advanced_query():
        """高级记忆查询"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            user_id = data.get('user_id', 'default')
            query_type = data.get('type', 'basic')  # basic, temporal, entity
            query_params = data.get('params', {})
            
            memory_manager = memory_ai.get_memory_manager(user_id)
            
            if query_type == 'temporal':
                # 时间查询
                start_time = query_params.get('start_time')
                end_time = query_params.get('end_time')
                # 这里可以添加时间范围查询逻辑
                result = {'type': 'temporal', 'data': []}
            elif query_type == 'entity':
                # 实体查询
                entity_type = query_params.get('entity_type')
                entity_value = query_params.get('entity_value')
                # 这里可以添加实体查询逻辑
                result = {'type': 'entity', 'data': []}
            else:
                # 基础查询
                query_text = query_params.get('query', '')
                result = {'type': 'basic', 'data': memory_manager.retrieve_memories(query_text, top_k=10)}
            
            return jsonify({
                'success': True,
                'query_type': query_type,
                'result': result
            })
            
        except Exception as e:
            logger.error(f"Error in advanced query: {e}")
            return jsonify({'error': str(e)}), 500
    
    # 注册DashScope路由
    if DASHSCOPE_AVAILABLE:
        app.register_blueprint(dashscope_bp)
        logger.info("DashScope API路由已注册")
    else:
        logger.warning("DashScope API路由未注册，请检查依赖")

    @app.route('/demo/mem0', methods=['GET'])
    def demo_mem0():
        """演示用前端页面（Mem0端到端）。"""
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'examples'))
            return send_from_directory(base_dir, 'mem0_frontend.html')
        except Exception as e:
            logger.error(f"Error serving demo: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


def main():
    """主函数"""
    config = get_config()
    
    # 验证配置
    if not config.validate_config():
        logger.error("Configuration validation failed")
        return
    
    # 创建应用
    app = create_app()
    
    # 启动服务
    logger.info(f"Starting Memory-X service on {config.HOST}:{config.PORT}")
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )


if __name__ == '__main__':
    main()
