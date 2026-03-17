from typing import List, Dict, Any, Callable

class ToolCoordinator:
    def __init__(self, tool_registry: Dict[str, Callable], llm_gateway):
        self.tool_registry = tool_registry # A dictionary mapping tool names to callable functions/objects
        self.llm_gateway = llm_gateway # For parameter generation if needed

    def execute_plan_step(self, step: Dict[str, Any], session_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a single step of the plan.
        """
        action = step.get("action")
        params = step.get("params", {})

        if action not in self.tool_registry:
            return {"status": "error", "message": f"Unknown action/tool: {action}"}

        tool_function = self.tool_registry[action]

        # In a more complex scenario, parameter generation with LLM would happen here
        # if params were in natural language. For now, assume params are ready.

        try:
            result = tool_function(**params) # Execute the tool with its parameters
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def integrate_results(self, results: List[Dict[str, Any]]) -> Any:
        """
        Integrates results from multiple tool executions.
        For now, just returns the last result or a summary.
        """
        if not results:
            return "No results to integrate."
        return results[-1] # Simple integration for now

if __name__ == '__main__':
    # Mock tools for testing
    def mock_load_data(source: str):
        print(f"Mock Tool: Loading data from {source}")
        return {"data_loaded": f"data from {source}", "schema": {"col1": "type1"}}

    def mock_plot_trend(column: str, value_column: str):
        print(f"Mock Tool: Plotting trend for {column} using {value_column}")
        return {"chart_generated": f"trend chart for {column}"}

    def mock_respond(message: str):
        print(f"Mock Tool: Responding with: {message}")
        return {"response_message": message}

    mock_tool_registry = {
        "load_data": mock_load_data,
        "plot_trend": mock_plot_trend,
        "respond": mock_respond,
    }

    class MockLLMGateway:
        def send_request(self, request_data: Dict) -> Dict:
            return {"response": "mocked llm response for parameter generation"}

    tool_coordinator = ToolCoordinator(mock_tool_registry, MockLLMGateway())

    # Test executing a step
    print("--- Executing 'load_data' step ---")
    step1 = {"action": "load_data", "params": {"source": "users.csv"}}
    result1 = tool_coordinator.execute_plan_step(step1, {})
    print(f"Result: {result1}")

    print("\n--- Executing 'plot_trend' step ---")
    step2 = {"action": "plot_trend", "params": {"column": "age", "value_column": "count"}}
    result2 = tool_coordinator.execute_plan_step(step2, {})
    print(f"Result: {result2}")

    print("\n--- Executing unknown action ---")
    step3 = {"action": "unknown_tool", "params": {}}
    result3 = tool_coordinator.execute_plan_step(step3, {})
    print(f"Result: {result3}")

    print("\n--- Integrating results ---")
    integrated_result = tool_coordinator.integrate_results([result1, result2])
    print(f"Integrated Result: {integrated_result}")
