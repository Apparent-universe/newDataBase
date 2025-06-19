from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Agent(UserMixin, db.Model):
    __tablename__ = 'agent'
    agent_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    contact = db.Column(db.String(100), nullable=False)  # 保持联系方式为必填
    free_time = db.Column(db.String(100))  # 改为可选
    personal_info = db.Column(db.Text)      # 改为可选
    wx_qrcode = db.Column(db.String(255))   # 改为可选
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

class FoundRecord(db.Model):
    __tablename__ = 'found_record'
    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.agent_id'), nullable=False)
    pickup_location = db.Column(db.String(255), nullable=False)
    detailed_description = db.Column(db.Text)
    hidden_info = db.Column(db.Text)
    created_time = db.Column(db.DateTime, default=datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    items = db.relationship('FoundItem', backref='record', lazy=True)
    rewards = db.relationship('Reward', backref='record', lazy=True)

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