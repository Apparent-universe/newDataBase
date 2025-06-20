from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.item_service import ItemService

item_bp = Blueprint('item', __name__, url_prefix='/items')

@item_bp.route('/publish', methods=['GET', 'POST'])
@login_required
def publish():
    if request.method == 'POST':
        try:
            result = ItemService.publish_item(
                agent_id=current_user.agent_id,
                pickup_location=request.form['pickup_location'],
                detailed_description=request.form['detailed_description'],
                hidden_info=request.form.get('hidden_info', ''),
                item_names=request.form.getlist('items[][name]')
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