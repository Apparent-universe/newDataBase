from app import db
from app.models import Reward

class RewardService:
    """打赏服务"""
    
    @staticmethod
    def create_reward(record_id, amount):
        """创建打赏记录"""
        try:
            if amount <= 0:
                return {'success': False, 'message': '打赏金额必须大于0'}
            
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