# robot_controller_final_fixed.py
# FIXED - Proper JSON structure for waste tracking

import time
import json
import os
import threading
from datetime import datetime
from sensor_reader import SensorReader
from quality_predictor import QualityPredictor

class AquaticRobot:
    """Fixed robot with proper JSON structure"""
    
    def __init__(self, robot_id="robot-001", river_name="River 1", data_file="robot_data.json"):
        self.robot_id = robot_id
        self.river_name = river_name
        self.sensor_reader = SensorReader()
        self.quality_predictor = QualityPredictor()
        
        self.data_file = data_file
        self.all_data = []
        self.waste_collected = 0
        
        self.state = "IDLE"
        self.is_running = False
        self.mission_count = 0
        
        self.load_existing_data()
        print(f"✓ Robot {robot_id} initialized for {river_name}!")
    
    def load_existing_data(self):
        """Load existing data from file - FIXED"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    file_data = json.load(f)
                    
                    # Handle both old and new format
                    if isinstance(file_data, dict):
                        self.all_data = file_data.get('readings', [])
                        self.waste_collected = file_data.get('total_waste', 0)
                    elif isinstance(file_data, list):
                        # Old format - convert to new
                        self.all_data = file_data
                        self.waste_collected = sum(
                            d.get('waste', {}).get('weight', 0) 
                            for d in file_data
                        )
                        
                print(f"✓ Loaded {len(self.all_data)} readings")
            except Exception as e:
                print(f"⚠️  Error loading data: {e}")
                self.all_data = []
                self.waste_collected = 0
    
    def save_data_to_file(self, robot_data):
        """Save data point to file - FIXED"""
        try:
            # Load current data
            if os.path.exists(self.data_file):
                try:
                    with open(self.data_file, 'r') as f:
                        file_data = json.load(f)
                        
                        # Handle both formats
                        if isinstance(file_data, dict):
                            self.all_data = file_data.get('readings', [])
                            self.waste_collected = file_data.get('total_waste', 0)
                        elif isinstance(file_data, list):
                            self.all_data = file_data
                except:
                    self.all_data = []
            
            # Update waste
            waste_weight = robot_data.get('waste', {}).get('weight', 0)
            self.waste_collected += waste_weight
            
            # Add new reading
            self.all_data.append(robot_data)
            
            # Keep only last 1000
            if len(self.all_data) > 1000:
                self.all_data = self.all_data[-1000:]
            
            # Save with proper structure
            save_data = {
                'readings': self.all_data,
                'total_waste': self.waste_collected,
                'last_update': datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(save_data, f)
            
        except Exception as e:
            print(f"  ❌ Error saving: {e}")
    
    def simulate_waste_collection(self):
        """Simulate waste collection"""
        import random
        if random.random() < 0.15:
            waste_types = ["plastic_bottle", "plastic_bag", "foam", "organic"]
            waste_type = random.choice(waste_types)
            waste_weight = random.uniform(0.1, 0.5)
            
            self.waste_collected += waste_weight
            
            print(f"  ♻️  WASTE: {waste_type} ({waste_weight:.2f}kg)")
            return waste_type, waste_weight
        return None, 0
    
    def read_and_save_sensors(self):
        """Read sensors and save data"""
        sensor_data = self.sensor_reader.read_all_sensors()
        quality_details = self.quality_predictor.get_quality_details(sensor_data)
        
        waste_type, waste_weight = self.simulate_waste_collection()
        
        robot_data = {
            "robot_id": self.robot_id,
            "river_name": self.river_name,
            "timestamp": datetime.now().isoformat(),
            "mission": self.mission_count,
            "state": self.state,
            "sensor_readings": {
                "pH": sensor_data["pH"],
                "turbidity": sensor_data["turbidity"],
                "temperature": sensor_data["temperature"],
                "TDS": sensor_data["TDS"]
            },
            "water_quality": {
                "score": quality_details["quality_score"],
                "status": quality_details["status"],
                "warnings": quality_details["warnings"]
            },
            "waste": {
                "detected": waste_type is not None,
                "type": waste_type,
                "weight": waste_weight if waste_type else 0
            }
        }
        
        self.save_data_to_file(robot_data)
        return robot_data
    
    def run_mission_in_thread(self, duration_seconds=300):
        """Run mission in background thread"""
        def mission_worker():
            self.mission_count += 1
            self.is_running = True
            self.state = "NAVIGATING"
            
            print(f"\n{'='*70}")
            print(f"🚀 MISSION #{self.mission_count} - {self.river_name}")
            print(f"⏱️  Duration: {duration_seconds}s")
            print(f"{'='*70}\n")
            
            mission_start = time.time()
            
            try:
                while self.is_running:
                    elapsed = time.time() - mission_start
                    remaining = duration_seconds - elapsed
                    
                    if elapsed > duration_seconds:
                        print(f"\n✓ Mission completed!")
                        self.is_running = False
                        break
                    
                    robot_data = self.read_and_save_sensors()
                    
                    quality = robot_data['water_quality']
                    sensors = robot_data['sensor_readings']
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.river_name}")
                    print(f"  pH: {sensors['pH']:.2f} | Quality: {quality['score']:.1f}")
                    print(f"  Total waste: {self.waste_collected:.2f}kg\n")
                    
                    time.sleep(1)
            
            except Exception as e:
                print(f"❌ Error: {e}")
            
            finally:
                self.is_running = False
        
        thread = threading.Thread(target=mission_worker, daemon=True)
        thread.start()
    
    def start_mission(self, duration_seconds=300):
        """Start mission"""
        if not self.is_running:
            self.run_mission_in_thread(duration_seconds)
            return {"status": "started", "message": f"Mission started"}
        else:
            return {"status": "already_running", "message": "Already running"}
    
    def stop_mission(self):
        """Stop mission"""
        if self.is_running:
            self.is_running = False
            return {"status": "stopped", "message": "Mission stopped"}
        else:
            return {"status": "not_running", "message": "Not running"}
    
    def get_status(self):
        """Get robot status"""
        return {
            "robot_id": self.robot_id,
            "river_name": self.river_name,
            "is_running": self.is_running,
            "mission_count": self.mission_count,
            "state": self.state,
            "data_points": len(self.all_data),
            "waste_collected": round(self.waste_collected, 2),
            "waste_items": sum(
                1 for d in self.all_data 
                if d.get('waste', {}).get('detected', False)
            )
        }


# ==================== 5 ROBOTS ====================

robots = {
    "river1": AquaticRobot(robot_id="robot-001", river_name="River 1", data_file="robot_data_river1.json"),
    "river2": AquaticRobot(robot_id="robot-002", river_name="River 2", data_file="robot_data_river2.json"),
    "river3": AquaticRobot(robot_id="robot-003", river_name="River 3", data_file="robot_data_river3.json"),
    "river4": AquaticRobot(robot_id="robot-004", river_name="River 4", data_file="robot_data_river4.json"),
    "river5": AquaticRobot(robot_id="robot-005", river_name="River 5", data_file="robot_data_river5.json"),
}

def start_mission_api(river_id, duration=300):
    if river_id in robots:
        return robots[river_id].start_mission(duration)
    return {"error": "River not found"}

def stop_mission_api(river_id):
    if river_id in robots:
        return robots[river_id].stop_mission()
    return {"error": "River not found"}

def get_robot_status(river_id):
    if river_id in robots:
        return robots[river_id].get_status()
    return {"error": "River not found"}

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🤖 AQUATIC ROBOT - FIXED VERSION")
    print("="*70)
    print("\nAvailable Rivers:")
    for rid, robot in robots.items():
        print(f"  {rid}: {robot.river_name}")
    print("\n" + "="*70 + "\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutdown...")
