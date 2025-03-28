import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import joblib
import shap
from .data_processing import DataProcessor

class ModelTrainer:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.models = {
            'xgboost': XGBClassifier(),
            'random_forest': RandomForestClassifier(),
            'logistic_regression': LogisticRegression()
        }
        self.best_model = None
        self.explainer = None

    def load_data(self, data_path):
        """Load and preprocess the data"""
        data = pd.read_csv(data_path)
        X = data.drop('converted', axis=1)
        y = data['converted']
        return X, y

    def train_models(self, X_train, y_train):
        """Train multiple models and select the best one"""
        self.data_processor.fit_preprocessor(X_train)
        X_train_processed = self.data_processor.transform_data(X_train)
        
        best_score = 0
        for name, model in self.models.items():
            model.fit(X_train_processed, y_train)
            score = model.score(X_train_processed, y_train)
            if score > best_score:
                best_score = score
                self.best_model = model
                joblib.dump(model, f'models/{name}_model.joblib')
        
        # Create SHAP explainer
        self.explainer = shap.Explainer(self.best_model)
        joblib.dump(self.explainer, 'models/shap_explainer.joblib')
        
        return self.best_model

    def evaluate_model(self, X_test, y_test):
        """Evaluate model performance on test set"""
        X_test_processed = self.data_processor.transform_data(X_test)
        y_pred = self.best_model.predict(X_test_processed)
        y_proba = self.best_model.predict_proba(X_test_processed)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_proba)
        }
        
        return metrics

    def explain_prediction(self, X_sample):
        """Generate SHAP explanation for a single prediction"""
        if self.explainer is None:
            self.explainer = joblib.load('models/shap_explainer.joblib')
            
        X_processed = self.data_processor.transform_data(X_sample)
        shap_values = self.explainer(X_processed)
        return shap_values