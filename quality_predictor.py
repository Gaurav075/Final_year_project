# quality_predictor.py
# AI Model for predicting water quality based on sensor readings

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import json

class QualityPredictor:
    """
    Machine Learning model to predict water quality score
    Based on pH, turbidity, temperature, and TDS
    """
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.train_model()
    
    def train_model(self):
        """
        Train the model with sample water quality data
        """
        # Training data: [pH, Turbidity, Temperature, TDS]
        X_train = np.array([
            [7.0, 2.0, 25, 300],    # Good water
            [7.5, 1.5, 26, 250],    # Excellent water
            [6.8, 3.0, 24, 400],    # Fair water
            [8.0, 4.0, 28, 500],    # Poor water
            [7.2, 2.5, 25, 350],    # Good water
            [6.5, 5.0, 30, 600],    # Bad water
            [8.2, 1.0, 22, 200],    # Excellent water
            [5.5, 8.0, 35, 800],    # Very bad water
            [7.8, 2.0, 27, 300],    # Good water
            [7.1, 3.5, 26, 450],    # Fair water
        ])
        
        # Quality scores (0-100, higher is better)
        y_train = np.array([85, 95, 70, 50, 80, 40, 98, 20, 82, 65])
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        print("AI Model trained successfully!")
    
    def predict_quality(self, sensor_data):
        """
        Predict water quality score
        Input: {pH, turbidity, temperature, TDS}
        Output: Quality score (0-100)
        """
        features = np.array([[
            sensor_data["pH"],
            sensor_data["turbidity"],
            sensor_data["temperature"],
            sensor_data["TDS"]
        ]])
        
        # Scale features using the same scaler
        features_scaled = self.scaler.transform(features)
        
        # Predict
        quality_score = self.model.predict(features_scaled)[0]
        
        # Clamp between 0-100
        quality_score = max(0, min(100, quality_score))
        
        return round(quality_score, 2)
    
    def get_quality_status(self, quality_score):
        """
        Convert quality score to status
        """
        if quality_score >= 90:
            return "Excellent"
        elif quality_score >= 70:
            return "Good"
        elif quality_score >= 50:
            return "Fair"
        elif quality_score >= 30:
            return "Poor"
        else:
            return "Very Poor"
    
    def get_quality_details(self, sensor_data):
        """
        Get detailed quality analysis
        """
        quality_score = self.predict_quality(sensor_data)
        status = self.get_quality_status(quality_score)
        
        # Generate warnings
        warnings = []
        if sensor_data["pH"] < 6.5 or sensor_data["pH"] > 8.5:
            warnings.append("pH level is out of safe range (6.5-8.5)")
        if sensor_data["turbidity"] > 5:
            warnings.append("Turbidity is high (>5 NTU)")
        if sensor_data["temperature"] > 30:
            warnings.append("Temperature is too high (>30°C)")
        if sensor_data["TDS"] > 500:
            warnings.append("TDS level is high (>500 ppm)")
        
        result = {
            "quality_score": quality_score,
            "status": status,
            "warnings": warnings,
            "sensor_data": sensor_data
        }
        
        return result
    
    def save_model(self, filepath="quality_model.pkl"):
        """
        Save trained model to file
        """
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler
            }, f)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath="quality_model.pkl"):
        """
        Load trained model from file
        """
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
            self.is_trained = True
        print(f"Model loaded from {filepath}")


# Test the predictor
if __name__ == "__main__":
    predictor = QualityPredictor()
    
    # Test data
    test_data = {
        "pH": 7.5,
        "turbidity": 2.0,
        "temperature": 25,
        "TDS": 300
    }
    
    result = predictor.get_quality_details(test_data)
    print(json.dumps(result, indent=2))
