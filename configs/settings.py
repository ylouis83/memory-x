#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Memory-X 配置文件
集中管理应用的所有配置信息
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用配置类"""
    
    # 基础配置
    PROJECT_NAME = "Memory-X"
    VERSION = "1.0.0"
    DEBUG = os.getenv('MEMORY_DEBUG', 'true').lower() == 'true'
    
    # 服务配置
    HOST = os.getenv('MEMORY_SERVICE_HOST', '0.0.0.0')
    PORT = int(os.getenv('MEMORY_SERVICE_PORT', 5000))
    
    # 数据库配置
    DATABASE = {
        'type': os.getenv('MEMORY_DB_TYPE', 'sqlite'),
        'path': os.getenv('MEMORY_DB_PATH', './memory_db/memory.db'),
        'host': os.getenv('MEMORY_DB_HOST', 'localhost'),
        'port': int(os.getenv('MEMORY_DB_PORT', 3306)),
        # Use environment variables without hard-coded defaults to avoid
        # committing sensitive credentials to the repository.
        'user': os.getenv('MEMORY_DB_USER', ''),
        'password': os.getenv('MEMORY_DB_PASSWORD', ''),
        'database': os.getenv('MEMORY_DB_NAME', 'memory_x'),
        'pool_size': int(os.getenv('MEMORY_DB_POOL_SIZE', 10)),
        'max_overflow': int(os.getenv('MEMORY_DB_MAX_OVERFLOW', 20)),
        'echo': DEBUG
    }
    
    # 记忆配置
    MEMORY = {
        'max_short_term': int(os.getenv('MEMORY_MAX_SHORT_TERM', 10)),
        'max_working_memory': int(os.getenv('MEMORY_MAX_WORKING_MEMORY', 100)),
        'importance_threshold': int(os.getenv('MEMORY_IMPORTANCE_THRESHOLD', 3)),
        'ttl_days': int(os.getenv('MEMORY_TTL_DAYS', 365)),
        'max_context_rounds': int(os.getenv('MEMORY_MAX_CONTEXT_ROUNDS', 50)),
        'entity_recognition_enabled': os.getenv('MEMORY_ENTITY_RECOGNITION', 'true').lower() == 'true',
        'intent_detection_enabled': os.getenv('MEMORY_INTENT_DETECTION', 'true').lower() == 'true'
    }
    
    # API配置
    API = {
        'rate_limit': int(os.getenv('MEMORY_API_RATE_LIMIT', 1000)),
        'timeout': int(os.getenv('MEMORY_API_TIMEOUT', 30)),
        'cors_origins': os.getenv('MEMORY_CORS_ORIGINS', '*').split(','),
        'max_request_size': int(os.getenv('MEMORY_MAX_REQUEST_SIZE', 16 * 1024 * 1024)),  # 16MB
        'enable_compression': os.getenv('MEMORY_ENABLE_COMPRESSION', 'true').lower() == 'true'
    }
    
    # 日志配置
    LOGGING = {
        'level': os.getenv('MEMORY_LOG_LEVEL', 'INFO'),
        'file': os.getenv('MEMORY_LOG_FILE', './logs/memory.log'),
        'max_bytes': int(os.getenv('MEMORY_LOG_MAX_BYTES', 10 * 1024 * 1024)),  # 10MB
        'backup_count': int(os.getenv('MEMORY_LOG_BACKUP_COUNT', 5)),
        'format': os.getenv('MEMORY_LOG_FORMAT', 
                           '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    }
    
    # 安全配置
    SECURITY = {
        # Remove hard-coded secret values; these must be provided via
        # environment variables in deployment.
        'secret_key': os.getenv('MEMORY_SECRET_KEY', ''),
        'jwt_secret': os.getenv('MEMORY_JWT_SECRET', ''),
        'jwt_expire_hours': int(os.getenv('MEMORY_JWT_EXPIRE_HOURS', 24)),
        'password_salt_rounds': int(os.getenv('MEMORY_PASSWORD_SALT_ROUNDS', 12)),
        'enable_rate_limiting': os.getenv('MEMORY_ENABLE_RATE_LIMITING', 'true').lower() == 'true'
    }
    
    # 缓存配置
    CACHE = {
        'type': os.getenv('MEMORY_CACHE_TYPE', 'memory'),  # memory, redis
        'redis_url': os.getenv('MEMORY_REDIS_URL', 'redis://localhost:6379/0'),
        'default_timeout': int(os.getenv('MEMORY_CACHE_TIMEOUT', 300)),  # 5分钟
        'max_size': int(os.getenv('MEMORY_CACHE_MAX_SIZE', 1000))
    }
    
    # 实体识别配置
    ENTITY_RECOGNITION = {
        'enabled': True,
        'models': {
            'chinese': 'zh_core_web_sm',
            'english': 'en_core_web_sm'
        },
        'custom_entities': [
            'PERSON', 'LOCATION', 'ORGANIZATION', 'MEDICINE', 
            'SYMPTOM', 'DISEASE', 'TREATMENT'
        ],
        'confidence_threshold': 0.7
    }
    
    # 意图检测配置
    INTENT_DETECTION = {
        'enabled': True,
        'patterns': {
            'INTRODUCE': ['我叫', '我是', '我的名字是'],
            'REQUEST_MEDICINE': ['开药', '配药', '买药', '需要药'],
            'PRESCRIPTION_INQUIRY': ['怎么吃', '用法', '副作用', '注意事项'],
            'EMERGENCY': ['救命', '紧急', '胸痛', '呼吸困难'],
            'NORMAL_CONSULTATION': ['咨询', '问诊', '看病']
        },
        'confidence_threshold': 0.6
    }
    
    # 重要性评估配置
    IMPORTANCE_EVALUATION = {
        'factors': {
            'intent_weight': 0.3,
            'entity_weight': 0.2,
            'frequency_weight': 0.2,
            'recency_weight': 0.15,
            'user_feedback_weight': 0.15
        },
        'thresholds': {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
    }
    
    @classmethod
    def get_database_url(cls) -> str:
        """获取数据库连接URL"""
        db_config = cls.DATABASE
        
        if db_config['type'] == 'sqlite':
            return f"sqlite:///{db_config['path']}"
        elif db_config['type'] == 'mysql':
            return (f"mysql+pymysql://{db_config['user']}:{db_config['password']}"
                   f"@{db_config['host']}:{db_config['port']}/{db_config['database']}")
        elif db_config['type'] == 'postgresql':
            return (f"postgresql://{db_config['user']}:{db_config['password']}"
                   f"@{db_config['host']}:{db_config['port']}/{db_config['database']}")
        else:
            raise ValueError(f"Unsupported database type: {db_config['type']}")
    
    @classmethod
    def get_flask_config(cls) -> Dict[str, Any]:
        """获取Flask配置"""
        return {
            'SECRET_KEY': cls.SECURITY['secret_key'],
            'DEBUG': cls.DEBUG,
            'TESTING': False,
            'JSON_AS_ASCII': False,
            'JSONIFY_PRETTYPRINT_REGULAR': cls.DEBUG,
            'MAX_CONTENT_LENGTH': cls.API['max_request_size']
        }
    
    @classmethod
    def get_server_config(cls) -> Dict[str, Any]:
        """获取服务器配置"""
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'debug': cls.DEBUG
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置有效性"""
        try:
            # 验证数据库配置
            if cls.DATABASE['type'] not in ['sqlite', 'mysql', 'postgresql']:
                raise ValueError(f"Invalid database type: {cls.DATABASE['type']}")
            
            # 验证端口范围
            if not (1 <= cls.PORT <= 65535):
                raise ValueError(f"Invalid port number: {cls.PORT}")
            
            # 验证记忆配置
            if cls.MEMORY['max_short_term'] <= 0:
                raise ValueError("max_short_term must be positive")
            
            if cls.MEMORY['importance_threshold'] < 1 or cls.MEMORY['importance_threshold'] > 5:
                raise ValueError("importance_threshold must be between 1 and 5")
            
            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOGGING = {
        **Config.LOGGING,
        'level': 'DEBUG'
    }


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOGGING = {
        **Config.LOGGING,
        'level': 'WARNING'
    }
    
    # 生产环境安全配置
    SECURITY = {
        **Config.SECURITY,
        'secret_key': os.getenv('MEMORY_SECRET_KEY'),
        'jwt_secret': os.getenv('MEMORY_JWT_SECRET')
    }


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    
    # 测试数据库配置
    DATABASE = {
        **Config.DATABASE,
        'type': 'sqlite',
        'path': ':memory:'  # 内存数据库
    }


# 配置映射
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> Config:
    """获取配置实例"""
    if config_name is None:
        config_name = os.getenv('MEMORY_ENV', 'default')
    
    config_class = config_map.get(config_name, config_map['default'])
    return config_class()
