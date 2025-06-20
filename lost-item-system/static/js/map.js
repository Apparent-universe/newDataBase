/**
 * 地图搜索页面的JavaScript模块
 */
class MapSearchModule {
    constructor() {
        this.map = null;
        this.markers = [];
        this.currentLocationMarker = null;
        this.currentLocation = null;
        this.allRecords = [];
        this.filteredRecords = [];
        this.infoWindow = null;
        this.geolocation = null;
        
        this.init();
    }

    async init() {
        try {
            await this.initMap();
            this.bindEvents();
            await this.loadMapData();
        } catch (error) {
            console.error('地图初始化失败:', error);
            this.showError('地图初始化失败，请刷新页面重试');
        }
    }

    async initMap() {
        // 初始化地图
        this.map = new AMap.Map('map-container', {
            zoom: 13,
            center: [116.397428, 39.90923], // 北京天安门
            mapStyle: 'amap://styles/normal',
            showLabel: true
        });

        // 初始化信息窗体
        this.infoWindow = new AMap.InfoWindow({
            offset: new AMap.Pixel(0, -30),
            autoMove: true
        });

        // 初始化定位插件
        this.geolocation = new AMap.Geolocation({
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0,
            convert: true,
            showButton: false,
            showMarker: false,
            showCircle: false
        });

        this.map.addControl(this.geolocation);

        // 地图加载完成后隐藏loading
        this.map.on('complete', () => {
            document.querySelector('.loading').style.display = 'none';
        });
    }

    bindEvents() {
        // 定位按钮事件
        document.getElementById('current-location-btn').addEventListener('click', () => {
            this.getCurrentLocation();
        });

        // 搜索半径变化事件
        document.getElementById('search-radius').addEventListener('change', () => {
            if (this.currentLocation) {
                this.searchNearbyRecords();
            }
        });

        // 物品筛选事件
        let filterTimeout;
        document.getElementById('item-filter').addEventListener('input', (e) => {
            clearTimeout(filterTimeout);
            filterTimeout = setTimeout(() => {
                this.filterRecords(e.target.value);
            }, 300);
        });
    }

    async loadMapData() {
        try {
            const response = await fetch('/api/map/records');
            const result = await response.json();

            if (result.success) {
                this.allRecords = result.records;
                this.displayRecordsOnMap(this.allRecords);
                console.log(`成功加载 ${this.allRecords.length} 条记录`);
            } else {
                throw new Error(result.message || '获取地图数据失败');
            }
        } catch (error) {
            console.error('加载地图数据失败:', error);
            this.showError('加载地图数据失败: ' + error.message);
        }
    }

    displayRecordsOnMap(records) {
        // 清除现有标记
        this.clearMarkers();

        // 为每个记录添加标记
        records.forEach(record => {
            const marker = new AMap.Marker({
                position: [record.longitude, record.latitude],
                title: record.pickup_location,
                icon: new AMap.Icon({
                    size: new AMap.Size(32, 32),
                    image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
                    imageSize: new AMap.Size(32, 32)
                })
            });

            // 点击标记显示信息窗体
            marker.on('click', () => {
                this.showRecordInfo(record, marker);
            });

            this.map.add(marker);
            this.markers.push(marker);
        });

        // 如果有记录，调整地图视野
        if (records.length > 0) {
            this.map.setFitView(this.markers, false, [20, 20, 20, 20]);
        }
    }

    showRecordInfo(record, marker) {
        const itemsHtml = record.items.map(item => 
            `<span class="item-tag">${item}</span>`
        ).join('');

        const content = `
            <div class="record-info-window">
                <h6>${record.pickup_location}</h6>
                <div class="items">${itemsHtml}</div>
                <p><small>拾获时间: ${record.created_time}</small></p>
                <p><small>探员: ${record.agent_username}</small></p>
                <div class="mt-2">
                    <button class="btn btn-sm btn-primary" onclick="mapSearch.showRecordDetail(${record.record_id})">
                        查看详情
                    </button>
                </div>
            </div>
        `;

        this.infoWindow.setContent(content);
        this.infoWindow.open(this.map, marker.getPosition());
    }

    async showRecordDetail(recordId) {
        try {
            // 从当前记录中找到详细信息
            const record = this.allRecords.find(r => r.record_id === recordId);
            if (!record) {
                throw new Error('记录不存在');
            }

            const itemsHtml = record.items.map(item => 
                `<span class="badge bg-primary me-1">${item}</span>`
            ).join('');

            const content = `
                <div class="row">
                    <div class="col-12">
                        <h5>拾获地点: ${record.pickup_location}</h5>
                        ${record.formatted_address ? `<p class="text-muted">${record.formatted_address}</p>` : ''}
                    </div>
                    <div class="col-12 mt-3">
                        <strong>拾获物品:</strong>
                        <div class="mt-2">${itemsHtml}</div>
                    </div>
                    <div class="col-12 mt-3">
                        <strong>详细描述:</strong>
                        <p class="mt-2">${record.detailed_description}</p>
                    </div>
                    <div class="col-12 mt-3">
                        <div class="row">
                            <div class="col-6">
                                <strong>拾获时间:</strong>
                                <p>${record.created_time}</p>
                            </div>
                            <div class="col-6">
                                <strong>探员:</strong>
                                <p>${record.agent_username}</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.getElementById('recordDetailContent').innerHTML = content;
            document.getElementById('viewInListBtn').href = `/items/search?record_id=${recordId}`;
            
            const modal = new bootstrap.Modal(document.getElementById('recordDetailModal'));
            modal.show();

        } catch (error) {
            console.error('显示记录详情失败:', error);
            alert('显示记录详情失败: ' + error.message);
        }
    }

    getCurrentLocation() {
        const btn = document.getElementById('current-location-btn');
        const originalText = btn.innerHTML;
        
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 定位中...';
        btn.disabled = true;

        this.geolocation.getCurrentPosition((status, result) => {
            btn.innerHTML = originalText;
            btn.disabled = false;

            if (status === 'complete') {
                this.currentLocation = {
                    longitude: result.position.lng,
                    latitude: result.position.lat,
                    address: result.formattedAddress || '当前位置'
                };

                // 在地图上显示当前位置
                this.showCurrentLocation();
                
                // 搜索附近记录
                this.searchNearbyRecords();

                // 移动地图到当前位置
                this.map.setCenter([this.currentLocation.longitude, this.currentLocation.latitude]);
                this.map.setZoom(15);

            } else {
                console.error('定位失败:', result);
                this.showError('定位失败: ' + (result.message || '请检查GPS权限'));
            }
        });
    }

    showCurrentLocation() {
        // 移除之前的当前位置标记
        if (this.currentLocationMarker) {
            this.map.remove(this.currentLocationMarker);
        }

        // 添加当前位置标记
        this.currentLocationMarker = new AMap.Marker({
            position: [this.currentLocation.longitude, this.currentLocation.latitude],
            title: '我的位置',
            icon: new AMap.Icon({
                size: new AMap.Size(36, 36),
                image: 'https://webapi.amap.com/theme/v1.3/markers/n/loc.png',
                imageSize: new AMap.Size(36, 36)
            })
        });

        this.map.add(this.currentLocationMarker);
    }

    async searchNearbyRecords() {
        if (!this.currentLocation) {
            return;
        }

        try {
            const radius = document.getElementById('search-radius').value;
            
            const response = await fetch('/api/map/nearby', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    latitude: this.currentLocation.latitude,
                    longitude: this.currentLocation.longitude,
                    radius: parseFloat(radius)
                })
            });

            const result = await response.json();

            if (result.success) {
                this.displayNearbyRecords(result.data);
            } else {
                throw new Error(result.message || '搜索附近记录失败');
            }

        } catch (error) {
            console.error('搜索附近记录失败:', error);
            this.showError('搜索附近记录失败: ' + error.message);
        }
    }

    displayNearbyRecords(records) {
        const recordsList = document.getElementById('records-list');
        const recordsCount = document.getElementById('records-count');
        
        recordsCount.textContent = records.length;

        if (records.length === 0) {
            recordsList.innerHTML = '<div class="col-12 text-center text-muted">附近没有找到拾获记录</div>';
            return;
        }

        const recordsHtml = records.map(record => {
            const itemsHtml = record.items.map(item => 
                `<span class="badge bg-primary me-1">${item}</span>`
            ).join('');

            return `
                <div class="col-12 col-md-6 col-lg-4">
                    <div class="card h-100">
                        <div class="card-body">
                            <h6 class="card-title">${record.pickup_location}</h6>
                            <div class="mb-2">${itemsHtml}</div>
                            <p class="card-text small text-muted">${record.detailed_description}</p>
                            <div class="d-flex justify-content-between align-items-center">
                                <small class="text-muted">${Math.round(record.distance)}米</small>
                                <button class="btn btn-sm btn-outline-primary" 
                                        onclick="mapSearch.focusOnRecord(${record.record_id})">
                                    在地图中查看
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        recordsList.innerHTML = recordsHtml;
    }

    focusOnRecord(recordId) {
        const record = this.allRecords.find(r => r.record_id === recordId);
        if (record) {
            const marker = this.markers.find(m => 
                m.getPosition().lng === record.longitude && 
                m.getPosition().lat === record.latitude
            );
            
            if (marker) {
                this.map.setCenter([record.longitude, record.latitude]);
                this.map.setZoom(16);
                this.showRecordInfo(record, marker);
            }
        }
    }

    filterRecords(keyword) {
        if (!keyword.trim()) {
            this.displayRecordsOnMap(this.allRecords);
            return;
        }

        const filtered = this.allRecords.filter(record => 
            record.items.some(item => 
                item.toLowerCase().includes(keyword.toLowerCase())
            ) ||
            record.pickup_location.toLowerCase().includes(keyword.toLowerCase())
        );

        this.displayRecordsOnMap(filtered);
    }

    clearMarkers() {
        this.markers.forEach(marker => {
            this.map.remove(marker);
        });
        this.markers = [];
    }

    showError(message) {
        const alertHtml = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = document.querySelector('.container-fluid');
        container.insertAdjacentHTML('afterbegin', alertHtml);
    }
}

// 全局变量，供模板中的onclick调用
let mapSearch;

// 初始化地图搜索模块
document.addEventListener('DOMContentLoaded', () => {
    mapSearch = new MapSearchModule();
});