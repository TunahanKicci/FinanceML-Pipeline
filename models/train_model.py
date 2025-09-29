# models/train_model.py
"""
LSTM Model Training Pipeline
"""
import os
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import pickle
from datetime import datetime

# Local imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.sources.yahoo_finance import YahooFinanceClient
from data.feature_engineering import FeatureEngineer


class StockPredictor:
    """LSTM Stock Prediction Model"""
    
    def __init__(self, sequence_length=60):
        self.sequence_length = sequence_length
        self.model = None
        self.feature_scaler = MinMaxScaler()
        self.target_scaler = MinMaxScaler()
        
    def prepare_data(self, symbol="AAPL", period="2y"):
        """Veriyi hazırla"""
        print(f"\n{'='*50}")
        print(f"📊 PREPARING DATA FOR {symbol}")
        print(f"{'='*50}\n")
        
        # 1. Veri çek
        client = YahooFinanceClient()
        df = client.fetch_stock_data(symbol, period=period)
        
        # 2. Feature engineering
        engineer = FeatureEngineer()
        df = engineer.add_technical_indicators(df)
        
        # 3. NaN temizle
        df = df.dropna()
        print(f"✅ Clean data shape: {df.shape}")
        
        # 4. Target'ı ayır
        target = df['Close'].values.reshape(-1, 1)
        features = df.drop(['Close'], axis=1).values
        
        # 5. Scaling
        features_scaled = self.feature_scaler.fit_transform(features)
        target_scaled = self.target_scaler.fit_transform(target)
        
        # 6. Scaled dataframe oluştur
        df_scaled = pd.DataFrame(features_scaled, columns=df.drop(['Close'], axis=1).columns)
        df_scaled['Close'] = target_scaled
        
        # 7. Sequences oluştur
        X, y = engineer.create_sequences(df_scaled, self.sequence_length)
        
        print(f"✅ Sequences created: X{X.shape}, y{y.shape}")
        
        # 8. Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False  # Time series için shuffle=False
        )
        
        print(f"✅ Train: {X_train.shape}, Test: {X_test.shape}")
        
        return X_train, X_test, y_train, y_test
    
    def build_model(self, input_shape):
        """LSTM model oluştur"""
        print(f"\n{'='*50}")
        print(f"🏗️ BUILDING MODEL")
        print(f"{'='*50}\n")
        
        model = Sequential([
            # LSTM Layer 1
            LSTM(units=50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            
            # LSTM Layer 2
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),
            
            # LSTM Layer 3
            LSTM(units=50, return_sequences=False),
            Dropout(0.2),
            
            # Dense layers
            Dense(units=25, activation='relu'),
            Dense(units=1)  # Output: next day price
        ])
        
        model.compile(
            optimizer='adam',
            loss='mean_squared_error',
            metrics=['mae', 'mse']
        )
        
        print(model.summary())
        self.model = model
        return model
    
    def train(self, X_train, y_train, X_test, y_test, epochs=50, batch_size=32):
        """Model'i eğit"""
        print(f"\n{'='*50}")
        print(f"🚀 TRAINING MODEL")
        print(f"{'='*50}\n")

        # Artifacts klasörünü oluştur
        os.makedirs('models/artifacts', exist_ok=True)
        
        # Callbacks
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        checkpoint = ModelCheckpoint(
            'models/artifacts/best_model.keras',
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        )
        
        # Training
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop, checkpoint],
            verbose=1
        )
        
        return history
    
    def evaluate(self, X_test, y_test):
        """Model performansını değerlendir"""
        print(f"\n{'='*50}")
        print(f"📊 EVALUATING MODEL")
        print(f"{'='*50}\n")
        
        # Predictions
        y_pred = self.model.predict(X_test)
        
        # Inverse transform
        y_test_actual = self.target_scaler.inverse_transform(y_test.reshape(-1, 1))
        y_pred_actual = self.target_scaler.inverse_transform(y_pred)
        
        # Metrics
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        mse = mean_squared_error(y_test_actual, y_pred_actual)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test_actual, y_pred_actual)
        r2 = r2_score(y_test_actual, y_pred_actual)
        
        # MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((y_test_actual - y_pred_actual) / y_test_actual)) * 100
        
        metrics = {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'r2': float(r2),
            'mape': float(mape)
        }
        
        print(f"📈 MSE:  {mse:.4f}")
        print(f"📈 RMSE: {rmse:.4f}")
        print(f"📈 MAE:  {mae:.4f}")
        print(f"📈 R²:   {r2:.4f}")
        print(f"📈 MAPE: {mape:.2f}%")
        
        return metrics
    
    def save_artifacts(self, symbol, metrics):
        """Model ve metadata'yı kaydet"""
        print(f"\n{'='*50}")
        print(f"💾 SAVING ARTIFACTS")
        print(f"{'='*50}\n")
        
        artifacts_dir = 'models/artifacts'
        os.makedirs(artifacts_dir, exist_ok=True)
        
        # 1. Model (.h5)
        model_path = f'{artifacts_dir}/stock_predictor_v1.keras'
        self.model.save(model_path)
        print(f"✅ Model saved: {model_path}")
        
        # 2. Scalers (.pkl)
        with open(f'{artifacts_dir}/feature_scaler.pkl', 'wb') as f:
            pickle.dump(self.feature_scaler, f)
        
        with open(f'{artifacts_dir}/label_scaler.pkl', 'wb') as f:
            pickle.dump(self.target_scaler, f)
        print(f"✅ Scalers saved")
        
        # 3. Metadata (.json)
        metadata = {
            'model_version': 'v1.0.0',
            'trained_on': datetime.now().isoformat(),
            'symbol': symbol,
            'sequence_length': self.sequence_length,
            'model_format': 'keras',
            'architecture': {
                'type': 'LSTM',
                'layers': [
                    {'type': 'LSTM', 'units': 50, 'return_sequences': True},
                    {'type': 'Dropout', 'rate': 0.2},
                    {'type': 'LSTM', 'units': 50, 'return_sequences': True},
                    {'type': 'Dropout', 'rate': 0.2},
                    {'type': 'LSTM', 'units': 50, 'return_sequences': False},
                    {'type': 'Dropout', 'rate': 0.2},
                    {'type': 'Dense', 'units': 25, 'activation': 'relu'},
                    {'type': 'Dense', 'units': 1}
                ]
            }
        }
        
        with open(f'{artifacts_dir}/model_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Metadata saved")
        
        # 4. Performance metrics (.json)
        with open(f'{artifacts_dir}/model_performance.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"✅ Performance metrics saved")
        
        print(f"\n🎉 All artifacts saved successfully!")


def main():
    """Ana training pipeline"""
    print(f"\n{'='*60}")
    print(f"🤖 STOCK PREDICTION MODEL TRAINING")
    print(f"{'='*60}\n")
    
    # Configuration
    SYMBOL = "AAPL"  # Apple stock
    PERIOD = "2y"     # 2 years of data
    SEQUENCE_LENGTH = 60  # 60 days lookback
    EPOCHS = 50
    BATCH_SIZE = 32
    
    # Initialize
    predictor = StockPredictor(sequence_length=SEQUENCE_LENGTH)
    
    # 1. Prepare data
    X_train, X_test, y_train, y_test = predictor.prepare_data(SYMBOL, PERIOD)
    
    # 2. Build model
    input_shape = (X_train.shape[1], X_train.shape[2])
    predictor.build_model(input_shape)
    
    # 3. Train
    history = predictor.train(X_train, y_train, X_test, y_test, EPOCHS, BATCH_SIZE)
    
    # 4. Evaluate
    metrics = predictor.evaluate(X_test, y_test)
    
    # 5. Save
    predictor.save_artifacts(SYMBOL, metrics)
    
    print(f"\n{'='*60}")
    print(f"✅ TRAINING COMPLETED SUCCESSFULLY!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()