import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import io
import base64

class ResultProcessingModule:
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_visualization(self, df: pd.DataFrame, plot_type: str, x: str = None, y: str = None,
                               hue: str = None, title: str = "", **kwargs) -> Dict[str, Any]:
        plt.switch_backend('Agg')
        fig, ax = plt.subplots(figsize=kwargs.get('figsize', (10, 6)))
        
        try:
            if plot_type == 'line':
                sns.lineplot(data=df, x=x, y=y, hue=hue, ax=ax)
            elif plot_type == 'bar':
                sns.barplot(data=df, x=x, y=y, hue=hue, ax=ax)
            elif plot_type == 'scatter':
                sns.scatterplot(data=df, x=x, y=y, hue=hue, ax=ax)
            elif plot_type == 'histogram':
                sns.histplot(data=df, x=x, hue=hue, ax=ax)
            elif plot_type == 'box':
                sns.boxplot(data=df, x=x, y=y, hue=hue, ax=ax)
            elif plot_type == 'heatmap':
                corr = df.select_dtypes(include=[np.number]).corr()
                sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
            else:
                raise ValueError(f"Unsupported plot type: {plot_type}")
            
            ax.set_title(title or f"{plot_type.capitalize()} Plot")
            plt.tight_layout()
            
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=100)
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            plt.close(fig)
            
            return {
                'status': 'success',
                'plot_type': plot_type,
                'image_base64': img_base64,
                'title': title
            }
        
        except Exception as e:
            plt.close(fig)
            return {
                'status': 'error',
                'error_message': str(e)
            }
    
    def save_chart(self, viz_result: Dict[str, Any], filename: Optional[str] = None) -> str:
        if viz_result['status'] != 'success':
            raise ValueError("Cannot save failed visualization")
        
        if filename is None:
            filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        filepath = self.output_dir / filename
        
        img_data = base64.b64decode(viz_result['image_base64'])
        with open(filepath, 'wb') as f:
            f.write(img_data)
        
        return str(filepath)
    
    def auto_select_chart(self, df: pd.DataFrame, x: Optional[str] = None, y: Optional[str] = None) -> str:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if x is None and y is None:
            if len(numeric_cols) >= 2:
                return 'heatmap'
            elif len(numeric_cols) >= 1:
                return 'histogram'
            else:
                return 'bar'
        
        if x and y:
            if pd.api.types.is_datetime64_any_dtype(df[x]) or df[x].dtype == 'object':
                return 'line' if y in numeric_cols else 'bar'
            elif x in numeric_cols and y in numeric_cols:
                return 'scatter'
        
        if x and x in numeric_cols:
            return 'histogram'
        
        return 'bar'
    
    def generate_text_summary(self, results: Dict[str, Any]) -> str:
        summary_parts = []
        
        if 'analysis_type' in results:
            summary_parts.append(f"Analysis Type: {results['analysis_type']}")
        
        if 'stats' in results:
            stats = results['stats']
            summary_parts.append(f"\nDataset Shape: {stats['shape'][0]} rows × {stats['shape'][1]} columns")
            summary_parts.append(f"Columns: {', '.join(stats['columns'])}")
            
            if 'numeric_summary' in stats and stats['numeric_summary']:
                summary_parts.append("\nNumeric Statistics:")
                for col, col_stats in stats['numeric_summary'].items():
                    summary_parts.append(f"  {col}: mean={col_stats.get('mean', 'N/A'):.2f}, std={col_stats.get('std', 'N/A'):.2f}")
        
        if 'outlier_info' in results:
            info = results['outlier_info']
            summary_parts.append(f"\nOutlier Detection:")
            summary_parts.append(f"  Method: {info['method']}")
            summary_parts.append(f"  Outliers found: {info['outlier_count']}")
        
        return "\n".join(summary_parts)
    
    def process_results(self, analysis_results: Dict[str, Any], df: Optional[pd.DataFrame] = None,
                       generate_chart: bool = False, **kwargs) -> Dict[str, Any]:
        processed = {
            'timestamp': datetime.now().isoformat(),
            'text_summary': self.generate_text_summary(analysis_results)
        }
        
        if generate_chart and df is not None:
            plot_type = kwargs.get('plot_type')
            if plot_type is None:
                plot_type = self.auto_select_chart(df, kwargs.get('x'), kwargs.get('y'))
            
            viz_result = self.generate_visualization(
                df, plot_type,
                x=kwargs.get('x'),
                y=kwargs.get('y'),
                hue=kwargs.get('hue'),
                title=kwargs.get('title', '')
            )
            processed['visualization'] = viz_result
            
            if kwargs.get('save_chart', False):
                chart_path = self.save_chart(viz_result, kwargs.get('filename'))
                processed['chart_saved_at'] = chart_path
        
        if analysis_results.get('status') == 'error':
            processed['error'] = analysis_results.get('error_message')
        
        return processed

if __name__ == '__main__':
    import pandas as pd
    
    print("--- Testing ResultProcessingModule ---")
    
    test_data = {
        'date': pd.date_range('2023-01-01', periods=10),
        'sales': [100, 150, 120, 200, 180, 220, 190, 250, 230, 280],
        'customers': [10, 15, 12, 20, 18, 22, 19, 25, 23, 28],
        'expenses': [50, 75, 60, 100, 90, 110, 95, 125, 115, 140]
    }
    df_test = pd.DataFrame(test_data)
    
    rpm = ResultProcessingModule()
    
    print("\n--- Testing Auto Chart Selection ---")
    print(f"Auto-selected chart: {rpm.auto_select_chart(df_test, 'date', 'sales')}")
    
    print("\n--- Generating Text Summary ---")
    sample_results = {
        'analysis_type': 'descriptive_stats',
        'stats': {
            'shape': (10, 4),
            'columns': ['date', 'sales', 'customers', 'expenses'],
            'numeric_summary': {
                'sales': {'mean': 192.0, 'std': 54.3},
                'customers': {'mean': 19.2, 'std': 5.43},
                'expenses': {'mean': 96.0, 'std': 27.15}
            }
        }
    }
    
    summary = rpm.generate_text_summary(sample_results)
    print(summary)
    
    print("\n--- Generating Visualization ---")
    viz_result = rpm.generate_visualization(df_test, 'line', x='date', y='sales', title='Sales Trend')
    print(f"Visualization status: {viz_result['status']}")
    if viz_result['status'] == 'success':
        print(f"Image base64 length: {len(viz_result['image_base64'])}")
