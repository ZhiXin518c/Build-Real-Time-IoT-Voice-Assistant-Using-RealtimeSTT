// Voice Assistant Web Interface JavaScript

class VoiceAssistantUI {
    constructor() {
        this.isAssistantActive = false;
        this.eventSource = null;
        this.devices = [];
        this.events = [];
        
        this.initializeElements();
        this.bindEvents();
        this.loadInitialData();
        this.startEventPolling();
    }
    
    initializeElements() {
        // Control elements
        this.startBtn = document.getElementById('startBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.wakeWordsSelect = document.getElementById('wakeWords');
        this.modelSelect = document.getElementById('model');
        this.testBtn = document.getElementById('testBtn');
        this.testCommandInput = document.getElementById('testCommand');
        
        // Status elements
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusText = this.statusIndicator.querySelector('.status-text');
        
        // Transcription elements
        this.transcriptionDisplay = document.getElementById('transcriptionDisplay');
        this.clearTranscriptionBtn = document.getElementById('clearTranscription');
        
        // Device elements
        this.devicesGrid = document.getElementById('devicesGrid');
        this.refreshDevicesBtn = document.getElementById('refreshDevices');
        this.addDeviceBtn = document.getElementById('addDevice');
        this.locationFilter = document.getElementById('locationFilter');
        this.typeFilter = document.getElementById('typeFilter');
        
        // Activity elements
        this.activityLog = document.getElementById('activityLog');
        this.eventFilter = document.getElementById('eventFilter');
        this.clearLogBtn = document.getElementById('clearLog');
        
        // Modal elements
        this.deviceModal = document.getElementById('deviceModal');
        this.addDeviceModal = document.getElementById('addDeviceModal');
        this.closeModalBtn = document.getElementById('closeModal');
        this.closeAddModalBtn = document.getElementById('closeAddModal');
        this.addDeviceForm = document.getElementById('addDeviceForm');
        this.cancelAddBtn = document.getElementById('cancelAdd');
    }
    
    bindEvents() {
        // Voice assistant controls
        this.startBtn.addEventListener('click', () => this.startAssistant());
        this.stopBtn.addEventListener('click', () => this.stopAssistant());
        this.testBtn.addEventListener('click', () => this.testCommand());
        
        // Transcription controls
        this.clearTranscriptionBtn.addEventListener('click', () => this.clearTranscription());
        
        // Device controls
        this.refreshDevicesBtn.addEventListener('click', () => this.loadDevices());
        this.addDeviceBtn.addEventListener('click', () => this.showAddDeviceModal());
        this.locationFilter.addEventListener('change', () => this.filterDevices());
        this.typeFilter.addEventListener('change', () => this.filterDevices());
        
        // Activity controls
        this.eventFilter.addEventListener('change', () => this.filterEvents());
        this.clearLogBtn.addEventListener('click', () => this.clearEvents());
        
        // Modal controls
        this.closeModalBtn.addEventListener('click', () => this.hideDeviceModal());
        this.closeAddModalBtn.addEventListener('click', () => this.hideAddDeviceModal());
        this.cancelAddBtn.addEventListener('click', () => this.hideAddDeviceModal());
        this.addDeviceForm.addEventListener('submit', (e) => this.handleAddDevice(e));
        
        // Click outside modal to close
        this.deviceModal.addEventListener('click', (e) => {
            if (e.target === this.deviceModal) this.hideDeviceModal();
        });
        this.addDeviceModal.addEventListener('click', (e) => {
            if (e.target === this.addDeviceModal) this.hideAddDeviceModal();
        });
        
        // Enter key for test command
        this.testCommandInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.testCommand();
        });
    }
    
    async loadInitialData() {
        await this.loadDevices();
        await this.loadEvents();
        await this.checkAssistantStatus();
    }
    
    startEventPolling() {
        // Poll for events every 2 seconds
        setInterval(() => {
            if (this.isAssistantActive) {
                this.loadEvents();
            }
        }, 2000);
        
        // Poll for status every 5 seconds
        setInterval(() => {
            this.checkAssistantStatus();
        }, 5000);
    }
    
    async startAssistant() {
        try {
            this.setLoading(this.startBtn, true);
            
            const response = await fetch('/api/voice/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    wake_words: this.wakeWordsSelect.value,
                    model: this.modelSelect.value
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.isAssistantActive = true;
                this.updateStatus('active', 'Voice assistant started');
                this.startBtn.disabled = true;
                this.stopBtn.disabled = false;
                this.showNotification('Voice assistant started successfully', 'success');
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            console.error('Error starting assistant:', error);
            this.showNotification('Failed to start voice assistant', 'error');
        } finally {
            this.setLoading(this.startBtn, false);
        }
    }
    
    async stopAssistant() {
        try {
            this.setLoading(this.stopBtn, true);
            
            const response = await fetch('/api/voice/stop', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.isAssistantActive = false;
                this.updateStatus('offline', 'Voice assistant stopped');
                this.startBtn.disabled = false;
                this.stopBtn.disabled = true;
                this.showNotification('Voice assistant stopped', 'info');
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            console.error('Error stopping assistant:', error);
            this.showNotification('Failed to stop voice assistant', 'error');
        } finally {
            this.setLoading(this.stopBtn, false);
        }
    }
    
    async testCommand() {
        const command = this.testCommandInput.value.trim();
        if (!command) {
            this.showNotification('Please enter a command to test', 'warning');
            return;
        }
        
        try {
            this.setLoading(this.testBtn, true);
            
            const response = await fetch('/api/voice/test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: command })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Command processed successfully', 'success');
                this.testCommandInput.value = '';
                // Refresh events to see the result
                setTimeout(() => this.loadEvents(), 500);
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            console.error('Error testing command:', error);
            this.showNotification('Failed to test command', 'error');
        } finally {
            this.setLoading(this.testBtn, false);
        }
    }
    
    async checkAssistantStatus() {
        try {
            const response = await fetch('/api/voice/status');
            const data = await response.json();
            
            if (data.success) {
                const status = data.status;
                this.isAssistantActive = status.is_active;
                
                if (status.is_active) {
                    if (status.is_listening) {
                        this.updateStatus('listening', 'Listening...');
                    } else {
                        this.updateStatus('active', 'Active');
                    }
                    this.startBtn.disabled = true;
                    this.stopBtn.disabled = false;
                } else {
                    this.updateStatus('offline', 'Offline');
                    this.startBtn.disabled = false;
                    this.stopBtn.disabled = true;
                }
            }
        } catch (error) {
            console.error('Error checking status:', error);
        }
    }
    
    updateStatus(status, text) {
        this.statusIndicator.className = `status-indicator ${status}`;
        this.statusText.textContent = text;
    }
    
    async loadDevices() {
        try {
            const response = await fetch('/api/devices/');
            const data = await response.json();
            
            if (data.success) {
                this.devices = Object.values(data.devices);
                this.renderDevices();
                this.updateFilters();
            }
        } catch (error) {
            console.error('Error loading devices:', error);
            this.showNotification('Failed to load devices', 'error');
        }
    }
    
    renderDevices() {
        const filteredDevices = this.getFilteredDevices();
        
        if (filteredDevices.length === 0) {
            this.devicesGrid.innerHTML = `
                <div class="no-devices">
                    <i class="fas fa-home"></i>
                    <p>No devices found</p>
                </div>
            `;
            return;
        }
        
        this.devicesGrid.innerHTML = filteredDevices.map(device => `
            <div class="device-card" onclick="app.showDeviceDetails('${device.id}')">
                <div class="device-header">
                    <div class="device-info">
                        <h4>${device.name}</h4>
                        <span class="device-type">${device.device_type}</span>
                    </div>
                    <span class="device-status ${device.status}">${device.status}</span>
                </div>
                <div class="device-location">
                    <i class="fas fa-map-marker-alt"></i>
                    ${device.location}
                </div>
                <div class="device-controls-inline">
                    ${this.getDeviceControls(device)}
                </div>
            </div>
        `).join('');
    }
    
    getDeviceControls(device) {
        const controls = [];
        
        if (device.status === 'off') {
            controls.push(`<button class="btn btn-primary btn-small" onclick="event.stopPropagation(); app.controlDevice('${device.id}', 'turn_on')">
                <i class="fas fa-power-off"></i> Turn On
            </button>`);
        } else {
            controls.push(`<button class="btn btn-secondary btn-small" onclick="event.stopPropagation(); app.controlDevice('${device.id}', 'turn_off')">
                <i class="fas fa-power-off"></i> Turn Off
            </button>`);
        }
        
        return controls.join('');
    }
    
    getFilteredDevices() {
        let filtered = this.devices;
        
        const locationFilter = this.locationFilter.value;
        const typeFilter = this.typeFilter.value;
        
        if (locationFilter) {
            filtered = filtered.filter(device => device.location === locationFilter);
        }
        
        if (typeFilter) {
            filtered = filtered.filter(device => device.device_type === typeFilter);
        }
        
        return filtered;
    }
    
    updateFilters() {
        // Update location filter
        const locations = [...new Set(this.devices.map(device => device.location))];
        this.locationFilter.innerHTML = '<option value="">All Locations</option>' +
            locations.map(location => `<option value="${location}">${location}</option>`).join('');
        
        // Update type filter
        const types = [...new Set(this.devices.map(device => device.device_type))];
        this.typeFilter.innerHTML = '<option value="">All Types</option>' +
            types.map(type => `<option value="${type}">${type}</option>`).join('');
    }
    
    filterDevices() {
        this.renderDevices();
    }
    
    async controlDevice(deviceId, action, params = {}) {
        try {
            const response = await fetch(`/api/devices/${deviceId}/control`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ action, ...params })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification(data.message, 'success');
                await this.loadDevices(); // Refresh devices
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            console.error('Error controlling device:', error);
            this.showNotification('Failed to control device', 'error');
        }
    }
    
    async showDeviceDetails(deviceId) {
        const device = this.devices.find(d => d.id === deviceId);
        if (!device) return;
        
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        
        modalTitle.textContent = device.name;
        modalBody.innerHTML = `
            <div class="device-details">
                <div class="detail-row">
                    <strong>Type:</strong> ${device.device_type}
                </div>
                <div class="detail-row">
                    <strong>Location:</strong> ${device.location}
                </div>
                <div class="detail-row">
                    <strong>Status:</strong> <span class="device-status ${device.status}">${device.status}</span>
                </div>
                <div class="detail-row">
                    <strong>Last Updated:</strong> ${new Date(device.last_updated * 1000).toLocaleString()}
                </div>
                ${device.properties ? `
                    <div class="detail-row">
                        <strong>Properties:</strong>
                        <pre>${JSON.stringify(device.properties, null, 2)}</pre>
                    </div>
                ` : ''}
                <div class="device-actions">
                    <button class="btn btn-primary" onclick="app.controlDevice('${device.id}', 'turn_on')">Turn On</button>
                    <button class="btn btn-secondary" onclick="app.controlDevice('${device.id}', 'turn_off')">Turn Off</button>
                    <button class="btn btn-danger" onclick="app.removeDevice('${device.id}')">Remove Device</button>
                </div>
            </div>
        `;
        
        this.deviceModal.classList.add('show');
    }
    
    hideDeviceModal() {
        this.deviceModal.classList.remove('show');
    }
    
    showAddDeviceModal() {
        this.addDeviceModal.classList.add('show');
    }
    
    hideAddDeviceModal() {
        this.addDeviceModal.classList.remove('show');
        this.addDeviceForm.reset();
    }
    
    async handleAddDevice(e) {
        e.preventDefault();
        
        const formData = new FormData(this.addDeviceForm);
        const deviceData = {
            id: formData.get('deviceId') || document.getElementById('deviceId').value,
            name: formData.get('deviceName') || document.getElementById('deviceName').value,
            device_type: formData.get('deviceType') || document.getElementById('deviceType').value,
            location: formData.get('deviceLocation') || document.getElementById('deviceLocation').value
        };
        
        try {
            const response = await fetch('/api/devices/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(deviceData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Device added successfully', 'success');
                this.hideAddDeviceModal();
                await this.loadDevices();
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            console.error('Error adding device:', error);
            this.showNotification('Failed to add device', 'error');
        }
    }
    
    async removeDevice(deviceId) {
        if (!confirm('Are you sure you want to remove this device?')) return;
        
        try {
            const response = await fetch(`/api/devices/${deviceId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Device removed successfully', 'success');
                this.hideDeviceModal();
                await this.loadDevices();
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            console.error('Error removing device:', error);
            this.showNotification('Failed to remove device', 'error');
        }
    }
    
    async loadEvents() {
        try {
            const response = await fetch('/api/voice/events?limit=50');
            const data = await response.json();
            
            if (data.success) {
                this.events = data.events;
                this.renderEvents();
                this.updateTranscription();
            }
        } catch (error) {
            console.error('Error loading events:', error);
        }
    }
    
    renderEvents() {
        const filteredEvents = this.getFilteredEvents();
        
        if (filteredEvents.length === 0) {
            this.activityLog.innerHTML = `
                <div class="no-events">
                    <i class="fas fa-history"></i>
                    <p>No events found</p>
                </div>
            `;
            return;
        }
        
        this.activityLog.innerHTML = filteredEvents.map(event => `
            <div class="activity-item">
                <div class="activity-header">
                    <span class="activity-type ${event.type}">${event.type}</span>
                    <span class="activity-timestamp">${new Date(event.timestamp * 1000).toLocaleString()}</span>
                </div>
                <div class="activity-message">${event.message}</div>
                ${event.data && Object.keys(event.data).length > 0 ? `
                    <div class="activity-details">${JSON.stringify(event.data, null, 2)}</div>
                ` : ''}
            </div>
        `).join('');
    }
    
    getFilteredEvents() {
        const filter = this.eventFilter.value;
        if (!filter) return this.events;
        return this.events.filter(event => event.type === filter);
    }
    
    filterEvents() {
        this.renderEvents();
    }
    
    updateTranscription() {
        const transcriptionEvents = this.events.filter(event => 
            event.type === 'transcription_final' || event.type === 'transcription_partial'
        );
        
        if (transcriptionEvents.length === 0) {
            if (!this.isAssistantActive) {
                this.transcriptionDisplay.innerHTML = `
                    <div class="placeholder">
                        <i class="fas fa-microphone-slash"></i>
                        <p>Voice assistant is not active. Start the assistant to see transcriptions.</p>
                    </div>
                `;
            } else {
                this.transcriptionDisplay.innerHTML = `
                    <div class="placeholder">
                        <i class="fas fa-microphone"></i>
                        <p>Waiting for voice input...</p>
                    </div>
                `;
            }
            return;
        }
        
        this.transcriptionDisplay.innerHTML = transcriptionEvents.slice(-10).map(event => `
            <div class="transcription-item ${event.type === 'transcription_partial' ? 'partial' : ''}">
                <div class="timestamp">${new Date(event.timestamp * 1000).toLocaleString()}</div>
                <div class="text">${event.message}</div>
            </div>
        `).join('');
        
        // Scroll to bottom
        this.transcriptionDisplay.scrollTop = this.transcriptionDisplay.scrollHeight;
    }
    
    clearTranscription() {
        this.transcriptionDisplay.innerHTML = `
            <div class="placeholder">
                <i class="fas fa-microphone"></i>
                <p>Transcription cleared. ${this.isAssistantActive ? 'Waiting for voice input...' : 'Start the assistant to see transcriptions.'}</p>
            </div>
        `;
    }
    
    async clearEvents() {
        try {
            const response = await fetch('/api/voice/events/clear', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.events = [];
                this.renderEvents();
                this.clearTranscription();
                this.showNotification('Events cleared', 'info');
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            console.error('Error clearing events:', error);
            this.showNotification('Failed to clear events', 'error');
        }
    }
    
    setLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            const icon = button.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-spinner fa-spin';
            }
        } else {
            button.disabled = false;
            const icon = button.querySelector('i');
            if (icon) {
                // Restore original icon based on button
                if (button === this.startBtn) {
                    icon.className = 'fas fa-play';
                } else if (button === this.stopBtn) {
                    icon.className = 'fas fa-stop';
                } else if (button === this.testBtn) {
                    icon.className = 'fas fa-play-circle';
                }
            }
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => document.body.removeChild(notification), 300);
        }, 3000);
    }
    
    getNotificationIcon(type) {
        switch (type) {
            case 'success': return 'fa-check-circle';
            case 'error': return 'fa-exclamation-circle';
            case 'warning': return 'fa-exclamation-triangle';
            default: return 'fa-info-circle';
        }
    }
}

// Initialize the application
const app = new VoiceAssistantUI();

// Add notification styles
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        padding: 16px;
        z-index: 1001;
        transform: translateX(100%);
        transition: transform 0.3s ease-in-out;
        max-width: 400px;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .notification-success {
        border-left: 4px solid var(--success-color);
    }
    
    .notification-error {
        border-left: 4px solid var(--danger-color);
    }
    
    .notification-warning {
        border-left: 4px solid var(--warning-color);
    }
    
    .notification-info {
        border-left: 4px solid var(--primary-color);
    }
    
    .notification i {
        font-size: 18px;
    }
    
    .notification-success i {
        color: var(--success-color);
    }
    
    .notification-error i {
        color: var(--danger-color);
    }
    
    .notification-warning i {
        color: var(--warning-color);
    }
    
    .notification-info i {
        color: var(--primary-color);
    }
    
    .no-devices, .no-events {
        text-align: center;
        padding: 40px;
        color: var(--text-muted);
    }
    
    .no-devices i, .no-events i {
        font-size: 48px;
        margin-bottom: 16px;
        display: block;
    }
    
    .device-details .detail-row {
        margin-bottom: 12px;
        padding: 8px 0;
        border-bottom: 1px solid var(--border-color);
    }
    
    .device-details .detail-row:last-child {
        border-bottom: none;
    }
    
    .device-details pre {
        background: var(--bg-tertiary);
        padding: 8px;
        border-radius: 4px;
        font-size: 12px;
        margin-top: 8px;
    }
    
    .device-actions {
        margin-top: 20px;
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }
    
    .btn-danger {
        background: var(--danger-color);
        color: white;
    }
    
    .btn-danger:hover {
        background: #dc2626;
    }
`;

// Add styles to head
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

