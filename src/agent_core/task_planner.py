import json
from typing import List, Dict, Any
from ..llm_gateway.llm_api_gateway import LLMRequest

class TaskPlanner:
    def __init__(self, llm_gateway, model: str = "mock-model"):
        self.llm_gateway = llm_gateway
        self.model = model

    def plan_task(self, user_message: str, session_context: str) -> List[Dict[str, Any]]:
        prompt = self._construct_planning_prompt(user_message, session_context)
        print(f"DEBUG: Planning task for: {user_message}")
        
        messages = [
            {"role": "system", "content": "You are a data analysis assistant that generates task plans in JSON format."},
            {"role": "user", "content": prompt}
        ]
        
        request = LLMRequest(
            messages=messages,
            model_params={"model": self.model, "temperature": 0.1, "max_tokens": 1000}
        )
        
        try:
            response = self.llm_gateway.send_request(request)
            plan_text = response.text.strip()
            
            plan = self._parse_plan(plan_text)
            return plan
        except Exception as e:
            print(f"Error in task planning: {e}")
            return [{"action": "respond", "params": {"message": f"Error planning task: {str(e)}"}}]

    def _construct_planning_prompt(self, user_message: str, session_context: str) -> str:
        prompt = f"""You are an AI assistant designed to plan data analysis tasks.
Given the user's message and the current session context, generate a JSON list of steps.
Each step should have an "action" and "params" field.

Available actions:
- "load_data": Loads a dataset. Params: {{"source": "file_path_or_uri"}}
- "descriptive_stats": Shows descriptive statistics. Params: {{}}
- "plot_trend": Plots a trend chart. Params: {{"column": "column_name", "value_column": "value_column_name"}}
- "correlation": Shows correlation heatmap. Params: {{}}
- "clean_data": Cleans the data. Params: {{"drop_na": false, "fill_na": "mean"}}
- "feature_engineering": Feature engineering. Params: {{"date_columns": [], "categorical_columns": []}}
- "outlier_detection": Detects outliers. Params: {{"column": "column_name", "method": "iqr"}}
- "respond": Respond with a message. Params: {{"message": "text_message"}}

IMPORTANT: Respond ONLY with a valid JSON array, no other text.

Session Context:
{session_context}

User Message: "{user_message}"

JSON Plan:"""
        return prompt

    def _parse_plan(self, plan_text: str) -> List[Dict[str, Any]]:
        plan_text = plan_text.strip()
        
        if plan_text.startswith("```json"):
            plan_text = plan_text[7:]
        if plan_text.startswith("```"):
            plan_text = plan_text[3:]
        if plan_text.endswith("```"):
            plan_text = plan_text[:-3]
        
        plan_text = plan_text.strip()
        
        try:
            plan = json.loads(plan_text)
            if isinstance(plan, list):
                return plan
            else:
                return [{"action": "respond", "params": {"message": "Invalid plan format"}}]
        except json.JSONDecodeError:
            print(f"Failed to parse plan: {plan_text}")
            return [{"action": "respond", "params": {"message": "Could not understand the request."}}]

    def adjust_plan(self, current_plan: List[Dict[str, Any]], step_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        print(f"DEBUG: Adjusting plan based on step result: {step_result}")
        return current_plan

    def handle_error(self, current_plan: List[Dict[str, Any]], error: str) -> List[Dict[str, Any]]:
        print(f"DEBUG: Handling error: {error}")
        return [{"action": "respond", "params": {"message": f"An error occurred: {error}. Please clarify or try again."}}]

if __name__ == '__main__':
    # Mock LLM Gateway for testing
    class MockLLMGateway:
        def __init__(self):
            pass
        def send_request(self, request_data: Dict) -> Dict:
            print(f"MockLLMGateway received request: {request_data['prompt']}")
            if "load sales data" in request_data['prompt'].lower():
                return {"response": json.dumps([{"action": "load_data", "params": {"source": "sales.csv"}}])}
            elif "plot sales trend" in request_data['prompt'].lower():
                return {"response": json.dumps([{"action": "plot_trend", "params": {"column": "date", "value_column": "sales"}}])}
            else:
                return {"response": json.dumps([{"action": "respond", "params": {"message": "I'm not sure how to plan that yet."}}])}

    mock_llm_gateway = MockLLMGateway()
    planner = TaskPlanner(mock_llm_gateway)

    print("--- Planning 'load sales data' ---")
    plan1 = planner.plan_task("load sales data", "Previous message: None")
    print(f"Plan: {plan1}")

    print("\n--- Planning 'plot sales trend' ---")
    plan2 = planner.plan_task("plot sales trend", "Current Data: sales.csv loaded")
    print(f"Plan: {plan2}")

    print("\n--- Planning an unknown task ---")
    plan3 = planner.plan_task("do something weird", "Current Data: None")
    print(f"Plan: {plan3}")

    print("\n--- Adjusting plan ---")
    adjusted_plan = planner.adjust_plan(plan1, {"status": "success", "data_loaded": "sales.csv"})
    print(f"Adjusted Plan: {adjusted_plan}")

    print("\n--- Handling error ---")
    error_plan = planner.handle_error(plan2, "Failed to load data")
    print(f"Error Plan: {error_plan}")
