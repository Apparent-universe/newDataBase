# Web路由模块 (Web Routes)

处理所有Web页面请求，包括用户认证、页面渲染和表单处理。

## 📁 模块结构

```
routes/
├── __init__.py          # 路由模块初始化
├── auth_routes.py       # 认证相关路由
├── item_routes.py       # 物品管理路由
├── main_routes.py       # 主页面路由
└── user_routes.py       # 用户管理路由
```

## 🌐 路由组织

### 认证路由 (`auth_routes.py`)
- `/auth/login` - 用户登录页面
- `/auth/register` - 用户注册页面
- `/auth/logout` - 用户登出

### 主页面路由 (`main_routes.py`)
- `/` - 系统首页
- `/about` - 关于页面

### 物品管理路由 (`item_routes.py`)
- `/items/search` - 物品搜索页面
- `/items/publish` - 发布物品页面
- `/items/edit/<id>` - 编辑记录页面
- `/items/archived` - 归档记录页面
- `/items/record-map/<id>` - 单个记录地图页面
- `/map` - 地图搜索页面

### 用户管理路由 (`user_routes.py`)
- `/profile` - 个人中心页面
- `/users/qrcode/<agent_id>` - 微信二维码接口

## 🔒 权限控制

### 登录保护装饰器
```python
from flask_login import login_required

@bp.route('/protected')
@login_required
def protected_page():
    return render_template('protected.html')
```

### 权限检查
- 用户只能编辑自己的记录
- 管理员可以管理所有记录
- 归档记录的访问控制

## 📝 表单处理

### 表单验证
- 服务器端验证
- 错误信息展示
- 数据清理和转换

### 文件上传
- 微信二维码图片上传
- 文件类型验证
- 文件大小限制

## 🎨 模板渲染

### 上下文数据
- 用户信息注入
- 权限状态传递
- 配置参数共享

### 错误处理
- 404页面处理
- 500错误页面
- 友好错误提示