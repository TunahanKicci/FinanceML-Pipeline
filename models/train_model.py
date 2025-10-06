"""
Stable Stock Predictor - return-based target, unidirectional LSTM
Updated: save artifacts with multiple filenames to remain backward-compatible
with different ModelLoader conventions (scaler_X/scaler_y, feature_scaler/label_scaler,
model_metadata.json/meta.json, feature_columns.json/features.json) and copy root-level
artifacts (stock_predictor_v1.keras, feature_scaler.pkl, label_scaler.pkl, feature_columns.json, model_metadata.json).
"""
import os
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
import pickle
from datetime import datetime
import shutil
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.sources.yahoo_finance import YahooFinanceClient
from data.feature_engineering import FeatureEngineer


class StableStockPredictor:
    """Return-based stock prediction with unidirectional LSTM"""
    def __init__(self, sequence_length=60, feature_scaler=None, target_scaler=None):
        self.sequence_length = sequence_length
        self.model = None
        # Default scalers
        self.feature_scaler = feature_scaler if feature_scaler is not None else StandardScaler()
        self.target_scaler = target_scaler if target_scaler is not None else StandardScaler()

    def add_return_features(self, df):
        df = df.copy()
        df['Return'] = df['Close'].pct_change().fillna(0)
        df['Return_lag_1'] = df['Return'].shift(1).fillna(0)
        df['Return_lag_2'] = df['Return'].shift(2).fillna(0)
        df['Volatility_5'] = df['Return'].rolling(5).std().ffill().fillna(0)
        df['Volatility_20'] = df['Return'].rolling(20).std().ffill().fillna(0)
        df['Price_Position'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'] + 1e-8)
        df['Price_Position'] = df['Price_Position'].fillna(0.5)
        df['Volume_MA_20'] = df['Volume'].rolling(20).mean().ffill().fillna(0)
        df['Volume_Ratio'] = (df['Volume'] / (df['Volume_MA_20'] + 1e-8)).fillna(1.0)
        if 'SMA_5' in df.columns and 'SMA_20' in df.columns:
            df['SMA_ratio'] = df['SMA_5'] / (df['SMA_20'] + 1e-8)
        else:
            df['SMA_ratio'] = 1.0
        if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
            df['MACD_diff'] = df['MACD'] - df['MACD_Signal']
        else:
            df['MACD_diff'] = 0.0
        if 'RSI' in df.columns:
            df['RSI_change'] = df['RSI'].diff().fillna(0)
        else:
            df['RSI_change'] = 0.0
        df['HL_Ratio'] = (df['High'] / (df['Low'] + 1e-8)).fillna(1.0)
        df['CO_Ratio'] = (df['Close'] / (df['Open'] + 1e-8)).fillna(1.0)
        df = df.ffill().bfill().fillna(0)
        return df

    def prepare_data(self, symbol, period="3y"):
        print(f"\n{'='*40}\nPREPARING DATA FOR: {symbol}\n{'='*40}\n")
        client = YahooFinanceClient()
        df = client.fetch_stock_data(symbol, period=period)
        engineer = FeatureEngineer()
        df = engineer.add_technical_indicators(df)
        df = self.add_return_features(df)
        # TARGET: next day return
        df['Target_Return'] = (df['Close'].shift(-1) - df['Close']) / (df['Close'] + 1e-8)
        df = df[:-1].copy()
        df = df.replace([np.inf, -np.inf], 0)
        df = df.ffill().bfill().fillna(0)
        feature_cols = [
            'RSI', 'RSI_change',
            'MACD', 'MACD_Signal', 'MACD_diff',
            'SMA_5', 'SMA_10', 'SMA_20', 'SMA_50', 'SMA_ratio',
            'BB_Width', 'ATR',
            'Volatility_5', 'Volatility_20',
            'Volume', 'Volume_Ratio',
            'Price_Position', 'HL_Ratio', 'CO_Ratio',
            'Return_lag_1', 'Return_lag_2'
        ]
        feature_cols = [c for c in feature_cols if c in df.columns]
        print(f"Using {len(feature_cols)} features: {feature_cols}")
        X = df[feature_cols].values
        y = df['Target_Return'].values
        close_prices = df['Close'].values
        X_scaled = self.feature_scaler.fit_transform(X)
        y_scaled = self.target_scaler.fit_transform(y.reshape(-1, 1)).flatten()
        X_seq, y_seq, close_seq = self._create_sequences(X_scaled, y_scaled, close_prices)
        total = len(X_seq)
        train_end = int(total * 0.70)
        val_end = int(total * 0.85)
        X_train = X_seq[:train_end]
        y_train = y_seq[:train_end]
        X_val = X_seq[train_end:val_end]
        y_val = y_seq[train_end:val_end]
        X_test = X_seq[val_end:]
        y_test = y_seq[val_end:]
        close_test = close_seq[val_end:]
        print(f"Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")
        return X_train, X_val, X_test, y_train, y_val, y_test, close_test, feature_cols

    def _create_sequences(self, X, y, close_prices):
        X_seq, y_seq, close_seq = [], [], []
        for i in range(self.sequence_length, len(X)):
            X_seq.append(X[i-self.sequence_length:i])
            y_seq.append(y[i])
            close_seq.append(close_prices[i])
        return np.array(X_seq), np.array(y_seq), np.array(close_seq)

    def build_model(self, input_shape, lr=0.001):
        print(f"\n{'='*40}\nBUILDING MODEL\n{'='*40}\n")
        print(f"Input shape: {input_shape}")
        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=input_shape),
            Dropout(0.3),
            LSTM(32, return_sequences=False),
            Dropout(0.3),
            Dense(16, activation='relu'),
            Dense(1, activation='linear')
        ])
        model.compile(optimizer=Adam(learning_rate=lr), loss='mse', metrics=['mae'])
        model.summary()
        self.model = model
        return model

    def train(self, X_train, y_train, X_val, y_val, symbol, epochs=100, batch_size=32):
        print(f"\n{'='*40}\nTRAINING MODEL FOR {symbol}\n{'='*40}\n")
        artifacts_dir = f'models/artifacts/{symbol}'
        os.makedirs(artifacts_dir, exist_ok=True)
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True, verbose=1),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=8, min_lr=1e-6, verbose=1)
        ]
        history = self.model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=epochs, batch_size=batch_size, callbacks=callbacks, verbose=1)
        return history

    def evaluate(self, X_test, y_test_scaled, close_test):
        print(f"\n{'='*40}\nEVALUATING MODEL\n{'='*40}\n")
        pred_scaled = self.model.predict(X_test, verbose=0).flatten()
        pred_returns = self.target_scaler.inverse_transform(pred_scaled.reshape(-1, 1)).flatten()
        true_returns = self.target_scaler.inverse_transform(y_test_scaled.reshape(-1, 1)).flatten()
        return_mae = mean_absolute_error(true_returns, pred_returns)
        return_rmse = np.sqrt(mean_squared_error(true_returns, pred_returns))
        return_r2 = r2_score(true_returns, pred_returns)
        true_dir = np.sign(true_returns)
        pred_dir = np.sign(pred_returns)
        directional_accuracy = (true_dir == pred_dir).mean() * 100.0
        pred_prices = close_test * (1 + pred_returns)
        true_prices = close_test * (1 + true_returns)
        price_mae = mean_absolute_error(true_prices, pred_prices)
        price_rmse = np.sqrt(mean_squared_error(true_prices, pred_prices))
        price_mape = np.mean(np.abs((true_prices - pred_prices) / (true_prices + 1e-8))) * 100.0
        price_r2 = r2_score(true_prices, pred_prices)
        metrics = {
            'return_mae': float(return_mae),
            'return_rmse': float(return_rmse),
            'return_r2': float(return_r2),
            'directional_accuracy_pct': float(directional_accuracy),
            'price_mae': float(price_mae),
            'price_rmse': float(price_rmse),
            'price_mape_pct': float(price_mape),
            'price_r2': float(price_r2)
        }
        print(f"Return MAE: {return_mae:.6f}")
        print(f"Return RMSE: {return_rmse:.6f}")
        print(f"Return R²: {return_r2:.6f}")
        print(f"Directional accuracy: {directional_accuracy:.2f}%")
        print(f"Price MAE: {price_mae:.4f}")
        print(f"Price RMSE: {price_rmse:.4f}")
        print(f"Price MAPE: {price_mape:.2f}%")
        print(f"Price R²: {price_r2:.4f}")
        return metrics

    def save_artifacts(self, symbol, metrics, feature_columns):
        print(f"\n{'='*40}\nSAVING ARTIFACTS FOR {symbol}\n{'='*40}\n")
        artifacts_dir = f'models/artifacts/{symbol}'
        os.makedirs(artifacts_dir, exist_ok=True)

        # Save model (keras native)
        model_path = f'{artifacts_dir}/{symbol}_model.keras'
        self.model.save(model_path)
        print(f"Model saved: {model_path}")

        # Save scalers
        with open(f'{artifacts_dir}/feature_scaler.pkl', 'wb') as f:
            pickle.dump(self.feature_scaler, f)
        with open(f'{artifacts_dir}/target_scaler.pkl', 'wb') as f:
            pickle.dump(self.target_scaler, f)
        print("Scalers saved")

        # Save feature columns
        with open(f'{artifacts_dir}/feature_columns.json', 'w') as f:
            json.dump(feature_columns, f, indent=2)
        print(f"Features saved ({len(feature_columns)})")

        # Save metadata
        metadata = {
            'model_version': 'v3.0.0',
            'model_type': 'LSTM_Return_Prediction',
            'trained_on': datetime.now().isoformat(),
            'symbol': symbol,
            'sequence_length': self.sequence_length,
            'feature_count': len(feature_columns),
            'metrics': metrics,
            'prediction_type': 'return'
        }
        with open(f'{artifacts_dir}/model_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        print("Metadata saved")

        # ---- Compatibility layer: also save alternate filenames expected by different loaders ----
        try:
            # alternate scaler names
            shutil.copy2(f'{artifacts_dir}/feature_scaler.pkl', f'{artifacts_dir}/scaler_X.pkl')
            shutil.copy2(f'{artifacts_dir}/target_scaler.pkl', f'{artifacts_dir}/scaler_y.pkl')

            # alternate metadata/name
            shutil.copy2(f'{artifacts_dir}/model_metadata.json', f'{artifacts_dir}/meta.json')

            # alternate feature file
            shutil.copy2(f'{artifacts_dir}/feature_columns.json', f'{artifacts_dir}/features.json')

            # copy root-level artifacts for legacy loaders
            root_dir = 'models/artifacts'
            os.makedirs(root_dir, exist_ok=True)
            shutil.copy2(model_path, f'{root_dir}/{symbol}_model.keras')
            shutil.copy2(model_path, f'{root_dir}/stock_predictor_v1.keras')
            shutil.copy2(f'{artifacts_dir}/feature_scaler.pkl', f'{root_dir}/feature_scaler.pkl')
            shutil.copy2(f'{artifacts_dir}/target_scaler.pkl', f'{root_dir}/target_scaler.pkl')
            shutil.copy2(f'{artifacts_dir}/feature_columns.json', f'{root_dir}/feature_columns.json')
            shutil.copy2(f'{artifacts_dir}/model_metadata.json', f'{root_dir}/model_metadata.json')

            print("Compatibility copies saved to both symbol folder and root artifacts folder")
        except Exception as e:
            print("Warning: failed to create compatibility copies:", e)

    def train_single_stock(self, symbol, period="3y", epochs=100, batch_size=32):
        try:
            X_train, X_val, X_test, y_train, y_val, y_test_scaled, close_test, features = \
                self.prepare_data(symbol, period=period)
            
                    # --- CSV olarak kaydetme eklemesi ---
            artifacts_dir = f'models/artifacts/{symbol}'
            os.makedirs(artifacts_dir, exist_ok=True)

            # X_train'i sequence düzleştir ve DataFrame yap
            train_df = pd.DataFrame(
                X_train.reshape(X_train.shape[0], -1), 
                columns=[f"{f}_t{i}" for i in range(X_train.shape[1]) for f in features]
            )
            train_df['Target_Return'] = y_train
            train_df.to_csv(f'{artifacts_dir}/{symbol}_training_set.csv', index=False)
            print(f"✅ Training dataset saved as CSV for {symbol}")

            input_shape = (X_train.shape[1], X_train.shape[2])
            self.build_model(input_shape)

            self.train(X_train, y_train, X_val, y_val, symbol, epochs=epochs, batch_size=batch_size)

            metrics = self.evaluate(X_test, y_test_scaled, close_test)

            self.save_artifacts(symbol, metrics, features)
            return True, metrics
        except Exception as e:
            print(f"ERROR training {symbol}: {e}")
            import traceback
            traceback.print_exc()
            return False, None


# Example driver
if __name__ == "__main__":
    predictor = StableStockPredictor(sequence_length=60)
    SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
               "META", "NVDA", "JPM", "V", "WMT"]

    results = {}
    first_successful = None

    for i, s in enumerate(SYMBOLS, 1):
        print(f"\n[{i}/{len(SYMBOLS)}] Training {s} ...")
        success, metrics = predictor.train_single_stock(s, period="3y", epochs=100, batch_size=32)
        results[s] = {'success': success, 'metrics': metrics}
        if success and first_successful is None:
            first_successful = s
            # copy artifacts to root as in your original code
            src_dir = f'models/artifacts/{s}'
            dst_dir = 'models/artifacts'
            os.makedirs(dst_dir, exist_ok=True)
            try:
                shutil.copy2(f'{src_dir}/{s}_model.keras', f'{dst_dir}/best_model')
                shutil.copy2(f'{src_dir}/feature_scaler.pkl', f'{dst_dir}/feature_scaler.pkl')
                shutil.copy2(f'{src_dir}/target_scaler.pkl', f'{dst_dir}/target_scaler.pkl')
                shutil.copy2(f'{src_dir}/feature_columns.json', f'{dst_dir}/feature_columns.json')
                shutil.copy2(f'{src_dir}/model_metadata.json', f'{dst_dir}/model_metadata.json')
                performance = {
                    'base_model': s,
                    'trained_on': datetime.now().isoformat(),
                    'metrics': metrics,
                    'model_type': 'LSTM_Return_Prediction',
                    'prediction_type': 'return'
                }
                with open(f'{dst_dir}/model_performance.json', 'w') as f:
                    json.dump(performance, f, indent=2)
                shutil.copy2(f'{src_dir}/{s}_model.keras', f'{dst_dir}/stock_predictor_v1.keras')
                print("Root-level artifacts saved.")
            except Exception as e:
                print("Failed to copy root artifacts:", e)

    with open('models/artifacts/training_summary.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\nTraining finished. Summary written to models/artifacts/training_summary.json")
