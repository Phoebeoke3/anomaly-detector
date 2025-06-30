"""
Anomaly Model - Handles machine learning operations and predictions.
"""

import logging
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class AnomalyModel:
    """Model for handling anomaly detection operations."""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.model = None
        self.scaler = None
        self.features = ['temperature', 'humidity', 'sound_level']
        self._load_model()
    
    def _load_model(self):
        """Load the trained model and scaler."""
        try:
            # Try to load the latest model
            model_path = os.path.join(self.models_dir, "anomaly_detector.joblib")
            scaler_path = os.path.join(self.models_dir, "scaler.joblib")
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                logger.info("Loaded existing anomaly detection model")
            else:
                logger.warning("No existing model found, will train new model")
                self._train_new_model()
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self._train_new_model()
    
    def _train_new_model(self):
        """Train a new anomaly detection model."""
        try:
            # Create a simple model for demonstration
            self.model = IsolationForest(
                contamination=0.1,  # Expected 10% anomaly rate
                random_state=42,
                n_estimators=100
            )
            
            self.scaler = StandardScaler()
            
            # Generate some sample data for training
            np.random.seed(42)
            n_samples = 1000
            
            # Generate normal wind turbine manufacturing data
            temperature = np.random.normal(25, 5, n_samples)  # 25°C ± 5°C
            humidity = np.random.normal(50, 15, n_samples)    # 50% ± 15%
            sound_level = np.random.normal(65, 10, n_samples) # 65 dB ± 10 dB
            
            # Ensure values are within realistic ranges
            temperature = np.clip(temperature, 10, 40)
            humidity = np.clip(humidity, 20, 80)
            sound_level = np.clip(sound_level, 40, 90)
            
            # Create training data
            X_train = np.column_stack([temperature, humidity, sound_level])
            
            # Fit scaler and model
            X_scaled = self.scaler.fit_transform(X_train)
            self.model.fit(X_scaled)
            
            # Save the model
            self._save_model()
            
            logger.info("Trained and saved new anomaly detection model")
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
    
    def _save_model(self):
        """Save the trained model and scaler."""
        try:
            os.makedirs(self.models_dir, exist_ok=True)
            
            model_path = os.path.join(self.models_dir, "anomaly_detector.joblib")
            scaler_path = os.path.join(self.models_dir, "scaler.joblib")
            
            joblib.dump(self.model, model_path)
            joblib.dump(self.scaler, scaler_path)
            
            # Save metadata
            metadata = {
                'features': self.features,
                'model_type': 'IsolationForest',
                'trained_at': datetime.now().isoformat(),
                'contamination': 0.1
            }
            
            metadata_path = os.path.join(self.models_dir, "metadata.json")
            import json
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def predict(self, data: Dict[str, Any]) -> Tuple[float, str]:
        """Predict anomaly score for given sensor data."""
        try:
            if self.model is None or self.scaler is None:
                logger.error("Model not loaded")
                return 0.5, "unknown"
            
            # Extract features
            features = [data.get(feature, 0) for feature in self.features]
            
            # Create DataFrame
            df = pd.DataFrame([features], columns=self.features)
            
            # Scale features
            X_scaled = self.scaler.transform(df)
            
            # Predict anomaly score
            anomaly_score = self.model.decision_function(X_scaled)[0]
            
            # Normalize score to 0-1 range
            normalized_score = 1 - (anomaly_score + 0.5)  # Convert to 0-1 range
            
            # Classify status
            status = self._classify_status(normalized_score)
            
            return normalized_score, status
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return 0.5, "error"
    
    def _classify_status(self, anomaly_score: float) -> str:
        """Classify manufacturing status based on anomaly score."""
        if anomaly_score < 0.3:
            return "normal"
        elif anomaly_score < 0.6:
            return "warning"
        else:
            return "anomaly"
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get current model status."""
        return {
            'model_loaded': self.model is not None,
            'scaler_loaded': self.scaler is not None,
            'features': self.features,
            'model_type': 'IsolationForest' if self.model else None
        }
    
    def retrain_model(self, training_data: Optional[pd.DataFrame] = None):
        """Retrain the model with new data."""
        try:
            if training_data is None:
                # Use existing data from database
                from src.models.sensor_model import SensorModel
                sensor_model = SensorModel()
                recent_data = sensor_model.get_recent_sensor_data(1000)
                
                if not recent_data:
                    logger.warning("No training data available")
                    return
                
                # Convert to DataFrame
                df = pd.DataFrame(recent_data)
                training_data = df[self.features]
            
            # Retrain model
            X_scaled = self.scaler.fit_transform(training_data)
            self.model.fit(X_scaled)
            
            # Save updated model
            self._save_model()
            
            logger.info("Model retrained successfully")
            
        except Exception as e:
            logger.error(f"Error retraining model: {e}")
    
    def get_anomaly_thresholds(self) -> Dict[str, float]:
        """Get anomaly detection thresholds."""
        return {
            'normal_threshold': 0.3,
            'warning_threshold': 0.6,
            'anomaly_threshold': 0.8
        } 