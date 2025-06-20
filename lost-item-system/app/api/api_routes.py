from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.item_service import ItemService
from app.services.reward_service import RewardService

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