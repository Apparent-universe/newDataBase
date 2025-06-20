from app import db
from app.models import Reward
from app.utils.helpers import ValidationUtils

class RewardService:
    """打赏服务"""
    
    @staticmethod
    def create_reward(record_id, amount):
        """创建打赏记录"""
        try:
            # 使用工具类验证打赏金额，而不是硬编码
            validation_result = ValidationUtils.validate_reward_amount(amount)
            if not validation_result['valid']:
                return {'success': False, 'message': validation_result['message']}
            
            reward = Reward(
                record_id=record_id,
                reward_amount=amount
            )
            
            db.session.add(reward)
            db.session.commit()
            
            return {'success': True, 'reward': reward}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'打赏失败: {str(e)}'}