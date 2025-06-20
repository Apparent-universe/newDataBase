from flask import Blueprint, request, render_template, redirect, url_for, flash, Response, current_app
from flask_login import login_required, current_user
from app.services.user_service import UserService
from app.utils.helpers import ValidationUtils

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            # 处理文件上传 - 终极修复版本
            wx_qrcode_file_data = None
            wx_qrcode_mimetype = None
            
            if 'wx_qrcode' in request.files:
                file = request.files['wx_qrcode']
                if file.filename:  # 确实选择了文件
                    print(f"Debug: 收到文件上传请求，文件名: {file.filename}")
                    
                    # 立即读取文件数据，避免指针问题
                    file.seek(0)  # 确保从头开始读取
                    file_data = file.read()
                    
                    if not file_data or len(file_data) == 0:
                        flash('文件内容为空，请重新选择文件', 'danger')
                        return redirect(url_for('user.profile'))
                    
                    # 验证文件
                    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                    allowed_extensions = current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})
                    
                    if file_ext not in allowed_extensions:
                        flash(f'文件格式不支持，支持的格式：{", ".join(allowed_extensions)}', 'danger')
                        return redirect(url_for('user.profile'))
                    
                    # 检查文件大小
                    max_size = current_app.config.get('MAX_IMAGE_SIZE', 2 * 1024 * 1024)
                    if len(file_data) > max_size:
                        flash(f'文件大小不能超过{max_size // (1024*1024)}MB', 'danger')
                        return redirect(url_for('user.profile'))
                    
                    # 准备数据
                    wx_qrcode_file_data = file_data
                    wx_qrcode_mimetype = file.mimetype or f'image/{file_ext}'
                    
                    print(f"Debug: 文件验证通过，准备更新用户 {current_user.username} 的二维码")
                    print(f"Debug: 文件大小: {len(file_data)} bytes, MIME类型: {wx_qrcode_mimetype}")
                else:
                    print("Debug: 没有选择文件，跳过二维码更新")
            
            # 调用服务层更新 - 使用预读取的数据
            result = UserService.update_profile_with_data(
                user=current_user,
                contact=request.form.get('contact'),
                free_time=request.form.get('free_time'),
                personal_info=request.form.get('personal_info'),
                wx_qrcode_data=wx_qrcode_file_data,
                wx_qrcode_mimetype=wx_qrcode_mimetype
            )
            
            if result['success']:
                if wx_qrcode_file_data:
                    flash('个人信息和二维码更新成功', 'success')
                else:
                    flash('个人信息更新成功', 'success')
            else:
                flash(result['message'], 'danger')
                
            return redirect(url_for('user.profile'))
            
        except Exception as e:
            print(f"Debug: 路由层异常: {str(e)}")
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

@user_bp.route('/qrcode/<int:agent_id>')
def get_qrcode(agent_id):
    """获取用户的微信二维码图片"""
    from app.models import Agent
    
    try:
        agent = Agent.query.get_or_404(agent_id)
        
        if not agent.has_wx_qrcode():
            return Response("No QR code found", status=404)
        
        # 使用更新时间作为ETag，实现更好的缓存控制
        etag = f'"{agent.updated_time.timestamp()}"'
        
        return Response(
            agent.wx_qrcode,
            mimetype=agent.wx_qrcode_mimetype or 'image/jpeg',
            headers={
                'Content-Disposition': 'inline; filename="qrcode.jpg"',
                'Cache-Control': 'public, max-age=86400',  # 缓存24小时
                'ETag': etag,  # 使用ETag进行缓存验证
                'Last-Modified': agent.updated_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
            }
        )
    except Exception as e:
        return Response(f"Error: {str(e)}", status=500)