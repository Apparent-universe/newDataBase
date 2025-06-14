import os
import sys

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app, db
from flask_login import LoginManager
from app.models import Agent

app = create_app()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'
login_manager.login_message = '请先登录'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Agent, int(user_id))

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("数据库表创建成功!")
        except Exception as e:
            print(f"数据库初始化错误: {e}")
    app.run(debug=True, host='127.0.0.1', port=5000)