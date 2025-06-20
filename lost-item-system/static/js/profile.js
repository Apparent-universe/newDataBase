/**
 * 个人中心页面的JavaScript模块
 */
class ProfileModule {
    constructor() {
        this.init();
    }

    init() {
        this.bindFileValidation();
        this.bindRecordActions();
    }

    bindFileValidation() {
        const fileInput = document.getElementById('wx_qrcode');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.validateFile(e.target);
            });
        }
    }

    validateFile(input) {
        if (input.files && input.files[0]) {
            const file = input.files[0];
            if (!file.type.match('image.*')) {
                alert('请上传图片文件');
                input.value = '';
                return;
            }
            if (file.size > 2 * 1024 * 1024) {
                alert('图片大小不能超过2MB');
                input.value = '';
                return;
            }
        }
    }

    bindRecordActions() {
        // 绑定归档和删除按钮事件
        window.archiveRecord = this.archiveRecord.bind(this);
        window.deleteRecord = this.deleteRecord.bind(this);
        window.restoreRecord = this.restoreRecord.bind(this);
    }

    async archiveRecord(recordId) {
        if (!confirm('确定要归档这条记录吗？')) return;
        
        try {
            const response = await fetch(`/api/found-items/${recordId}/archive`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            alert(data.message);
            location.reload();
        } catch (error) {
            alert('操作失败，请重试');
        }
    }

    async deleteRecord(recordId) {
        if (!confirm('确定要删除这条记录吗？此操作不可恢复！')) return;
        
        try {
            const response = await fetch(`/api/found-items/${recordId}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            alert(data.message);
            location.reload();
        } catch (error) {
            alert('操作失败，请重试');
        }
    }

    async restoreRecord(archivedId) {
        if (!confirm('确定要恢复这条记录吗？恢复后将重新显示在活跃记录中。')) return;
        
        try {
            const response = await fetch(`/api/archived-items/${archivedId}/restore`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            alert(data.message);
            location.reload();
        } catch (error) {
            alert('恢复失败，请重试');
        }
    }
}

// 初始化个人中心模块
document.addEventListener('DOMContentLoaded', () => {
    new ProfileModule();
});