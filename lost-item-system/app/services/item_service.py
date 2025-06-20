from app import db
from app.models import FoundRecord, FoundItem, ArchivedRecord, ArchivedItem, Agent, check_and_auto_archive
from sqlalchemy.orm import selectinload
from flask import current_app

class ItemService:
    """物品管理服务"""
    
    @staticmethod
    def publish_item(agent_id, pickup_location, detailed_description, hidden_info, item_names):
        """发布拾获物品"""
        try:
            # 创建记录
            record = FoundRecord(
                agent_id=agent_id,
                pickup_location=pickup_location,
                detailed_description=detailed_description,
                hidden_info=hidden_info
            )
            
            db.session.add(record)
            db.session.flush()
            
            # 添加物品
            for name in item_names:
                if name.strip():
                    item = FoundItem(
                        record_id=record.record_id,
                        item_name=name.strip()
                    )
                    db.session.add(item)
            
            db.session.commit()
            return {'success': True, 'record': record}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'发布失败: {str(e)}'}
    
    @staticmethod
    def search_items(keyword=None, location=None, record_id=None):
        """搜索物品"""
        try:
            # 执行自动归档检查
            check_and_auto_archive()
            
            query = FoundRecord.query.join(Agent).filter(Agent.status == 1)
            
            if record_id:
                query = query.filter(FoundRecord.record_id == record_id)
            else:
                if keyword:
                    query = query.join(FoundItem).filter(FoundItem.item_name.ilike(f'%{keyword}%'))
                if location:
                    query = query.filter(FoundRecord.pickup_location.ilike(f'%{location}%'))
            
            # 使用配置文件中的搜索结果限制，而不是硬编码的20
            search_limit = current_app.config.get('SEARCH_RESULTS_LIMIT', 20)
            
            # 优化查询：预加载关联数据
            records = query.options(
                selectinload(FoundRecord.items),
                selectinload(FoundRecord.agent)
            ).order_by(FoundRecord.created_time.desc()).limit(search_limit).all()
            
            return {'success': True, 'records': records}
            
        except Exception as e:
            return {'success': False, 'records': [], 'message': f'搜索失败: {str(e)}'}
    
    @staticmethod
    def get_archived_items(agent_id):
        """获取用户的归档记录"""
        try:
            archived_records = ArchivedRecord.query.filter(
                ArchivedRecord.agent_id == agent_id,
                ArchivedRecord.archive_reason != 'USER_DELETE'
            ).options(
                selectinload(ArchivedRecord.items),
                selectinload(ArchivedRecord.archived_by)
            ).order_by(ArchivedRecord.archived_time.desc()).all()
            
            return {'success': True, 'records': archived_records}
            
        except Exception as e:
            return {'success': False, 'records': [], 'message': f'获取归档记录失败: {str(e)}'}
    
    @staticmethod
    def archive_record(record_id, current_user_id, current_user_role):
        """归档记录"""
        try:
            record = FoundRecord.query.get_or_404(record_id)
            
            # 检查权限
            if current_user_id != record.agent_id and current_user_role != 'admin':
                return {'success': False, 'message': '权限不足'}
            
            # 获取物品数据
            items_data = []
            for item in record.items:
                items_data.append({
                    'item_id': item.item_id,
                    'item_name': item.item_name
                })
            
            # 创建归档记录
            archived_record = ArchivedRecord(
                original_record_id=record.record_id,
                agent_id=record.agent_id,
                pickup_location=record.pickup_location,
                detailed_description=record.detailed_description,
                hidden_info=record.hidden_info,
                created_time=record.created_time,
                archive_reason='USER_ARCHIVE',
                archived_by_agent_id=current_user_id
            )
            db.session.add(archived_record)
            db.session.flush()
            
            # 转移物品数据
            for item_data in items_data:
                archived_item = ArchivedItem(
                    archived_record_id=archived_record.archived_record_id,
                    original_item_id=item_data['item_id'],
                    item_name=item_data['item_name']
                )
                db.session.add(archived_item)
            
            # 删除原记录
            db.session.delete(record)
            db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'归档失败: {str(e)}'}
    
    @staticmethod
    def delete_record(record_id, current_user_id, current_user_role):
        """删除记录"""
        try:
            record = FoundRecord.query.get_or_404(record_id)
            
            # 检查权限
            if current_user_id != record.agent_id and current_user_role != 'admin':
                return {'success': False, 'message': '权限不足'}
            
            # 获取物品数据
            items_data = []
            for item in record.items:
                items_data.append({
                    'item_id': item.item_id,
                    'item_name': item.item_name
                })
            
            # 创建归档记录（标记为删除）
            archived_record = ArchivedRecord(
                original_record_id=record.record_id,
                agent_id=record.agent_id,
                pickup_location=record.pickup_location,
                detailed_description=record.detailed_description,
                hidden_info=record.hidden_info,
                created_time=record.created_time,
                archive_reason='USER_DELETE',
                archived_by_agent_id=current_user_id
            )
            db.session.add(archived_record)
            db.session.flush()
            
            # 转移物品数据
            for item_data in items_data:
                archived_item = ArchivedItem(
                    archived_record_id=archived_record.archived_record_id,
                    original_item_id=item_data['item_id'],
                    item_name=item_data['item_name']
                )
                db.session.add(archived_item)
            
            # 删除原记录
            db.session.delete(record)
            db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'删除失败: {str(e)}'}
    
    @staticmethod
    def restore_archived_record(archived_id, current_user_id, current_user_role):
        """恢复归档记录"""
        try:
            archived_record = ArchivedRecord.query.filter_by(archived_record_id=archived_id).first_or_404()
            
            # 检查权限
            if current_user_id != archived_record.agent_id and current_user_role != 'admin':
                return {'success': False, 'message': '权限不足'}
            
            # 检查是否为已删除的记录
            if archived_record.archive_reason == 'USER_DELETE':
                return {'success': False, 'message': '已删除的记录无法恢复'}
            
            # 创建新的活跃记录
            new_record = FoundRecord(
                agent_id=archived_record.agent_id,
                pickup_location=archived_record.pickup_location,
                detailed_description=archived_record.detailed_description,
                hidden_info=archived_record.hidden_info,
                created_time=archived_record.created_time
            )
            db.session.add(new_record)
            db.session.flush()
            
            # 恢复物品
            for item in archived_record.items:
                new_item = FoundItem(
                    record_id=new_record.record_id,
                    item_name=item.item_name
                )
                db.session.add(new_item)
            
            # 删除归档记录
            db.session.delete(archived_record)
            db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'恢复失败: {str(e)}'}