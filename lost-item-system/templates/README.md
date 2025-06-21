# 模板文件模块 (Templates)

管理系统的HTML模板文件，采用Jinja2模板引擎，支持模板继承和组件化开发。

## 📁 模块结构

```
templates/
├── base.html               # 基础模板
├── index.html              # 首页模板
├── auth/                   # 认证相关模板
│   ├── login.html         # 登录页面
│   └── register.html      # 注册页面
├── pages/                  # 主要页面模板
│   ├── archived.html      # 归档记录页面
│   ├── edit_record.html   # 编辑记录页面
│   ├── map.html           # 地图搜索页面
│   ├── profile.html       # 个人中心页面
│   ├── publish.html       # 发布物品页面
│   ├── record_map.html    # 单个记录地图页面
│   └── search.html        # 搜索结果页面
└── components/             # 组件模板
    └── archived_items.html # 归档物品组件
```

## 🏗 模板架构

### 基础模板 (base.html)
- **模板继承根**：所有页面模板的父模板
- **通用布局**：导航栏、页脚、基础样式
- **块定义**：title, extra_css, content, extra_js等
- **全局变量**：用户信息、配置参数

#### 主要块结构
```html
{% block title %}{% endblock %}          <!-- 页面标题 -->
{% block extra_css %}{% endblock %}     <!-- 额外CSS -->
{% block content %}{% endblock %}       <!-- 页面内容 -->
{% block extra_js %}{% endblock %}      <!-- 额外JavaScript -->
```

### 导航组件
```html
<!-- 主导航菜单 -->
<nav class="navbar navbar-expand-lg">
    <div class="container">
        <a class="navbar-brand" href="/">丢物小助手</a>
        <div class="navbar-nav">
            <a href="/items/search">搜索物品</a>
            <a href="/map">地图搜索</a>
            <a href="/items/publish">发布物品</a>
        </div>
    </div>
</nav>
```

## 📄 页面模板详解

### 认证模板 (auth/)

#### login.html - 登录页面
- **功能**：用户登录表单
- **验证**：前端表单验证
- **样式**：居中布局，响应式设计
- **跳转**：登录成功后重定向

#### register.html - 注册页面
- **功能**：用户注册表单
- **字段**：用户名、密码、联系方式
- **验证**：密码强度、字段格式检查
- **协议**：用户协议确认

### 主要页面模板 (pages/)

#### search.html - 搜索结果页面
```html
<!-- 搜索表单 -->
<form class="search-form">
    <input type="text" name="keyword" placeholder="输入物品名称或地点">
    <button type="submit">搜索</button>
</form>

<!-- 结果展示 -->
<div class="search-results">
    {% for record in records %}
        <div class="result-item">
            <!-- 记录信息展示 -->
        </div>
    {% endfor %}
</div>
```

#### map.html - 地图搜索页面
- **地图容器**：全屏地图显示
- **控制面板**：搜索半径、物品筛选
- **结果列表**：附近记录展示
- **定位按钮**：获取当前位置

#### publish.html - 发布物品页面
- **分步表单**：物品信息、位置选择
- **动态列表**：可添加多个物品
- **地图选点**：集成地图位置选择
- **表单验证**：实时输入验证

#### profile.html - 个人中心页面
- **个人信息**：用户资料编辑
- **统计信息**：发布记录、打赏统计
- **记录管理**：已发布记录的操作
- **二维码上传**：微信收款码管理

### 组件模板 (components/)

#### archived_items.html - 归档物品组件
```html
<!-- 可复用的归档记录展示组件 -->
<div class="archived-item">
    <div class="item-header">
        <h5>{{ record.pickup_location }}</h5>
        <span class="archive-date">{{ record.archived_time.strftime('%Y-%m-%d') }}</span>
    </div>
    <div class="item-content">
        <!-- 物品详情 -->
    </div>
    <div class="item-actions">
        <!-- 操作按钮 -->
    </div>
</div>
```

## 🎨 样式系统

### Bootstrap集成
- **版本**：Bootstrap 5.0+
- **主题**：自定义主题色彩
- **组件**：卡片、表单、按钮、模态框
- **工具类**：间距、颜色、排版

### 响应式设计
```html
<!-- 响应式网格 -->
<div class="row">
    <div class="col-12 col-md-8 col-lg-6">
        <!-- 内容 -->
    </div>
</div>

<!-- 响应式表格 -->
<div class="table-responsive">
    <table class="table">
        <!-- 表格内容 -->
    </table>
</div>
```

## 🔧 模板功能

### 数据传递
```python
# 在路由中传递数据
return render_template('search.html', 
    records=records,
    keyword=keyword,
    total_count=len(records)
)
```

### 模板变量
```html
<!-- 在模板中使用变量 -->
<h1>搜索结果 ({{ total_count }} 条)</h1>
{% for record in records %}
    <p>{{ record.pickup_location }}</p>
{% endfor %}
```

### 条件渲染
```html
<!-- 条件显示 -->
{% if current_user.is_authenticated %}
    <a href="/profile">个人中心</a>
{% else %}
    <a href="/auth/login">登录</a>
{% endif %}

<!-- 循环渲染 -->
{% for item in record.items %}
    <span class="badge">{{ item.item_name }}</span>
{% endfor %}
```

## 🛡 安全特性

### XSS防护
```html
<!-- 自动转义用户输入 -->
<p>{{ user_input | e }}</p>

<!-- 安全的HTML渲染 -->
<div>{{ content | safe }}</div>
```

### CSRF保护
```html
<!-- 表单CSRF令牌 -->
<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <!-- 表单字段 -->
</form>
```

## 📱 移动端优化

### 视口设置
```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### 触摸优化
- 按钮最小尺寸44px
- 适当的间距和填充
- 大号字体和图标
- 滑动友好的交互

### 性能优化
- 延迟加载非关键资源
- 压缩HTML输出
- 合并CSS和JS文件
- 优化图片加载

## 🔧 开发最佳实践

### 模板组织
1. **继承层次**：base.html → 页面模板
2. **组件复用**：提取公共组件
3. **命名规范**：语义化的块名称
4. **文件组织**：按功能分组存放

### 代码规范
```html
<!-- 良好的HTML结构 -->
<div class="container">
    <div class="row">
        <div class="col-md-8">
            <article class="content">
                <h1>{{ title }}</h1>
                <p>{{ description }}</p>
            </article>
        </div>
    </div>
</div>
```

### 可访问性
- 语义化HTML标签
- Alt属性用于图片
- 适当的标题层级
- 键盘导航支持
- 屏幕阅读器友好