import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

class MetadataDB:
    def __init__(self, db_path: str = "metadata.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                session_id TEXT,
                created_at TEXT,
                status TEXT,
                action TEXT,
                params TEXT,
                result TEXT,
                error_message TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_metadata (
                cache_key TEXT PRIMARY KEY,
                data_hash TEXT,
                created_at TEXT,
                last_accessed TEXT,
                size_bytes INTEGER,
                description TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dataset_info (
                dataset_id TEXT PRIMARY KEY,
                source_uri TEXT,
                loaded_at TEXT,
                row_count INTEGER,
                column_count INTEGER,
                columns_json TEXT,
                fingerprint TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_task(self, task_id: str, session_id: str, action: str, params: Dict,
                   status: str = "pending", result: Optional[Dict] = None,
                   error_message: Optional[str] = None) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO tasks 
            (task_id, session_id, created_at, status, action, params, result, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_id,
            session_id,
            datetime.now().isoformat(),
            status,
            action,
            json.dumps(params),
            json.dumps(result) if result else None,
            error_message
        ))
        
        conn.commit()
        conn.close()
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "task_id": row[0],
                "session_id": row[1],
                "created_at": row[2],
                "status": row[3],
                "action": row[4],
                "params": json.loads(row[5]),
                "result": json.loads(row[6]) if row[6] else None,
                "error_message": row[7]
            }
        return None
    
    def record_dataset(self, dataset_id: str, source_uri: str, row_count: int,
                      column_count: int, columns: List[str], fingerprint: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO dataset_info
            (dataset_id, source_uri, loaded_at, row_count, column_count, columns_json, fingerprint)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            dataset_id,
            source_uri,
            datetime.now().isoformat(),
            row_count,
            column_count,
            json.dumps(columns),
            fingerprint
        ))
        
        conn.commit()
        conn.close()
    
    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM dataset_info WHERE dataset_id = ?", (dataset_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "dataset_id": row[0],
                "source_uri": row[1],
                "loaded_at": row[2],
                "row_count": row[3],
                "column_count": row[4],
                "columns": json.loads(row[5]),
                "fingerprint": row[6]
            }
        return None
    
    def record_cache_entry(self, cache_key: str, data_hash: str, size_bytes: int,
                          description: str = "") -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO cache_metadata
            (cache_key, data_hash, created_at, last_accessed, size_bytes, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (cache_key, data_hash, now, now, size_bytes, description))
        
        conn.commit()
        conn.close()
    
    def update_cache_access(self, cache_key: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE cache_metadata SET last_accessed = ? WHERE cache_key = ?
        ''', (datetime.now().isoformat(), cache_key))
        
        conn.commit()
        conn.close()

if __name__ == '__main__':
    import os
    
    db = MetadataDB("test_metadata.db")
    
    print("--- Testing MetadataDB ---")
    db.record_task("task123", "session456", "load_data", {"source": "test.csv"}, "completed", {"rows": 100})
    task = db.get_task("task123")
    print(f"Recorded task: {task}")
    
    db.record_dataset("ds1", "file://test.csv", 100, 5, ["col1", "col2", "col3", "col4", "col5"], "abc123")
    dataset = db.get_dataset("ds1")
    print(f"Recorded dataset: {dataset}")
    
    os.remove("test_metadata.db")
    print("Test database cleaned up.")
