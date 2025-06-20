import os
from datetime import timedelta

class Config:
    # 数据库配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'SU20031203su')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'loss_system')
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    
    # 上传文件配置
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 限制文件大小为16MB
    
    # 文件验证配置
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB
    
    # 业务逻辑配置
    # 自动归档配置
    AUTO_ARCHIVE_DAYS = int(os.environ.get('AUTO_ARCHIVE_DAYS', '14'))  # 超过14天自动归档
    
    # 搜索和分页配置
    SEARCH_RESULTS_LIMIT = int(os.environ.get('SEARCH_RESULTS_LIMIT', '20'))  # 搜索结果最大数量
    HOME_PAGE_ITEMS_LIMIT = int(os.environ.get('HOME_PAGE_ITEMS_LIMIT', '6'))  # 首页显示的最新物品数量
    
    # 用户验证配置
    USERNAME_MIN_LENGTH = int(os.environ.get('USERNAME_MIN_LENGTH', '3'))
    USERNAME_MAX_LENGTH = int(os.environ.get('USERNAME_MAX_LENGTH', '20'))
    PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', '6'))
    
    # 打赏配置
    MIN_REWARD_AMOUNT = float(os.environ.get('MIN_REWARD_AMOUNT', '0.01'))  # 最小打赏金额
    MAX_REWARD_AMOUNT = float(os.environ.get('MAX_REWARD_AMOUNT', '10000.00'))  # 最大打赏金额
    
    # 描述文本长度配置
    MAX_DESCRIPTION_LENGTH = int(os.environ.get('MAX_DESCRIPTION_LENGTH', '1000'))
    MAX_HIDDEN_INFO_LENGTH = int(os.environ.get('MAX_HIDDEN_INFO_LENGTH', '500'))
    MAX_LOCATION_LENGTH = int(os.environ.get('MAX_LOCATION_LENGTH', '100'))
    MAX_ITEM_NAME_LENGTH = int(os.environ.get('MAX_ITEM_NAME_LENGTH', '50'))
    
    # 联系信息配置
    MAX_CONTACT_LENGTH = int(os.environ.get('MAX_CONTACT_LENGTH', '100'))
    MAX_FREE_TIME_LENGTH = int(os.environ.get('MAX_FREE_TIME_LENGTH', '100'))
    MAX_PERSONAL_INFO_LENGTH = int(os.environ.get('MAX_PERSONAL_INFO_LENGTH', '500'))
    
    # 系统行为配置
    AUTO_REFRESH_DELAY = int(os.environ.get('AUTO_REFRESH_DELAY', '1500'))  # 操作成功后自动刷新延迟(毫秒)
    SUCCESS_MESSAGE_DURATION = int(os.environ.get('SUCCESS_MESSAGE_DURATION', '3000'))  # 成功消息显示时长(毫秒)
    
    # 数据库连接池配置
    DB_POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', '5'))
    DB_POOL_TIMEOUT = int(os.environ.get('DB_POOL_TIMEOUT', '20'))
    DB_POOL_RECYCLE = int(os.environ.get('DB_POOL_RECYCLE', '3600'))
    DB_MAX_OVERFLOW = int(os.environ.get('DB_MAX_OVERFLOW', '10'))
    
    # 高德地图配置 - 支持分离的API密钥
    AMAP_WEB_SERVICE_KEY = os.environ.get('AMAP_WEB_SERVICE_KEY', '7a17809022b1c1fd130bb0dbc11b8cd5')  # Web服务API密钥（后端用）
    AMAP_JS_API_KEY = os.environ.get('AMAP_JS_API_KEY', '8eab57b8c12c66104c1776924242f945')  # JS API密钥（前端用）
    AMAP_SECURITY_CODE = os.environ.get('AMAP_SECURITY_CODE', '90bbadc2211f93cb8c4fb71eb676acfe')  # 安全密钥
    
    # 向后兼容 - 如果没有设置分离的密钥，使用通用密钥
    @property
    def AMAP_API_KEY(self):
        """向后兼容的API密钥属性"""
        return self.AMAP_WEB_SERVICE_KEY
    
    @classmethod
    def get_auto_archive_timedelta(cls):
        """获取自动归档时间间隔"""
        return timedelta(days=cls.AUTO_ARCHIVE_DAYS)
    
    @classmethod
    def validate_config(cls):
        """验证配置合理性"""
        errors = []
        
        if cls.AUTO_ARCHIVE_DAYS <= 0:
            errors.append("AUTO_ARCHIVE_DAYS必须大于0")
        
        if cls.MIN_REWARD_AMOUNT <= 0:
            errors.append("MIN_REWARD_AMOUNT必须大于0")
            
        if cls.MAX_REWARD_AMOUNT <= cls.MIN_REWARD_AMOUNT:
            errors.append("MAX_REWARD_AMOUNT必须大于MIN_REWARD_AMOUNT")
            
        if cls.USERNAME_MIN_LENGTH >= cls.USERNAME_MAX_LENGTH:
            errors.append("USERNAME_MIN_LENGTH必须小于USERNAME_MAX_LENGTH")
            
        if errors:
            raise ValueError(f"配置错误: {'; '.join(errors)}")
        
        return True


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    AUTO_ARCHIVE_DAYS = 7  # 开发环境缩短自动归档时间


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')  # 生产环境必须设置
    
    # 生产环境更严格的配置
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 生产环境限制为8MB
    MAX_IMAGE_SIZE = 1 * 1024 * 1024  # 生产环境限制为1MB


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    MYSQL_DB = 'loss_system_test'
    AUTO_ARCHIVE_DAYS = 1  # 测试环境1天归档


# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}