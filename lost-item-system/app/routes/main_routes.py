from flask import Blueprint, render_template, current_app
from app.services.item_service import ItemService
from app.models import check_and_auto_archive

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # 执行自动归档检查
    check_and_auto_archive()
    
    try:
        # 获取最新的物品记录
        result = ItemService.search_items()
        # 使用配置文件中的首页显示数量，而不是硬编码的6
        home_page_limit = current_app.config.get('HOME_PAGE_ITEMS_LIMIT', 6)
        latest_items = result['records'][:home_page_limit] if result['success'] else []
        
        return render_template('index.html', latest_items=latest_items)
    except Exception as e:
        return render_template('index.html', latest_items=[])