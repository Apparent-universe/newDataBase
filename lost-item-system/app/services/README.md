# 业务服务模块 (Business Services)

封装业务逻辑，提供可复用的服务接口，实现数据处理和业务规则。

## 📁 模块结构

```
services/
├── __init__.py          # 服务模块初始化
├── auth_service.py      # 认证服务
├── item_service.py      # 物品管理服务
├── map_service.py       # 地图服务
├── reward_service.py    # 打赏服务
└── user_service.py      # 用户服务
```

## 🔧 服务组件

### 认证服务 (`auth_service.py`)
```python
class AuthService:
    @staticmethod
    def login_user(username, password)
    @staticmethod
    def register_user(username, password, contact)
    @staticmethod
    def logout_user()
```

### 物品管理服务 (`item_service.py`)
```python
class ItemService:
    @staticmethod
    def publish_item(agent_id, location, description, items, ...)
    @staticmethod
    def search_items(keyword, location, record_id)
    @staticmethod
    def archive_record(record_id, user_id, role)
    @staticmethod
    def delete_record(record_id, user_id, role)
    @staticmethod
    def restore_archived_record(archived_id, user_id, role)
```

### 地图服务 (`map_service.py`)
```python
class MapService:
    @staticmethod
    def geocode_address(address)
    @staticmethod
    def reverse_geocode(longitude, latitude)
    @staticmethod
    def search_nearby_records(lat, lng, radius)
```

### 打赏服务 (`reward_service.py`)
```python
class RewardService:
    @staticmethod
    def create_reward(record_id, amount)
    @staticmethod
    def get_user_rewards(agent_id)
    @staticmethod
    def get_total_rewards(agent_id)
```

### 用户服务 (`user_service.py`)
```python
class UserService:
    @staticmethod
    def update_profile(agent_id, contact, free_time, personal_info)
    @staticmethod
    def upload_qrcode(agent_id, file_data, mimetype)
    @staticmethod
    def get_user_statistics(agent_id)
```

## 🎯 设计原则

### 单一职责
每个服务类只负责特定的业务领域，职责明确。

### 静态方法
使用静态方法，无需实例化，便于调用。

### 事务管理
在服务层处理数据库事务，确保数据一致性。

### 错误处理
统一的错误处理和返回格式：
```python
return {
    'success': True/False,
    'data': ...,
    'message': '操作结果描述'
}
```

## 🔄 调用流程

```
Controller (路由) 
    ↓
Service (业务逻辑)
    ↓
Model (数据操作)
    ↓
Database (数据存储)
```

## 📊 数据处理

### 地理位置处理
- 坐标验证和转换
- 地址格式化
- 距离计算

### 归档管理
- 自动归档检查
- 数据迁移
- 恢复机制

### 统计计算
- 用户记录统计
- 打赏金额汇总
- 性能指标计算