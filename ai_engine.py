import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
from database import get_db
from models import Checklist, Barn
import joblib
import os

class FarmRiskPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
            'hygiene_score', 'mortality_count', 'feed_quality', 
            'water_quality', 'ventilation_score', 'temperature', 'humidity'
        ]
    
    def prepare_training_data(self):
        """Prepare training data from database"""
        db = get_db()
        try:
            # Get checklist data with features
            checklists = db.query(Checklist).all()
            
            if len(checklists) < 10:  # Not enough data for training
                return self.create_synthetic_data()
            
            data = []
            for checklist in checklists:
                features = [
                    checklist.hygiene_score,
                    checklist.mortality_count,
                    checklist.feed_quality,
                    checklist.water_quality,
                    checklist.ventilation_score,
                    checklist.temperature,
                    checklist.humidity
                ]
                
                # Calculate risk level based on thresholds
                risk_level = self.calculate_risk_level(features)
                data.append(features + [risk_level])
            
            df = pd.DataFrame(data, columns=self.feature_columns + ['risk_level'])
            return df
            
        finally:
            db.close()
    
    def create_synthetic_data(self):
        """Create synthetic training data for demo purposes"""
        np.random.seed(42)
        n_samples = 1000
        
        data = []
        for _ in range(n_samples):
            # Generate features with some correlation to risk
            hygiene = np.random.normal(7, 2)
            mortality = np.random.poisson(1)
            feed_quality = np.random.normal(8, 1.5)
            water_quality = np.random.normal(8.5, 1)
            ventilation = np.random.normal(7.5, 1.5)
            temperature = np.random.normal(22, 3)
            humidity = np.random.normal(55, 10)
            
            features = [hygiene, mortality, feed_quality, water_quality, 
                       ventilation, temperature, humidity]
            risk_level = self.calculate_risk_level(features)
            
            data.append(features + [risk_level])
        
        df = pd.DataFrame(data, columns=self.feature_columns + ['risk_level'])
        return df
    
    def calculate_risk_level(self, features):
        """Calculate risk level based on feature thresholds"""
        hygiene, mortality, feed_quality, water_quality, ventilation, temperature, humidity = features
        
        risk_score = 0
        
        # Hygiene score (lower is worse)
        if hygiene < 5:
            risk_score += 3
        elif hygiene < 7:
            risk_score += 1
        
        # Mortality count (higher is worse)
        if mortality > 3:
            risk_score += 3
        elif mortality > 1:
            risk_score += 1
        
        # Feed quality (lower is worse)
        if feed_quality < 6:
            risk_score += 2
        elif feed_quality < 8:
            risk_score += 1
        
        # Water quality (lower is worse)
        if water_quality < 7:
            risk_score += 2
        elif water_quality < 8:
            risk_score += 1
        
        # Ventilation (lower is worse)
        if ventilation < 6:
            risk_score += 2
        elif ventilation < 7:
            risk_score += 1
        
        # Temperature (extreme values are worse)
        if temperature < 15 or temperature > 28:
            risk_score += 2
        elif temperature < 18 or temperature > 25:
            risk_score += 1
        
        # Humidity (extreme values are worse)
        if humidity < 30 or humidity > 80:
            risk_score += 2
        elif humidity < 40 or humidity > 70:
            risk_score += 1
        
        # Classify risk level
        if risk_score >= 6:
            return 2  # High risk
        elif risk_score >= 3:
            return 1  # Medium risk
        else:
            return 0  # Low risk
    
    def train_model(self):
        """Train the risk prediction model"""
        df = self.prepare_training_data()
        
        X = df[self.feature_columns]
        y = df['risk_level']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        return True
    
    def predict_risk(self, features):
        """Predict risk level for given features"""
        if not self.is_trained:
            self.train_model()
        
        # Ensure features is a 2D array
        if len(features) == len(self.feature_columns):
            features = [features]
        
        features_scaled = self.scaler.transform(features)
        prediction = self.model.predict(features_scaled)
        probabilities = self.model.predict_proba(features_scaled)
        
        return prediction[0], probabilities[0]
    
    def get_risk_label(self, risk_level):
        """Convert risk level to label"""
        labels = {0: "Low", 1: "Medium", 2: "High"}
        return labels.get(risk_level, "Unknown")
    
    def predict_barn_risk(self, barn_id):
        """Predict risk for a specific barn based on latest checklist"""
        db = get_db()
        try:
            # Get latest checklist for barn
            latest_checklist = db.query(Checklist).filter(
                Checklist.barn_id == barn_id
            ).order_by(Checklist.submitted_at.desc()).first()
            
            if not latest_checklist:
                return "No data", None
            
            features = [
                latest_checklist.hygiene_score or 7,
                latest_checklist.mortality_count or 0,
                latest_checklist.feed_quality or 8,
                latest_checklist.water_quality or 8,
                latest_checklist.ventilation_score or 7,
                latest_checklist.temperature or 22,
                latest_checklist.humidity or 55
            ]
            
            risk_level, probabilities = self.predict_risk(features)
            return self.get_risk_label(risk_level), probabilities
            
        finally:
            db.close()
    
    def update_barn_risks(self):
        """Update risk levels for all barns"""
        db = get_db()
        try:
            barns = db.query(Barn).all()
            
            for barn in barns:
                risk_label, _ = self.predict_barn_risk(barn.id)
                if risk_label != "No data":
                    barn.risk_level = risk_label.lower()
                    barn.last_updated = datetime.utcnow()
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error updating barn risks: {e}")
            return False
        finally:
            db.close()

# Global predictor instance
risk_predictor = FarmRiskPredictor()
