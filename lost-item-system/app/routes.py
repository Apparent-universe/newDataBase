from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import Agent, FoundRecord, FoundItem, Reward, FoundHistory
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
import jwt
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': '缺少认证令牌'}), 401
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = Agent.query.get(data['agent_id'])
        except:
            return jsonify({'message': '无效的令牌'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Web路由
@main.route('/')
def index():
    latest_items = FoundRecord.query.join(Agent).filter(
        Agent.status == 1
    ).order_by(FoundRecord.created_time.desc()).limit(6).all()
    return render_template('index.html', latest_items=latest_items)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        if Agent.query.filter_by(username=request.form['username']).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('main.register'))
        
        # 创建新用户，只需要基本信息
        agent = Agent(
            username=request.form['username'],
            contact=request.form['contact']
        )
        agent.set_password(request.form['password'])
        
        # 检查是否是首个用户，如果是则设置为管理员
        if Agent.query.count() == 0:
            agent.role = 'admin'
        
        db.session.add(agent)
        db.session.commit()
        
        flash('注册成功，请登录', 'success')
        return redirect(url_for('main.login'))
        
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        agent = Agent.query.filter_by(username=request.form['username']).first()
        
        if not agent or not agent.check_password(request.form['password']):
            flash('用户名或密码错误', 'danger')
            return redirect(url_for('main.login'))
            
        if agent.status == 0:
            flash('账号已被封禁', 'danger')
            return redirect(url_for('main.login'))
            
        login_user(agent)
        flash('登录成功', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('main.index'))

@main.route('/publish', methods=['GET', 'POST'])
@login_required
def publish():
    if request.method == 'POST':
        record = FoundRecord(
            agent_id=current_user.agent_id,
            pickup_location=request.form['pickup_location'],
            detailed_description=request.form['detailed_description'],
            hidden_info=request.form.get('hidden_info', '')
        )
        
        db.session.add(record)
        db.session.flush()
        
        # 获取物品名称和代表性标记
        item_names = request.form.getlist('items[][name]')
        item_representatives = request.form.getlist('items[][is_representative]')
        
        # 创建字典来匹配名称和代表性
        items_data = []
        for i, name in enumerate(item_names):
            is_representative = str(i) in item_representatives
            items_data.append({
                'name': name,
                'is_representative': is_representative
            })
        
        # 添加物品
        for item_data in items_data:
            item = FoundItem(
                record_id=record.record_id,
                item_name=item_data['name'],
                is_representative=item_data['is_representative']
            )
            db.session.add(item)
        
        db.session.commit()
        flash('物品信息发布成功', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('publish.html')

@main.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')
    record_id = request.args.get('record_id')
    
    query = FoundRecord.query.join(Agent).filter(Agent.status == 1)
    
    if record_id:
        query = query.filter(FoundRecord.record_id == record_id)
    else:
        if keyword:
            query = query.join(FoundItem).filter(FoundItem.item_name.ilike(f'%{keyword}%'))
        if location:
            query = query.filter(FoundRecord.pickup_location.ilike(f'%{location}%'))
    
    records = query.order_by(FoundRecord.created_time.desc()).all()
    return render_template('search.html', records=records, keyword=keyword, location=location)

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    my_records = FoundRecord.query.filter_by(agent_id=current_user.agent_id).order_by(FoundRecord.created_time.desc()).all()
    records_count = len(my_records)
    archived_count = FoundHistory.query.filter_by(agent_id=current_user.agent_id).count()
    
    # 计算总打赏金额
    total_rewards = db.session.query(db.func.sum(Reward.reward_amount)).join(
        FoundRecord, Reward.record_id == FoundRecord.record_id
    ).filter(FoundRecord.agent_id == current_user.agent_id).scalar() or 0
    
    if request.method == 'POST':
        current_user.contact = request.form.get('contact', current_user.contact)
        current_user.free_time = request.form.get('free_time', current_user.free_time)
        current_user.personal_info = request.form.get('personal_info', current_user.personal_info)
        
        if 'wx_qrcode' in request.files:
            file = request.files['wx_qrcode']
            if file.filename:
                filename = secure_filename(f"{current_user.username}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                current_user.wx_qrcode = filename
        
        db.session.commit()
        flash('个人信息更新成功', 'success')
        return redirect(url_for('main.profile'))
        
    return render_template('profile.html', 
                         my_records=my_records,
                         records_count=records_count,
                         archived_count=archived_count,
                         total_rewards=total_rewards)

# API路由
@main.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if Agent.query.filter_by(username=data['username']).first():
        return jsonify({'message': '用户名已存在'}), 400
    
    agent = Agent(
        username=data['username'],
        contact=data.get('contact'),
        free_time=data.get('free_time'),
        personal_info=data.get('personal_info')
    )
    agent.set_password(data['password'])
    
    db.session.add(agent)
    db.session.commit()
    
    return jsonify({'message': '注册成功'}), 201

@main.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    agent = Agent.query.filter_by(username=data['username']).first()
    
    if not agent or not agent.check_password(data['password']):
        return jsonify({'message': '用户名或密码错误'}), 401
        
    if agent.status == 0:
        return jsonify({'message': '账号已被封禁'}), 403
    
    token = jwt.encode({
        'agent_id': agent.agent_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }, current_app.config['SECRET_KEY'])
    
    return jsonify({
        'token': token,
        'role': agent.role
    })

@main.route('/api/profile', methods=['GET', 'PUT'])
@token_required
def api_profile(current_user):
    if request.method == 'GET':
        return jsonify({
            'username': current_user.username,
            'contact': current_user.contact,
            'free_time': current_user.free_time,
            'personal_info': current_user.personal_info,
            'wx_qrcode': current_user.wx_qrcode
        })
    
    data = request.get_json()
    for key, value in data.items():
        if hasattr(current_user, key):
            setattr(current_user, key, value)
    
    db.session.commit()
    return jsonify({'message': '个人信息更新成功'})

@main.route('/api/upload-qrcode', methods=['POST'])
@token_required
def api_upload_qrcode(current_user):
    if 'file' not in request.files:
        return jsonify({'message': '没有文件被上传'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': '没有选择文件'}), 400
        
    if file:
        filename = secure_filename(f"{current_user.username}_{file.filename}")
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        current_user.wx_qrcode = filename
        db.session.commit()
        return jsonify({'message': '二维码上传成功'})

@main.route('/api/found-items', methods=['POST'])
@token_required
def api_create_found_record(current_user):
    data = request.get_json()
    
    record = FoundRecord(
        agent_id=current_user.agent_id,
        pickup_location=data['pickup_location'],
        detailed_description=data['detailed_description'],
        hidden_info=data.get('hidden_info')
    )
    
    db.session.add(record)
    db.session.flush()
    
    for item_data in data['items']:
        item = FoundItem(
            record_id=record.record_id,
            item_name=item_data['name'],
            is_representative=item_data.get('is_representative', False)
        )
        db.session.add(item)
    
    db.session.commit()
    return jsonify({'message': '物品信息发布成功', 'record_id': record.record_id}), 201

@main.route('/api/found-items', methods=['GET'])
def api_search_found_items():
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')
    
    query = FoundRecord.query.join(FoundItem).join(Agent)
    
    if keyword:
        query = query.filter(FoundItem.item_name.ilike(f'%{keyword}%'))
    if location:
        query = query.filter(FoundRecord.pickup_location.ilike(f'%{location}%'))
    
    records = query.filter(Agent.status == 1).all()
    
    result = []
    for record in records:
        items = [{'name': item.item_name, 'is_representative': item.is_representative} 
                for item in record.items if item.is_representative]
        result.append({
            'record_id': record.record_id,
            'pickup_location': record.pickup_location,
            'detailed_description': record.detailed_description,
            'created_time': record.created_time.strftime('%Y-%m-%d %H:%M:%S'),
            'items': items,
            'agent': {
                'contact': record.agent.contact,
                'free_time': record.agent.free_time,
                'wx_qrcode': record.agent.wx_qrcode
            }
        })
    
    return jsonify(result)

@main.route('/api/found-items/<int:record_id>/reward', methods=['POST'])
def api_create_reward(record_id):
    data = request.get_json()
    reward = Reward(
        record_id=record_id,
        reward_amount=data['amount']
    )
    db.session.add(reward)
    db.session.commit()
    return jsonify({'message': '打赏成功'})

# 管理员接口
@main.route('/api/admin/agents/<int:agent_id>/status', methods=['PUT'])
@token_required
def api_update_agent_status(current_user, agent_id):
    if current_user.role != 'admin':
        return jsonify({'message': '权限不足'}), 403
        
    agent = Agent.query.get_or_404(agent_id)
    data = request.get_json()
    agent.status = data['status']
    
    if agent.status == 0:  # 如果封禁用户，归档其所有记录
        records = FoundRecord.query.filter_by(agent_id=agent_id).all()
        for record in records:
            history = FoundHistory(
                origin_record_id=record.record_id,
                agent_id=record.agent_id,
                pickup_location=record.pickup_location,
                detailed_description=record.detailed_description,
                hidden_info=record.hidden_info,
                created_time=record.created_time
            )
            db.session.add(history)
            db.session.delete(record)
    
    db.session.commit()
    return jsonify({'message': '状态更新成功'})

@main.route('/api/found-items/<int:record_id>/archive', methods=['POST'])
@token_required
def api_archive_record(current_user, record_id):
    record = FoundRecord.query.get_or_404(record_id)
    
    history = FoundHistory(
        origin_record_id=record.record_id,
        agent_id=record.agent_id,
        pickup_location=record.pickup_location,
        detailed_description=record.detailed_description,
        hidden_info=record.hidden_info,
        created_time=record.created_time
    )
    
    db.session.add(history)
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({'message': '记录已归档'})