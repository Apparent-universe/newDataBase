from datetime import datetime, timedelta
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app

class Agent(UserMixin, db.Model):
    __tablename__ = 'agent'
    agent_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    contact = db.Column(db.String(100), nullable=False)  # 保持联系方式为必填
    free_time = db.Column(db.String(100))  # 改为可选
    personal_info = db.Column(db.Text)      # 改为可选
    wx_qrcode = db.Column(db.LargeBinary)   # 只保留图片数据
    wx_qrcode_mimetype = db.Column(db.String(100))   # 只保留MIME类型，用于正确显示
    role = db.Column(db.Enum('agent', 'admin'), default='agent')
    status = db.Column(db.Integer, default=1)
    created_time = db.Column(db.DateTime, default=datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    records = db.relationship('FoundRecord', backref='agent', lazy=True)
    
    def get_id(self):
        return str(self.agent_id)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_wx_qrcode(self, file_data, mimetype=None):
        """设置微信二维码数据 - 简化版本"""
        self.wx_qrcode = file_data
        self.wx_qrcode_mimetype = mimetype
    
    def has_wx_qrcode(self):
        """检查是否有微信二维码"""
        return self.wx_qrcode is not None and len(self.wx_qrcode) > 0

class FoundRecord(db.Model):
    __tablename__ = 'found_record'
    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.agent_id'), nullable=False)
    pickup_location = db.Column(db.String(255), nullable=False)
    # 新增地理位置字段
    latitude = db.Column(db.DECIMAL(10, 8), nullable=True)  # 纬度
    longitude = db.Column(db.DECIMAL(11, 8), nullable=True)  # 经度
    formatted_address = db.Column(db.String(500), nullable=True)  # 格式化地址
    detailed_description = db.Column(db.Text)
    hidden_info = db.Column(db.Text)
    created_time = db.Column(db.DateTime, default=datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 修复级联删除配置
    items = db.relationship('FoundItem', backref='record', lazy=True, cascade='all, delete-orphan')
    rewards = db.relationship('Reward', backref='record', lazy=True, cascade='all, delete-orphan')

    def has_location(self):
        """检查是否有地理坐标"""
        return self.latitude is not None and self.longitude is not None
    
    def get_location_dict(self):
        """获取位置信息字典"""
        if self.has_location():
            return {
                'latitude': float(self.latitude),
                'longitude': float(self.longitude),
                'formatted_address': self.formatted_address,
                'pickup_location': self.pickup_location
            }
        return None

class FoundItem(db.Model):
    __tablename__ = 'found_item'
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    record_id = db.Column(db.Integer, db.ForeignKey('found_record.record_id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)

class Reward(db.Model):
    __tablename__ = 'reward'
    reward_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    record_id = db.Column(db.Integer, db.ForeignKey('found_record.record_id'), nullable=False)
    reward_amount = db.Column(db.DECIMAL(10, 2), nullable=False)
    reward_time = db.Column(db.DateTime, default=datetime.now)

class FoundHistory(db.Model):
    __tablename__ = 'found_history'
    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    origin_record_id = db.Column(db.Integer, nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.agent_id'), nullable=False)
    pickup_location = db.Column(db.String(255), nullable=False)
    detailed_description = db.Column(db.Text)
    hidden_info = db.Column(db.Text)
    created_time = db.Column(db.DateTime)
    confirm_time = db.Column(db.DateTime, default=datetime.now)

# 新增归档表
class ArchivedRecord(db.Model):
    __tablename__ = 'archived_record'
    archived_record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 匹配现有主键名
    original_record_id = db.Column(db.Integer, nullable=False)  # 原记录ID
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.agent_id'), nullable=False)
    pickup_location = db.Column(db.String(255), nullable=False)
    detailed_description = db.Column(db.Text)
    hidden_info = db.Column(db.Text)
    created_time = db.Column(db.DateTime, nullable=False)  # 匹配现有字段名
    archived_time = db.Column(db.DateTime, default=datetime.now)  # 归档时间
    archive_reason = db.Column(db.Enum('USER_ARCHIVE', 'USER_DELETE', 'AUTO_ARCHIVE'), nullable=True)
    archived_by_agent_id = db.Column(db.Integer, db.ForeignKey('agent.agent_id'), nullable=True)
    
    # 关联关系
    agent = db.relationship('Agent', foreign_keys=[agent_id], backref='archived_records')
    archived_by = db.relationship('Agent', foreign_keys=[archived_by_agent_id])
    items = db.relationship('ArchivedItem', backref='record', lazy=True, cascade='all, delete-orphan')
    
class ArchivedItem(db.Model):
    __tablename__ = 'archived_item'
    archived_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    archived_record_id = db.Column(db.Integer, db.ForeignKey('archived_record.archived_record_id'), nullable=False)
    original_item_id = db.Column(db.Integer, nullable=True)  # 原物品ID，设为可选
    item_name = db.Column(db.String(100), nullable=False)

# 添加自动归档检查函数
def check_and_auto_archive():
    """检查并自动归档超过配置时间的记录"""
    try:
        # 使用配置文件中的归档时间，而不是硬编码的14天
        archive_timedelta = current_app.config.get('AUTO_ARCHIVE_DAYS', 14)
        cutoff_time = datetime.now() - timedelta(days=archive_timedelta)
        
        old_records = FoundRecord.query.filter(
            FoundRecord.created_time < cutoff_time
        ).all()
        
        archived_count = 0
        for record in old_records:
            # 创建归档记录
            archived_record = ArchivedRecord(
                original_record_id=record.record_id,
                agent_id=record.agent_id,
                pickup_location=record.pickup_location,
                detailed_description=record.detailed_description,
                hidden_info=record.hidden_info,
                created_time=record.created_time,
                archive_reason='AUTO_ARCHIVE',
                archived_by_agent_id=None  # 自动归档无操作用户
            )
            db.session.add(archived_record)
            db.session.flush()
            
            # 转移物品
            for item in record.items:
                archived_item = ArchivedItem(
                    archived_record_id=archived_record.archived_record_id,
                    original_item_id=item.item_id,
                    item_name=item.item_name
                )
                db.session.add(archived_item)
            
            # 删除原记录（级联删除物品和打赏记录）
            db.session.delete(record)
            archived_count += 1
        
        if archived_count > 0:
            db.session.commit()
            print(f"自动归档了 {archived_count} 条超期记录")
        
        return archived_count
    except Exception as e:
        db.session.rollback()
        print(f"自动归档失败: {e}")
        return 0