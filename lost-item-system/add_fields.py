#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单添加缺失字段到现有归档表
"""
import sys
import os
import pymysql

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def add_missing_fields():
    """给现有的归档表添加缺失的字段"""
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
            print("正在检查和添加缺失字段...")
            
            # 检查 archived_record 表的现有字段
            cursor.execute("DESCRIBE archived_record")
            existing_columns = [col[0] for col in cursor.fetchall()]
            print(f"现有字段: {existing_columns}")
            
            # 需要添加的字段
            fields_to_add = []
            
            # 检查并添加 archive_reason 字段
            if 'archive_reason' not in existing_columns:
                fields_to_add.append(
                    "ADD COLUMN archive_reason ENUM('USER_ARCHIVE', 'USER_DELETE', 'AUTO_ARCHIVE') DEFAULT 'USER_ARCHIVE'"
                )
            
            # 检查并添加 archived_by_agent_id 字段
            if 'archived_by_agent_id' not in existing_columns:
                fields_to_add.append(
                    "ADD COLUMN archived_by_agent_id INT, ADD FOREIGN KEY (archived_by_agent_id) REFERENCES agent(agent_id)"
                )
            
            # 检查并添加 original_created_time 字段
            if 'original_created_time' not in existing_columns:
                fields_to_add.append(
                    "ADD COLUMN original_created_time DATETIME"
                )
            
            # 执行添加字段的SQL
            if fields_to_add:
                alter_sql = f"ALTER TABLE archived_record {', '.join(fields_to_add)}"
                cursor.execute(alter_sql)
                print(f"✓ 添加了 {len(fields_to_add)} 个字段")
            else:
                print("✓ 所有必要字段都已存在")
            
            # 检查 archived_item 表
            cursor.execute("DESCRIBE archived_item")
            item_columns = [col[0] for col in cursor.fetchall()]
            print(f"archived_item 现有字段: {item_columns}")
            
            # 添加 original_item_id 字段（如果不存在）
            if 'original_item_id' not in item_columns:
                cursor.execute("ALTER TABLE archived_item ADD COLUMN original_item_id INT DEFAULT 0")
                print("✓ 添加了 original_item_id 字段")
            
            connection.commit()
            print("✓ 字段添加完成！")
            
            return True
            
    except Exception as e:
        print(f"添加字段时出错: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    print("=" * 50)
    print("添加归档表缺失字段")
    print("=" * 50)
    
    if add_missing_fields():
        print("\n✓ 完成！现在可以启动应用: python run.py")
    else:
        print("\n✗ 失败")