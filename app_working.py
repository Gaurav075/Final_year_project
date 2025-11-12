# app_with_reset_button.py
# ADDED - Reset button to clear river data

from flask import Flask, jsonify, render_template_string, request, send_file
from flask_cors import CORS
from datetime import datetime
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from io import BytesIO, StringIO
import csv
import statistics

import robot_controller_final_fixed as rc

app = Flask(__name__)
CORS(app)

# ==================== RIVER NAMES STORAGE ====================

RIVER_NAMES_FILE = "river_names.json"

def load_river_names():
    """Load custom river names"""
    if os.path.exists(RIVER_NAMES_FILE):
        try:
            with open(RIVER_NAMES_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "river1": "River 1",
        "river2": "River 2",
        "river3": "River 3",
        "river4": "River 4",
        "river5": "River 5"
    }

def save_river_names(names):
    """Save custom river names"""
    try:
        with open(RIVER_NAMES_FILE, 'w') as f:
            json.dump(names, f, indent=2)
        return True
    except:
        return False

river_names = load_river_names()

# ==================== DASHBOARD WITH RESET BUTTON ====================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Aquatic Waste Collector</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%);
            min-height: 100vh;
            display: flex;
            color: #333;
        }
        
        .sidebar {
            width: 280px;
            background: rgba(0,0,0,0.9);
            color: white;
            padding: 25px;
            height: 100vh;
            overflow-y: auto;
            box-shadow: 5px 0 15px rgba(0,0,0,0.3);
            position: fixed;
        }
        
        .sidebar h2 {
            text-align: center;
            margin-bottom: 25px;
            font-size: 1.4em;
            color: #00d4ff;
        }
        
        .river-item {
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 8px 0;
        }
        
        .river-btn {
            flex: 1;
            padding: 12px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: 2px solid transparent;
            color: white;
            cursor: pointer;
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .river-btn:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(102,126,234,0.4);
        }
        
        .river-btn.active {
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            box-shadow: 0 0 20px rgba(0,212,255,0.6);
        }
        
        .download-options {
            display: flex;
            gap: 5px;
        }
        
        .download-btn {
            padding: 8px 10px;
            background: #4caf50;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 0.9em;
            transition: all 0.3s;
        }
        
        .download-btn.pdf {
            background: #f44336;
        }
        
        .download-btn:hover {
            transform: scale(1.05);
        }
        
        .controls-section {
            margin-top: 35px;
            padding-top: 25px;
            border-top: 1px solid rgba(255,255,255,0.2);
        }
        
        .control-label {
            display: block;
            margin: 15px 0 8px;
            font-weight: bold;
            color: #00d4ff;
        }
        
        .duration-input {
            width: 100%;
            padding: 10px;
            border: 2px solid #667eea;
            border-radius: 6px;
            background: rgba(255,255,255,0.1);
            color: white;
            font-weight: bold;
            margin-bottom: 15px;
        }
        
        .control-btn {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: none;
            color: white;
            cursor: pointer;
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s;
            text-transform: uppercase;
        }
        
        .control-btn.start {
            background: linear-gradient(135deg, #4caf50, #45a049);
        }
        
        .control-btn.start:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(76,175,80,0.5);
        }
        
        .control-btn.stop {
            background: linear-gradient(135deg, #f44336, #da190b);
        }
        
        .control-btn.stop:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(244,67,54,0.5);
        }
        
        /* NEW: Reset button styling */
        .control-btn.reset {
            background: linear-gradient(135deg, #ff9800, #f57c00);
            margin-top: 15px;
        }
        
        .control-btn.reset:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255,152,0,0.5);
        }
        
        .main-content {
            margin-left: 280px;
            flex: 1;
            padding: 30px;
            overflow-y: auto;
        }
        
        header {
            background: rgba(255,255,255,0.95);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        header h1 {
            color: #1e3c72;
            font-size: 2em;
            margin: 0;
        }
        
        header p {
            color: #666;
            margin: 8px 0 0 0;
            font-size: 1em;
        }
        
        .header-actions {
            display: flex;
            gap: 10px;
        }
        
        .reset-btn-header {
            padding: 10px 20px;
            background: linear-gradient(135deg, #ff9800, #f57c00);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .reset-btn-header:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(255,152,0,0.4);
        }
        
        .robot-status {
            background: linear-gradient(135deg, rgba(0,212,255,0.1), rgba(126,34,206,0.1));
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #00d4ff;
        }
        
        .status-item {
            display: inline-block;
            background: rgba(255,255,255,0.9);
            padding: 12px 18px;
            margin: 8px 12px 8px 0;
            border-radius: 8px;
            font-weight: bold;
            color: #1e3c72;
            border-left: 3px solid #667eea;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255,255,255,0.95);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
            min-height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .card:hover {
            transform: translateY(-10px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.15);
        }
        
        .card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1em;
            text-transform: uppercase;
            font-weight: bold;
        }
        
        .value {
            font-size: 2.5em;
            font-weight: bold;
            color: #1e3c72;
            margin: 10px 0;
        }
        
        .label {
            color: #999;
            font-size: 0.95em;
            margin-top: 8px;
        }
        
        .chart-container {
            background: rgba(255,255,255,0.95);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            margin-bottom: 25px;
            border-top: 3px solid #667eea;
        }
        
        .chart-wrapper {
            position: relative;
            height: 350px;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .modal.active { display: flex; }
        
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 15px;
            max-width: 500px;
            width: 90%;
        }
        
        .modal-content h2 {
            color: #1e3c72;
            margin-bottom: 20px;
        }
        
        .modal-input {
            width: 100%;
            padding: 12px;
            border: 2px solid #667eea;
            border-radius: 8px;
            font-size: 1em;
            margin-bottom: 20px;
        }
        
        .modal-buttons {
            display: flex;
            gap: 10px;
        }
        
        .modal-buttons button {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }
        
        .save-btn {
            background: #4caf50;
            color: white;
        }
        
        .cancel-btn {
            background: #999;
            color: white;
        }
        
        .reset-confirm {
            background: #ff9800;
            color: white;
        }
        
        @media (max-width: 900px) {
            .dashboard { grid-template-columns: repeat(2, 1fr); }
        }
        
        @media (max-width: 768px) {
            .sidebar { width: 100%; height: auto; }
            .main-content { margin-left: 0; }
            .dashboard { grid-template-columns: 1fr; }
            header { flex-direction: column; align-items: flex-start; }
            .header-actions { margin-top: 15px; }
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>🌍 RIVERS</h2>
        <div id="rivers-container"></div>
        
        <div class="controls-section">
            <div class="control-label">⏱️ Duration (sec)</div>
            <input type="number" id="duration" class="duration-input" value="300" min="10" max="1800">
            <button class="control-btn start" onclick="startMission()">▶️ START</button>
            <button class="control-btn stop" onclick="stopMission()">⏹️ STOP</button>
            <button class="control-btn reset" onclick="openResetModal()">🔄 RESET</button>
        </div>
    </div>
    
    <div class="main-content">
        <header>
            <div>
                <h1>🤖 Aquatic Waste Collector</h1>
                <p id="river-title">📍 Monitoring: Select a river</p>
            </div>
            <div class="header-actions">
                <button class="reset-btn-header" onclick="openResetModal()" title="Reset current river data">🔄 RESET DATA</button>
            </div>
        </header>
        
        <div class="robot-status">
            <div class="status-item">🤖 <span id="robot-id">--</span></div>
            <div class="status-item" id="status-badge">🟡 IDLE</div>
            <div class="status-item">📊 <span id="mission-count">0</span></div>
            <div class="status-item">📈 <span id="data-count">0</span></div>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h3>📊 Quality Score</h3>
                <div class="value" id="score">--</div>
                <div class="label" id="status">--</div>
            </div>
            
            <div class="card">
                <h3>♻️ Total Waste</h3>
                <div class="value" id="waste-total">0.00</div>
                <div class="label">kg collected</div>
                <div class="label">Items: <span id="waste-items">0</span></div>
            </div>
            
            <div class="card">
                <h3>🌊 pH Level</h3>
                <div class="value" id="ph">--</div>
                <div class="label">Safe: 6.5-8.5</div>
            </div>
            
            <div class="card">
                <h3>💧 Turbidity</h3>
                <div class="value" id="turbidity">--</div>
                <div class="label">NTU</div>
            </div>
            
            <div class="card">
                <h3>🌡️ Temperature</h3>
                <div class="value" id="temp">--</div>
                <div class="label">°C</div>
            </div>
            
            <div class="card">
                <h3>⚗️ TDS Level</h3>
                <div class="value" id="tds">--</div>
                <div class="label">ppm</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>📈 Quality Score Trend</h3>
            <div class="chart-wrapper">
                <canvas id="chart1"></canvas>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>📊 Sensor Analysis</h3>
            <div class="chart-wrapper">
                <canvas id="chart2"></canvas>
            </div>
        </div>
    </div>
    
    <div class="modal" id="renameModal">
        <div class="modal-content">
            <h2>Rename River</h2>
            <input type="text" id="newRiverName" class="modal-input" placeholder="Enter new river name">
            <div class="modal-buttons">
                <button class="save-btn" onclick="saveRiverName()">Save</button>
                <button class="cancel-btn" onclick="closeModal()">Cancel</button>
            </div>
        </div>
    </div>
    
    <div class="modal" id="resetModal">
        <div class="modal-content">
            <h2>⚠️ Reset River Data</h2>
            <p style="color: #666; margin-bottom: 20px;">
                Are you sure you want to reset all data for the current river?<br><br>
                <strong>This action cannot be undone!</strong><br><br>
                All readings, waste data, and statistics will be cleared.
            </p>
            <div class="modal-buttons">
                <button class="reset-confirm" onclick="confirmReset()">🔄 RESET</button>
                <button class="cancel-btn" onclick="closeResetModal()">Cancel</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentRiver = 'river1';
        let renamingRiver = null;
        let chart1 = null, chart2 = null;
        
        async function loadRiverNames() {
            try {
                const res = await fetch('/api/river-names');
                const names = await res.json();
                renderRivers(names);
            } catch(e) {
                console.error(e);
            }
        }
        
        function renderRivers(names) {
            const container = document.getElementById('rivers-container');
            container.innerHTML = '';
            
            for (const [id, name] of Object.entries(names)) {
                const item = document.createElement('div');
                item.className = 'river-item';
                item.innerHTML = `
                    <button class="river-btn ${id === currentRiver ? 'active' : ''}" 
                            ondblclick="openRenameModal('${id}')"
                            onclick="selectRiver('${id}')">${name}</button>
                    <div class="download-options">
                        <button class="download-btn" onclick="downloadReport('${id}', 'csv')">📊</button>
                        <button class="download-btn pdf" onclick="downloadReport('${id}', 'pdf')">📄</button>
                    </div>
                `;
                container.appendChild(item);
            }
        }
        
        function selectRiver(river) {
            currentRiver = river;
            loadRiverNames();
            const activeBtn = document.querySelector('.river-btn.active');
            const riverName = activeBtn ? activeBtn.textContent.trim() : 'Unknown';
            document.getElementById('river-title').textContent = '📍 Monitoring: ' + riverName;
            fetchData();
        }
        
        function openRenameModal(river) {
            renamingRiver = river;
            document.getElementById('newRiverName').value = '';
            document.getElementById('renameModal').classList.add('active');
            document.getElementById('newRiverName').focus();
        }
        
        function closeModal() {
            document.getElementById('renameModal').classList.remove('active');
            renamingRiver = null;
        }
        
        /* NEW: Reset Modal Functions */
        function openResetModal() {
            document.getElementById('resetModal').classList.add('active');
        }
        
        function closeResetModal() {
            document.getElementById('resetModal').classList.remove('active');
        }
        
        async function confirmReset() {
            try {
                const res = await fetch(`/api/reset-river?river=${currentRiver}`, {method: 'POST'});
                const data = await res.json();
                if (data.status === 'success') {
                    alert('✅ River data reset successfully!');
                    closeResetModal();
                    fetchData();
                } else {
                    alert('❌ Error: ' + data.message);
                }
            } catch(e) {
                alert('❌ Error: ' + e.message);
            }
        }
        
        async function saveRiverName() {
            const newName = document.getElementById('newRiverName').value.trim();
            if (!newName) {
                alert('Please enter a name');
                return;
            }
            
            try {
                const res = await fetch('/api/rename-river', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ river: renamingRiver, name: newName })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    alert('✅ River renamed!');
                    closeModal();
                    loadRiverNames();
                    selectRiver(renamingRiver);
                } else {
                    alert('❌ Error: ' + data.message);
                }
            } catch(e) {
                alert('❌ Error: ' + e.message);
            }
        }
        
        async function downloadReport(river, format) {
            river = river || currentRiver;
            try {
                const endpoint = format === 'pdf' ? '/api/download-report-pdf' : '/api/download-report';
                window.location.href = `${endpoint}?river=${river}`;
            } catch(e) {
                alert('❌ Error: ' + e.message);
            }
        }
        
        async function startMission() {
            const duration = document.getElementById('duration').value;
            try {
                const res = await fetch(`/api/robot/start?river=${currentRiver}&duration=${duration}`, {method: 'POST'});
                const data = await res.json();
                alert('✅ ' + (data.message || 'Started'));
                fetchData();
            } catch(e) {
                alert('❌ Error: ' + e.message);
            }
        }
        
        async function stopMission() {
            try {
                const res = await fetch(`/api/robot/stop?river=${currentRiver}`, {method: 'POST'});
                const data = await res.json();
                alert('✅ ' + (data.message || 'Stopped'));
                fetchData();
            } catch(e) {
                alert('❌ Error: ' + e.message);
            }
        }
        
        async function fetchData() {
            try {
                const statusRes = await fetch(`/api/robot/status?river=${currentRiver}`);
                const status = await statusRes.json();
                
                if (!status.error) {
                    document.getElementById('robot-id').textContent = status.robot_id;
                    const badge = document.getElementById('status-badge');
                    if (status.is_running) {
                        badge.textContent = '🟢 RUNNING';
                        badge.style.background = 'rgba(76,175,80,0.2)';
                    } else {
                        badge.textContent = '🟡 IDLE';
                        badge.style.background = 'rgba(255,152,0,0.2)';
                    }
                    document.getElementById('mission-count').textContent = status.mission_count;
                    document.getElementById('data-count').textContent = status.data_points;
                    document.getElementById('waste-total').textContent = status.waste_collected.toFixed(2);
                    document.getElementById('waste-items').textContent = status.waste_items;
                }
                
                const res = await fetch(`/api/dashboard/summary?river=${currentRiver}`);
                const data = await res.json();
                
                if (data.current) {
                    document.getElementById('score').textContent = data.current.quality_score.toFixed(1);
                    document.getElementById('status').textContent = 'Status: ' + data.current.status;
                    document.getElementById('ph').textContent = data.current.pH.toFixed(2);
                    document.getElementById('turbidity').textContent = data.current.turbidity.toFixed(2);
                    document.getElementById('temp').textContent = data.current.temperature.toFixed(1);
                    document.getElementById('tds').textContent = data.current.TDS.toFixed(0);
                    updateCharts();
                }
            } catch(e) {
                console.error(e);
            }
        }
        
        async function updateCharts() {
            try {
                const res = await fetch(`/api/water-quality/latest?river=${currentRiver}`);
                const data = await res.json();
                
                if (data.data && data.data.length > 0) {
                    const readings = data.data;
                    const labels = readings.map(r => new Date(r.timestamp).toLocaleTimeString());
                    const scores = readings.map(r => r.water_quality.score);
                    const phVals = readings.map(r => r.sensor_readings.pH);
                    const turbVals = readings.map(r => r.sensor_readings.turbidity);
                    const tempVals = readings.map(r => r.sensor_readings.temperature);
                    
                    if (chart1) {
                        chart1.data.labels = labels;
                        chart1.data.datasets[0].data = scores;
                        chart1.update();
                    } else {
                        const ctx = document.getElementById('chart1').getContext('2d');
                        chart1 = new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: labels,
                                datasets: [{
                                    label: 'Quality',
                                    data: scores,
                                    borderColor: '#667eea',
                                    backgroundColor: 'rgba(102,126,234,0.1)',
                                    borderWidth: 2,
                                    fill: true,
                                    tension: 0.4
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                scales: { y: { beginAtZero: true, max: 100 } }
                            }
                        });
                    }
                    
                    if (chart2) {
                        chart2.data.labels = labels;
                        chart2.data.datasets[0].data = phVals;
                        chart2.data.datasets[1].data = turbVals;
                        chart2.data.datasets[2].data = tempVals;
                        chart2.update();
                    } else {
                        const ctx = document.getElementById('chart2').getContext('2d');
                        chart2 = new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: labels,
                                datasets: [
                                    { label: 'pH', data: phVals, borderColor: '#8bc34a', borderWidth: 2 },
                                    { label: 'Turbidity', data: turbVals, borderColor: '#ff9800', borderWidth: 2 },
                                    { label: 'Temp', data: tempVals, borderColor: '#f44336', borderWidth: 2 }
                                ]
                            },
                            options: { responsive: true, maintainAspectRatio: false }
                        });
                    }
                }
            } catch(e) {
                console.error(e);
            }
        }
        
        window.addEventListener('load', () => {
            loadRiverNames();
            selectRiver('river1');
            fetchData();
            setInterval(fetchData, 2000);
        });
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') saveRiverName();
            if (e.key === 'Escape') {
                closeModal();
                closeResetModal();
            }
        });
    </script>
</body>
</html>
"""

# ==================== ROUTES ====================

@app.route('/', methods=['GET'])
def home():
    return render_template_string(DASHBOARD_HTML)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "online"})

@app.route('/api/river-names', methods=['GET'])
def get_river_names():
    global river_names
    river_names = load_river_names()
    return jsonify(river_names)

@app.route('/api/rename-river', methods=['POST'])
def rename_river():
    global river_names
    data = request.json
    river_id = data.get('river')
    new_name = data.get('name')
    
    if not river_id or not new_name:
        return jsonify({"status": "error", "message": "Invalid data"})
    
    river_names[river_id] = new_name
    if save_river_names(river_names):
        if river_id in rc.robots:
            rc.robots[river_id].river_name = new_name
        return jsonify({"status": "success", "message": "River renamed"})
    else:
        return jsonify({"status": "error", "message": "Failed to save"})

@app.route('/api/reset-river', methods=['POST'])
def reset_river():
    """RESET: Clear all data for a river"""
    river = request.args.get('river', 'river1')
    data_file = f"robot_data_{river}.json"
    
    try:
        if os.path.exists(data_file):
            os.remove(data_file)
        
        # Reset robot's data
        if river in rc.robots:
            rc.robots[river].all_data = []
            rc.robots[river].waste_collected = 0
        
        return jsonify({"status": "success", "message": f"Data for {river} cleared"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def load_river_data(river_id):
    data_file = f"robot_data_{river_id}.json"
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data.get('readings', [])
                else:
                    return data
        except:
            return []
    return []

@app.route('/api/download-report-pdf', methods=['GET'])
def download_report_pdf():
    """Generate PDF report with before/after comparison"""
    river = request.args.get('river', 'river1')
    data_file = f"robot_data_{river}.json"
    
    if not os.path.exists(data_file):
        return jsonify({"error": "No data for this river"}), 404
    
    try:
        with open(data_file, 'r') as f:
            file_data = json.load(f)
            readings = file_data.get('readings', []) if isinstance(file_data, dict) else file_data
        
        if not readings:
            return jsonify({"error": "No readings available"}), 404
        
        global river_names
        river_names = load_river_names()
        river_display_name = river_names.get(river, river)
        
        # Create PDF
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                               rightMargin=0.5*inch, leftMargin=0.5*inch,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3c72'),
            spaceAfter=6,
            alignment=1
        )
        story.append(Paragraph("🤖 AQUATIC WASTE COLLECTOR", title_style))
        story.append(Paragraph("Water Quality Monitoring & Cleaning Report", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Report Info
        report_style = ParagraphStyle(
            'ReportInfo',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#666'),
            spaceAfter=12
        )
        story.append(Paragraph(f"<b>River Name:</b> {river_display_name}", report_style))
        story.append(Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", report_style))
        story.append(Paragraph(f"<b>Total Readings:</b> {len(readings)}", report_style))
        
        if isinstance(file_data, dict):
            total_waste = file_data.get('total_waste', 0)
            story.append(Paragraph(f"<b>Total Waste Collected:</b> {total_waste:.2f} kg ♻️", report_style))
        
        story.append(Spacer(1, 12))
        
        # BEFORE/AFTER COMPARISON
        first_reading = readings[0]
        last_reading = readings[-1]
        
        section_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=10,
            spaceBefore=15
        )
        
        story.append(Paragraph("📊 WATER QUALITY STATUS: BEFORE & AFTER", section_style))
        
        # Before/After Table
        before_after_data = [
            ['Metric', 'BEFORE Cleaning', 'AFTER Cleaning', 'Improvement'],
            [
                'Quality Score',
                f"{first_reading['water_quality']['score']:.1f}/100",
                f"{last_reading['water_quality']['score']:.1f}/100",
                f"+{last_reading['water_quality']['score'] - first_reading['water_quality']['score']:.1f}"
            ],
            [
                'Water Status',
                first_reading['water_quality']['status'],
                last_reading['water_quality']['status'],
                '✅' if last_reading['water_quality']['status'] >= first_reading['water_quality']['status'] else '⚠️'
            ],
            [
                'pH Level',
                f"{first_reading['sensor_readings']['pH']:.2f}",
                f"{last_reading['sensor_readings']['pH']:.2f}",
                f"{last_reading['sensor_readings']['pH'] - first_reading['sensor_readings']['pH']:+.2f}"
            ],
            [
                'Turbidity (NTU)',
                f"{first_reading['sensor_readings']['turbidity']:.2f}",
                f"{last_reading['sensor_readings']['turbidity']:.2f}",
                f"{first_reading['sensor_readings']['turbidity'] - last_reading['sensor_readings']['turbidity']:+.2f}"
            ],
            [
                'Temperature (°C)',
                f"{first_reading['sensor_readings']['temperature']:.2f}",
                f"{last_reading['sensor_readings']['temperature']:.2f}",
                f"{last_reading['sensor_readings']['temperature'] - first_reading['sensor_readings']['temperature']:+.2f}"
            ],
            [
                'TDS (ppm)',
                f"{first_reading['sensor_readings']['TDS']:.2f}",
                f"{last_reading['sensor_readings']['TDS']:.2f}",
                f"{first_reading['sensor_readings']['TDS'] - last_reading['sensor_readings']['TDS']:+.2f}"
            ],
        ]
        
        before_after_table = Table(before_after_data, colWidths=[1.8*inch, 1.6*inch, 1.6*inch, 1.2*inch])
        before_after_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(before_after_table)
        story.append(Spacer(1, 20))
        
        # WASTE COLLECTION
        story.append(Paragraph("♻️ WASTE COLLECTION SUMMARY", section_style))
        
        waste_items = [r for r in readings if r.get('waste', {}).get('detected')]
        waste_data = [['No.', 'Type', 'Weight (kg)', 'Time']]
        
        for idx, item in enumerate(waste_items[:20], 1):
            waste_data.append([
                str(idx),
                item['waste']['type'] or 'Unknown',
                f"{item['waste']['weight']:.2f}",
                datetime.fromisoformat(item['timestamp']).strftime('%H:%M:%S')
            ])
        
        if waste_items:
            waste_table = Table(waste_data, colWidths=[0.6*inch, 1.5*inch, 1.2*inch, 1.5*inch])
            waste_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff9800')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 9)
            ]))
            story.append(waste_table)
        else:
            story.append(Paragraph("No waste items detected during monitoring period", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # STATISTICS
        story.append(Paragraph("📈 OVERALL STATISTICS", section_style))
        
        avg_quality = statistics.mean([r['water_quality']['score'] for r in readings])
        avg_ph = statistics.mean([r['sensor_readings']['pH'] for r in readings])
        avg_turbidity = statistics.mean([r['sensor_readings']['turbidity'] for r in readings])
        avg_temp = statistics.mean([r['sensor_readings']['temperature'] for r in readings])
        avg_tds = statistics.mean([r['sensor_readings']['TDS'] for r in readings])
        total_waste = sum(r['waste']['weight'] for r in readings if r.get('waste', {}).get('weight'))
        
        stats_data = [
            ['Statistic', 'Value', 'Status'],
            ['Average Quality Score', f"{avg_quality:.1f}/100", '✅'],
            ['Average pH', f"{avg_ph:.2f}", '✅'],
            ['Average Turbidity', f"{avg_turbidity:.2f} NTU", '✅'],
            ['Average Temperature', f"{avg_temp:.2f}°C", '✅'],
            ['Average TDS', f"{avg_tds:.2f} ppm", '✅'],
            ['Total Waste Collected', f"{total_waste:.2f} kg", '✅'],
        ]
        
        stats_table = Table(stats_data, colWidths=[2.5*inch, 1.5*inch, 0.8*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4caf50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(stats_table)
        
        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        
        filename = f"{river_display_name.replace(' ', '_')}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)
    
    except Exception as e:
        print(f"PDF Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/download-report', methods=['GET'])
def download_report():
    """CSV download"""
    river = request.args.get('river', 'river1')
    data = load_river_data(river)
    
    if not data:
        return jsonify({"error": "No data"}), 404
    
    try:
        global river_names
        river_names = load_river_names()
        river_display_name = river_names.get(river, river)
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Aquatic Water Quality Report - CSV'])
        writer.writerow([f'River: {river_display_name}'])
        writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
        writer.writerow([])
        writer.writerow(['Timestamp','pH','Turbidity','Temp','TDS','Quality','Status','Waste Type','Waste kg'])
        
        for r in data:
            writer.writerow([
                r.get('timestamp',''),
                f"{r.get('sensor_readings',{}).get('pH',''):.2f}",
                f"{r.get('sensor_readings',{}).get('turbidity',''):.2f}",
                f"{r.get('sensor_readings',{}).get('temperature',''):.2f}",
                f"{r.get('sensor_readings',{}).get('TDS',''):.2f}",
                f"{r.get('water_quality',{}).get('score',''):.2f}",
                r.get('water_quality',{}).get('status',''),
                r.get('waste',{}).get('type',''),
                f"{r.get('waste',{}).get('weight',''):.2f}"
            ])
        
        csv_bytes = BytesIO(output.getvalue().encode('utf-8'))
        csv_bytes.seek(0)
        filename = f"{river_display_name.replace(' ','_')}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return send_file(csv_bytes, mimetype='text/csv', as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/robot/start', methods=['POST'])
def start_robot():
    river = request.args.get('river', 'river1')
    duration = int(request.args.get('duration', 300))
    return jsonify(rc.start_mission_api(river, duration))

@app.route('/api/robot/stop', methods=['POST'])
def stop_robot():
    river = request.args.get('river', 'river1')
    return jsonify(rc.stop_mission_api(river))

@app.route('/api/robot/status', methods=['GET'])
def robot_status():
    river = request.args.get('river', 'river1')
    return jsonify(rc.get_robot_status(river))

@app.route('/api/water-quality/latest', methods=['GET'])
def latest():
    river = request.args.get('river', 'river1')
    data = load_river_data(river)
    if not data:
        return jsonify({"status": "success", "count": 0, "data": []})
    latest_data = data[-20:] if len(data) >= 20 else data
    return jsonify({"status": "success", "count": len(latest_data), "total": len(data), "data": latest_data})

@app.route('/api/dashboard/summary', methods=['GET'])
def summary():
    river = request.args.get('river', 'river1')
    data = load_river_data(river)
    if not data:
        return jsonify({"status": "success", "current": None, "statistics": {"total_readings": 0}})
    latest = data[-1]
    recent = data[-50:] if len(data) >= 50 else data
    avg_quality = sum(d['water_quality']['score'] for d in recent) / len(recent)
    return jsonify({
        "status": "success",
        "current": {
            "quality_score": latest['water_quality']['score'],
            "status": latest['water_quality']['status'],
            "pH": latest['sensor_readings']['pH'],
            "turbidity": latest['sensor_readings']['turbidity'],
            "temperature": latest['sensor_readings']['temperature'],
            "TDS": latest['sensor_readings']['TDS']
        },
        "statistics": {"average_quality_score": round(avg_quality, 2), "total_readings": len(data)}
    })

if __name__ == "__main__":
    print("\n" + "="*70)
    print("✅ AQUATIC WASTE COLLECTOR - WITH RESET BUTTON")
    print("="*70)
    print("\n🌐 Dashboard: http://localhost:5000")
    print("\n✨ Features:")
    print("   ✅ Reset button in sidebar")
    print("   ✅ Reset button in header")
    print("   ✅ Confirmation modal")
    print("   ✅ Clears all data for river")
    print("\n" + "="*70 + "\n")
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
