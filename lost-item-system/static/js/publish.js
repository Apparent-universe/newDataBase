/**
 * 发布页面的JavaScript模块
 */
class PublishModule {
    constructor() {
        this.locationMap = null;
        this.locationMarker = null;
        this.selectedLocation = null;
        this.geocoder = null;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.initValidation();
    }

    bindEvents() {
        // 添加物品按钮
        document.getElementById('add-item').addEventListener('click', () => {
            this.addItemEntry();
        });

        // 删除物品按钮（事件委托）
        document.getElementById('items-container').addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-item')) {
                this.removeItemEntry(e.target);
            }
        });

        // 地图选点相关按钮
        document.getElementById('select-location-btn').addEventListener('click', () => {
            this.showLocationSelector();
        });

        document.getElementById('cancel-location-btn').addEventListener('click', () => {
            this.hideLocationSelector();
        });

        document.getElementById('confirm-location-btn').addEventListener('click', () => {
            this.confirmLocation();
        });

        // 表单提交验证
        document.querySelector('form').addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
            }
        });
    }

    addItemEntry() {
        const container = document.getElementById('items-container');
        const newEntry = document.createElement('div');
        newEntry.className = 'item-entry mb-3';
        newEntry.innerHTML = `
            <div class="card">
                <div class="card-body p-3">
                    <div class="row g-2">
                        <div class="col-12">
                            <input type="text" class="form-control" name="items[][name]" 
                                   placeholder="物品名称" required>
                        </div>
                        <div class="col-12 d-flex justify-content-end mt-2">
                            <button type="button" class="btn btn-outline-danger btn-sm remove-item">
                                删除物品
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(newEntry);
        
        // 聚焦到新添加的输入框
        const newInput = newEntry.querySelector('input');
        newInput.focus();
    }

    removeItemEntry(button) {
        const container = document.getElementById('items-container');
        const entries = container.querySelectorAll('.item-entry');
        
        // 至少保留一个物品条目
        if (entries.length <= 1) {
            alert('至少需要一个物品条目');
            return;
        }
        
        const entry = button.closest('.item-entry');
        entry.classList.add('fade-out');
        
        setTimeout(() => {
            entry.remove();
        }, 300);
    }

    async showLocationSelector() {
        const selector = document.getElementById('location-selector');
        selector.style.display = 'block';
        
        // 初始化地图（如果还没有初始化）
        if (!this.locationMap) {
            await this.initLocationMap();
        }
        
        // 滚动到地图区域
        selector.scrollIntoView({ behavior: 'smooth' });
    }

    hideLocationSelector() {
        document.getElementById('location-selector').style.display = 'none';
        this.selectedLocation = null;
        this.updateLocationDisplay();
    }

    async initLocationMap() {
        try {
            // 显示定位提示
            document.getElementById('selected-address').textContent = '正在获取当前位置...';
            
            // 先尝试获取用户位置，再初始化地图
            const userLocation = await this.getUserLocation();
            
            // 使用用户位置或默认位置初始化地图
            const center = userLocation || [116.397428, 39.90923]; // 如果定位失败则使用北京
            
            this.locationMap = new AMap.Map('location-map', {
                zoom: userLocation ? 16 : 13, // 如果有用户位置，放大显示
                center: center,
                mapStyle: 'amap://styles/normal'
            });

            // 初始化地理编码服务
            this.geocoder = new AMap.Geocoder({
                radius: 1000,
                extensions: "all"
            });

            // 如果成功获取用户位置，自动添加标记
            if (userLocation) {
                this.onMapClick({ lnglat: { lng: userLocation[0], lat: userLocation[1] } });
                document.getElementById('selected-address').textContent = '已定位到当前位置，点击地图选择其他位置';
            } else {
                document.getElementById('selected-address').textContent = '定位失败，请手动点击地图选择位置';
            }

            // 地图点击事件
            this.locationMap.on('click', (e) => {
                this.onMapClick(e);
            });

        } catch (error) {
            console.error('地图初始化失败:', error);
            alert('地图初始化失败，请检查网络连接');
        }
    }

    async getUserLocation() {
        // 检查是否为HTTPS环境
        if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
            console.warn('定位功能需要HTTPS环境或本地环境');
            return null;
        }

        // 尝试使用浏览器原生定位（优先使用，兼容性更好）
        try {
            const browserLocation = await this.getBrowserLocation();
            if (browserLocation) {
                console.log('浏览器定位成功:', browserLocation);
                return browserLocation;
            }
        } catch (error) {
            console.warn('浏览器定位失败:', error);
        }

        // 尝试使用高德地图定位
        try {
            const amapLocation = await this.getAmapLocation();
            if (amapLocation) {
                console.log('高德定位成功:', amapLocation);
                return amapLocation;
            }
        } catch (error) {
            console.warn('高德定位失败:', error);
        }

        return null; // 所有定位方式都失败
    }

    getAmapLocation() {
        return new Promise((resolve, reject) => {
            const geolocation = new AMap.Geolocation({
                enableHighAccuracy: true,
                timeout: 8000,
                convert: true,
                showButton: false,
                showMarker: false,
                showCircle: false
            });

            geolocation.getCurrentPosition((status, result) => {
                if (status === 'complete') {
                    resolve([result.position.lng, result.position.lat]);
                } else {
                    reject(new Error('高德定位失败: ' + (result.message || '未知错误')));
                }
            });
        });
    }

    getBrowserLocation() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('浏览器不支持地理定位'));
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    resolve([position.coords.longitude, position.coords.latitude]);
                },
                (error) => {
                    let errorMsg = '浏览器定位失败';
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMsg = '用户拒绝了定位权限';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMsg = '定位信息不可用';
                            break;
                        case error.TIMEOUT:
                            errorMsg = '定位请求超时';
                            break;
                    }
                    reject(new Error(errorMsg + ': ' + error.message));
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000
                }
            );
        });
    }

    onMapClick(e) {
        const position = e.lnglat;
        
        // 移除之前的标记
        if (this.locationMarker) {
            this.locationMap.remove(this.locationMarker);
        }

        // 添加新标记
        this.locationMarker = new AMap.Marker({
            position: [position.lng, position.lat],
            icon: new AMap.Icon({
                size: new AMap.Size(32, 32),
                image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png',
                imageSize: new AMap.Size(32, 32)
            })
        });

        this.locationMap.add(this.locationMarker);

        // 逆地理编码获取地址
        this.reverseGeocode(position.lng, position.lat);
    }

    async reverseGeocode(longitude, latitude) {
        try {
            // 显示加载状态
            document.getElementById('selected-address').textContent = '正在获取地址...';

            const response = await fetch('/api/map/reverse-geocode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    longitude: longitude,
                    latitude: latitude
                })
            });

            const result = await response.json();

            if (result.success) {
                this.selectedLocation = {
                    longitude: longitude,
                    latitude: latitude,
                    formatted_address: result.data.formatted_address
                };

                this.updateLocationDisplay();
                document.getElementById('confirm-location-btn').disabled = false;
            } else {
                throw new Error(result.message || '获取地址失败');
            }

        } catch (error) {
            console.error('逆地理编码失败:', error);
            document.getElementById('selected-address').textContent = '获取地址失败';
            document.getElementById('confirm-location-btn').disabled = true;
        }
    }

    updateLocationDisplay() {
        const addressElement = document.getElementById('selected-address');
        
        if (this.selectedLocation) {
            addressElement.textContent = this.selectedLocation.formatted_address;
            addressElement.className = 'text-success';
        } else {
            addressElement.textContent = '点击地图选择位置';
            addressElement.className = 'text-muted';
        }
    }

    confirmLocation() {
        if (!this.selectedLocation) {
            alert('请先在地图上选择位置');
            return;
        }

        // 填充表单字段
        document.getElementById('pickup_location').value = this.selectedLocation.formatted_address;
        document.getElementById('latitude').value = this.selectedLocation.latitude;
        document.getElementById('longitude').value = this.selectedLocation.longitude;
        document.getElementById('formatted_address').value = this.selectedLocation.formatted_address;

        // 显示成功提示
        const locationInput = document.getElementById('pickup_location');
        locationInput.classList.add('is-valid');
        
        // 隐藏地图选择器
        this.hideLocationSelector();

        // 显示成功消息
        this.showMessage('位置选择成功！', 'success');
    }

    showMessage(message, type = 'info') {
        const alertClass = `alert-${type}`;
        const alertHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const form = document.querySelector('form');
        form.insertAdjacentHTML('beforebegin', alertHtml);
        
        // 自动移除消息
        setTimeout(() => {
            const alert = document.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 3000);
    }

    initValidation() {
        // 实时验证
        const inputs = document.querySelectorAll('input[required], textarea[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
        });
    }

    validateField(field) {
        const isValid = field.checkValidity();
        
        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
        }
        
        return isValid;
    }

    validateForm() {
        let isValid = true;
        
        // 验证必填字段
        const requiredFields = document.querySelectorAll('input[required], textarea[required]');
        requiredFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        // 验证至少有一个物品
        const itemInputs = document.querySelectorAll('input[name="items[][name]"]');
        const hasValidItem = Array.from(itemInputs).some(input => input.value.trim());
        
        if (!hasValidItem) {
            alert('请至少添加一个物品');
            isValid = false;
        }

        return isValid;
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new PublishModule();
});

// 高德地图API加载完成后的回调
window.onMapApiLoaded = function() {
    console.log('高德地图API加载完成');
};