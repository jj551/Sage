import uuid
import os
from typing import Dict, Any, Optional, List
import pandas as pd

from .task_planner import TaskPlanner
from .tool_coordinator import ToolCoordinator
from ..llm_gateway.llm_api_gateway import LLMAPIGateway, LLMRequest, LLMResponse
from ..llm_gateway.adapters import AdapterFactory
from ..llm_gateway.cost_tracker import CostTracker
from ..llm_gateway.rate_limiter import RateLimiter
from ..llm_gateway.response_cache import ResponseCache
from ..session_management.session_manager import SessionManager
from ..tool_execution.data_access import DataAccessModule
from ..tool_execution.analysis_execution import AnalysisExecutionModule
from ..tool_execution.result_processing import ResultProcessingModule
from ..data_storage.external_data_source import ExternalDataSource
from ..data_storage.metadata_db import MetadataDB
from ..cli.output_renderer import OutputRenderer

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class SageAgent:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        self.model = self.config.get('model', os.getenv('SAGE_MODEL', 'mock-model'))
        
        self.session_manager = SessionManager(db_path=self.config.get('session_db', 'sessions.db'))
        self.llm_gateway = self._init_llm_gateway()
        self.task_planner = TaskPlanner(self.llm_gateway, model=self.model)
        self.data_access = DataAccessModule()
        self.analysis_execution = AnalysisExecutionModule()
        self.result_processing = ResultProcessingModule(output_dir=self.config.get('output_dir', './output'))
        self.external_data_source = ExternalDataSource()
        self.metadata_db = MetadataDB(db_path=self.config.get('metadata_db', 'metadata.db'))
        self.output_renderer = OutputRenderer()
        
        self.current_session_id: Optional[str] = None
        self.current_dataset: Optional[pd.DataFrame] = None
        self.current_dataset_id: Optional[str] = None
        
        self.tool_registry = self._build_tool_registry()
        self.tool_coordinator = ToolCoordinator(self.tool_registry, self.llm_gateway)
    
    def _init_llm_gateway(self) -> LLMAPIGateway:
        adapter_factory = AdapterFactory()
        response_cache = ResponseCache(max_size=100, ttl=3600)
        rate_limiter = RateLimiter()
        cost_tracker = CostTracker()
        return LLMAPIGateway(adapter_factory, response_cache, rate_limiter, cost_tracker)
    
    def _build_tool_registry(self) -> Dict[str, Any]:
        return {
            "load_data": self._tool_load_data,
            "descriptive_stats": self._tool_descriptive_stats,
            "plot_trend": self._tool_plot_trend,
            "correlation": self._tool_correlation,
            "clean_data": self._tool_clean_data,
            "feature_engineering": self._tool_feature_engineering,
            "outlier_detection": self._tool_outlier_detection,
            "respond": self._tool_respond
        }
    
    def create_session(self, session_id: Optional[str] = None, data_source_uri: str = "") -> str:
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        self.session_manager.create_session(session_id, data_source_uri)
        self.current_session_id = session_id
        
        return session_id
    
    def load_dataset(self, source: str) -> Dict[str, Any]:
        try:
            df = self.data_access.load_data(source)
            self.current_dataset = df
            self.current_dataset_id = str(uuid.uuid4())
            
            overview = self.data_access.get_data_overview(df)
            
            self.metadata_db.record_dataset(
                self.current_dataset_id,
                source,
                overview['shape'][0],
                overview['shape'][1],
                overview['columns'],
                ""
            )
            
            return {
                "status": "success",
                "dataset_id": self.current_dataset_id,
                "overview": overview
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def process_message(self, user_message: str) -> Dict[str, Any]:
        if self.current_session_id is None:
            self.create_session()
        
        context = self.session_manager.get_context_for_llm(self.current_session_id)
        
        if self.current_dataset is not None:
            context += f"\nCurrent Dataset Loaded: Yes"
            context += f"\nDataset shape: {self.current_dataset.shape}"
            context += f"\nDataset columns: {list(self.current_dataset.columns)}"
        
        plan = self.task_planner.plan_task(user_message, context)
        
        results = []
        current_plan = plan
        
        for step in current_plan:
            step_result = self.tool_coordinator.execute_plan_step(step, {})
            results.append(step_result)
            
            if step_result['status'] == 'success':
                current_plan = self.task_planner.adjust_plan(current_plan, step_result)
            else:
                current_plan = self.task_planner.handle_error(current_plan, step_result['message'])
                break
        
        integrated_result = self.tool_coordinator.integrate_results(results)
        
        self._update_session_history(user_message, str(integrated_result))
        
        return {
            "plan": plan,
            "results": results,
            "final_result": integrated_result
        }
    
    def _update_session_history(self, user_msg: str, agent_msg: str) -> None:
        session = self.session_manager.get_session(self.current_session_id)
        if session:
            history = session.get("message_history", [])
            history.append({"user": user_msg, "agent": agent_msg})
            self.session_manager.update_session(self.current_session_id, {"message_history": history})
    
    def _tool_load_data(self, source: str) -> Dict[str, Any]:
        return self.load_dataset(source)
    
    def _tool_descriptive_stats(self) -> Dict[str, Any]:
        if self.current_dataset is None:
            return {"status": "error", "message": "No dataset loaded"}
        
        result = self.analysis_execution.execute_analysis(self.current_dataset, 'descriptive_stats')
        
        if result['status'] == 'success':
            processed = self.result_processing.process_results(result, self.current_dataset)
            return {"status": "success", "result": processed}
        return result
    
    def _tool_plot_trend(self, column: str, value_column: Optional[str] = None) -> Dict[str, Any]:
        if self.current_dataset is None:
            return {"status": "error", "message": "No dataset loaded"}
        
        analysis_result = {
            'analysis_type': 'plot_trend',
            'stats': self.data_access.get_data_overview(self.current_dataset)
        }
        
        processed = self.result_processing.process_results(
            analysis_result,
            self.current_dataset,
            generate_chart=True,
            x=column,
            y=value_column,
            plot_type='line',
            title=f'Trend: {column}'
        )
        
        return {"status": "success", "result": processed}
    
    def _tool_correlation(self) -> Dict[str, Any]:
        if self.current_dataset is None:
            return {"status": "error", "message": "No dataset loaded"}
        
        result = self.analysis_execution.execute_analysis(self.current_dataset, 'correlation')
        
        if result['status'] == 'success':
            processed = self.result_processing.process_results(
                result,
                self.current_dataset,
                generate_chart=True,
                plot_type='heatmap',
                title='Correlation Heatmap'
            )
            return {"status": "success", "result": processed}
        return result
    
    def _tool_clean_data(self, **kwargs) -> Dict[str, Any]:
        if self.current_dataset is None:
            return {"status": "error", "message": "No dataset loaded"}
        
        result = self.analysis_execution.execute_analysis(self.current_dataset, 'clean_data', **kwargs)
        
        if result['status'] == 'success':
            self.current_dataset = result['data']
            return {"status": "success", "result": result}
        return result
    
    def _tool_feature_engineering(self, **kwargs) -> Dict[str, Any]:
        if self.current_dataset is None:
            return {"status": "error", "message": "No dataset loaded"}
        
        result = self.analysis_execution.execute_analysis(self.current_dataset, 'feature_engineering', **kwargs)
        
        if result['status'] == 'success':
            self.current_dataset = result['data']
            return {"status": "success", "result": result}
        return result
    
    def _tool_outlier_detection(self, column: str, method: str = 'iqr') -> Dict[str, Any]:
        if self.current_dataset is None:
            return {"status": "error", "message": "No dataset loaded"}
        
        result = self.analysis_execution.execute_analysis(
            self.current_dataset,
            'outlier_detection',
            column=column,
            method=method
        )
        
        if result['status'] == 'success':
            processed = self.result_processing.process_results(result)
            return {"status": "success", "result": processed}
        return result
    
    def _tool_respond(self, message: str) -> Dict[str, Any]:
        return {"status": "success", "message": message}
    
    def get_cost_summary(self) -> Dict[str, Any]:
        cost_tracker = self.llm_gateway.cost_tracker
        return {
            "global": cost_tracker.get_global_cost(),
            "session": cost_tracker.get_session_cost(self.current_session_id or "global"),
            "monthly": cost_tracker.get_current_monthly_usage()
        }

if __name__ == '__main__':
    print("=== Sage Agent Test ===")
    
    agent = SageAgent()
    
    session_id = agent.create_session()
    print(f"Created session: {session_id}")
    
    print("\n--- Creating test data ---")
    import pandas as pd
    import os
    
    test_csv = """date,sales,customers,expenses
2023-01-01,100,10,50
2023-01-02,150,15,75
2023-01-03,120,12,60
2023-01-04,200,20,100
2023-01-05,180,18,90
"""
    
    with open("test_sales.csv", "w") as f:
        f.write(test_csv)
    
    print("\n--- Loading dataset ---")
    load_result = agent.process_message("load sales data from test_sales.csv")
    print(load_result)
    
    print("\n--- Getting descriptive stats ---")
    stats_result = agent.process_message("show descriptive statistics")
    print(stats_result)
    
    print("\n--- Cost summary ---")
    cost_summary = agent.get_cost_summary()
    print(cost_summary)
    
    os.remove("test_sales.csv")
    print("\nTest completed!")
