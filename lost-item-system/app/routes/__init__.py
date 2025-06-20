# routes包初始化文件
from .main_routes import main_bp
from .auth_routes import auth_bp
from .item_routes import item_bp
from .user_routes import user_bp

__all__ = ['main_bp', 'auth_bp', 'item_bp', 'user_bp']