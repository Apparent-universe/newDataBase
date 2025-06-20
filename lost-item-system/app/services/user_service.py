from app import db
from app.models import FoundRecord, ArchivedRecord, Reward

class UserService:
    """用户管理服务"""
    
    @staticmethod
    def update_profile(user, contact=None, free_time=None, personal_info=None, wx_qrcode=None):
        """更新用户资料"""
        try:
            if contact is not None:
                user.contact = contact
            if free_time is not None:
                user.free_time = free_time
            if personal_info is not None:
                user.personal_info = personal_info
            if wx_qrcode is not None:
                user.wx_qrcode = wx_qrcode
            
            db.session.commit()
            return {'success': True}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'更新失败: {str(e)}'}
    
    @staticmethod
    def get_user_stats(agent_id):
        """获取用户统计数据"""
        try:
            # 获取用户的发布记录
            my_records = FoundRecord.query.filter_by(agent_id=agent_id).order_by(
                FoundRecord.created_time.desc()
            ).all()
            records_count = len(my_records)
            
            # 获取归档记录数量（不包括删除的记录）
            archived_count = ArchivedRecord.query.filter(
                ArchivedRecord.agent_id == agent_id,
                ArchivedRecord.archive_reason != 'USER_DELETE'
            ).count()
            
            # 获取总打赏金额
            total_rewards = db.session.query(db.func.sum(Reward.reward_amount)).join(
                FoundRecord, Reward.record_id == FoundRecord.record_id
            ).filter(FoundRecord.agent_id == agent_id).scalar() or 0
            
            return {
                'success': True,
                'records': my_records,
                'records_count': records_count,
                'archived_count': archived_count,
                'total_rewards': total_rewards
            }
            
        except Exception as e:
            return {
                'success': False,
                'records': [],
                'records_count': 0,
                'archived_count': 0,
                'total_rewards': 0,
                'message': f'获取用户统计失败: {str(e)}'
            }