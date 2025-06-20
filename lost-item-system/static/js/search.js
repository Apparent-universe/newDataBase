/**
 * 搜索和打赏功能的JavaScript模块
 */
class SearchModule {
    constructor() {
        this.init();
    }

    init() {
        this.bindRewardEvents();
    }

    bindRewardEvents() {
        // 使用事件委托，减少事件监听器数量
        document.addEventListener('submit', async (e) => {
            if (!e.target.classList.contains('reward-form')) return;
            
            e.preventDefault();
            await this.handleRewardSubmit(e.target);
        });
    }

    async handleRewardSubmit(form) {
        const recordId = form.dataset.recordId;
        const amountInput = document.getElementById(`amount${recordId}`);
        const amount = parseFloat(amountInput.value);
        
        if (isNaN(amount) || amount <= 0) {
            alert('请输入有效的打赏金额');
            return;
        }
        
        // 防止重复提交
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn.disabled) return;
        
        submitBtn.disabled = true;
        submitBtn.textContent = '处理中...';
        
        try {
            const response = await fetch(`/api/found-items/${recordId}/reward`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount })
            });

            if (!response.ok) throw new Error('网络错误');
            
            // 关闭模态框
            const modalElement = document.getElementById(`rewardModal${recordId}`);
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) modal.hide();
            
            // 显示成功消息
            this.showSuccessMessage('打赏成功！');
            
            // 延迟刷新
            setTimeout(() => location.reload(), 1500);
            
        } catch (error) {
            submitBtn.disabled = false;
            submitBtn.textContent = '确认打赏';
            alert('打赏失败，请重试');
        }
    }

    showSuccessMessage(message) {
        // 移除已存在的消息
        const existingAlert = document.querySelector('.success-message');
        if (existingAlert) existingAlert.remove();
        
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success position-fixed top-0 start-50 translate-middle-x mt-3 success-message';
        alertDiv.style.zIndex = '9999';
        alertDiv.textContent = message;
        document.body.appendChild(alertDiv);
        
        // 自动移除
        setTimeout(() => alertDiv.remove(), 3000);
    }
}

/**
 * 显示登录提示
 */
function showLoginRequired() {
    alert('请先登录才能查看地图位置');
    // 可选：直接跳转到登录页面
    if (confirm('是否立即前往登录页面？')) {
        window.location.href = '/auth/login';
    }
}

// 初始化搜索模块
document.addEventListener('DOMContentLoaded', () => {
    new SearchModule();
});