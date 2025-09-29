# models/model_loader.py
"""
Model Loader - Trained modeli yükle ve cache'le
"""
import os
import pickle
import numpy as np
from tensorflow import keras
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ModelLoader:
    """ML Model yükleme ve cache servisi"""
    
    def __init__(self, artifacts_dir: str = "models/artifacts"):
        self.artifacts_dir = artifacts_dir
        self.model = None
        self.feature_scaler = None
        self.label_scaler = None
        self.metadata = None
        self.is_loaded = False
    
    def load_model(self, model_name: str = "stock_predictor_v1.keras") -> keras.Model:
        """Model'i yükle"""
        try:
            model_path = os.path.join(self.artifacts_dir, model_name)
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model not found: {model_path}")
            
            logger.info(f"Loading model from {model_path}")
            self.model = keras.models.load_model(model_path)
            logger.info(f"✅ Model loaded successfully")
            
            return self.model
            
        except Exception as e:
            logger.error(f"❌ Error loading model: {str(e)}")
            raise
    
    def load_scalers(self) -> Tuple:
        """Feature ve target scaler'ları yükle"""
        try:
            feature_scaler_path = os.path.join(self.artifacts_dir, "feature_scaler.pkl")
            label_scaler_path = os.path.join(self.artifacts_dir, "label_scaler.pkl")
            
            with open(feature_scaler_path, 'rb') as f:
                self.feature_scaler = pickle.load(f)
            
            with open(label_scaler_path, 'rb') as f:
                self.label_scaler = pickle.load(f)
            
            logger.info("✅ Scalers loaded successfully")
            return self.feature_scaler, self.label_scaler
            
        except Exception as e:
            logger.error(f"❌ Error loading scalers: {str(e)}")
            raise
    
    def load_metadata(self) -> dict:
        """Model metadata'sını yükle"""
        try:
            import json
            metadata_path = os.path.join(self.artifacts_dir, "model_metadata.json")
            
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
            
            logger.info("✅ Metadata loaded successfully")
            return self.metadata
            
        except Exception as e:
            logger.error(f"❌ Error loading metadata: {str(e)}")
            raise
    
    def load_all(self) -> bool:
        """Tüm artifactları yükle"""
        try:
            logger.info("🔄 Loading all artifacts...")
            
            self.load_model()
            self.load_scalers()
            self.load_metadata()
            
            self.is_loaded = True
            logger.info("✅ All artifacts loaded successfully!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load artifacts: {str(e)}")
            self.is_loaded = False
            return False
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Tahmin yap"""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_all() first.")
        
        if self.model is None:
            raise RuntimeError("Model is None")
        
        # Predict
        predictions_scaled = self.model.predict(X, verbose=0)
        
        # Inverse transform
        predictions = self.label_scaler.inverse_transform(predictions_scaled)
        
        return predictions
    
    def get_model_info(self) -> dict:
        """Model bilgilerini döndür"""
        if not self.is_loaded:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "version": self.metadata.get("model_version"),
            "trained_on": self.metadata.get("trained_on"),
            "symbol": self.metadata.get("symbol"),
            "sequence_length": self.metadata.get("sequence_length"),
            "model_format": self.metadata.get("model_format"),
        }


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    loader = ModelLoader()
    
    # Tüm artifactları yükle
    loader.load_all()
    
    # Model bilgisi
    info = loader.get_model_info()
    print("\n📊 Model Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test prediction (dummy data)
    print("\n🧪 Testing prediction...")
    dummy_input = np.random.rand(1, 60, 30)  # (batch, sequence, features)
    prediction = loader.predict(dummy_input)
    print(f"✅ Prediction: ${prediction[0][0]:.2f}")