from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from flask import current_app
from app.services.user_service import UserService

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            # 处理文件上传
            wx_qrcode_file = None
            if 'wx_qrcode' in request.files:
                file = request.files['wx_qrcode']
                if file.filename:
                    filename = secure_filename(f"{current_user.username}_{file.filename}")
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    wx_qrcode_file = filename
            
            result = UserService.update_profile(
                user=current_user,
                contact=request.form.get('contact'),
                free_time=request.form.get('free_time'),
                personal_info=request.form.get('personal_info'),
                wx_qrcode=wx_qrcode_file
            )
            
            if result['success']:
                flash('个人信息更新成功', 'success')
            else:
                flash(result['message'], 'danger')
                
            return redirect(url_for('user.profile'))
            
        except Exception as e:
            flash(f'更新失败: {str(e)}', 'danger')
            return redirect(url_for('user.profile'))
    
    try:
        # 获取用户统计数据
        stats = UserService.get_user_stats(current_user.agent_id)
        
        return render_template('pages/profile.html', 
                             my_records=stats['records'],
                             records_count=stats['records_count'],
                             archived_count=stats['archived_count'],
                             total_rewards=stats['total_rewards'])
    except Exception as e:
        flash(f'获取用户信息失败: {str(e)}', 'danger')
        return render_template('pages/profile.html', 
                             my_records=[],
                             records_count=0,
                             archived_count=0,
                             total_rewards=0)