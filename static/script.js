// Liberation System - JavaScript

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Liberation System Web Interface Initialized');
    
    // Initialize WebSocket connection
    initializeWebSocket();
    
    // Setup event listeners
    setupEventListeners();
    
    // Start periodic updates
    startPeriodicUpdates();
});

// WebSocket connection for real-time updates
let socket = null;

function initializeWebSocket() {
    // Connect to WebSocket server
    const wsUrl = `ws://${window.location.host}/ws`;
    socket = new WebSocket(wsUrl);
    
    socket.onopen = function(event) {
        console.log('🔗 WebSocket connected');
        updateStatus('Connected to Liberation System');
    };
    
    socket.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        } catch (error) {
            console.error('❌ Error parsing WebSocket message:', error);
        }
    };
    
    socket.onclose = function(event) {
        console.log('🔌 WebSocket disconnected');
        updateStatus('Disconnected from Liberation System');
        
        // Attempt to reconnect after 5 seconds
        setTimeout(initializeWebSocket, 5000);
    };
    
    socket.onerror = function(error) {
        console.error('❌ WebSocket error:', error);
        updateStatus('Connection error');
    };
}

function handleWebSocketMessage(data) {
    switch(data.type) {
        case 'system_update':
            updateSystemStatus(data.payload);
            break;
        case 'resource_update':
            updateResourceDisplay(data.payload);
            break;
        case 'mesh_update':
            updateMeshStatus(data.payload);
            break;
        case 'truth_update':
            updateTruthStatus(data.payload);
            break;
        default:
            console.log('📨 Unknown message type:', data.type);
    }
}

// Setup event listeners for buttons
function setupEventListeners() {
    const buttons = document.querySelectorAll('.control-btn');
    buttons.forEach(button => {
        button.addEventListener('click', handleButtonClick);
    });
}

function handleButtonClick(event) {
    const action = event.target.dataset.action;
    const button = event.target;
    
    // Disable button during operation
    button.disabled = true;
    button.textContent = 'Processing...';
    
    // Send API request
    performAction(action).then(result => {
        console.log(`✅ Action ${action} completed:`, result);
        updateStatus(`Action ${action} completed successfully`);
    }).catch(error => {
        console.error(`❌ Action ${action} failed:`, error);
        updateStatus(`Action ${action} failed: ${error.message}`);
    }).finally(() => {
        // Re-enable button
        button.disabled = false;
        button.textContent = button.dataset.originalText || 'Action';
    });
}

// API functions
async function performAction(action) {
    const response = await fetch(`/api/${action}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

async function fetchSystemStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        updateSystemStatus(data);
    } catch (error) {
        console.error('❌ Failed to fetch system status:', error);
    }
}

async function fetchResourceStatus() {
    try {
        const response = await fetch('/api/resources');
        const data = await response.json();
        updateResourceDisplay(data);
    } catch (error) {
        console.error('❌ Failed to fetch resource status:', error);
    }
}

// Update functions
function updateSystemStatus(data) {
    const statusElement = document.getElementById('system-status');
    if (statusElement) {
        statusElement.innerHTML = `
            <div class="status-item">
                <span class="status-label">System:</span>
                <span class="status-value ${data.system_active ? 'active' : 'inactive'}">
                    ${data.system_active ? 'ACTIVE' : 'INACTIVE'}
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">Uptime:</span>
                <span class="status-value">${data.uptime || 'N/A'}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Version:</span>
                <span class="status-value">${data.version || '1.0.0'}</span>
            </div>
        `;
    }
}

function updateResourceDisplay(data) {
    const resourceElement = document.getElementById('resource-pool');
    if (resourceElement) {
        const utilization = ((data.allocated_resources / data.total_resources) * 100).toFixed(6);
        resourceElement.innerHTML = `
            <div class="resource-item">
                <span class="resource-label">Total Resources:</span>
                <span class="resource-value">${formatNumber(data.total_resources)}</span>
            </div>
            <div class="resource-item">
                <span class="resource-label">Available:</span>
                <span class="resource-value">${formatNumber(data.available_resources)}</span>
            </div>
            <div class="resource-item">
                <span class="resource-label">Allocated:</span>
                <span class="resource-value">${formatNumber(data.allocated_resources)}</span>
            </div>
            <div class="resource-item">
                <span class="resource-label">Utilization:</span>
                <span class="resource-value">${utilization}%</span>
            </div>
        `;
    }
}

function updateMeshStatus(data) {
    const meshElement = document.getElementById('mesh-network');
    if (meshElement) {
        meshElement.innerHTML = `
            <div class="mesh-item">
                <span class="mesh-label">Active Nodes:</span>
                <span class="mesh-value">${data.active_nodes || 0}</span>
            </div>
            <div class="mesh-item">
                <span class="mesh-label">Total Connections:</span>
                <span class="mesh-value">${data.total_connections || 0}</span>
            </div>
            <div class="mesh-item">
                <span class="mesh-label">Network Health:</span>
                <span class="mesh-value">${(data.network_health * 100).toFixed(1)}%</span>
            </div>
        `;
    }
}

function updateTruthStatus(data) {
    const truthElement = document.getElementById('truth-channels');
    if (truthElement) {
        truthElement.innerHTML = `
            <div class="truth-item">
                <span class="truth-label">Active Channels:</span>
                <span class="truth-value">${data.active_channels || 0}</span>
            </div>
            <div class="truth-item">
                <span class="truth-label">Total Subscribers:</span>
                <span class="truth-value">${data.total_subscribers || 0}</span>
            </div>
            <div class="truth-item">
                <span class="truth-label">Last Spread:</span>
                <span class="truth-value">${data.last_spread || 'Never'}</span>
            </div>
        `;
    }
}

function updateStatus(message) {
    const statusElement = document.getElementById('status-message');
    if (statusElement) {
        statusElement.textContent = message;
        statusElement.className = 'status-message';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            statusElement.textContent = '';
            statusElement.className = '';
        }, 5000);
    }
}

// Utility functions
function formatNumber(num) {
    if (num >= 1e12) {
        return (num / 1e12).toFixed(2) + 'T';
    } else if (num >= 1e9) {
        return (num / 1e9).toFixed(2) + 'B';
    } else if (num >= 1e6) {
        return (num / 1e6).toFixed(2) + 'M';
    } else if (num >= 1e3) {
        return (num / 1e3).toFixed(2) + 'K';
    }
    return num.toString();
}

// Periodic updates
function startPeriodicUpdates() {
    // Update system status every 5 seconds
    setInterval(fetchSystemStatus, 5000);
    
    // Update resource status every 10 seconds
    setInterval(fetchResourceStatus, 10000);
    
    // Initial fetch
    fetchSystemStatus();
    fetchResourceStatus();
}

// Export functions for global access
window.LiberationSystem = {
    performAction,
    fetchSystemStatus,
    fetchResourceStatus,
    updateStatus
};
