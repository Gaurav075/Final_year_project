# sensor_reader.py
# Module to read sensor data from water quality sensors

import random
import time
from datetime import datetime

class SensorReader:
    """
    Simulates reading from water quality sensors
    """
    
    def __init__(self):
        # Sensor calibration values
        self.ph_min = 6.5
        self.ph_max = 8.5
        self.turbidity_min = 0
        self.turbidity_max = 10
        self.temp_min = 15
        self.temp_max = 35
        self.tds_min = 50
        self.tds_max = 1000
        
    def read_ph_sensor(self):
        """
        Read pH sensor (0-14 scale, safe range 6.5-8.5)
        """
        ph_value = random.uniform(self.ph_min - 1, self.ph_max + 1)
        return round(ph_value, 2)
    
    def read_turbidity_sensor(self):
        """
        Read Turbidity sensor (NTU units, lower is better)
        """
        turbidity_value = random.uniform(self.turbidity_min, self.turbidity_max)
        return round(turbidity_value, 2)
    
    def read_temperature_sensor(self):
        """
        Read Temperature sensor (Celsius)
        """
        temp_value = random.uniform(self.temp_min, self.temp_max)
        return round(temp_value, 2)
    
    def read_tds_sensor(self):
        """
        Read TDS (Total Dissolved Solids) sensor (ppm - parts per million)
        """
        tds_value = random.uniform(self.tds_min, self.tds_max)
        return round(tds_value, 2)
    
    def read_all_sensors(self):
        """
        Read all sensors and return a dictionary
        """
        sensor_data = {
            "timestamp": datetime.now().isoformat(),
            "pH": self.read_ph_sensor(),
            "turbidity": self.read_turbidity_sensor(),
            "temperature": self.read_temperature_sensor(),
            "TDS": self.read_tds_sensor()
        }
        return sensor_data


# Test the sensor reader
if __name__ == "__main__":
    reader = SensorReader()
    for i in range(5):
        data = reader.read_all_sensors()
        print(f"Reading {i+1}: {data}")
        time.sleep(1)
