/**
 * 发布页面的JavaScript模块
 */
class PublishModule {
    constructor() {
        this.locationMap = null;
        this.locationMarker = null;
        this.selectedLocation = null;
        this.geocoder = null;
        this.isMapVisible = false;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.initValidation();
        this.checkGeolocationSupport();
    }

    checkGeolocationSupport() {
        // 检查定位支持情况
        if (!navigator.geolocation) {
            console.warn('浏览器不支持地理定位功能');
        } else if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
            console.warn('定位功能在非HTTPS环境下可能受限');
        }
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
        const selectBtn = document.getElementById('select-location-btn');
        
        // 防止重复初始化
        if (this.isMapVisible) {
            selector.scrollIntoView({ behavior: 'smooth' });
            return;
        }
        
        // 显示加载状态
        selectBtn.disabled = true;
        selectBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 加载中...';
        
        try {
            selector.style.display = 'block';
            this.isMapVisible = true;
            
            // 初始化地图（如果还没有初始化）
            if (!this.locationMap) {
                await this.initLocationMap();
            }
            
            // 滚动到地图区域
            selector.scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            console.error('地图显示失败:', error);
            this.showMessage('地图加载失败，请检查网络连接', 'danger');
            this.hideLocationSelector();
        } finally {
            // 恢复按钮状态
            selectBtn.disabled = false;
            selectBtn.innerHTML = '<i class="fas fa-map-marker-alt"></i> 地图选点';
        }
    }

    hideLocationSelector() {
        document.getElementById('location-selector').style.display = 'none';
        this.isMapVisible = false;
        this.selectedLocation = null;
        this.updateLocationDisplay();
    }

    async initLocationMap() {
        try {
            // 显示定位提示
            document.getElementById('selected-address').textContent = '正在初始化地图和获取位置...';
            
            // 先尝试获取用户位置
            const userLocation = await this.getUserLocation();
            
            // 使用用户位置或默认位置初始化地图
            const center = userLocation || [116.397428, 39.90923]; // 默认北京
            const zoom = userLocation ? 17 : 13; // 有用户位置时放大显示
            
            this.locationMap = new AMap.Map('location-map', {
                zoom: zoom,
                center: center,
                mapStyle: 'amap://styles/normal',
                resizeEnable: true,
                rotateEnable: false,
                pitchEnable: false,
                zoomEnable: true,
                dragEnable: true
            });

            // 初始化地理编码服务
            this.geocoder = new AMap.Geocoder({
                radius: 1000,
                extensions: "all"
            });

            // 如果成功获取用户位置，自动添加标记
            if (userLocation) {
                await this.onMapClick({ 
                    lnglat: { 
                        lng: userLocation[0], 
                        lat: userLocation[1] 
                    } 
                });
                document.getElementById('selected-address').textContent = '已定位到当前位置，可点击地图选择其他位置';
            } else {
                document.getElementById('selected-address').textContent = '无法获取当前位置，请点击地图选择位置';
            }

            // 地图点击事件
            this.locationMap.on('click', (e) => {
                this.onMapClick(e);
            });

            // 地图加载完成事件
            this.locationMap.on('complete', () => {
                console.log('地图加载完成');
            });

        } catch (error) {
            console.error('地图初始化失败:', error);
            throw new Error('地图初始化失败: ' + error.message);
        }
    }

    async getUserLocation() {
        const timeout = 15000; // 15秒超时
        
        // 优先使用浏览器原生定位
        try {
            const browserLocation = await Promise.race([
                this.getBrowserLocation(),
                new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('浏览器定位超时')), timeout)
                )
            ]);
            
            if (browserLocation) {
                console.log('浏览器定位成功:', browserLocation);
                return browserLocation;
            }
        } catch (error) {
            console.warn('浏览器定位失败:', error.message);
        }

        // 尝试高德地图定位
        try {
            const amapLocation = await Promise.race([
                this.getAmapLocation(),
                new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('高德定位超时')), timeout)
                )
            ]);
            
            if (amapLocation) {
                console.log('高德定位成功:', amapLocation);
                return amapLocation;
            }
        } catch (error) {
            console.warn('高德定位失败:', error.message);
        }

        console.warn('所有定位方式均失败，将使用默认位置');
        return null;
    }

    getBrowserLocation() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('浏览器不支持地理定位'));
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const coords = [position.coords.longitude, position.coords.latitude];
                    resolve(coords);
                },
                (error) => {
                    let errorMsg = '浏览器定位失败';
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMsg = '用户拒绝了定位权限请求';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMsg = '位置信息不可用';
                            break;
                        case error.TIMEOUT:
                            errorMsg = '定位请求超时';
                            break;
                    }
                    reject(new Error(errorMsg));
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000 // 5分钟缓存
                }
            );
        });
    }

    getAmapLocation() {
        return new Promise((resolve, reject) => {
            try {
                const geolocation = new AMap.Geolocation({
                    enableHighAccuracy: true,
                    timeout: 10000,
                    convert: true,
                    showButton: false,
                    showMarker: false,
                    showCircle: false
                });

                geolocation.getCurrentPosition((status, result) => {
                    if (status === 'complete' && result.position) {
                        resolve([result.position.lng, result.position.lat]);
                    } else {
                        const errorMsg = result.message || '高德定位服务异常';
                        reject(new Error(errorMsg));
                    }
                });
            } catch (error) {
                reject(new Error('高德定位初始化失败: ' + error.message));
            }
        });
    }

    async onMapClick(e) {
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
                image: '/static/images/biaoji.jpg',
                imageSize: new AMap.Size(32, 32)
            }),
            // 设置锚点为图片下边缘的中心
            anchor: 'bottom-center',
            title: '选中的位置'
        });

        this.locationMap.add(this.locationMarker);

        // 逆地理编码获取地址
        await this.reverseGeocode(position.lng, position.lat);
    }

    async reverseGeocode(longitude, latitude) {
        try {
            // 显示加载状态
            document.getElementById('selected-address').textContent = '正在获取地址信息...';
            document.getElementById('confirm-location-btn').disabled = true;

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

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.success && result.data) {
                this.selectedLocation = {
                    longitude: longitude,
                    latitude: latitude,
                    formatted_address: result.data.formatted_address
                };

                this.updateLocationDisplay();
                document.getElementById('confirm-location-btn').disabled = false;
            } else {
                throw new Error(result.message || '获取地址信息失败');
            }

        } catch (error) {
            console.error('逆地理编码失败:', error);
            document.getElementById('selected-address').textContent = '获取地址失败: ' + error.message;
            document.getElementById('confirm-location-btn').disabled = true;
            
            // 显示错误提示
            this.showMessage('获取地址信息失败，请重新选择位置', 'warning');
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
            this.showMessage('请先在地图上选择位置', 'warning');
            return;
        }

        // 填充表单字段
        document.getElementById('pickup_location').value = this.selectedLocation.formatted_address;
        document.getElementById('latitude').value = this.selectedLocation.latitude;
        document.getElementById('longitude').value = this.selectedLocation.longitude;
        document.getElementById('formatted_address').value = this.selectedLocation.formatted_address;

        // 显示成功状态
        const locationInput = document.getElementById('pickup_location');
        locationInput.classList.remove('is-invalid');
        locationInput.classList.add('is-valid');
        
        // 隐藏地图选择器
        this.hideLocationSelector();

        // 显示成功消息
        this.showMessage('位置选择成功！您可以继续填写其他信息', 'success');
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