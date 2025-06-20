from app import db
from app.models import Agent

class AuthService:
    """用户认证服务"""
    
    @staticmethod
    def register_user(username, password, contact):
        """注册新用户"""
        try:
            # 检查用户名是否已存在
            if Agent.query.filter_by(username=username).first():
                return {'success': False, 'message': '用户名已存在'}
            
            # 创建新用户
            agent = Agent(
                username=username,
                contact=contact
            )
            agent.set_password(password)
            
            # 如果是第一个用户，设为管理员
            if Agent.query.count() == 0:
                agent.role = 'admin'
            
            db.session.add(agent)
            db.session.commit()
            
            return {'success': True, 'user': agent}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'注册失败: {str(e)}'}
    
    @staticmethod
    def login_user(username, password):
        """用户登录验证"""
        try:
            agent = Agent.query.filter_by(username=username).first()
            
            if not agent:
                return {'success': False, 'message': '用户名不存在'}
            
            if not agent.check_password(password):
                return {'success': False, 'message': '密码错误'}
                
            if agent.status == 0:
                return {'success': False, 'message': '账号已被封禁'}
            
            return {'success': True, 'user': agent}
            
        except Exception as e:
            return {'success': False, 'message': f'登录失败: {str(e)}'}