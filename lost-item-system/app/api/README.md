# API模块 (REST API)

提供RESTful API接口，支持前端JavaScript和移动应用调用。

## 📋 API概览

### 地图相关API
- **GET** `/api/map/records` - 获取所有地图记录
- **POST** `/api/map/geocode` - 地理编码（地址转坐标）
- **POST** `/api/map/reverse-geocode` - 逆地理编码（坐标转地址）
- **POST** `/api/map/nearby` - 搜索附近记录

### 打赏相关API
- **POST** `/api/found-items/{id}/reward` - 创建打赏记录

## 🔧 使用示例

### 获取地图记录
```javascript
fetch('/api/map/records')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('记录数量:', data.records.length);
    }
  });
```

### 逆地理编码
```javascript
fetch('/api/map/reverse-geocode', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    longitude: 116.397428,
    latitude: 39.90923
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('地址:', data.data.formatted_address);
  }
});
```

## 📊 响应格式

### 标准响应结构
```json
{
  "success": true,
  "data": {...},
  "message": "操作成功",
  "timestamp": "2024-06-21T10:30:00Z"
}
```

### 错误响应
```json
{
  "success": false,
  "error": "错误类型",
  "message": "详细错误信息",
  "timestamp": "2024-06-21T10:30:00Z"
}
```

## 🛡 安全机制

- 登录状态验证
- 权限检查
- 输入参数验证
- 错误信息过滤