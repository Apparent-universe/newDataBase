from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from app.services.item_service import ItemService
from app.services.reward_service import RewardService
from app.services.map_service import MapService

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/found-items/<int:record_id>/reward', methods=['POST'])
def create_reward(record_id):
    try:
        data = request.get_json()
        result = RewardService.create_reward(
            record_id=record_id,
            amount=data['amount']
        )
        
        if result['success']:
            return jsonify({'message': '打赏成功'})
        else:
            return jsonify({'message': result['message']}), 400
            
    except Exception as e:
        return jsonify({'message': f'打赏失败: {str(e)}'}), 500

@api_bp.route('/found-items/<int:record_id>/archive', methods=['POST'])
@login_required
def archive_record(record_id):
    try:
        result = ItemService.archive_record(
            record_id=record_id,
            current_user_id=current_user.agent_id,
            current_user_role=current_user.role
        )
        
        if result['success']:
            return jsonify({'message': '记录已归档'})
        else:
            return jsonify({'message': result['message']}), 400
            
    except Exception as e:
        return jsonify({'message': f'归档失败: {str(e)}'}), 500

@api_bp.route('/found-items/<int:record_id>', methods=['DELETE'])
@login_required
def delete_record(record_id):
    try:
        result = ItemService.delete_record(
            record_id=record_id,
            current_user_id=current_user.agent_id,
            current_user_role=current_user.role
        )
        
        if result['success']:
            return jsonify({'message': '记录已删除'})
        else:
            return jsonify({'message': result['message']}), 400
            
    except Exception as e:
        return jsonify({'message': f'删除失败: {str(e)}'}), 500

@api_bp.route('/archived-items/<int:archived_id>/restore', methods=['POST'])
@login_required
def restore_archived_record(archived_id):
    try:
        result = ItemService.restore_archived_record(
            archived_id=archived_id,
            current_user_id=current_user.agent_id,
            current_user_role=current_user.role
        )
        
        if result['success']:
            return jsonify({'message': '记录已恢复'})
        else:
            return jsonify({'message': result['message']}), 400
            
    except Exception as e:
        return jsonify({'message': f'恢复失败: {str(e)}'}), 500

# 地图相关API
@api_bp.route('/map/records', methods=['GET'])
@login_required
def get_map_records():
    """获取地图上的所有记录点"""
    try:
        result = ItemService.get_records_with_location()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取地图数据失败: {str(e)}'})

@api_bp.route('/map/geocode', methods=['POST'])
def geocode_address():
    """地理编码：将地址转换为坐标"""
    try:
        data = request.get_json()
        address = data.get('address')
        
        if not address:
            return jsonify({'success': False, 'message': '地址不能为空'})
        
        result = MapService.geocode_address(address)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': f'地理编码失败: {str(e)}'})

@api_bp.route('/map/reverse-geocode', methods=['POST'])
def reverse_geocode():
    """逆地理编码：将坐标转换为地址 - 发布页面需要使用，不需要登录"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not latitude or not longitude:
            return jsonify({'success': False, 'message': '坐标不能为空'})
        
        # 验证坐标有效性
        is_valid, message = MapService.validate_coordinates(latitude, longitude)
        if not is_valid:
            return jsonify({'success': False, 'message': message})
        
        result = MapService.reverse_geocode(latitude, longitude)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': f'逆地理编码失败: {str(e)}'})

@api_bp.route('/map/nearby', methods=['POST'])
@login_required
def get_nearby_records():
    """获取附近的拾获记录"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        radius = data.get('radius', 10)  # 默认10公里
        
        if not latitude or not longitude:
            return jsonify({'success': False, 'message': '坐标不能为空'})
        
        # 验证坐标有效性
        is_valid, message = MapService.validate_coordinates(latitude, longitude)
        if not is_valid:
            return jsonify({'success': False, 'message': message})
        
        result = MapService.get_nearby_records(float(latitude), float(longitude), float(radius))
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': f'搜索附近记录失败: {str(e)}'})