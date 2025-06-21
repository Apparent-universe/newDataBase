# 配置模块 (Configuration)

管理系统配置参数，支持多环境配置和敏感信息管理。

## 📁 模块结构

```
config/
├── config.py            # 主配置文件
└── README.md           # 配置说明文档
```

## ⚙️ 配置项说明

### 数据库配置
```python
# MySQL数据库连接配置
MYSQL_HOST = 'localhost'        # 数据库主机地址
MYSQL_USER = 'root'             # 数据库用户名
MYSQL_PASSWORD = 'password'     # 数据库密码
MYSQL_DB = 'lost_item_system'   # 数据库名称
MYSQL_PORT = 3306               # 数据库端口

# 数据库连接池配置
DB_POOL_SIZE = 5                # 连接池大小
DB_POOL_TIMEOUT = 20            # 连接超时时间(秒)
DB_POOL_RECYCLE = 3600          # 连接回收时间(秒)
```

### 高德地图API配置
```python
# 高德地图API密钥配置
AMAP_WEB_SERVICE_KEY = 'your_web_service_key'  # Web服务API密钥
AMAP_JS_API_KEY = 'your_js_api_key'            # JavaScript API密钥
AMAP_SECURITY_CODE = 'your_security_code'      # 安全密钥(可选)

# 地图配置参数
DEFAULT_MAP_CENTER = [116.397428, 39.90923]   # 默认地图中心(北京天安门)
DEFAULT_MAP_ZOOM = 13                          # 默认缩放级别
GEOCODING_TIMEOUT = 10                         # 地理编码超时时间(秒)
```

### 应用配置
```python
# Flask应用配置
SECRET_KEY = 'your-secret-key-here'            # 会话密钥
DEBUG = False                                  # 调试模式
TESTING = False                                # 测试模式

# 服务器配置
HOST = '0.0.0.0'                              # 监听地址
PORT = 5050                                    # 监听端口
THREADED = True                                # 多线程支持
```

### 业务配置
```python
# 归档管理配置
AUTO_ARCHIVE_DAYS = 14                         # 自动归档天数
ARCHIVE_BATCH_SIZE = 100                       # 批量归档大小

# 搜索配置
SEARCH_RESULTS_LIMIT = 20                      # 搜索结果限制
NEARBY_SEARCH_RADIUS = 10                      # 附近搜索默认半径(公里)

# 文件上传配置
MAX_CONTENT_LENGTH = 16 * 1024 * 1024         # 最大上传文件大小(16MB)
UPLOAD_FOLDER = 'static/uploads'               # 上传文件夹
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # 允许的文件扩展名
```

### 安全配置
```python
# 会话配置
PERMANENT_SESSION_LIFETIME = timedelta(days=7) # 会话有效期
SESSION_COOKIE_SECURE = True                   # HTTPS下的安全Cookie
SESSION_COOKIE_HTTPONLY = True                 # 防止XSS攻击

# 密码策略
MIN_PASSWORD_LENGTH = 6                        # 最小密码长度
REQUIRE_PASSWORD_COMPLEXITY = False            # 是否要求密码复杂度
```

## 🌍 环境配置

### 开发环境
```python
class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = 'localhost'
    # ...其他开发环境配置
```

### 生产环境
```python
class ProductionConfig(Config):
    DEBUG = False
    MYSQL_HOST = 'prod-db-server'
    # ...其他生产环境配置
```

### 测试环境
```python
class TestingConfig(Config):
    TESTING = True
    MYSQL_DB = 'test_lost_item_system'
    # ...其他测试环境配置
```

## 🔧 配置使用

### 加载配置
```python
from config.config import Config

app.config.from_object(Config)
```

### 获取配置值
```python
from flask import current_app

# 在应用上下文中获取配置
db_host = current_app.config['MYSQL_HOST']
api_key = current_app.config['AMAP_WEB_SERVICE_KEY']
```

## 🛡 安全注意事项

### 敏感信息保护
- 不要将密钥提交到版本控制系统
- 使用环境变量存储敏感配置
- 定期更换API密钥和密码

### 环境变量示例
```bash
# .env文件示例
MYSQL_PASSWORD=your_secure_password
AMAP_WEB_SERVICE_KEY=your_api_key
SECRET_KEY=your_secret_key
```

### 配置验证
```python
def validate_config():
    """验证必要的配置项是否存在"""
    required_configs = [
        'MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD',
        'AMAP_WEB_SERVICE_KEY', 'SECRET_KEY'
    ]
    
    for config_name in required_configs:
        if not current_app.config.get(config_name):
            raise ValueError(f"必需的配置项 {config_name} 未设置")
```

## 📝 配置最佳实践

1. **分离敏感配置**：将敏感信息放在环境变量中
2. **环境隔离**：为不同环境创建独立的配置
3. **配置验证**：启动时验证必需的配置项
4. **文档更新**：配置变更时及时更新文档
5. **版本管理**：配置文件的版本控制和变更记录