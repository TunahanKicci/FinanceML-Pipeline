"""
Model Loader - Çoklu hisse senedi modelini yükle ve cache'le
"""
import os
import pickle
import numpy as np
from tensorflow import keras
from typing import Optional, Tuple
import logging
import json

logger = logging.getLogger(__name__)


class ModelLoader:
    """ML Model yükleme ve cache servisi (çoklu sembol desteğiyle)"""
    
    def __init__(self, base_dir: str = "models/artifacts", symbol: str = "V"):
        """
        Args:
            base_dir (str): Model artifactlarının bulunduğu ana klasör
            symbol (str): Hisse sembolü (ör: 'V', 'WMT')
        """
        self.base_dir = base_dir
        self.symbol = symbol.upper()
        self.artifacts_dir = os.path.join(base_dir, self.symbol)
        
        self.model = None
        self.feature_scaler = None
        self.label_scaler = None
        self.metadata = None
        self.is_loaded = False

    # -----------------------------------------------------------
    # MODEL YÜKLEME
    # -----------------------------------------------------------
    def load_model(self) -> keras.Model:
        """Belirli bir sembole ait modeli yükle"""
        try:
            model_path = os.path.join(self.artifacts_dir, f"{self.symbol}_model.keras")

            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model not found: {model_path}")

            logger.info(f" Loading model from {model_path}")
            self.model = keras.models.load_model(model_path)
            logger.info(" Model loaded successfully")

            return self.model

        except Exception as e:
            logger.error(f" Error loading model: {str(e)}")
            raise

    # -----------------------------------------------------------
    # SCALER YÜKLEME
    # -----------------------------------------------------------
    def load_scalers(self) -> Tuple:
        """Feature ve target scaler'ları yükle"""
        try:
            feature_scaler_path = os.path.join(self.artifacts_dir, "scaler_X.pkl")
            label_scaler_path = os.path.join(self.artifacts_dir, "scaler_y.pkl")

            if not os.path.exists(feature_scaler_path):
                raise FileNotFoundError(f"Feature scaler not found: {feature_scaler_path}")
            if not os.path.exists(label_scaler_path):
                raise FileNotFoundError(f"Label scaler not found: {label_scaler_path}")

            with open(feature_scaler_path, "rb") as f:
                self.feature_scaler = pickle.load(f)
            with open(label_scaler_path, "rb") as f:
                self.label_scaler = pickle.load(f)

            logger.info(" Scalers loaded successfully")
            return self.feature_scaler, self.label_scaler

        except Exception as e:
            logger.error(f" Error loading scalers: {str(e)}")
            raise

    # -----------------------------------------------------------
    # METADATA YÜKLEME
    # -----------------------------------------------------------
    def load_metadata(self) -> dict:
        """Model metadata'sını yükle"""
        try:
            metadata_path = os.path.join(self.artifacts_dir, "meta.json")

            if not os.path.exists(metadata_path):
                raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

            with open(metadata_path, "r") as f:
                self.metadata = json.load(f)

            logger.info(" Metadata loaded successfully")
            return self.metadata

        except Exception as e:
            logger.error(f" Error loading metadata: {str(e)}")
            raise

    # -----------------------------------------------------------
    # TÜM ARTEFAKTLARI YÜKLE
    # -----------------------------------------------------------
    def load_all(self) -> bool:
        """Tüm artifactları (model, scaler, metadata) yükle"""
        try:
            logger.info(f" Loading all artifacts for symbol: {self.symbol}")
            self.load_model()
            self.load_scalers()
            self.load_metadata()

            self.is_loaded = True
            logger.info(" All artifacts loaded successfully!")
            return True

        except Exception as e:
            logger.error(f" Failed to load artifacts: {str(e)}")
            self.is_loaded = False
            return False

    # -----------------------------------------------------------
    # TAHMİN
    # -----------------------------------------------------------
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Scaled veriden tahmin yap ve inverse-transform uygula"""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_all() first.")
        if self.model is None:
            raise RuntimeError("Model is None")

        predictions_scaled = self.model.predict(X, verbose=0)
        predictions = self.label_scaler.inverse_transform(predictions_scaled)
        return predictions

    # -----------------------------------------------------------
    # MODEL BİLGİLERİ
    # -----------------------------------------------------------
    def get_model_info(self) -> dict:
        """Model metadata'sını döndür"""
        if not self.is_loaded or self.metadata is None:
            return {"status": "not_loaded"}

        return {
            "status": "loaded",
            "symbol": self.symbol,
            "trained_on": self.metadata.get("trained_on"),
            "model_format": self.metadata.get("model_format"),
            "sequence_length": self.metadata.get("sequence_length"),
            "version": self.metadata.get("model_version", "1.0"),
        }


# -----------------------------------------------------------
# LOCAL TEST
# -----------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    loader = ModelLoader(symbol="WMT")  # veya "V"
    
    if loader.load_all():
        info = loader.get_model_info()
        print("\n Model Info:")
        for k, v in info.items():
            print(f"  {k}: {v}")

        print("\n Testing dummy prediction...")
        dummy_input = np.random.rand(1, 60, 13)  # (batch, seq, features)
        pred = loader.predict(dummy_input)
        print(f" Dummy prediction: {pred[0][0]:.5f}")
