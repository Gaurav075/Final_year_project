# app_final.py
# FINAL BACKEND - Simple and reliable

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import json
import os
import traceback

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

DATA_FILE = "robot_data.json"

print(f"\n✓ Backend looking for data file: {os.path.abspath(DATA_FILE)}")

def load_data():
    """Load data from local file"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return data
        else:
            print(f"⚠️  File not found: {DATA_FILE}")
            return []
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        traceback.print_exc()
        return []

# ==================== ROUTES ====================

@app.route('/', methods=['GET'])
def home():
    """Serve dashboard"""
    try:
        return send_from_directory('.', 'dashboard.html')
    except Exception as e:
        return f"Error serving dashboard: {e}", 500

@app.route('/dashboard.html', methods=['GET'])
def dashboard():
    """Serve dashboard"""
    try:
        return send_from_directory('.', 'dashboard.html')
    except Exception as e:
        return f"Error serving dashboard: {e}", 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    data = load_data()
    return jsonify({
        "status": "online",
        "data_file": os.path.abspath(DATA_FILE),
        "data_points": len(data),
        "file_exists": os.path.exists(DATA_FILE),
        "timestamp": datetime.now().isoformat()
    })

# ==================== API ENDPOINTS ====================

@app.route('/api/water-quality/latest', methods=['GET'])
def get_latest_water_quality():
    """Get latest water quality readings"""
    data = load_data()
    
    if not data:
        return jsonify({
            "status": "success",
            "count": 0,
            "data": [],
            "message": "No data yet. Check if robot is running."
        })
    
    latest_data = data[-20:] if len(data) >= 20 else data
    
    return jsonify({
        "status": "success",
        "count": len(latest_data),
        "total": len(data),
        "data": latest_data
    })

@app.route('/api/water-quality/status', methods=['GET'])
def get_quality_status():
    """Get current status"""
    data = load_data()
    
    if not data:
        return jsonify({
            "status": "success",
            "data": None,
            "message": "No data available"
        })
    
    latest = data[-1]
    
    return jsonify({
        "status": "success",
        "latest": {
            "robot_id": latest.get('robot_id', 'unknown'),
            "timestamp": latest.get('timestamp', ''),
            "pH": latest['sensor_readings']['pH'],
            "turbidity": latest['sensor_readings']['turbidity'],
            "temperature": latest['sensor_readings']['temperature'],
            "TDS": latest['sensor_readings']['TDS'],
            "quality_score": latest['water_quality']['score'],
            "quality_status": latest['water_quality']['status'],
            "warnings": latest['water_quality']['warnings']
        }
    })

@app.route('/api/water-quality/average', methods=['GET'])
def get_average_water_quality():
    """Get average metrics"""
    data = load_data()
    
    if not data:
        return jsonify({"error": "No data available"}), 404
    
    recent_data = data[-100:] if len(data) >= 100 else data
    
    avg_ph = sum(d['sensor_readings']['pH'] for d in recent_data) / len(recent_data)
    avg_turbidity = sum(d['sensor_readings']['turbidity'] for d in recent_data) / len(recent_data)
    avg_temp = sum(d['sensor_readings']['temperature'] for d in recent_data) / len(recent_data)
    avg_tds = sum(d['sensor_readings']['TDS'] for d in recent_data) / len(recent_data)
    avg_quality = sum(d['water_quality']['score'] for d in recent_data) / len(recent_data)
    
    return jsonify({
        "status": "success",
        "samples": len(recent_data),
        "averages": {
            "pH": round(avg_ph, 2),
            "turbidity": round(avg_turbidity, 2),
            "temperature": round(avg_temp, 2),
            "TDS": round(avg_tds, 2),
            "quality_score": round(avg_quality, 2)
        }
    })

@app.route('/api/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    """Get complete dashboard summary"""
    data = load_data()
    
    if not data:
        return jsonify({
            "status": "success",
            "current": None,
            "statistics": {
                "average_quality_score": 0,
                "total_readings": 0,
                "recent_readings": 0,
                "total_warnings": 0
            },
            "message": "No data available yet"
        })
    
    latest = data[-1]
    recent = data[-50:] if len(data) >= 50 else data
    
    avg_quality = sum(d['water_quality']['score'] for d in recent) / len(recent)
    total_warnings = sum(len(d['water_quality']['warnings']) for d in recent)
    
    summary = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
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
            "recent_readings": len(recent),
            "total_warnings": total_warnings
        }
    }
    
    return jsonify(summary)

@app.route('/api/data/export', methods=['GET'])
def export_data():
    """Export all data"""
    data = load_data()
    
    export = {
        "timestamp": datetime.now().isoformat(),
        "total_readings": len(data),
        "data": data
    }
    
    return jsonify(export)

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 AQUATIC ROBOT BACKEND (FINAL)")
    print("="*70)
    print(f"\n📂 Data file: {os.path.abspath(DATA_FILE)}")
    print(f"📍 Current directory: {os.getcwd()}")
    print(f"\n🌐 Dashboard: http://localhost:5000")
    print(f"💚 Health: http://localhost:5000/health")
    print(f"📊 API: http://localhost:5000/api/dashboard/summary")
    print("\n" + "="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
