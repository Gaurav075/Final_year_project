# test_api.py
# Quick test to check if API is working

import json
import os

print("\n=== API TEST ===\n")

# Check file
if os.path.exists('robot_data.json'):
    with open('robot_data.json', 'r') as f:
        data = json.load(f)
    
    print(f"✓ File exists: robot_data.json")
    print(f"✓ Total data points: {len(data)}")
    
    if data:
        latest = data[-1]
        print(f"\n📊 Latest Reading:")
        print(f"  Robot ID: {latest['robot_id']}")
        print(f"  Time: {latest['timestamp']}")
        print(f"  pH: {latest['sensor_readings']['pH']}")
        print(f"  Quality Score: {latest['water_quality']['score']}")
        print(f"  Status: {latest['water_quality']['status']}")
    
    print(f"\n✅ DATA IS AVAILABLE!\n")
    print("Now checking if backend can read it...")
    print("\n1. Open: http://localhost:5000/health")
    print("   Should show: data_points: " + str(len(data)))
    print("\n2. Open: http://localhost:5000/api/dashboard/summary")
    print("   Should show latest data in JSON")
    print("\n3. Open: http://localhost:5000")
    print("   Should show dashboard\n")
    
else:
    print("❌ robot_data.json NOT FOUND")
    print("   Robot needs to run first!\n")
