#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
丢物小助手性能测试脚本
"""
import time
import sys
import os
import requests
import threading
from concurrent.futures import ThreadPoolExecutor

def test_startup_time():
    """测试应用启动时间"""
    print("=== 应用启动时间测试 ===")
    
    # 测试各个组件导入时间
    start = time.time()
    import pymysql
    pymysql_time = time.time() - start
    
    start = time.time()
    from flask import Flask
    flask_time = time.time() - start
    
    start = time.time()
    from flask_sqlalchemy import SQLAlchemy
    sqlalchemy_time = time.time() - start
    
    # 测试完整应用启动时间
    start = time.time()
    from app import create_app
    app = create_app()
    total_time = time.time() - start
    
    print(f"PyMySQL 导入时间: {pymysql_time:.3f}秒")
    print(f"Flask 导入时间: {flask_time:.3f}秒") 
    print(f"SQLAlchemy 导入时间: {sqlalchemy_time:.3f}秒")
    print(f"应用总启动时间: {total_time:.3f}秒")
    print(f"启动优化效果: {'✓ 良好' if total_time < 1.0 else '⚠ 需要优化' if total_time < 2.0 else '✗ 较慢'}")
    
    return app

def test_page_load(url="http://localhost:5050", num_requests=5):
    """测试页面加载时间"""
    def make_request():
        start = time.time()
        try:
            response = requests.get(url, timeout=10)
            load_time = time.time() - start
            return load_time, response.status_code
        except Exception as e:
            return None, str(e)
    
    print(f"\n测试页面加载时间 ({num_requests}次请求):")
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        results = [future.result() for future in futures]
    
    successful_requests = [r for r in results if r[0] is not None]
    if successful_requests:
        times = [r[0] for r in successful_requests]
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        print(f"平均响应时间: {avg_time:.2f}秒")
        print(f"最快响应时间: {min_time:.2f}秒") 
        print(f"最慢响应时间: {max_time:.2f}秒")
        print(f"成功请求数: {len(successful_requests)}/{num_requests}")
    else:
        print("所有请求都失败了")

def test_database_queries():
    """测试数据库查询性能"""
    print("\n=== 数据库查询性能测试 ===")
    
    try:
        from app import create_app, db
        from app.models import Agent, FoundRecord, FoundItem
        from sqlalchemy.orm import selectinload
        
        app = create_app()
        
        with app.app_context():
            # 测试简单查询
            start = time.time()
            agents_count = Agent.query.count()
            simple_query_time = time.time() - start
            
            # 测试复杂查询（首页查询）
            start = time.time()
            latest_items = FoundRecord.query.join(Agent).filter(
                Agent.status == 1
            ).options(
                selectinload(FoundRecord.items),
                selectinload(FoundRecord.agent)
            ).order_by(FoundRecord.created_time.desc()).limit(6).all()
            complex_query_time = time.time() - start
            
            # 测试搜索查询
            start = time.time()
            search_results = FoundRecord.query.join(Agent).filter(
                Agent.status == 1
            ).join(FoundItem).options(
                selectinload(FoundRecord.items),
                selectinload(FoundRecord.agent)
            ).limit(10).all()
            search_query_time = time.time() - start
            
            print(f"Agent 数量: {agents_count}")
            print(f"简单查询时间: {simple_query_time:.3f}秒")
            print(f"首页查询时间: {complex_query_time:.3f}秒")
            print(f"搜索查询时间: {search_query_time:.3f}秒")
            print(f"数据库性能: {'✓ 良好' if complex_query_time < 0.1 else '⚠ 一般' if complex_query_time < 0.5 else '✗ 需要优化'}")
            
    except Exception as e:
        print(f"数据库测试失败: {e}")

def print_optimization_suggestions():
    """打印优化建议"""
    print("\n=== 性能优化建议 ===")
    print("1. 数据库优化:")
    print("   - 为常用查询字段添加索引")
    print("   - 使用数据库连接池")
    print("   - 启用查询缓存")
    
    print("\n2. 前端优化:")
    print("   - 使用CDN加载静态资源")
    print("   - 压缩CSS和JavaScript")
    print("   - 启用浏览器缓存")
    
    print("\n3. 服务器优化:")
    print("   - 使用Gunicorn等WSGI服务器")
    print("   - 启用Gzip压缩")
    print("   - 配置反向代理(Nginx)")

if __name__ == "__main__":
    print("丢物小助手性能测试工具")
    print("=" * 50)
    
    try:
        # 启动时间测试
        app = test_startup_time()
        
        # 提示用户启动服务器
        print("\n请在另一个终端中运行: python run.py")
        input("服务器启动后按回车继续测试...")
        
        # 测试页面加载
        test_page_load()
        test_page_load("http://localhost:5050/search")
        test_page_load("http://localhost:5050/login")
        
        # 数据库查询测试
        test_database_queries()
        
        # 优化建议
        print_optimization_suggestions()
        
        print("\n测试完成!")
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        sys.exit(1)