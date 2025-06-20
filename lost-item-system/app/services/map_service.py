#!/usr/bin/env python3
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
    
    @classmethod
    def set_api_credentials(cls, web_service_key, security_code=None):
        """设置高德地图API密钥和安全密钥"""
        cls.AMAP_API_KEY = web_service_key
        if security_code:
            cls.AMAP_SECURITY_CODE = security_code
    
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
    
    @staticmethod
    def get_nearby_records(center_lat, center_lon, radius_km=10):
        """
        获取指定坐标周围的拾获记录
        center_lat: 中心纬度
        center_lon: 中心经度
        radius_km: 搜索半径（公里）
        """
        from app.models import FoundRecord, Agent
        from app import db
        
        try:
            # 简单的矩形范围过滤
            lat_offset = radius_km / 111.0  # 1度纬度约111公里
            lon_offset = radius_km / (111.0 * abs(math.cos(math.radians(center_lat))))
            
            records = FoundRecord.query.join(Agent).filter(
                Agent.status == 1,
                FoundRecord.latitude.isnot(None),
                FoundRecord.longitude.isnot(None),
                FoundRecord.latitude.between(center_lat - lat_offset, center_lat + lat_offset),
                FoundRecord.longitude.between(center_lon - lon_offset, center_lon + lon_offset)
            ).all()
            
            # 计算精确距离并过滤
            nearby_records = []
            for record in records:
                distance = MapService.calculate_distance(
                    center_lat, center_lon,
                    float(record.latitude), float(record.longitude)
                )
                
                if distance <= radius_km * 1000:  # 转换为米
                    record_data = {
                        'record_id': record.record_id,
                        'pickup_location': record.pickup_location,
                        'formatted_address': record.formatted_address,
                        'latitude': float(record.latitude),
                        'longitude': float(record.longitude),
                        'distance': round(distance),
                        'items': [item.item_name for item in record.items],
                        'created_time': record.created_time.strftime('%Y-%m-%d %H:%M'),
                        'agent_username': record.agent.username,
                        'detailed_description': record.detailed_description[:100] + '...' if len(record.detailed_description) > 100 else record.detailed_description
                    }
                    nearby_records.append(record_data)
            
            # 按距离排序
            nearby_records.sort(key=lambda x: x['distance'])
            
            return {
                'success': True,
                'data': nearby_records
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'搜索附近记录失败: {str(e)}'
            }
