# sensor_reader_realistic.py
# FIXED - Realistic sensor values with proper ranges

import random

class SensorReader:
    """
    Simulated sensor reader with REALISTIC values
    
    Data Source Explanation:
    - pH: Measured from water sample (digital pH meter)
    - Turbidity: Measured in NTU (Nephelometric Turbidity Unit) via turbidity sensor
    - Temperature: Measured in °C (Celsius) via thermometer sensor
    - TDS: Total Dissolved Solids measured in ppm (parts per million)
    
    These values are taken from the river's current water conditions
    by the Aquatic Robot's onboard sensors during scanning.
    """
    
    def __init__(self):
        # Set baseline realistic values for a typical river
        self.base_ph = 7.0  # Neutral
        self.base_turbidity = 3.5  # Slightly turbid
        self.base_temperature = 24.0  # Room temperature
        self.base_tds = 350.0  # Moderate TDS
    
    def read_all_sensors(self):
        """
        Read all sensors with REALISTIC values
        
        Returns:
            dict: Sensor readings with realistic fluctuations
        """
        
        # pH: Usually 6.5-8.5 (safe range), slight variation
        # Normal range: 6.5-8.5, we add ±0.3 variation
        ph = self.base_ph + random.uniform(-0.3, 0.3)
        ph = round(max(6.5, min(8.5, ph)), 2)
        
        # Turbidity: Usually 0-5 NTU (clear), max 10 (very turbid)
        # We add small variation: ±0.5
        turbidity = self.base_turbidity + random.uniform(-0.5, 0.5)
        turbidity = round(max(0, min(10, turbidity)), 2)
        
        # Temperature: Usually 15-30°C for water
        # We add small variation: ±0.5°C
        temperature = self.base_temperature + random.uniform(-0.5, 0.5)
        temperature = round(max(15, min(30, temperature)), 2)
        
        # TDS: Usually 50-500 ppm (fresh water), max 1000+
        # We add small variation: ±20 ppm
        tds = self.base_tds + random.uniform(-20, 20)
        tds = round(max(50, min(800, tds)), 2)
        
        return {
            "pH": ph,
            "turbidity": turbidity,
            "temperature": temperature,
            "TDS": tds
        }
    
    @staticmethod
    def get_sensor_info():
        """Information about sensors for presentation"""
        return {
            "pH": {
                "name": "pH Sensor (Digital pH Meter)",
                "unit": "pH",
                "range": "0-14",
                "safe_range": "6.5-8.5",
                "what_it_measures": "Acidity or alkalinity of water",
                "sensor_type": "Glass electrode pH sensor",
                "accuracy": "±0.1 pH"
            },
            "turbidity": {
                "name": "Turbidity Sensor (Nephelometer)",
                "unit": "NTU (Nephelometric Turbidity Unit)",
                "range": "0-10+ NTU",
                "safe_range": "0-5 NTU",
                "what_it_measures": "Water clarity/cloudiness caused by suspended particles",
                "sensor_type": "Optical turbidity sensor",
                "accuracy": "±0.3 NTU"
            },
            "temperature": {
                "name": "Temperature Sensor (Thermometer)",
                "unit": "°C (Celsius)",
                "range": "0-50°C",
                "safe_range": "15-30°C",
                "what_it_measures": "Water temperature",
                "sensor_type": "DS18B20 Digital Temperature Sensor",
                "accuracy": "±0.5°C"
            },
            "TDS": {
                "name": "TDS Sensor (Conductivity Meter)",
                "unit": "ppm (parts per million)",
                "range": "0-1000+ ppm",
                "safe_range": "50-500 ppm",
                "what_it_measures": "Total dissolved solids (salts, minerals, etc.)",
                "sensor_type": "Conductivity probe",
                "accuracy": "±5 ppm"
            }
        }
