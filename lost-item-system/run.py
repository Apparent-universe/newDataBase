import os
import sys

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 验证配置
    print("=== 失物招领系统启动 ===")
    print(f"当前环境: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"数据库: {app.config['MYSQL_DB']}")
    print(f"高德地图Web服务密钥: {app.config['AMAP_WEB_SERVICE_KEY'][:10]}...")
    print(f"高德地图JS密钥: {app.config['AMAP_JS_API_KEY'][:10]}...")
    
    # 检查是否有SSL证书文件
    cert_file = 'cert.pem'
    key_file = 'key.pem'
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("⚠️  使用HTTPS模式启动（支持地理定位）")
        print(f"系统运行在: https://192.168.31.133:5050")
        print(f"发布页面: https://192.168.31.133:5050/items/publish")
        print("========================")
        
        # 启动HTTPS应用
        app.run(debug=True, host='0.0.0.0', port=5050, ssl_context=(cert_file, key_file))
    else:
        print("⚠️  HTTP模式启动（局域网访问时定位功能受限）")
        print(f"本地访问（支持定位）: http://127.0.0.1:5050")
        print(f"局域网访问（定位受限）: http://192.168.31.133:5050")
        print(f"发布页面: http://127.0.0.1:5050/items/publish")
        print("💡 提示：要在局域网使用定位功能，请配置HTTPS证书")
        print("========================")
        
        # 启动HTTP应用
        app.run(debug=True, host='0.0.0.0', port=5050)