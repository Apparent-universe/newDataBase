from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import Agent, FoundRecord, FoundItem, Reward, FoundHistory
from flask_login import login_user, logout_user, login_required, current_user

main = Blueprint('main', __name__)

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
        
        agent = Agent(
            username=request.form['username'],
            contact=request.form['contact']
        )
        agent.set_password(request.form['password'])
        
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
        
        item_names = request.form.getlist('items[][name]')
        
        for name in item_names:
            if name.strip():
                item = FoundItem(
                    record_id=record.record_id,
                    item_name=name.strip()
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

# AJAX API接口
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

@main.route('/api/found-items/<int:record_id>/archive', methods=['POST'])
@login_required
def api_archive_record(record_id):
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

@main.route('/api/found-items/<int:record_id>', methods=['DELETE'])
@login_required
def api_delete_record(record_id):
    record = FoundRecord.query.get_or_404(record_id)
    
    if current_user.agent_id != record.agent_id and current_user.role != 'admin':
        return jsonify({'message': '权限不足'}), 403
    
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({'message': '记录已删除'})