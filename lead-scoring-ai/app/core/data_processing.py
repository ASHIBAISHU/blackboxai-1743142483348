import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import joblib
import logging
from typing import Dict, Any
import shap

class DataProcessor:
    def __init__(self):
        self.preprocessor = None
        self.feature_columns = [
            'company_size',
            'annual_revenue',
            'num_employees',
            'industry',
            'lead_source',
            'past_interactions'
        ]
        self.logger = logging.getLogger(__name__)
        self.feature_importance = {}
        
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate input data structure and content"""
        required_columns = set(self.feature_columns)
        if not required_columns.issubset(data.columns):
            missing = required_columns - set(data.columns)
            self.logger.error(f"Missing required columns: {missing}")
            return False
            
        if data.empty:
            self.logger.error("Empty dataset provided")
            return False
            
        return True
        
    def create_preprocessor(self) -> None:
        """Create the data preprocessing pipeline with missing value handling"""
        numeric_features = ['company_size', 'annual_revenue', 'num_employees']
        categorical_features = ['industry', 'lead_source']
        
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        
    def fit_preprocessor(self, data: pd.DataFrame) -> None:
        """Fit the preprocessor on training data and calculate initial feature importance"""
        if not self.validate_data(data):
            raise ValueError("Invalid input data")
            
        if self.preprocessor is None:
            self.create_preprocessor()
            
        self.logger.info("Fitting preprocessor on training data")
        self.preprocessor.fit(data[self.feature_columns])
        
        # Calculate initial feature importance
        self._calculate_feature_importance(data)
        joblib.dump(self.preprocessor, 'models/preprocessor.joblib')
        
    def transform_data(self, data: pd.DataFrame) -> np.ndarray:
        """Transform input data using fitted preprocessor"""
        if not self.validate_data(data):
            raise ValueError("Invalid input data")
            
        if self.preprocessor is None:
            try:
                self.preprocessor = joblib.load('models/preprocessor.joblib')
            except FileNotFoundError:
                raise ValueError("Preprocessor not fitted yet")
                
        self.logger.info("Transforming input data")
        return self.preprocessor.transform(data[self.feature_columns])
        
    def _calculate_feature_importance(self, data: pd.DataFrame) -> None:
        """Calculate and store initial feature importance using SHAP values"""
        try:
            # Sample data for initial importance calculation
            sample_data = data.sample(min(100, len(data)))
            transformed = self.preprocessor.transform(sample_data)
            
            # Calculate SHAP values (placeholder - would use actual model in production)
            explainer = shap.Explainer(model=None, masker=transformed)
            shap_values = explainer(transformed)
            
            # Store importance by feature
            feature_names = self._get_feature_names()
            for i, name in enumerate(feature_names):
                self.feature_importance[name] = np.abs(shap_values.values[:,i]).mean()
                
            self.logger.info(f"Calculated initial feature importance: {self.feature_importance}")
        except Exception as e:
            self.logger.warning(f"Failed to calculate feature importance: {str(e)}")
            
    def _get_feature_names(self) -> list:
        """Get feature names after preprocessing"""
        if self.preprocessor is None:
            return []
            
        numeric_features = ['company_size', 'annual_revenue', 'num_employees']
        categorical_features = ['industry', 'lead_source']
        
        # Get categorical feature names from onehot encoder
        cat_transformer = self.preprocessor.named_transformers_['cat']
        if hasattr(cat_transformer, 'named_steps'):
            onehot = cat_transformer.named_steps['onehot']
            cat_features = onehot.get_feature_names_out(categorical_features)
        else:
            cat_features = []
            
        return numeric_features + list(cat_features)
        
    def get_feature_importance(self) -> Dict[str, float]:
        """Get current feature importance metrics"""
        return self.feature_importance
