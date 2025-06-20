/**
 * 发布物品页面的JavaScript模块
 */
document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('items-container');
    const addButton = document.getElementById('add-item');
    
    // 添加物品
    addButton.addEventListener('click', function() {
        const template = container.querySelector('.item-entry').cloneNode(true);
        template.querySelector('input[type="text"]').value = '';
        container.appendChild(template);
        
        // 滚动到新添加的元素
        template.scrollIntoView({ behavior: 'smooth', block: 'end' });
    });
    
    // 删除物品
    container.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-item')) {
            const itemEntries = container.querySelectorAll('.item-entry');
            if (itemEntries.length > 1) {
                const entry = e.target.closest('.item-entry');
                entry.classList.add('fade-out');
                setTimeout(() => entry.remove(), 300);
            } else {
                alert('至少需要保留一个物品信息');
            }
        }
    });
});