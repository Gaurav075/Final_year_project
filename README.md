# README.md
# Autonomous Aqueous Robot - Water Quality Prediction & Real-Time Monitoring

## Project Overview

This project implements an **AI-powered autonomous aqueous robot** that predicts water quality and transmits real-time data to devices. The system combines sensor data processing, machine learning-based quality prediction, and cloud-based real-time monitoring.

## Features

- 🤖 **AI-Based Water Quality Prediction** - Uses Random Forest ML model
- 📡 **Real-Time Data Transmission** - MQTT protocol to cloud
- 📊 **Interactive Dashboard** - Beautiful web-based visualization
- 🚨 **Alert System** - Automatic warnings for quality issues
- 🌊 **Obstacle Detection** - Avoidance capabilities
- ♻️ **Waste Detection** - Identifies floating debris
- ⚡ **Auto-Refresh** - Live data updates

## System Architecture

```
Robot (Sensors) 
    ↓
Sensor Reader (Python)
    ↓
AI Quality Predictor (ML Model)
    ↓
MQTT Client (Sends Data)
    ↓
Cloud Broker (MQTT Server)
    ↓
Flask Backend (Receives & Stores)
    ↓
Web Dashboard (Real-Time Visualization)
```

## Project Structure

```
aquatic-robot/
├── sensor_reader.py          # Sensor data simulation
├── quality_predictor.py       # AI ML model for prediction
├── mqtt_client.py             # Cloud data transmission
├── robot_controller.py        # Main robot control system
├── app.py                     # Flask backend server
├── dashboard.html             # Web dashboard
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser

### Step 1: Clone/Download Project Files
```bash
cd aquatic-robot
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Backend Server
```bash
python app.py
```
The Flask server will start at `http://localhost:5000`

### Step 4: Run the Robot Simulation
In a new terminal:
```bash
python robot_controller.py
```
This will run a 2-minute mission with sensor readings and data transmission.

### Step 5: Open the Dashboard
Open your web browser and navigate to:
```
http://localhost:5000/dashboard.html
```

## Usage

### Running a Mission
```python
from robot_controller import AquaticRobot

# Create robot instance
robot = AquaticRobot(robot_id="robot-001")

# Connect to cloud
robot.connect_to_cloud()

# Run a 10-minute mission
robot.run_mission(duration_minutes=10)

# Disconnect
robot.disconnect_from_cloud()
```

### API Endpoints

#### Get Latest Water Quality
```
GET /api/water-quality/latest
```
Returns the latest 20 water quality readings.

#### Get Water Quality by Robot
```
GET /api/water-quality/<robot_id>
```
Returns latest 50 readings for specific robot.

#### Get Average Quality Metrics
```
GET /api/water-quality/average
```
Returns average of last 100 readings.

#### Get Quality Status
```
GET /api/water-quality/status
```
Returns current quality status summary.

#### Get Obstacle Alerts
```
GET /api/obstacles/latest
```
Returns latest obstacle detection events.

#### Get Waste Events
```
GET /api/waste/latest
```
Returns latest waste detection events.

#### Get Dashboard Summary
```
GET /api/dashboard/summary
```
Returns complete dashboard summary with statistics.

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.8+ |
| **Backend** | Flask |
| **ML Framework** | Scikit-learn |
| **Communication** | MQTT (Paho) |
| **Cloud Broker** | EMQX (Free) |
| **Frontend** | HTML5 + JavaScript |
| **Charts** | Chart.js |
| **Database** | In-memory (can be upgraded) |

## AI Model Details

### Water Quality Prediction Model
- **Algorithm**: Random Forest Regressor
- **Features**: pH, Turbidity, Temperature, TDS
- **Output**: Quality Score (0-100)
- **Status Categories**:
  - Excellent (90-100)
  - Good (70-90)
  - Fair (50-70)
  - Poor (30-50)
  - Very Poor (0-30)

### Training Data
The model is trained on 10 sample data points representing different water conditions.

```python
# Example training data
X_train = [
    [7.0, 2.0, 25, 300],    # Good water
    [7.5, 1.5, 26, 250],    # Excellent water
    [8.0, 4.0, 28, 500],    # Poor water
    ...
]
y_train = [85, 95, 50, ...]  # Quality scores
```

## Real-Time Data Flow

1. **Robot**: Reads sensors every 5 seconds
2. **Predictor**: AI model predicts quality (instant)
3. **MQTT**: Sends data every 10 seconds
4. **Cloud**: Broker receives and stores
5. **Backend**: Flask API processes data
6. **Dashboard**: Updates every 5 seconds

## Sensor Specifications

| Sensor | Range | Unit | Accuracy |
|--------|-------|------|----------|
| **pH** | 0-14 | pH | ±0.1 |
| **Turbidity** | 0-10 | NTU | ±0.2 |
| **Temperature** | 15-35 | °C | ±0.5 |
| **TDS** | 50-1000 | ppm | ±10 |

## Safe Ranges

- **pH**: 6.5 - 8.5 (neutral)
- **Turbidity**: 0 - 5 NTU (clear)
- **Temperature**: 15 - 30°C (optimal)
- **TDS**: 50 - 500 ppm (low to moderate)

## Configuration

### Change Robot ID
```python
robot = AquaticRobot(robot_id="my-robot")
```

### Change MQTT Broker
```python
mqtt_client = MQTTDataClient(broker_address="your-broker.com", port=1883)
```

### Change Backend Port
```python
app.run(port=8000)
```

### Adjust Sensor Read Interval
```python
robot.sensor_read_interval = 10  # Every 10 seconds
robot.mqtt_publish_interval = 20  # Publish every 20 seconds
```

## Troubleshooting

### MQTT Connection Error
- Ensure broker is reachable: `broker.emqx.io:1883`
- Check internet connection
- Try alternative broker address

### Flask Server Not Starting
```bash
pip install --upgrade flask flask-cors
```

### No Data in Dashboard
1. Ensure robot is running
2. Check Flask backend is running
3. Clear browser cache
4. Check browser console for errors (F12)

### ML Model Issues
```python
# Retrain the model
predictor = QualityPredictor()
predictor.train_model()
predictor.save_model()
```

## Performance Metrics

Expected performance in testing:
- **Data Transmission Latency**: <2 seconds
- **ML Prediction Time**: <100ms
- **Dashboard Update Frequency**: 5 seconds
- **Memory Usage**: ~100-200MB
- **CPU Usage**: 5-15% during active mission

## Future Enhancements

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Multi-robot fleet management
- [ ] Advanced ML models (LSTM, GRU)
- [ ] Mobile app integration
- [ ] Historical data analysis
- [ ] Predictive analytics
- [ ] Real GPS integration
- [ ] Actual sensor hardware support

## Safety Considerations

- Robot operates in simulation mode (no actual hardware)
- Safe ranges ensure water quality standards compliance
- Automatic alerts for parameter violations
- Emergency stop capability

## License

This project is open-source and available for educational purposes.

## Support

For issues, questions, or contributions, please refer to the documentation or contact the development team.

## Authors

Autonomous Aqueous Robot Project Team
DTU - Delhi Technological University

---

**Last Updated**: November 2025
**Version**: 1.0.0
