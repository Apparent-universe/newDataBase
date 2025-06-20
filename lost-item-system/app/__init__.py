import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import pymysql

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 设置PyMySQL为MySQLdb的替代
pymysql.install_as_MySQLdb()

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name=None):
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # 动态选择配置
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from config.config import config
    config_class = config.get(config_name, config['default'])
    app.config.from_object(config_class)
    
    # 验证配置合理性
    try:
        config_class.validate_config()
    except ValueError as e:
        print(f"配置验证失败: {e}")
        raise
    
    # 优化数据库配置，使用配置文件中的连接池参数
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{app.config['MYSQL_USER']}:{app.config['MYSQL_PASSWORD']}"

        f"@{app.config['MYSQL_HOST']}/{app.config['MYSQL_DB']}?charset=utf8mb4"
        f"&autocommit=true&connect_timeout=10&read_timeout=10&write_timeout=10"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': app.config.get('DB_POOL_SIZE', 5),
        'pool_timeout': app.config.get('DB_POOL_TIMEOUT', 20),
        'pool_recycle': app.config.get('DB_POOL_RECYCLE', 3600),
        'max_overflow': app.config.get('DB_MAX_OVERFLOW', 10),
        'pool_pre_ping': True
    }
    
    # 确保上传文件夹存在
    uploads_dir = os.path.join(app.static_folder, 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir, exist_ok=True)
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    login_manager.login_message_category = 'info'
    
    # 初始化地图服务API密钥和安全密钥
    from app.services.map_service import MapService
    MapService.set_api_credentials(
        app.config['AMAP_WEB_SERVICE_KEY'], 
        app.config.get('AMAP_SECURITY_CODE')
    )
    
    # 注册蓝图
    from app.routes.main_routes import main_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.item_routes import item_bp
    from app.routes.user_routes import user_bp
    from app.api.api_routes import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(item_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(api_bp)
    
    print("所有蓝图注册完成!")
    
    # 用户加载回调
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Agent
        return Agent.query.get(int(user_id))
    
    # 创建数据库表
    with app.app_context():
        from app.models import Agent, FoundRecord, FoundItem, Reward, FoundHistory, ArchivedRecord, ArchivedItem
        try:
            db.create_all()
            print("数据库表检查/创建成功!")
            
            # 验证配置
            config[config_name].validate_config()
            print(f"当前配置环境: {config_name}")
            print(f"自动归档天数: {app.config['AUTO_ARCHIVE_DAYS']}天")
            print(f"搜索结果限制: {app.config['SEARCH_RESULTS_LIMIT']}条")
        except Exception as e:
            print(f"数据库初始化失败: {e}")
        
    return app