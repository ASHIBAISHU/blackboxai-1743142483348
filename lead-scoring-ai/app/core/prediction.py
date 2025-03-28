import pandas as pd
import joblib
from typing import Dict, Any
from .data_processing import DataProcessor

class LeadScorer:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.model = None
        self.confidence_threshold = 0.7  # Threshold for automatic decisions

    def load_model(self, model_path: str = 'models/xgboost_model.joblib'):
        """Load a trained model from disk"""
        try:
            self.model = joblib.load(model_path)
        except FileNotFoundError:
            raise ValueError("Model not found. Please train the model first.")

    def predict_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a prediction for a single lead"""
        if self.model is None:
            self.load_model()

        # Convert input to DataFrame for processing
        lead_df = pd.DataFrame([lead_data])
        
        try:
            # Process the input data
            processed_data = self.data_processor.transform_data(lead_df)
            
            # Make prediction
            probability = self.model.predict_proba(processed_data)[0][1]
            needs_review = not (probability > self.confidence_threshold or 
                              probability < (1 - self.confidence_threshold))
            
            return {
                'score': float(probability),
                'prediction': probability > 0.5,
                'needs_human_review': needs_review,
                'confidence': abs(probability - 0.5) * 2  # Normalized to 0-1
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'needs_human_review': True
            }

    def process_feedback(self, feedback_data: Dict[str, Any]) -> None:
        """Process human feedback to improve the model"""
        # In a production system, this would store feedback for model retraining
        # For now, we'll just log it
        print(f"Feedback received: {feedback_data}")