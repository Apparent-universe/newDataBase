# 应用核心模块 (App Core)

失物招领系统的核心应用模块，包含数据模型、路由管理和应用初始化。

## 📁 模块结构

```
app/
├── __init__.py          # Flask应用工厂
├── models.py           # 数据模型定义
├── routes.py           # 路由集成
├── api/                # REST API模块
├── routes/             # Web页面路由
├── services/           # 业务逻辑服务
└── utils/              # 工具函数
```

## 🏗 核心组件

### Flask应用工厂 (`__init__.py`)
- 应用实例创建和配置
- 数据库初始化
- 登录管理器配置
- 蓝图注册

### 数据模型 (`models.py`)
- **Agent**: 用户/探员模型
- **FoundRecord**: 拾获记录模型
- **FoundItem**: 拾获物品模型
- **ArchivedRecord**: 归档记录模型
- **ArchivedItem**: 归档物品模型
- **Reward**: 打赏记录模型

### 路由集成 (`routes.py`)
- 统一路由管理
- 蓝图组织和注册

## 🔧 使用方式

### 创建应用实例
```python
from app import create_app

app = create_app()
```

### 数据模型使用
```python
from app.models import Agent, FoundRecord

# 创建新用户
user = Agent(username='test', contact='123456')
user.set_password('password')

# 创建拾获记录
record = FoundRecord(
    agent_id=user.agent_id,
    pickup_location='图书馆',
    detailed_description='拾获一个钱包'
)
```

## 📊 数据库设计

### 主要表关系
```
Agent (用户)
├── FoundRecord (活跃记录) 1:N
├── ArchivedRecord (归档记录) 1:N
└── Reward (打赏记录) 1:N

FoundRecord (拾获记录)
├── FoundItem (物品) 1:N
└── Reward (打赏) 1:N

ArchivedRecord (归档记录)
└── ArchivedItem (归档物品) 1:N
```

### 地理位置支持
- `latitude`: 纬度 (DECIMAL(10,8))
- `longitude`: 经度 (DECIMAL(11,8))
- `formatted_address`: 格式化地址

## 🔄 生命周期管理

### 记录归档流程
1. **自动归档**: 超过配置天数的记录自动归档
2. **手动归档**: 用户主动归档不需要的记录
3. **删除归档**: 删除的记录也会保存到归档表
4. **恢复功能**: 支持从归档表恢复记录

## 🛡 安全特性

- 密码哈希存储 (Werkzeug)
- SQL注入防护 (SQLAlchemy ORM)
- CSRF保护
- 会话管理

## 📈 性能优化

- 数据库连接池
- 查询优化 (selectinload)
- 索引设计
- 缓存策略