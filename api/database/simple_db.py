# api/database/simple_db.py
"""
Simple SQLite database for prediction history
"""
import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional
import json
import logging

logger = logging.getLogger(__name__)

DB_FILE = "financeml_history.db"


class PredictionDatabase:
    """Simple database for storing prediction history"""
    
    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file
        self._init_db()
    
    def _init_db(self):
        """Create table if not exists"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    prediction_type TEXT NOT NULL,
                    prediction_date DATE NOT NULL,
                    current_price REAL,
                    predicted_price REAL,
                    forecast_days INTEGER,
                    trend TEXT,
                    prediction_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index for fast queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbol 
                ON predictions(symbol)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created 
                ON predictions(created_at)
            """)
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def save_prediction(
        self,
        symbol: str,
        prediction_type: str,
        prediction_date: str,
        current_price: float,
        predicted_price: float,
        forecast_days: int = 1,
        trend: str = None,
        prediction_data: dict = None
    ) -> int:
        """Save a prediction to database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO predictions 
                (symbol, prediction_type, prediction_date, current_price, 
                 predicted_price, forecast_days, trend, prediction_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol,
                prediction_type,
                prediction_date,
                current_price,
                predicted_price,
                forecast_days,
                trend,
                json.dumps(prediction_data) if prediction_data else None
            ))
            
            prediction_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Saved prediction for {symbol}: ID {prediction_id}")
            return prediction_id
            
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
            return None
    
    def get_history(
        self,
        symbol: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get prediction history"""
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if symbol:
                cursor.execute("""
                    SELECT * FROM predictions 
                    WHERE symbol = ?
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (symbol, limit))
            else:
                cursor.execute("""
                    SELECT * FROM predictions 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to dict
            results = []
            for row in rows:
                result = dict(row)
                if result['prediction_data']:
                    result['prediction_data'] = json.loads(result['prediction_data'])
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Total predictions
            cursor.execute("SELECT COUNT(*) FROM predictions")
            total = cursor.fetchone()[0]
            
            # By symbol
            cursor.execute("""
                SELECT symbol, COUNT(*) as count 
                FROM predictions 
                GROUP BY symbol 
                ORDER BY count DESC 
                LIMIT 10
            """)
            by_symbol = [{"symbol": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # Recent activity
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM predictions
                WHERE created_at >= date('now', '-7 days')
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """)
            recent_activity = [{"date": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                "total_predictions": total,
                "top_symbols": by_symbol,
                "recent_activity": recent_activity
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def delete_old_records(self, days: int = 90):
        """Delete records older than N days"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM predictions 
                WHERE created_at < date('now', '-' || ? || ' days')
            """, (days,))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Deleted {deleted} old records")
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting old records: {e}")
            return 0


# Global instance
db = PredictionDatabase()