from datetime import datetime
from flask import current_app

class DateUtils:
    """日期时间工具类"""
    
    @staticmethod
    def format_datetime(dt, format_str='%Y-%m-%d %H:%M'):
        """格式化日期时间"""
        if dt is None:
            return ''
        return dt.strftime(format_str)
    
    @staticmethod
    def format_date(dt, format_str='%Y-%m-%d'):
        """格式化日期"""
        if dt is None:
            return ''
        return dt.strftime(format_str)

class ValidationUtils:
    """验证工具类"""
    
    @staticmethod
    def validate_file(file, allowed_extensions=None, max_size=None):
        """验证上传文件"""
        if allowed_extensions is None:
            # 使用配置文件中的允许扩展名
            allowed_extensions = current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})
        
        if max_size is None:
            # 使用配置文件中的最大文件大小
            max_size = current_app.config.get('MAX_IMAGE_SIZE', 2 * 1024 * 1024)
        
        if not file or not file.filename:
            return {'valid': False, 'message': '请选择文件'}
        
        # 检查文件扩展名
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            return {'valid': False, 'message': f'文件格式不支持，支持的格式：{", ".join(allowed_extensions)}'}
        
        # 重要：验证完成后重置文件指针到开头
        file.seek(0)
        return {'valid': True}
    
    @staticmethod
    def validate_text_length(text, field_name, max_length_config_key):
        """验证文本长度"""
        if not text:
            return {'valid': True}
        
        max_length = current_app.config.get(max_length_config_key, 1000)
        if len(text) > max_length:
            return {'valid': False, 'message': f'{field_name}不能超过{max_length}个字符'}
        
        return {'valid': True}
    
    @staticmethod
    def validate_username(username):
        """验证用户名"""
        if not username:
            return {'valid': False, 'message': '用户名不能为空'}
        
        min_length = current_app.config.get('USERNAME_MIN_LENGTH', 3)
        max_length = current_app.config.get('USERNAME_MAX_LENGTH', 20)
        
        if len(username) < min_length:
            return {'valid': False, 'message': f'用户名不能少于{min_length}个字符'}
        
        if len(username) > max_length:
            return {'valid': False, 'message': f'用户名不能超过{max_length}个字符'}
        
        return {'valid': True}
    
    @staticmethod
    def validate_reward_amount(amount):
        """验证打赏金额"""
        if amount is None:
            return {'valid': False, 'message': '打赏金额不能为空'}
        
        min_amount = current_app.config.get('MIN_REWARD_AMOUNT', 0.01)
        max_amount = current_app.config.get('MAX_REWARD_AMOUNT', 10000.00)
        
        if amount < min_amount:
            return {'valid': False, 'message': f'打赏金额不能少于{min_amount}元'}
        
        if amount > max_amount:
            return {'valid': False, 'message': f'打赏金额不能超过{max_amount}元'}
        
        return {'valid': True}

class ResponseUtils:
    """响应工具类"""
    
    @staticmethod
    def success_response(data=None, message='操作成功'):
        """成功响应"""
        result = {'success': True, 'message': message}
        if data is not None:
            result['data'] = data
        return result
    
    @staticmethod
    def error_response(message='操作失败', code=None):
        """错误响应"""
        result = {'success': False, 'message': message}
        if code is not None:
            result['code'] = code
        return result