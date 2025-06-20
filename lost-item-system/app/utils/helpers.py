from datetime import datetime

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
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        
        if max_size is None:
            max_size = 2 * 1024 * 1024  # 2MB
        
        if not file or not file.filename:
            return {'valid': False, 'message': '请选择文件'}
        
        # 检查文件扩展名
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            return {'valid': False, 'message': f'文件格式不支持，支持的格式：{", ".join(allowed_extensions)}'}
        
        # 检查文件大小（这里只是示例，实际可能需要读取文件内容）
        # if hasattr(file, 'content_length') and file.content_length > max_size:
        #     return {'valid': False, 'message': f'文件大小不能超过{max_size // (1024*1024)}MB'}
        
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