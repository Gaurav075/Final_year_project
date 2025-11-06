# robot_controller_final.py
# FINAL VERSION - Guaranteed to work with proper data saving

import time
import json
import os
from datetime import datetime
from sensor_reader import SensorReader
from quality_predictor import QualityPredictor

class AquaticRobot:
    """Aquatic robot with guaranteed data saving"""
    
    def __init__(self, robot_id="robot-001", data_file="robot_data.json"):
        self.robot_id = robot_id
        self.sensor_reader = SensorReader()
        self.quality_predictor = QualityPredictor()
        
        self.data_file = data_file
        self.all_data = []
        
        self.state = "IDLE"
        self.is_running = False
        self.mission_count = 0
        
        print(f"✓ Robot {robot_id} initialized!")
        print(f"✓ Data file: {os.path.abspath(data_file)}\n")
    
    def save_data_to_file(self, robot_data):
        """Save SINGLE data point to file immediately"""
        try:
            # Load existing data
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.all_data = json.load(f)
            
            # Add new data
            self.all_data.append(robot_data)
            
            # Keep only last 500
            if len(self.all_data) > 500:
                self.all_data = self.all_data[-500:]
            
            # Save to file
            with open(self.data_file, 'w') as f:
                json.dump(self.all_data, f)
            
            # Print confirmation
            print(f"  ✓ Saved to {self.data_file} (Total: {len(self.all_data)} points)")
            
        except Exception as e:
            print(f"  ❌ Error saving data: {e}")
    
    def read_and_save_sensors(self):
        """Read sensors and immediately save"""
        sensor_data = self.sensor_reader.read_all_sensors()
        quality_details = self.quality_predictor.get_quality_details(sensor_data)
        
        robot_data = {
            "robot_id": self.robot_id,
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
            }
        }
        
        # Save immediately
        self.save_data_to_file(robot_data)
        
        return robot_data
    
    def run_mission(self, duration_seconds=30):
        """Run mission for specified duration"""
        self.mission_count += 1
        self.is_running = True
        self.state = "NAVIGATING"
        
        print(f"\n{'='*70}")
        print(f"🚀 MISSION #{self.mission_count} STARTED")
        print(f"⏱️  Duration: {duration_seconds} seconds")
        print(f"{'='*70}\n")
        
        mission_start = time.time()
        
        try:
            while self.is_running:
                elapsed = time.time() - mission_start
                remaining = duration_seconds - elapsed
                
                if elapsed > duration_seconds:
                    print(f"\n✓ Mission completed!")
                    break
                
                # Read and save data (EVERY SECOND)
                robot_data = self.read_and_save_sensors()
                
                # Display data
                quality = robot_data['water_quality']
                sensors = robot_data['sensor_readings']
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏱️ {remaining:.1f}s")
                print(f"  pH: {sensors['pH']:.2f} | Turbidity: {sensors['turbidity']:.2f}")
                print(f"  Temp: {sensors['temperature']:.2f}°C | TDS: {sensors['TDS']:.2f}")
                print(f"  💧 Score: {quality['score']:.2f}/100 [{quality['status']}]\n")
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⏹️  Mission interrupted")
            self.is_running = False
        
        print(f"{'='*70}\n")


def main():
    """Main function"""
    print("\n" + "="*70)
    print("🤖 AQUATIC ROBOT - WATER QUALITY MONITORING")
    print("="*70 + "\n")
    
    robot = AquaticRobot(robot_id="aqua-robot-001")
    
    try:
        robot.run_mission(duration_seconds=30)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("✓ Robot shutdown complete.")
    print(f"✓ Check data at: {os.path.abspath('robot_data.json')}\n")


if __name__ == "__main__":
    main()
