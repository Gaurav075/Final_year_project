# app_ultimate.py
# FINAL WORKING VERSION - All fixed

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

DATA_FILE = "robot_data.json"

def load_data():
    """Load data from file"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return []
    except:
        return []

# ==================== EMBEDDED DASHBOARD ====================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Aquatic Robot Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        header { text-align: center; color: white; margin-bottom: 30px; }
        h1 { font-size: 2.5em; margin: 10px 0; }
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            justify-content: center;
        }
        button {
            background: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            color: #667eea;
        }
        button:hover { background: #eee; }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .card h3 {
            color: #667eea;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
            margin: 10px 0;
        }
        .label {
            color: #666;
            font-size: 0.9em;
        }
        .chart-container {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        .chart-container h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        .chart-wrapper {
            position: relative;
            height: 300px;
        }
        .status-good { color: #4caf50; }
        .status-fair { color: #ff9800; }
        .status-poor { color: #f44336; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Aquatic Robot Dashboard</h1>
            <p>Real-Time Water Quality Monitoring</p>
        </header>
        
        <div class="controls">
            <button onclick="refreshNow()">🔄 Refresh</button>
            <button onclick="autoON()">⚡ Auto ON</button>
            <button onclick="autoOFF()">⏹️ Auto OFF</button>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h3>📊 Quality</h3>
                <div class="label">Score</div>
                <div class="value" id="score">--</div>
                <div class="label">Status</div>
                <div class="value" id="status">--</div>
            </div>
            
            <div class="card">
                <h3>🌊 pH</h3>
                <div class="label">Level</div>
                <div class="value" id="ph">--</div>
                <div class="label" style="font-size:0.8em">Safe: 6.5-8.5</div>
            </div>
            
            <div class="card">
                <h3>💧 Turbidity</h3>
                <div class="label">Level (NTU)</div>
                <div class="value" id="turbidity">--</div>
                <div class="label" style="font-size:0.8em">Ideal: 0-5</div>
            </div>
            
            <div class="card">
                <h3>🌡️ Temperature</h3>
                <div class="label">Value (°C)</div>
                <div class="value" id="temp">--</div>
                <div class="label" style="font-size:0.8em">Ideal: 15-30</div>
            </div>
            
            <div class="card">
                <h3>⚗️ TDS</h3>
                <div class="label">Level (ppm)</div>
                <div class="value" id="tds">--</div>
                <div class="label" style="font-size:0.8em">Ideal: 50-500</div>
            </div>
            
            <div class="card">
                <h3>📈 Info</h3>
                <div class="label">Total Readings</div>
                <div class="value" id="readings">--</div>
                <div class="label" style="font-size:0.8em">Last update: <span id="time">--</span></div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>Quality Score Trend</h3>
            <div class="chart-wrapper">
                <canvas id="chart1"></canvas>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>Sensor Readings</h3>
            <div class="chart-wrapper">
                <canvas id="chart2"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        let chart1 = null;
        let chart2 = null;
        let autoInterval = null;
        
        function getStatusClass(status) {
            if (status === 'Excellent' || status === 'Good') return 'status-good';
            if (status === 'Fair') return 'status-fair';
            if (status === 'Poor' || status === 'Very Poor') return 'status-poor';
            return '';
        }
        
        async function fetchData() {
            try {
                const res = await fetch('/api/dashboard/summary');
                const data = await res.json();
                
                if (data.current) {
                    // Update cards
                    document.getElementById('score').textContent = data.current.quality_score.toFixed(1);
                    document.getElementById('status').textContent = data.current.status;
                    document.getElementById('status').className = 'value ' + getStatusClass(data.current.status);
                    
                    document.getElementById('ph').textContent = data.current.pH.toFixed(2);
                    document.getElementById('turbidity').textContent = data.current.turbidity.toFixed(2);
                    document.getElementById('temp').textContent = data.current.temperature.toFixed(1);
                    document.getElementById('tds').textContent = data.current.TDS.toFixed(0);
                    document.getElementById('readings').textContent = data.statistics.total_readings;
                    document.getElementById('time').textContent = new Date().toLocaleTimeString();
                    
                    // Update charts
                    updateCharts();
                }
            } catch(e) {
                console.error('Error:', e);
            }
        }
        
        async function updateCharts() {
            try {
                const res = await fetch('/api/water-quality/latest');
                const data = await res.json();
                
                if (data.data && data.data.length > 0) {
                    const readings = data.data;
                    const labels = readings.map(r => new Date(r.timestamp).toLocaleTimeString());
                    const scores = readings.map(r => r.water_quality.score);
                    const phVals = readings.map(r => r.sensor_readings.pH);
                    const turbVals = readings.map(r => r.sensor_readings.turbidity);
                    const tempVals = readings.map(r => r.sensor_readings.temperature);
                    
                    // Chart 1: Quality Score
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
                                    label: 'Quality Score',
                                    data: scores,
                                    borderColor: '#667eea',
                                    backgroundColor: 'rgba(102,126,234,0.1)',
                                    borderWidth: 2,
                                    fill: true,
                                    tension: 0.3
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: { legend: { display: true } },
                                scales: { y: { beginAtZero: true, max: 100 } }
                            }
                        });
                    }
                    
                    // Chart 2: Sensors
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
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: { legend: { display: true } }
                            }
                        });
                    }
                }
            } catch(e) {
                console.error('Chart error:', e);
            }
        }
        
        function refreshNow() {
            console.log('Manual refresh');
            fetchData();
        }
        
        function autoON() {
            if (!autoInterval) {
                autoInterval = setInterval(fetchData, 2000);
                alert('Auto-refresh ON (2s)');
            }
        }
        
        function autoOFF() {
            if (autoInterval) {
                clearInterval(autoInterval);
                autoInterval = null;
                alert('Auto-refresh OFF');
            }
        }
        
        window.addEventListener('load', () => {
            fetchData();
            autoON();
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
    data = load_data()
    return jsonify({
        "status": "online",
        "data_points": len(data),
        "file_exists": os.path.exists(DATA_FILE),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/water-quality/latest', methods=['GET'])
def latest():
    data = load_data()
    if not data:
        return jsonify({"status": "success", "count": 0, "data": []})
    latest_data = data[-20:] if len(data) >= 20 else data
    return jsonify({
        "status": "success",
        "count": len(latest_data),
        "total": len(data),
        "data": latest_data
    })

@app.route('/api/dashboard/summary', methods=['GET'])
def summary():
    data = load_data()
    if not data:
        return jsonify({
            "status": "success",
            "current": None,
            "statistics": {"total_readings": 0}
        })
    
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
        "statistics": {
            "average_quality_score": round(avg_quality, 2),
            "total_readings": len(data),
            "recent_readings": len(recent)
        }
    })

if __name__ == "__main__":
    print("\n" + "="*60)
    print("✅ AQUATIC ROBOT - ULTIMATE WORKING VERSION")
    print("="*60)
    print(f"\n🌐 Dashboard: http://localhost:5000")
    print(f"💚 Health: http://localhost:5000/health")
    print(f"📊 API: http://localhost:5000/api/dashboard/summary")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
