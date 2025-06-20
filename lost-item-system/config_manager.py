#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理工具 - 查看和验证系统配置
"""
import sys
import os
from datetime import timedelta

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def show_current_config():
    """显示当前配置"""
    from config.config import Config, config
    
    env = os.environ.get('FLASK_ENV', 'development')
    current_config = config.get(env, Config)
    
    print("=" * 60)
    print(f"当前配置环境: {env.upper()}")
    print("=" * 60)
    
    print("\n📊 业务逻辑配置:")
    print(f"  自动归档时间: {current_config.AUTO_ARCHIVE_DAYS} 天")
    print(f"  搜索结果限制: {current_config.SEARCH_RESULTS_LIMIT} 条")
    print(f"  首页显示数量: {current_config.HOME_PAGE_ITEMS_LIMIT} 条")
    
    print("\n👤 用户验证配置:")
    print(f"  用户名长度: {current_config.USERNAME_MIN_LENGTH}-{current_config.USERNAME_MAX_LENGTH} 字符")
    print(f"  密码最小长度: {current_config.PASSWORD_MIN_LENGTH} 字符")
    
    print("\n💰 打赏配置:")
    print(f"  打赏金额范围: {current_config.MIN_REWARD_AMOUNT}-{current_config.MAX_REWARD_AMOUNT} 元")
    
    print("\n📝 文本长度限制:")
    print(f"  详细描述: {current_config.MAX_DESCRIPTION_LENGTH} 字符")
    print(f"  隐藏信息: {current_config.MAX_HIDDEN_INFO_LENGTH} 字符")
    print(f"  拾获地点: {current_config.MAX_LOCATION_LENGTH} 字符")
    print(f"  物品名称: {current_config.MAX_ITEM_NAME_LENGTH} 字符")
    
    print("\n🗄️ 数据库连接池:")
    print(f"  连接池大小: {current_config.DB_POOL_SIZE}")
    print(f"  连接超时: {current_config.DB_POOL_TIMEOUT} 秒")
    print(f"  连接回收: {current_config.DB_POOL_RECYCLE} 秒")
    print(f"  最大溢出: {current_config.DB_MAX_OVERFLOW}")
    
    print("\n📁 文件上传配置:")
    print(f"  最大文件大小: {current_config.MAX_CONTENT_LENGTH / (1024*1024):.1f} MB")
    print(f"  最大图片大小: {current_config.MAX_IMAGE_SIZE / (1024*1024):.1f} MB")
    print(f"  允许的图片格式: {', '.join(current_config.ALLOWED_IMAGE_EXTENSIONS)}")

def validate_config():
    """验证配置"""
    from config.config import Config, config
    
    env = os.environ.get('FLASK_ENV', 'development')
    current_config = config.get(env, Config)
    
    print("🔍 配置验证中...")
    
    try:
        current_config.validate_config()
        print("✅ 配置验证通过！")
        return True
    except ValueError as e:
        print(f"❌ 配置验证失败: {e}")
        return False

def show_env_variables():
    """显示相关的环境变量"""
    print("🌍 相关环境变量:")
    print("=" * 40)
    
    env_vars = [
        'FLASK_ENV', 'AUTO_ARCHIVE_DAYS', 'SEARCH_RESULTS_LIMIT', 
        'HOME_PAGE_ITEMS_LIMIT', 'USERNAME_MIN_LENGTH', 'USERNAME_MAX_LENGTH',
        'MIN_REWARD_AMOUNT', 'MAX_REWARD_AMOUNT', 'MYSQL_HOST', 'MYSQL_DB'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, '未设置')
        print(f"  {var}: {value}")

def test_auto_archive_logic():
    """测试自动归档逻辑"""
    from config.config import Config
    
    print("🧪 测试自动归档逻辑:")
    print("=" * 40)
    
    archive_days = Config.AUTO_ARCHIVE_DAYS
    archive_timedelta = timedelta(days=archive_days)
    
    print(f"配置的归档天数: {archive_days}")
    print(f"归档时间间隔: {archive_timedelta}")
    
    from datetime import datetime
    now = datetime.now()
    cutoff_time = now - archive_timedelta
    
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"归档截止时间: {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"早于 {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')} 的记录将被自动归档")

def main():
    print("🔧 失物招领系统 - 配置管理工具")
    print("=" * 60)
    
    while True:
        print("\n选择操作:")
        print("1. 查看当前配置")
        print("2. 验证配置")
        print("3. 查看环境变量")
        print("4. 测试自动归档逻辑")
        print("5. 退出")
        
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == "1":
            show_current_config()
        elif choice == "2":
            validate_config()
        elif choice == "3":
            show_env_variables()
        elif choice == "4":
            test_auto_archive_logic()
        elif choice == "5":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main()