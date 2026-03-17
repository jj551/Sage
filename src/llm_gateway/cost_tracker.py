from typing import Dict, Any
from collections import defaultdict
import datetime

class CostTracker:
    def __init__(self, token_costs: Dict[str, Dict[str, float]] = None):
        # token_costs example: {"gpt-4": {"input_cost_per_1k_tokens": 0.03, "output_cost_per_1k_tokens": 0.06}}
        self.token_costs = defaultdict(lambda: {"input_cost_per_1k_tokens": 0.0, "output_cost_per_1k_tokens": 0.0})
        if token_costs:
            for model, costs in token_costs.items():
                self.token_costs[model].update(costs)

        self.session_costs = defaultdict(lambda: {"total_tokens": 0, "total_cost": 0.0, "llm_calls": 0, "total_duration": 0.0})
        self.global_costs = {"total_tokens": 0, "total_cost": 0.0, "llm_calls": 0, "total_duration": 0.0}
        self.monthly_budget = None # e.g., {"amount": 100.0, "currency": "USD"}
        self.current_month_usage = {"cost": 0.0, "last_reset": datetime.date.today().replace(day=1)}

    def track_usage(self, model: str, usage: Dict, duration: float, session_id: str = "global"):
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = prompt_tokens + completion_tokens

        input_cost = (prompt_tokens / 1000) * self.token_costs[model]["input_cost_per_1k_tokens"]
        output_cost = (completion_tokens / 1000) * self.token_costs[model]["output_cost_per_1k_tokens"]
        total_cost = input_cost + output_cost

        # Update session costs
        self.session_costs[session_id]["total_tokens"] += total_tokens
        self.session_costs[session_id]["total_cost"] += total_cost
        self.session_costs[session_id]["llm_calls"] += 1
        self.session_costs[session_id]["total_duration"] += duration

        # Update global costs
        self.global_costs["total_tokens"] += total_tokens
        self.global_costs["total_cost"] += total_cost
        self.global_costs["llm_calls"] += 1
        self.global_costs["total_duration"] += duration

        # Update monthly budget usage
        self._update_monthly_usage(total_cost)

        print(f"CostTracker: Tracked - Model: {model}, Tokens: {total_tokens}, Cost: ${total_cost:.4f}, Session: {session_id}")
        self._check_budget_alert()

    def _update_monthly_usage(self, cost: float):
        today = datetime.date.today()
        if today.month != self.current_month_usage["last_reset"].month:
            self.current_month_usage = {"cost": 0.0, "last_reset": today.replace(day=1)}
        self.current_month_usage["cost"] += cost

    def set_monthly_budget(self, amount: float, currency: str = "USD"):
        self.monthly_budget = {"amount": amount, "currency": currency}
        print(f"Monthly budget set to {amount} {currency}")

    def _check_budget_alert(self):
        if self.monthly_budget and self.current_month_usage["cost"] > self.monthly_budget["amount"]:
            print(f"ALERT: Monthly budget of {self.monthly_budget['amount']} {self.monthly_budget['currency']} exceeded!")

    def get_session_cost(self, session_id: str) -> Dict[str, Any]:
        return self.session_costs[session_id]

    def get_global_cost(self) -> Dict[str, Any]:
        return self.global_costs

    def get_current_monthly_usage(self) -> Dict[str, Any]:
        self._update_monthly_usage(0) # Ensure it's up-to-date
        return self.current_month_usage

if __name__ == '__main__':
    token_costs_config = {
        "gpt-4": {"input_cost_per_1k_tokens": 0.03, "output_cost_per_1k_tokens": 0.06},
        "gpt-3.5-turbo": {"input_cost_per_1k_tokens": 0.0015, "output_cost_per_1k_tokens": 0.002}
    }
    tracker = CostTracker(token_costs=token_costs_config)
    tracker.set_monthly_budget(0.10) # Set a low budget for testing alerts

    print("--- Tracking usage ---")
    tracker.track_usage("gpt-4", {"prompt_tokens": 1000, "completion_tokens": 2000}, 1.5, "session_abc")
    tracker.track_usage("gpt-3.5-turbo", {"prompt_tokens": 500, "completion_tokens": 1000}, 0.8, "session_abc")
    tracker.track_usage("gpt-4", {"prompt_tokens": 1500, "completion_tokens": 3000}, 2.1, "session_xyz")

    print("\n--- Session ABC Cost ---")
    print(tracker.get_session_cost("session_abc"))

    print("\n--- Global Cost ---")
    print(tracker.get_global_cost())

    print("\n--- Monthly Usage ---")
    print(tracker.get_current_monthly_usage())

    print("\n--- Triggering budget alert ---")
    tracker.track_usage("gpt-4", {"prompt_tokens": 1000, "completion_tokens": 2000}, 1.0, "session_alert")
