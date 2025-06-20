from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.item_service import ItemService

item_bp = Blueprint('item', __name__, url_prefix='/items')

@item_bp.route('/publish', methods=['GET', 'POST'])
@login_required
def publish():
    if request.method == 'POST':
        try:
            # 获取地理位置信息
            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')
            formatted_address = request.form.get('formatted_address')
            
            # 转换坐标类型
            if latitude and longitude:
                try:
                    latitude = float(latitude)
                    longitude = float(longitude)
                except (ValueError, TypeError):
                    latitude = None
                    longitude = None
                    formatted_address = None
            else:
                latitude = None
                longitude = None
                formatted_address = None
            
            result = ItemService.publish_item(
                agent_id=current_user.agent_id,
                pickup_location=request.form['pickup_location'],
                detailed_description=request.form['detailed_description'],
                hidden_info=request.form.get('hidden_info', ''),
                item_names=request.form.getlist('items[][name]'),
                latitude=latitude,
                longitude=longitude,
                formatted_address=formatted_address
            )
            
            if result['success']:
                flash('物品信息发布成功', 'success')
                return redirect(url_for('main.index'))
            else:
                flash(result['message'], 'danger')
                return redirect(url_for('item.publish'))
                
        except Exception as e:
            flash(f'发布失败: {str(e)}', 'danger')
            return redirect(url_for('item.publish'))
        
    return render_template('pages/publish.html')

@item_bp.route('/search')
def search():
    try:
        keyword = request.args.get('keyword', '')
        location = request.args.get('location', '')
        record_id = request.args.get('record_id')
        
        result = ItemService.search_items(
            keyword=keyword,
            location=location,
            record_id=record_id
        )
        
        return render_template('pages/search.html', 
                             records=result['records'],
                             keyword=keyword,
                             location=location)
    except Exception as e:
        flash(f'搜索失败: {str(e)}', 'danger')
        return render_template('pages/search.html', records=[], keyword='', location='')

@item_bp.route('/archived')
@login_required
def archived():
    try:
        result = ItemService.get_archived_items(current_user.agent_id)
        return render_template('pages/archived.html', 
                             archived_records=result['records'])
    except Exception as e:
        flash(f'获取归档记录失败: {str(e)}', 'danger')
        return render_template('pages/archived.html', archived_records=[])

@item_bp.route('/map')
@login_required
def map_search():
    """地图搜索页面 - 仅限登录用户"""
    return render_template('pages/map.html')

@item_bp.route('/map/<int:record_id>')
@login_required
def record_map(record_id):
    """单个记录的地图查看页面"""
    try:
        from app.models import FoundRecord, Agent
        
        # 获取记录详情
        record = FoundRecord.query.join(Agent).filter(
            FoundRecord.record_id == record_id,
            Agent.status == 1
        ).first_or_404()
        
        # 检查是否有地理位置信息
        if not record.has_location():
            flash('该记录没有地理位置信息', 'warning')
            return redirect(url_for('item.search'))
        
        return render_template('pages/record_map.html', record=record)
        
    except Exception as e:
        flash(f'获取记录信息失败: {str(e)}', 'danger')
        return redirect(url_for('item.search'))

@item_bp.route('/edit/<int:record_id>')
@login_required
def edit_record(record_id):
    """编辑记录页面"""
    try:
        from app.models import FoundRecord
        
        # 获取记录并验证权限
        record = FoundRecord.query.filter_by(
            record_id=record_id,
            agent_id=current_user.agent_id
        ).first_or_404()
        
        return render_template('pages/edit_record.html', record=record)
        
    except Exception as e:
        flash(f'获取记录信息失败: {str(e)}', 'danger')
        return redirect(url_for('user.profile'))

@item_bp.route('/update/<int:record_id>', methods=['POST'])
@login_required
def update_record(record_id):
    """更新记录"""
    try:
        from app.services.item_service import ItemService
        
        # 获取表单数据
        pickup_location = request.form.get('pickup_location', '').strip()
        detailed_description = request.form.get('detailed_description', '').strip()
        hidden_info = request.form.get('hidden_info', '').strip()
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        formatted_address = request.form.get('formatted_address')
        
        # 获取物品列表
        item_names = []
        items_data = request.form.getlist('items[][name]')
        for item_name in items_data:
            if item_name.strip():
                item_names.append(item_name.strip())
        
        # 验证数据
        if not pickup_location:
            flash('拾获地点不能为空', 'danger')
            return redirect(url_for('item.edit_record', record_id=record_id))
        
        if not detailed_description:
            flash('详细描述不能为空', 'danger')
            return redirect(url_for('item.edit_record', record_id=record_id))
        
        if not item_names:
            flash('至少需要一个物品', 'danger')
            return redirect(url_for('item.edit_record', record_id=record_id))
        
        # 处理坐标
        lat_value = float(latitude) if latitude and latitude != '' else None
        lon_value = float(longitude) if longitude and longitude != '' else None
        
        # 更新记录
        result = ItemService.update_record(
            record_id=record_id,
            agent_id=current_user.agent_id,
            pickup_location=pickup_location,
            detailed_description=detailed_description,
            hidden_info=hidden_info,
            item_names=item_names,
            latitude=lat_value,
            longitude=lon_value,
            formatted_address=formatted_address
        )
        
        if result['success']:
            flash('记录更新成功！', 'success')
            return redirect(url_for('user.profile'))
        else:
            flash(result['message'], 'danger')
            return redirect(url_for('item.edit_record', record_id=record_id))
            
    except Exception as e:
        flash(f'更新失败: {str(e)}', 'danger')
        return redirect(url_for('item.edit_record', record_id=record_id))