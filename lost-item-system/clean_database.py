#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库清理脚本 - 删除无用的Django表和重复表
"""
import sys
import os
import pymysql

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def clean_unused_tables():
    """清理无用的表"""
    from config.config import Config
    
    # 需要删除的Django相关表
    django_tables = [
        'auth_group',
        'auth_group_permissions', 
        'auth_permission',
        'auth_user',
        'auth_user_groups',
        'auth_user_user_permissions',
        'django_admin_log',
        'django_content_type',
        'django_migrations',
        'django_session'
    ]
    
    # 重复的表
    duplicate_tables = [
        'agents'  # 与agent表重复
    ]
    
    all_tables_to_delete = django_tables + duplicate_tables
    
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 检查当前所有表
            cursor.execute("SHOW TABLES")
            existing_tables = [table[0] for table in cursor.fetchall()]
            
            print("当前数据库中的表:")
            for table in existing_tables:
                print(f"  - {table}")
            
            print(f"\n准备删除的无用表:")
            tables_to_delete = []
            for table in all_tables_to_delete:
                if table in existing_tables:
                    tables_to_delete.append(table)
                    print(f"  - {table} (Django相关)" if table in django_tables else f"  - {table} (重复表)")
            
            if not tables_to_delete:
                print("没有发现需要删除的无用表")
                return True
            
            # 确认删除
            print(f"\n将要删除 {len(tables_to_delete)} 个表")
            confirm = input("确定要删除这些表吗？(y/N): ").strip().lower()
            
            if confirm != 'y':
                print("操作已取消")
                return False
            
            # 禁用外键检查
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # 删除表
            deleted_count = 0
            for table in tables_to_delete:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
                    print(f"✓ 已删除表: {table}")
                    deleted_count += 1
                except Exception as e:
                    print(f"✗ 删除表 {table} 失败: {e}")
            
            # 重新启用外键检查
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            connection.commit()
            print(f"\n✓ 成功删除了 {deleted_count} 个无用表")
            
            # 显示清理后的表
            cursor.execute("SHOW TABLES")
            remaining_tables = [table[0] for table in cursor.fetchall()]
            print(f"\n清理后剩余的表 ({len(remaining_tables)} 个):")
            
            # 分类显示
            system_tables = ['agent', 'found_record', 'found_item', 'reward', 'found_history', 'archived_record', 'archived_item']
            
            print("  失物招领系统表:")
            for table in remaining_tables:
                if table in system_tables:
                    print(f"    ✓ {table}")
            
            print("  其他表:")
            for table in remaining_tables:
                if table not in system_tables:
                    print(f"    ? {table}")
            
            return True
            
    except Exception as e:
        print(f"清理过程中出错: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

def show_table_info():
    """显示当前表的详细信息"""
    from config.config import Config
    
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            print("数据库表详细信息:")
            print("=" * 60)
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                count = cursor.fetchone()[0]
                
                cursor.execute(f"SHOW CREATE TABLE `{table}`")
                create_sql = cursor.fetchone()[1]
                
                print(f"\n表名: {table}")
                print(f"记录数: {count}")
                print("用途:")
                
                if table == 'agent':
                    print("  - 存储探员用户信息")
                elif table == 'found_record':
                    print("  - 存储拾获物品记录")
                elif table == 'found_item':
                    print("  - 存储物品详细信息")
                elif table == 'reward':
                    print("  - 存储打赏记录")
                elif table == 'archived_record':
                    print("  - 存储归档的记录")
                elif table == 'archived_item':
                    print("  - 存储归档的物品")
                elif table == 'found_history':
                    print("  - 旧版历史记录（可考虑迁移到archived_record）")
                elif table.startswith('auth_') or table.startswith('django_'):
                    print("  - Django框架表（建议删除）")
                elif table == 'agents':
                    print("  - 重复的用户表（建议删除）")
                else:
                    print("  - 未知用途")
                    
    except Exception as e:
        print(f"获取表信息时出错: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    print("=" * 60)
    print("数据库表清理工具")
    print("=" * 60)
    
    print("选择操作:")
    print("1. 查看所有表的详细信息")
    print("2. 清理无用的Django表和重复表")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "1":
        show_table_info()
    elif choice == "2":
        clean_unused_tables()
    else:
        print("无效选择")