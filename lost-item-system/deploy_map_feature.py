#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地图功能数据库迁移脚本
"""
import sys
import os
import pymysql

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def migrate_database_for_map():
    """为地图功能迁移数据库"""
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
            print("🗺️ 开始地图功能数据库迁移...")
            print("=" * 50)
            
            # 1. 检查并添加地理位置字段
            print("1. 检查found_record表结构...")
            cursor.execute("SHOW COLUMNS FROM found_record")
            columns = [col[0] for col in cursor.fetchall()]
            
            fields_to_add = []
            if 'latitude' not in columns:
                fields_to_add.append(('latitude', 'DECIMAL(10,8)'))
            if 'longitude' not in columns:
                fields_to_add.append(('longitude', 'DECIMAL(11,8)'))
            if 'formatted_address' not in columns:
                fields_to_add.append(('formatted_address', 'VARCHAR(500)'))
            
            if fields_to_add:
                print("2. 添加地理位置字段...")
                for field_name, field_type in fields_to_add:
                    try:
                        sql = f"ALTER TABLE found_record ADD COLUMN {field_name} {field_type}"
                        cursor.execute(sql)
                        print(f"   ✓ 添加字段: {field_name} ({field_type})")
                    except Exception as e:
                        print(f"   ⚠ 字段 {field_name} 可能已存在: {e}")
            else:
                print("2. 地理位置字段已存在，跳过添加")
            
            # 3. 创建地理位置索引（可选，提高查询性能）
            print("3. 创建地理位置索引...")
            try:
                cursor.execute("CREATE INDEX idx_location ON found_record(latitude, longitude)")
                print("   ✓ 创建地理位置复合索引")
            except Exception as e:
                if "Duplicate key name" in str(e):
                    print("   ✓ 地理位置索引已存在")
                else:
                    print(f"   ⚠ 创建索引失败: {e}")
            
            connection.commit()
            print("\n✅ 地图功能数据库迁移完成！")
            
            # 4. 显示迁移后的表结构
            print("\n📋 found_record表当前结构:")
            cursor.execute("SHOW COLUMNS FROM found_record")
            columns = cursor.fetchall()
            
            for col in columns:
                field_name = col[0]
                field_type = col[1]
                if 'location' in field_name.lower() or field_name in ['latitude', 'longitude', 'formatted_address']:
                    print(f"   📍 {field_name}: {field_type}")
                else:
                    print(f"   📝 {field_name}: {field_type}")
            
            return True
            
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

def create_map_service_files():
    """创建地图服务相关文件"""
    print("\n🔧 创建地图服务文件...")
    
    # 1. 更新 app/services/map_service.py
    map_service_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地图服务 - 处理高德地图相关的业务逻辑
"""
import requests
from flask import current_app
import json
import math

class MapService:
    """地图服务类"""
    
    # 高德地图API配置
    AMAP_API_KEY = "your_amap_api_key_here"  # 需要替换为实际的API Key
    GEOCODING_URL = "https://restapi.amap.com/v3/geocode/geo"
    REVERSE_GEOCODING_URL = "https://restapi.amap.com/v3/geocode/regeo"
    
    @classmethod
    def set_api_key(cls, api_key):
        """设置高德地图API密钥"""
        cls.AMAP_API_KEY = api_key
    
    @staticmethod
    def geocode_address(address):
        """地理编码：将地址转换为坐标"""
        try:
            params = {
                'key': MapService.AMAP_API_KEY,
                'address': address,
                'output': 'JSON'
            }
            
            response = requests.get(MapService.GEOCODING_URL, params=params, timeout=10)
            data = response.json()
            
            if data['status'] == '1' and data['count'] != '0':
                geocode = data['geocodes'][0]
                location = geocode['location'].split(',')
                
                return {
                    'success': True,
                    'data': {
                        'longitude': float(location[0]),
                        'latitude': float(location[1]),
                        'formatted_address': geocode['formatted_address'],
                        'level': geocode.get('level', '')
                    }
                }
            else:
                return {
                    'success': False,
                    'message': '地址解析失败，请检查地址是否正确'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'地址解析异常: {str(e)}'
            }
    
    @staticmethod
    def reverse_geocode(latitude, longitude):
        """逆地理编码：将坐标转换为地址"""
        try:
            params = {
                'key': MapService.AMAP_API_KEY,
                'location': f'{longitude},{latitude}',
                'output': 'JSON',
                'radius': 1000,
                'extensions': 'all'
            }
            
            response = requests.get(MapService.REVERSE_GEOCODING_URL, params=params, timeout=10)
            data = response.json()
            
            if data['status'] == '1':
                regeocode = data['regeocode']
                
                return {
                    'success': True,
                    'data': {
                        'formatted_address': regeocode['formatted_address'],
                        'province': regeocode['addressComponent']['province'],
                        'city': regeocode['addressComponent']['city'],
                        'district': regeocode['addressComponent']['district'],
                        'township': regeocode['addressComponent']['township']
                    }
                }
            else:
                return {
                    'success': False,
                    'message': '坐标解析失败'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'坐标解析异常: {str(e)}'
            }
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """计算两点间的直线距离（米）"""
        # 转换为弧度
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine公式
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # 地球半径（米）
        r = 6371000
        
        return c * r
    
    @staticmethod
    def validate_coordinates(latitude, longitude):
        """验证坐标的有效性"""
        try:
            lat = float(latitude)
            lon = float(longitude)
            
            # 中国大陆坐标范围验证
            if not (3.86 <= lat <= 53.55):
                return False, "纬度超出中国范围"
            
            if not (73.66 <= lon <= 135.05):
                return False, "经度超出中国范围"
            
            return True, "坐标有效"
            
        except (ValueError, TypeError):
            return False, "坐标格式错误"
'''
    
    with open('app/services/map_service.py', 'w', encoding='utf-8') as f:
        f.write(map_service_content)
    print("   ✓ 创建 app/services/map_service.py")
    
    # 2. 创建地图页面模板
    map_template_content = '''{% extends "base.html" %}

{% block title %}地图搜索 - 丢物小助手{% endblock %}

{% block extra_css %}
<style>
#map-container {
    height: 600px;
    width: 100%;
    border-radius: 8px;
    overflow: hidden;
}

.map-controls {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    padding: 1rem;
    margin-bottom: 1rem;
}

@media (max-width: 768px) {
    #map-container {
        height: 400px;
    }
}
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="map-controls">
                <h4 class="mb-0">地图搜索</h4>
                <small class="text-muted">查看所有拾获物品的位置分布</small>
            </div>
        </div>
        
        <div class="col-12">
            <div class="card">
                <div class="card-body p-0">
                    <div id="map-container">
                        <div class="d-flex justify-content-center align-items-center h-100">
                            <div class="text-center">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">地图加载中...</span>
                                </div>
                                <p class="mt-2">正在加载地图...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<!-- 高德地图API -->
<script type="text/javascript" src="https://webapi.amap.com/maps?v=2.0&key={{ config.AMAP_API_KEY }}&plugin=AMap.Geolocation"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    // 简单的地图初始化
    if (typeof AMap !== 'undefined') {
        var map = new AMap.Map('map-container', {
            zoom: 13,
            center: [116.397428, 39.90923]
        });
        
        // 加载地图数据
        fetch('/api/map/records')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.records) {
                    data.records.forEach(record => {
                        var marker = new AMap.Marker({
                            position: [record.longitude, record.latitude],
                            title: record.pickup_location
                        });
                        map.add(marker);
                    });
                    
                    if (data.records.length > 0) {
                        var markers = map.getAllOverlays('marker');
                        map.setFitView(markers);
                    }
                }
            })
            .catch(error => {
                console.error('加载地图数据失败:', error);
            });
    }
});
</script>
{% endblock %}
'''
    
    with open('templates/pages/map.html', 'w', encoding='utf-8') as f:
        f.write(map_template_content)
    print("   ✓ 创建 templates/pages/map.html")

def update_existing_files():
    """更新现有文件以支持地图功能"""
    print("\n📝 更新现有文件...")
    
    print("   📋 需要手动更新的文件列表:")
    print("   1. app/models.py - 添加地理位置字段和方法")
    print("   2. app/api/api_routes.py - 添加地图相关API路由")
    print("   3. app/routes/item_routes.py - 添加地图页面路由和更新发布功能")
    print("   4. app/services/item_service.py - 更新发布方法支持地理位置")
    print("   5. templates/pages/search.html - 添加地图查看按钮")
    print("   6. templates/pages/publish.html - 添加地图选点功能")

def check_requirements():
    """检查依赖包"""
    print("\n📦 检查依赖包...")
    
    try:
        import requests
        print("   ✓ requests 已安装")
    except ImportError:
        print("   ❌ 需要安装 requests: pip install requests")
    
    try:
        import hashlib
        print("   ✓ hashlib 已安装（标准库）")
    except ImportError:
        print("   ❌ hashlib 不可用")
    
    print("\n⚠️ 高德地图API配置注意事项:")
    print("   1. 需要申请高德地图API密钥 (Web服务 + JS API)")
    print("   2. 需要申请安全密钥（数字签名）- 必须配置！")
    print("   3. 配置方式：")
    print("      方法1: 环境变量")
    print("         export AMAP_API_KEY='your_api_key'")
    print("         export AMAP_SECURITY_CODE='your_security_code'")
    print("      方法2: 修改 config/config.py")
    print("         AMAP_API_KEY = 'your_api_key'")
    print("         AMAP_SECURITY_CODE = 'your_security_code'")
    print("   4. 申请地址: https://console.amap.com/")
    print("   5. 记得设置域名白名单")
    
    print("\n🔐 安全密钥说明:")
    print("   - 高德地图现在强制要求使用安全密钥")
    print("   - 用于生成数字签名，防止API密钥被盗用")
    print("   - 在控制台的应用详情中可以找到")

def main():
    print("🗺️ 地图功能部署工具")
    print("=" * 60)
    
    while True:
        print("\n选择操作:")
        print("1. 数据库迁移（添加地理位置字段）")
        print("2. 创建地图服务文件")
        print("3. 显示手动更新列表")
        print("4. 检查依赖包")
        print("5. 全部执行")
        print("6. 退出")
        
        choice = input("\n请输入选择 (1-6): ").strip()
        
        if choice == "1":
            migrate_database_for_map()
        elif choice == "2":
            create_map_service_files()
        elif choice == "3":
            update_existing_files()
        elif choice == "4":
            check_requirements()
        elif choice == "5":
            print("执行全部操作...")
            migrate_database_for_map()
            create_map_service_files()
            update_existing_files()
            check_requirements()
            print("\n🎉 基础设置完成！接下来需要手动更新文件并设置API密钥")
        elif choice == "6":
            print("👋 部署工具退出")
            break
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main()