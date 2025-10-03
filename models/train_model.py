"""
LSTM Model Training Pipeline - Per Stock Strategy
Her hisse için ayrı model eğitimi
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
from data.processors.fundamental_processor import FundamentalProcessor


class StockPredictor:
    """LSTM Stock Prediction Model - Single Stock"""
    
    def __init__(self, sequence_length=60, use_fundamentals=True):
        self.sequence_length = sequence_length
        self.use_fundamentals = use_fundamentals
        self.model = None
        self.feature_scaler = MinMaxScaler()
        self.target_scaler = MinMaxScaler()
        
    def prepare_data(self, symbol, period="2y"):
        """Tek hisse için veriyi hazırla"""
        print(f"\n{'='*50}")
        print(f"📊 PREPARING DATA FOR: {symbol}")
        print(f"{'='*50}\n")

        client = YahooFinanceClient()
        df = client.fetch_stock_data(symbol, period=period)

        # Fundamental data ekle
        if self.use_fundamentals:
            fproc = FundamentalProcessor()
            df = fproc.fetch_and_merge_fundamentals(symbol, df)
            print("✅ Fundamental features added")

        # Feature engineering
        engineer = FeatureEngineer()
        df = engineer.add_technical_indicators(df)

        # NaN temizle
        df = df.dropna(axis=1, how="all")
        df = df.fillna(method="ffill").fillna(method="bfill")

        target_col = "Close"
        target = df[target_col].values.reshape(-1, 1)
        features_df = df.drop([target_col], axis=1)

        feature_columns = list(features_df.columns)

        print(f"\n🎯 TARGET: {target_col}")
        print(f"📋 FEATURE COUNT: {len(feature_columns)}")

        features = features_df.values

        # Scaling
        features_scaled = self.feature_scaler.fit_transform(features)
        target_scaled = self.target_scaler.fit_transform(target)

        df_scaled = pd.DataFrame(features_scaled, columns=feature_columns)
        df_scaled["Close"] = target_scaled

        X, y = engineer.create_sequences(df_scaled, self.sequence_length)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )

        return X_train, X_test, y_train, y_test, feature_columns
    
    def build_model(self, input_shape):
        """LSTM model oluştur"""
        print(f"\n{'='*50}")
        print(f"🏗️ BUILDING MODEL")
        print(f"{'='*50}\n")
        
        print(f"📐 Input shape: {input_shape}")
        print(f"   Sequence length: {input_shape[0]}")
        print(f"   Features: {input_shape[1]}")
        
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
    
    def train(self, X_train, y_train, X_test, y_test, symbol, epochs=50, batch_size=32):
        """Model'i eğit"""
        print(f"\n{'='*50}")
        print(f"🚀 TRAINING MODEL FOR {symbol}")
        print(f"{'='*50}\n")

        # Symbol-specific artifacts klasörü
        artifacts_dir = f'models/artifacts/{symbol}'
        os.makedirs(artifacts_dir, exist_ok=True)
        
        # Callbacks
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        checkpoint = ModelCheckpoint(
            f'{artifacts_dir}/best_model.keras',
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
    
    def save_artifacts(self, symbol, metrics, feature_columns):
        """Model ve metadata'yı kaydet"""
        print(f"\n{'='*50}")
        print(f"💾 SAVING ARTIFACTS FOR {symbol}")
        print(f"{'='*50}\n")
        
        artifacts_dir = f'models/artifacts/{symbol}'
        os.makedirs(artifacts_dir, exist_ok=True)
        
        # 1. Model (.keras)
        model_path = f'{artifacts_dir}/{symbol}_model.keras'
        self.model.save(model_path)
        print(f"✅ Model saved: {model_path}")
        
        # 2. Scalers (.pkl)
        with open(f'{artifacts_dir}/feature_scaler.pkl', 'wb') as f:
            pickle.dump(self.feature_scaler, f)
        
        with open(f'{artifacts_dir}/label_scaler.pkl', 'wb') as f:
            pickle.dump(self.target_scaler, f)
        print(f"✅ Scalers saved")
        
        # 3. Feature columns (.json)
        with open(f'{artifacts_dir}/feature_columns.json', 'w') as f:
            json.dump(feature_columns, f, indent=2)
        print(f"✅ Feature columns saved ({len(feature_columns)} features)")
        
        # 4. Metadata (.json)
        metadata = {
            'model_version': 'v1.0.0',
            'trained_on': datetime.now().isoformat(),
            'symbol': symbol,
            'sequence_length': self.sequence_length,
            'feature_count': len(feature_columns),
            'use_fundamentals': self.use_fundamentals,
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
            },
            'metrics': metrics
        }
        
        with open(f'{artifacts_dir}/model_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Metadata saved")
        
        # 5. Performance metrics (.json)
        with open(f'{artifacts_dir}/model_performance.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"✅ Performance metrics saved")
        
        print(f"\n🎉 All artifacts saved to: {artifacts_dir}")


def train_single_stock(symbol, period="5y", sequence_length=60, epochs=50, batch_size=32, use_fundamentals=True):
    """Tek hisse için training pipeline"""
    print(f"\n{'='*60}")
    print(f"🤖 TRAINING MODEL FOR: {symbol}")
    print(f"{'='*60}\n")
    
    try:
        # Initialize
        predictor = StockPredictor(sequence_length=sequence_length, use_fundamentals=use_fundamentals)
        
        # 1. Prepare data
        X_train, X_test, y_train, y_test, feature_columns = predictor.prepare_data(symbol, period)
        
        # 2. Build model
        input_shape = (X_train.shape[1], X_train.shape[2])
        predictor.build_model(input_shape)
        
        # 3. Train
        history = predictor.train(X_train, y_train, X_test, y_test, symbol, epochs, batch_size)
        
        # 4. Evaluate
        metrics = predictor.evaluate(X_test, y_test)
        
        # 5. Save
        predictor.save_artifacts(symbol, metrics, feature_columns)
        
        print(f"\n{'='*60}")
        print(f"✅ {symbol} TRAINING COMPLETED!")
        print(f"   R² Score: {metrics['r2']:.4f}")
        print(f"   MAPE: {metrics['mape']:.2f}%")
        print(f"{'='*60}\n")
        
        return True, metrics
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ ERROR TRAINING {symbol}: {str(e)}")
        print(f"{'='*60}\n")
        return False, None


def main():
    """Ana training pipeline - Tüm hisseler için"""
    print(f"\n{'='*60}")
    print(f"🚀 MULTI-STOCK TRAINING PIPELINE")
    print(f"   Strategy: Separate Model Per Stock")
    print(f"{'='*60}\n")
    
    # Configuration
    SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", 
               "META", "NVDA", "JPM", "V", "WMT"]
    PERIOD = "5y"
    SEQUENCE_LENGTH = 60
    EPOCHS = 50
    BATCH_SIZE = 32
    USE_FUNDAMENTALS = True
    
    # Training summary
    results = {}
    
    for i, symbol in enumerate(SYMBOLS, 1):
        print(f"\n{'#'*60}")
        print(f"# STOCK {i}/{len(SYMBOLS)}: {symbol}")
        print(f"{'#'*60}")
        
        success, metrics = train_single_stock(
            symbol=symbol,
            period=PERIOD,
            sequence_length=SEQUENCE_LENGTH,
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            use_fundamentals=USE_FUNDAMENTALS
        )
        
        results[symbol] = {
            'success': success,
            'metrics': metrics
        }
    
    # Final Summary
    print(f"\n\n{'='*60}")
    print(f"📊 TRAINING SUMMARY")
    print(f"{'='*60}\n")
    
    successful = [s for s, r in results.items() if r['success']]
    failed = [s for s, r in results.items() if not r['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(SYMBOLS)}")
    print(f"❌ Failed: {len(failed)}/{len(SYMBOLS)}")
    
    if successful:
        print(f"\n📈 Performance Summary:")
        print(f"{'Symbol':<10} {'R²':<10} {'MAPE':<10} {'RMSE':<10}")
        print(f"{'-'*40}")
        
        for symbol in successful:
            m = results[symbol]['metrics']
            print(f"{symbol:<10} {m['r2']:<10.4f} {m['mape']:<10.2f} {m['rmse']:<10.2f}")
    
    if failed:
        print(f"\n❌ Failed stocks: {', '.join(failed)}")
    
    # Save overall summary
    summary_path = 'models/artifacts/training_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Summary saved to: {summary_path}")
    
    print(f"\n{'='*60}")
    print(f"🎉 TRAINING PIPELINE COMPLETED!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()