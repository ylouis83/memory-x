#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Memory-X 启动脚本
"""

import os
import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.api.app import create_app
from configs.settings import get_config


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Memory-X 启动脚本')
    parser.add_argument('--config', '-c', default=None, help='配置文件名称')
    parser.add_argument('--host', default=None, help='服务主机地址')
    parser.add_argument('--port', '-p', type=int, default=None, help='服务端口')
    parser.add_argument('--debug', '-d', action='store_true', help='调试模式')
    parser.add_argument('--init-db', action='store_true', help='初始化数据库')
    
    args = parser.parse_args()
    
    # 获取配置
    config = get_config(args.config)
    
    # 初始化数据库
    if args.init_db:
        print("🔧 初始化数据库...")
        from src.core.init_database import DatabaseInitializer
        initializer = DatabaseInitializer(config)
        initializer.init_sqlite_database()
        print("✅ 数据库初始化完成")
    
    # 创建应用
    app = create_app(args.config)
    
    # 设置运行参数
    host = args.host or config.HOST
    port = args.port or config.PORT
    debug = args.debug or config.DEBUG
    
    print(f"🚀 启动 Memory-X 服务")
    print(f"📍 地址: {host}:{port}")
    print(f"🔧 调试模式: {debug}")
    print(f"🌍 环境: {os.getenv('MEMORY_ENV', 'default')}")
    print("=" * 50)
    
    # 启动服务
    app.run(
        host=host,
        port=port,
        debug=debug
    )


if __name__ == '__main__':
    main()
