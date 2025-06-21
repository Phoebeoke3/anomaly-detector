import os
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime
import json

# Add the src directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.generator import SensorDataGenerator
from data.sqlite_db import SQLiteDB

class AnomalyDetector:
    """Anomaly detection model for wind turbine component factory."""
    
    def __init__(self, model_version=None):
        self.model = None
        self.scaler = None
        self.model_version = model_version or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.metrics = {}
        self.db = SQLiteDB()
    
    def train(self, data):
        """Train the anomaly detection model."""
        # Prepare features
        features = ['temperature', 'humidity', 'sound']
        X = data[features].values
        
        # Scale the features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        self.model = IsolationForest(
            contamination=0.1,  # Expected proportion of anomalies
            random_state=42,
            n_estimators=100
        )
        self.model.fit(X_scaled)
        
        # Calculate anomaly scores
        anomaly_scores = -self.model.score_samples(X_scaled)
        
        # Calculate evaluation metrics
        self.metrics = self._calculate_metrics(anomaly_scores, data['target'])
        
        # Save model artifacts and metadata
        self._save_model()
        
        return self.metrics
    
    def _calculate_metrics(self, anomaly_scores, true_labels):
        """Calculate model evaluation metrics."""
        # Convert anomaly scores to binary predictions using a threshold
        threshold = np.percentile(anomaly_scores, 90)  # 90th percentile as threshold
        predictions = (anomaly_scores > threshold).astype(int)
        
        # Calculate metrics
        tp = np.sum((predictions == 1) & (true_labels == 1))
        fp = np.sum((predictions == 1) & (true_labels == 0))
        tn = np.sum((predictions == 0) & (true_labels == 0))
        fn = np.sum((predictions == 0) & (true_labels == 1))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        accuracy = (tp + tn) / (tp + tn + fp + fn)
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'accuracy': accuracy,
            'threshold': threshold,
            'mean_anomaly_score': float(np.mean(anomaly_scores)),
            'std_anomaly_score': float(np.std(anomaly_scores)),
            'max_anomaly_score': float(np.max(anomaly_scores)),
            'min_anomaly_score': float(np.min(anomaly_scores))
        }
    
    def predict(self, data):
        """Make predictions on new data."""
        if self.model is None or self.scaler is None:
            raise ValueError("Model not trained. Please train the model first.")
        
        # Scale the features
        X_scaled = self.scaler.transform(data)
        
        # Get anomaly scores
        anomaly_scores = -self.model.score_samples(X_scaled)
        
        return anomaly_scores
    
    def _save_model(self):
        """Save model artifacts and metadata."""
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        # Save model and scaler
        model_path = f'models/anomaly_detector_{self.model_version}.joblib'
        scaler_path = f'models/scaler_{self.model_version}.joblib'
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        # Save metadata to SQLite
        self.db.save_model_metadata(self.model_version, self.metrics)
    
    @classmethod
    def load_model(cls, version=None):
        """Load a trained model."""
        db = SQLiteDB()
        
        if version is None:
            # Load latest model version from SQLite
            version = db.get_latest_model_version()
            if version is None:
                raise ValueError("No trained model found.")
        
        # Load model artifacts
        model_path = f'models/anomaly_detector_{version}.joblib'
        scaler_path = f'models/scaler_{version}.joblib'
        
        detector = cls(model_version=version)
        detector.model = joblib.load(model_path)
        detector.scaler = joblib.load(scaler_path)
        
        # Load metadata from SQLite
        detector.metrics = db.get_model_metadata(version)
        
        return detector

def main():
    """Main training function for wind turbine component anomaly detection."""
    # Generate or load data
    generator = SensorDataGenerator()
    data = generator.generate_mixed_data(n_samples=1000)
    
    # Train model
    detector = AnomalyDetector()
    metrics = detector.train(data)
    
    # Print training statistics
    print("\nTraining Statistics (Wind Turbine Component Factory):")
    print(f"Model Version: {detector.model_version}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    print(f"F1 Score: {metrics['f1_score']:.4f}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Mean anomaly score: {metrics['mean_anomaly_score']:.4f}")
    print(f"Std anomaly score: {metrics['std_anomaly_score']:.4f}")
    print(f"Max anomaly score: {metrics['max_anomaly_score']:.4f}")
    print(f"Min anomaly score: {metrics['min_anomaly_score']:.4f}")

if __name__ == '__main__':
    main() 