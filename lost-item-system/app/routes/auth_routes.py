from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        try:
            result = AuthService.register_user(
                username=request.form['username'],
                password=request.form['password'],
                contact=request.form['contact']
            )
            
            if result['success']:
                flash('注册成功，请登录', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash(result['message'], 'danger')
                return redirect(url_for('auth.register'))
                
        except Exception as e:
            flash(f'注册失败: {str(e)}', 'danger')
            return redirect(url_for('auth.register'))
        
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        try:
            result = AuthService.login_user(
                username=request.form['username'],
                password=request.form['password']
            )
            
            if result['success']:
                login_user(result['user'])
                flash('登录成功', 'success')
                return redirect(url_for('main.index'))
            else:
                flash(result['message'], 'danger')
                return redirect(url_for('auth.login'))
                
        except Exception as e:
            flash(f'登录失败: {str(e)}', 'danger')
            return redirect(url_for('auth.login'))
        
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('main.index'))