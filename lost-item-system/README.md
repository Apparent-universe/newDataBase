# 失物招领系统 (Lost Item System)

一个基于Flask的现代化失物招领管理系统，支持地理定位、地图展示、打赏功能等。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.0+-purple.svg)

## 📋 目录

- [功能特性](#-功能特性)
- [技术栈](#-技术栈)
- [系统架构](#-系统架构)
- [安装部署](#-安装部署)
- [使用指南](#-使用指南)
- [API文档](#-api文档)
- [开发指南](#-开发指南)
- [项目结构](#-项目结构)
- [配置说明](#-配置说明)
- [常见问题](#-常见问题)
- [更新日志](#-更新日志)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

## 🚀 功能特性

### 核心功能
- **物品发布**：用户可以发布拾获的物品信息
- **智能搜索**：支持物品名称、地点关键词搜索
- **地理定位**：集成高德地图，支持精确定位和地图展示
- **用户管理**：完整的用户注册、登录、个人资料管理
- **打赏系统**：支持对帮助找回物品的用户进行打赏

### 高级功能
- **地图可视化**：在地图上查看所有拾获物品的分布
- **附近搜索**：基于地理位置搜索附近的拾获记录
- **记录归档**：自动和手动归档过期记录
- **移动端适配**：响应式设计，完美支持手机端
- **安全认证**：HTTPS支持，数据传输加密

### 管理功能
- **权限控制**：用户和管理员角色管理
- **数据统计**：发布记录、打赏统计
- **记录管理**：编辑、删除、归档记录
- **微信集成**：支持微信二维码展示

## 🛠 技术栈

### 后端技术
- **框架**：Flask 2.0+
- **数据库**：MySQL 8.0+
- **ORM**：SQLAlchemy
- **认证**：Flask-Login
- **密码加密**：Werkzeug Security

### 前端技术
- **UI框架**：Bootstrap 5.0+
- **地图服务**：高德地图 API
- **图标库**：Font Awesome
- **JavaScript**：原生ES6+

### 开发工具
- **包管理**：pip
- **版本控制**：Git
- **SSL证书**：自签名证书生成
- **配置管理**：多环境配置支持

## 🏗 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面      │    │    Flask应用    │    │   MySQL数据库   │
│  (Bootstrap)    │◄──►│   (RESTful)     │◄──►│   (关系型)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐             │
         │              │   高德地图API    │             │
         └──────────────►│   (地理定位)    │             │
                        └─────────────────┘             │
                                 │                      │
                        ┌─────────────────┐             │
                        │   文件存储      │◄────────────┘
                        │ (图片/附件)     │
                        └─────────────────┘
```

## 📦 安装部署

### 环境要求
- Python 3.8+
- MySQL 8.0+
- pip (Python包管理器)

### 快速开始

1. **克隆项目**
```bash
git clone <repository-url>
cd lost-item-system
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置数据库**
```bash
# 创建MySQL数据库
mysql -u root -p
CREATE DATABASE lost_item_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. **配置环境变量**
```bash
# 复制配置文件并修改
cp config/config.py.example config/config.py
# 编辑配置文件，填入数据库连接信息和API密钥
```

5. **生成SSL证书**（可选，用于HTTPS）
```bash
python generate_ssl_cert.py
```

6. **更新数据库结构**
```bash
python update_database.py
```

7. **启动应用**
```bash
python run.py
```

8. **访问应用**
- HTTP: http://localhost:5050
- HTTPS: https://localhost:5050

### Docker部署（推荐）

```bash
# 使用Docker Compose
docker-compose up -d
```

## 📖 使用指南

### 用户操作

#### 注册和登录
1. 访问系统首页
2. 点击"注册"创建新账户
3. 填写用户名、密码和联系方式
4. 登录系统开始使用

#### 发布拾获物品
1. 登录后点击"发布物品"
2. 填写拾获地点和详细描述
3. 添加拾获的物品清单
4. 选择地图位置（可选）
5. 提交发布

#### 搜索物品
1. 在首页搜索框输入关键词
2. 可按物品名称或地点搜索
3. 查看搜索结果详情
4. 联系拾获者或进行打赏

#### 地图功能
1. 点击"地图搜索"查看所有标记
2. 点击标记查看详细信息
3. 使用定位功能查找附近记录

### 管理员操作
- 用户管理：查看和管理所有用户
- 记录管理：审核、编辑、删除记录
- 系统配置：修改系统参数

## 📡 API文档

### 认证相关
```
POST /auth/login          # 用户登录
POST /auth/register       # 用户注册
POST /auth/logout         # 用户登出
```

### 物品管理
```
GET  /items/search        # 搜索物品
POST /items/publish       # 发布物品
PUT  /items/update/{id}   # 更新记录
DELETE /items/{id}        # 删除记录
```

### 地图功能
```
GET  /api/map/records            # 获取地图记录
POST /api/map/geocode           # 地理编码
POST /api/map/reverse-geocode   # 逆地理编码
POST /api/map/nearby            # 附近搜索
```

### 打赏系统
```
POST /api/found-items/{id}/reward  # 创建打赏
```

详细API文档请参考：[API Documentation](docs/api.md)

## 👨‍💻 开发指南

### 本地开发环境设置

1. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

2. **安装开发依赖**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

3. **配置开发环境**
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
```

### 代码规范
- 遵循PEP 8规范
- 使用类型注解
- 编写单元测试
- 提交前运行代码检查

### 测试
```bash
# 运行所有测试
python -m pytest

# 运行特定测试
python -m pytest tests/test_auth.py

# 生成覆盖率报告
python -m pytest --cov=app
```

## 📁 项目结构

```
lost-item-system/
├── app/                    # 应用主目录
│   ├── __init__.py        # 应用初始化
│   ├── models.py          # 数据模型
│   ├── api/               # API路由
│   ├── routes/            # Web路由
│   ├── services/          # 业务逻辑
│   └── utils/             # 工具函数
├── config/                # 配置文件
├── static/                # 静态资源
│   ├── css/              # 样式文件
│   ├── js/               # JavaScript文件
│   └── images/           # 图片资源
├── templates/             # HTML模板
├── tests/                 # 测试文件
├── docs/                  # 文档
├── requirements.txt       # 依赖包列表
├── run.py                # 应用启动文件
└── README.md             # 项目说明
```

详细结构说明请参考各模块的README文档。

## ⚙️ 配置说明

### 数据库配置
```python
# config/config.py
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'your_password'
MYSQL_DB = 'lost_item_system'
```

### 地图API配置
```python
# 高德地图API密钥
AMAP_WEB_SERVICE_KEY = 'your_web_service_key'
AMAP_JS_API_KEY = 'your_js_api_key'
AMAP_SECURITY_CODE = 'your_security_code'  # 可选
```

### 系统配置
```python
# 自动归档天数
AUTO_ARCHIVE_DAYS = 14

# 搜索结果限制
SEARCH_RESULTS_LIMIT = 20

# 数据库连接池配置
DB_POOL_SIZE = 5
DB_POOL_TIMEOUT = 20
```

完整配置说明请参考：[配置文档](config/README.md)

## ❓ 常见问题

### Q: 如何配置HTTPS？
A: 运行 `python generate_ssl_cert.py` 生成自签名证书，系统会自动启用HTTPS。

### Q: 地图定位不工作怎么办？
A: 确保配置了正确的高德地图API密钥，并且在HTTPS环境下使用。

### Q: 如何备份数据库？
A: 使用MySQL导出功能：`mysqldump -u root -p lost_item_system > backup.sql`

### Q: 忘记管理员密码怎么办？
A: 可以通过数据库直接重置或使用提供的重置脚本。

更多问题请查看：[FAQ文档](docs/faq.md)

## 📝 更新日志

### v1.2.0 (2024-06-21)
- ✨ 新增地理定位功能
- ✨ 集成高德地图API
- ✨ 支持移动端定位
- 🐛 修复地图标记定位问题
- 📈 优化数据库查询性能

### v1.1.0 (2024-06-15)
- ✨ 新增打赏功能
- ✨ 支持微信二维码
- 🎨 UI界面优化
- 🐛 修复若干Bug

### v1.0.0 (2024-06-01)
- 🎉 项目正式发布
- ✨ 基础功能完成
- 📱 移动端适配

完整更新日志请查看：[CHANGELOG.md](CHANGELOG.md)

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献
1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 贡献类型
- 🐛 Bug修复
- ✨ 新功能开发
- 📝 文档改进
- 🎨 UI/UX改进
- ⚡ 性能优化

请确保您的代码符合项目的编码规范。

## 📄 许可证

本项目采用 MIT 许可证。详细信息请查看 [LICENSE](LICENSE) 文件。

## 📞 联系我们

- 📧 邮箱：[your-email@example.com]
- 🐛 问题反馈：[GitHub Issues]
- 📖 文档：[项目Wiki]

---

⭐ 如果这个项目对您有帮助，请给我们一个Star！

[![GitHub stars](https://img.shields.io/github/stars/username/lost-item-system.svg?style=social&label=Star)](https://github.com/username/lost-item-system)