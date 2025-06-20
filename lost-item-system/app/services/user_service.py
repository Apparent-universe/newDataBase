from app import db
from app.models import FoundRecord, ArchivedRecord, Reward

class UserService:
    """用户管理服务"""
    
    @staticmethod
    def update_profile(user, contact=None, free_time=None, personal_info=None, wx_qrcode_file=None):
        """更新用户资料"""
        try:
            if contact is not None:
                user.contact = contact
            if free_time is not None:
                user.free_time = free_time
            if personal_info is not None:
                user.personal_info = personal_info
            
            # 处理微信二维码文件 - 改进版本
            if wx_qrcode_file is not None:
                try:
                    # 确保文件指针在开头
                    wx_qrcode_file.seek(0)
                    
                    # 读取文件数据
                    file_data = wx_qrcode_file.read()
                    
                    # 验证文件数据不为空
                    if not file_data or len(file_data) == 0:
                        return {'success': False, 'message': '文件内容为空，请重新选择文件'}
                    
                    # 获取MIME类型
                    mimetype = wx_qrcode_file.mimetype
                    if not mimetype:
                        # 根据文件扩展名推断MIME类型
                        filename = wx_qrcode_file.filename.lower()
                        if filename.endswith('.png'):
                            mimetype = 'image/png'
                        elif filename.endswith(('.jpg', '.jpeg')):
                            mimetype = 'image/jpeg'
                        elif filename.endswith('.gif'):
                            mimetype = 'image/gif'
                        else:
                            mimetype = 'image/jpeg'  # 默认值
                    
                    # 设置二维码数据
                    user.set_wx_qrcode(file_data, mimetype)
                    
                    print(f"Debug: 更新用户 {user.username} 的二维码，文件大小: {len(file_data)} bytes, MIME类型: {mimetype}")
                    
                except Exception as file_error:
                    return {'success': False, 'message': f'处理文件时出错: {str(file_error)}'}
            
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
    
    @staticmethod
    def update_profile_with_data(user, contact=None, free_time=None, personal_info=None, wx_qrcode_data=None, wx_qrcode_mimetype=None):
        """更新用户资料 - 使用预读取的文件数据"""
        try:
            if contact is not None:
                user.contact = contact
            if free_time is not None:
                user.free_time = free_time
            if personal_info is not None:
                user.personal_info = personal_info
            
            # 处理微信二维码数据 - 直接使用传入的数据
            if wx_qrcode_data is not None:
                if not wx_qrcode_data or len(wx_qrcode_data) == 0:
                    return {'success': False, 'message': '二维码数据为空'}
                
                # 设置二维码数据
                user.set_wx_qrcode(wx_qrcode_data, wx_qrcode_mimetype)
                print(f"Debug: 服务层设置二维码成功，数据大小: {len(wx_qrcode_data)} bytes")
            
            db.session.commit()
            return {'success': True}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'更新失败: {str(e)}'}