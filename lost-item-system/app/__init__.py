import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import pymysql

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

pymysql.install_as_MySQLdb()

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
                
    from config.config import Config
    app.config.from_object(Config)
    
    # 优化数据库配置
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}"
        f"@{Config.MYSQL_HOST}/{Config.MYSQL_DB}?charset=utf8mb4"
        f"&autocommit=true&connect_timeout=10&read_timeout=10&write_timeout=10"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 5,
        'pool_timeout': 20,
        'pool_recycle': 3600,
        'max_overflow': 10,
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
    
    # 注册蓝图 - MVC架构
    from app.routes import main_bp, auth_bp, item_bp, user_bp
    from app.api.api_routes import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(item_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(api_bp)
    
    # 使用app_context来创建表（替代before_first_request）
    with app.app_context():
        try:
            db.create_all()
            print("数据库表检查/创建成功!")
        except Exception as e:
            print(f"数据库初始化警告: {e}")
        
    return app