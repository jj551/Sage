import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse

class DataAccessModule:
    def __init__(self):
        pass
    
    def load_data(self, source: str) -> pd.DataFrame:
        print(f"DataAccessModule: Loading data from {source}")
        
        if source.startswith('file://'):
            file_path = source[7:]
        else:
            file_path = source
        
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix.lower() == '.csv':
            df = pd.read_csv(path)
        elif path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(path)
        elif path.suffix.lower() == '.parquet':
            df = pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        print(f"Loaded {len(df)} rows from {path.name}")
        return df
    
    def get_data_overview(self, df: pd.DataFrame) -> Dict[str, Any]:
        overview = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'head': df.head().to_dict('records'),
            'describe': df.describe().to_dict() if not df.select_dtypes(include=['number']).empty else {}
        }
        return overview

if __name__ == '__main__':
    print("--- Testing DataAccessModule ---")
    
    dam = DataAccessModule()
    
    test_csv = """date,sales,customers,expenses
2023-01-01,100,10,50
2023-01-02,150,15,75
2023-01-03,120,12,60
"""
    
    with open("test_temp.csv", "w") as f:
        f.write(test_csv)
    
    df = dam.load_data("test_temp.csv")
    print(f"Loaded dataframe shape: {df.shape}")
    
    overview = dam.get_data_overview(df)
    print(f"Overview: {overview}")
    
    import os
    os.remove("test_temp.csv")
    print("Test complete!")
