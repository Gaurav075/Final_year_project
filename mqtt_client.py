# mqtt_client.py
# Module for sending data to cloud via MQTT

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

class MQTTDataClient:
    """
    MQTT client for transmitting water quality data to cloud
    """
    
    def __init__(self, broker_address="broker.emqx.io", port=1883):
        self.broker_address = broker_address
        self.port = port
        self.client = mqtt.Client()
        self.connected = False
        
        # Setup callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
    
    def on_connect(self, client, userdata, flags, rc):
        """
        Callback when client connects to broker
        """
        if rc == 0:
            self.connected = True
            print(f"Connected to MQTT broker at {self.broker_address}:{self.port}")
        else:
            print(f"Failed to connect, return code {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """
        Callback when client disconnects
        """
        self.connected = False
        if rc != 0:
            print(f"Unexpected disconnection: {rc}")
        else:
            print("Disconnected from MQTT broker")
    
    def on_publish(self, client, userdata, mid):
        """
        Callback when message is published
        """
        print(f"Message published with ID: {mid}")
    
    def connect(self):
        """
        Connect to MQTT broker
        """
        try:
            self.client.connect(self.broker_address, self.port, keepalive=60)
            self.client.loop_start()
            time.sleep(1)  # Wait for connection
        except Exception as e:
            print(f"Connection error: {e}")
    
    def disconnect(self):
        """
        Disconnect from MQTT broker
        """
        self.client.loop_stop()
        self.client.disconnect()
    
    def publish_water_quality(self, sensor_data, quality_data, robot_id="robot-001"):
        """
        Publish water quality data to MQTT topic
        """
        payload = {
            "robot_id": robot_id,
            "timestamp": datetime.now().isoformat(),
            "sensor_data": sensor_data,
            "quality_prediction": quality_data
        }
        
        topic = f"water/quality/{robot_id}"
        
        try:
            result = self.client.publish(topic, json.dumps(payload, indent=2), qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"Published to {topic}: Quality Score = {quality_data['quality_score']}")
            else:
                print(f"Failed to publish: {result.rc}")
        except Exception as e:
            print(f"Publish error: {e}")
    
    def publish_obstacle_alert(self, obstacle_data, robot_id="robot-001"):
        """
        Publish obstacle detection alert
        """
        payload = {
            "robot_id": robot_id,
            "timestamp": datetime.now().isoformat(),
            "event": "obstacle_detected",
            "distance": obstacle_data.get("distance", 0),
            "action": obstacle_data.get("action", "avoiding")
        }
        
        topic = f"water/obstacle/{robot_id}"
        
        try:
            self.client.publish(topic, json.dumps(payload), qos=1)
            print(f"Obstacle alert published: {obstacle_data}")
        except Exception as e:
            print(f"Publish error: {e}")
    
    def publish_waste_detected(self, waste_data, robot_id="robot-001"):
        """
        Publish waste detection event
        """
        payload = {
            "robot_id": robot_id,
            "timestamp": datetime.now().isoformat(),
            "event": "waste_detected",
            "waste_type": waste_data.get("type", "unknown"),
            "confidence": waste_data.get("confidence", 0),
            "action": "collecting"
        }
        
        topic = f"water/waste/{robot_id}"
        
        try:
            self.client.publish(topic, json.dumps(payload), qos=1)
            print(f"Waste detection published: {waste_data}")
        except Exception as e:
            print(f"Publish error: {e}")


# Test MQTT client
if __name__ == "__main__":
    mqtt_client = MQTTDataClient()
    mqtt_client.connect()
    
    # Test publish
    sensor_data = {
        "pH": 7.5,
        "turbidity": 2.0,
        "temperature": 25,
        "TDS": 300
    }
    
    quality_data = {
        "quality_score": 85,
        "status": "Good",
        "warnings": []
    }
    
    mqtt_client.publish_water_quality(sensor_data, quality_data)
    
    time.sleep(2)
    mqtt_client.disconnect()
