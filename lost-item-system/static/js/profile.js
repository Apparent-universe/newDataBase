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
        this.bindImagePreview();
    }

    bindImagePreview() {
        const fileInput = document.getElementById('wx_qrcode');
        const previewContainer = document.getElementById('qrcode-preview-container');
        const previewImg = document.getElementById('qrcode-preview');
        
        if (fileInput && previewContainer && previewImg) {
            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                
                if (file) {
                    // 验证文件类型
                    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                    if (!allowedTypes.includes(file.type)) {
                        alert('请选择有效的图片文件（JPG、PNG、GIF）');
                        fileInput.value = '';
                        return;
                    }
                    
                    // 验证文件大小（2MB）
                    const maxSize = 2 * 1024 * 1024;
                    if (file.size > maxSize) {
                        alert('文件大小不能超过2MB');
                        fileInput.value = '';
                        return;
                    }
                    
                    // 显示预览
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        previewImg.src = e.target.result;
                        previewContainer.style.display = 'block';
                        
                        // 更新提示文字
                        const caption = previewContainer.querySelector('small');
                        if (caption) {
                            caption.textContent = '新选择的二维码（未保存）';
                            caption.className = 'text-warning';
                        }
                    };
                    reader.readAsDataURL(file);
                } else {
                    // 如果取消选择文件，恢复原状态
                    this.restoreOriginalImage();
                }
            });
        }
    }

    restoreOriginalImage() {
        const previewContainer = document.getElementById('qrcode-preview-container');
        const previewImg = document.getElementById('qrcode-preview');
        
        // 检查是否有原始图片
        const hasOriginalImage = previewImg.dataset.originalSrc;
        
        if (hasOriginalImage) {
            previewImg.src = hasOriginalImage;
            const caption = previewContainer.querySelector('small');
            if (caption) {
                caption.textContent = '当前二维码';
                caption.className = 'text-muted';
            }
        } else {
            previewContainer.style.display = 'none';
        }
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

/**
 * 编辑记录
 */
function editRecord(recordId) {
    window.location.href = `/items/edit/${recordId}`;
}

// 初始化个人中心模块
document.addEventListener('DOMContentLoaded', () => {
    const profileModule = new ProfileModule();
    
    // 保存原始图片URL以便恢复
    const previewImg = document.getElementById('qrcode-preview');
    if (previewImg && previewImg.src && previewImg.src !== window.location.href + '#') {
        previewImg.dataset.originalSrc = previewImg.src;
    }
});