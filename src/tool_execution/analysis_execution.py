import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

class AnalysisExecutionModule:
    def __init__(self):
        pass
    
    def clean_data(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        df_clean = df.copy()
        
        if kwargs.get('drop_na', False):
            df_clean = df_clean.dropna()
        
        if kwargs.get('fill_na'):
            fill_strategy = kwargs['fill_na']
            if fill_strategy == 'mean':
                df_clean = df_clean.fillna(df_clean.mean(numeric_only=True))
            elif fill_strategy == 'median':
                df_clean = df_clean.fillna(df_clean.median(numeric_only=True))
            elif fill_strategy == 'mode':
                df_clean = df_clean.fillna(df_clean.mode().iloc[0])
        
        return df_clean
    
    def descriptive_stats(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        if columns:
            df = df[columns]
        
        numeric_df = df.select_dtypes(include=[np.number])
        
        stats = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'numeric_summary': numeric_df.describe().to_dict() if not numeric_df.empty else {},
            'correlation': numeric_df.corr().to_dict() if not numeric_df.empty and len(numeric_df.columns) > 1 else {}
        }
        
        return stats
    
    def correlation_analysis(self, df: pd.DataFrame, columns: Optional[List[str]] = None,
                           method: str = 'pearson') -> pd.DataFrame:
        if columns:
            df = df[columns]
        
        numeric_df = df.select_dtypes(include=[np.number])
        return numeric_df.corr(method=method)
    
    def feature_engineering(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        df_feat = df.copy()
        
        date_columns = kwargs.get('date_columns', [])
        for col in date_columns:
            if col in df_feat.columns:
                df_feat[col] = pd.to_datetime(df_feat[col], errors='ignore')
                if pd.api.types.is_datetime64_any_dtype(df_feat[col]):
                    df_feat[f'{col}_year'] = df_feat[col].dt.year
                    df_feat[f'{col}_month'] = df_feat[col].dt.month
                    df_feat[f'{col}_day'] = df_feat[col].dt.day
                    df_feat[f'{col}_dayofweek'] = df_feat[col].dt.dayofweek
        
        categorical_columns = kwargs.get('categorical_columns', [])
        if kwargs.get('one_hot_encode', False):
            df_feat = pd.get_dummies(df_feat, columns=categorical_columns, drop_first=True)
        
        return df_feat
    
    def detect_outliers(self, df: pd.DataFrame, column: str, method: str = 'iqr') -> Tuple[pd.DataFrame, Dict[str, Any]]:
        df_out = df.copy()
        
        if method == 'iqr':
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
            
            outlier_info = {
                'method': 'IQR',
                'Q1': Q1,
                'Q3': Q3,
                'IQR': IQR,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'outlier_count': len(outliers),
                'outlier_indices': outliers.index.tolist()
            }
        else:
            raise ValueError(f"Unknown outlier detection method: {method}")
        
        return outliers, outlier_info
    
    def execute_analysis(self, df: pd.DataFrame, analysis_type: str, **kwargs) -> Dict[str, Any]:
        results = {
            'analysis_type': analysis_type,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }
        
        try:
            if analysis_type == 'clean_data':
                cleaned_df = self.clean_data(df, **kwargs)
                results['data'] = cleaned_df
                results['original_shape'] = df.shape
                results['cleaned_shape'] = cleaned_df.shape
            
            elif analysis_type == 'descriptive_stats':
                stats = self.descriptive_stats(df, **kwargs)
                results['stats'] = stats
            
            elif analysis_type == 'correlation':
                corr_matrix = self.correlation_analysis(df, **kwargs)
                results['correlation_matrix'] = corr_matrix.to_dict()
            
            elif analysis_type == 'feature_engineering':
                feat_df = self.feature_engineering(df, **kwargs)
                results['data'] = feat_df
                results['original_columns'] = df.columns.tolist()
                results['new_columns'] = feat_df.columns.tolist()
            
            elif analysis_type == 'outlier_detection':
                outliers, info = self.detect_outliers(df, **kwargs)
                results['outliers'] = outliers
                results['outlier_info'] = info
            
            else:
                raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        except Exception as e:
            results['status'] = 'error'
            results['error_message'] = str(e)
        
        return results

if __name__ == '__main__':
    print("--- Testing AnalysisExecutionModule ---")
    
    test_data = {
        'date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
        'sales': [100, 150, 120, 200, 180],
        'customers': [10, 15, 12, 20, 18],
        'category': ['A', 'B', 'A', 'C', 'B']
    }
    df_test = pd.DataFrame(test_data)
    
    print("Test dataframe created:")
    print(df_test)
    
    aem = AnalysisExecutionModule()
    
    print("\n--- Descriptive Stats ---")
    stats_result = aem.execute_analysis(df_test, 'descriptive_stats')
    print(stats_result)
    
    print("\n--- Feature Engineering ---")
    feat_result = aem.execute_analysis(df_test, 'feature_engineering', 
                                      date_columns=['date'], categorical_columns=['category'])
    print(feat_result['data'])
    
    print("\n--- Correlation Analysis ---")
    corr_result = aem.execute_analysis(df_test, 'correlation')
    print("Correlation matrix:", corr_result['correlation_matrix'])
