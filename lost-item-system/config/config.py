class Config:
    # 数据库配置
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'SU20031203su'
    MYSQL_DB = 'loss_system'
    
    # Flask配置
    SECRET_KEY = 'dev'
    
    # 上传文件配置
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 限制文件大小为16MB