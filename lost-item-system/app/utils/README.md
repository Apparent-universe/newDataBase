# 工具函数模块 (Utilities)

提供通用的工具函数和辅助方法，支持其他模块的功能实现。

## 📁 模块结构

```
utils/
├── __init__.py          # 工具模块初始化
└── helpers.py           # 辅助函数集合
```

## 🔧 工具函数

### 数据验证
```python
def validate_email(email)          # 邮箱格式验证
def validate_phone(phone)          # 手机号验证
def validate_coordinates(lat, lng) # 坐标有效性验证
```

### 数据格式化
```python
def format_datetime(dt)            # 日期时间格式化
def format_distance(distance)      # 距离格式化
def format_currency(amount)        # 金额格式化
```

### 文件处理
```python
def allowed_file(filename)         # 文件类型检查
def secure_filename(filename)      # 安全文件名生成
def get_file_extension(filename)   # 获取文件扩展名
```

### 加密解密
```python
def generate_token()               # 生成随机token
def hash_password(password)        # 密码哈希
def verify_password(password, hash) # 密码验证
```

## 📊 数据转换

### 地理计算
```python
def calculate_distance(lat1, lng1, lat2, lng2)  # 计算两点距离
def is_within_radius(center, point, radius)     # 判断是否在半径内
```

### JSON序列化
```python
def to_json(obj)                   # 对象转JSON
def from_json(json_str)            # JSON转对象
```

## 🛡 安全函数

### 输入清理
```python
def sanitize_input(text)           # 清理用户输入
def escape_html(text)              # HTML转义
```

### 权限检查
```python
def check_permission(user, action) # 权限验证
def is_admin(user)                 # 管理员检查
```

## 📝 使用示例

```python
from app.utils.helpers import validate_email, format_datetime

# 验证邮箱
if validate_email(user_email):
    print("邮箱格式正确")

# 格式化时间
formatted_time = format_datetime(datetime.now())
```