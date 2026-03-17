from typing import Any, Dict
from tabulate import tabulate
import plotext as plt
# from imgcat import imgcat # Requires imgcat to be installed and terminal support

class OutputRenderer:
    def __init__(self):
        pass

    def render(self, data: Any, data_type: str = "text", terminal_capabilities: Dict = None):
        """
        Renders the output based on data type and terminal capabilities.
        data_type can be "text", "table", "chart", "image".
        terminal_capabilities could include "supports_inline_images": True
        """
        if terminal_capabilities is None:
            terminal_capabilities = {"supports_inline_images": False}

        if data_type == "text":
            print(data)
        elif data_type == "table":
            if isinstance(data, list) and all(isinstance(row, dict) for row in data):
                # Assuming list of dicts for table
                headers = list(data[0].keys()) if data else []
                rows = [list(row.values()) for row in data]
                print(tabulate(rows, headers=headers, tablefmt="grid"))
            else:
                print(f"Unsupported table data format: {data}")
        elif data_type == "chart":
            # Example for plotext (simple line chart)
            if isinstance(data, dict) and "x" in data and "y" in data:
                plt.clf() # Clear previous plot
                plt.plot(data["x"], data["y"])
                plt.title(data.get("title", "Chart"))
                plt.show()
            else:
                print(f"Unsupported chart data format: {data}")
        elif data_type == "image":
            if terminal_capabilities.get("supports_inline_images"):
                # try:
                #     imgcat(data) # data should be image bytes or path
                # except Exception as e:
                #     print(f"Failed to render inline image: {e}")
                print("[Image content - inline rendering not implemented or supported]")
            else:
                print("[Image content - terminal does not support inline images]")
        else:
            print(f"Unknown data type for rendering: {data_type}")

if __name__ == '__main__':
    renderer = OutputRenderer()

    print("--- Text Output ---")
    renderer.render("Hello, this is a text message from the Agent.")

    print("\n--- Table Output ---")
    table_data = [
        {"Name": "Alice", "Age": 30, "City": "New York"},
        {"Name": "Bob", "Age": 24, "City": "San Francisco"}
    ]
    renderer.render(table_data, data_type="table")

    print("\n--- Chart Output ---")
    chart_data = {"x": [1, 2, 3, 4, 5], "y": [1, 4, 2, 6, 3], "title": "Sample Line Chart"}
    renderer.render(chart_data, data_type="chart")

    print("\n--- Image Output (placeholder) ---")
    renderer.render(b"image_bytes", data_type="image", terminal_capabilities={"supports_inline_images": False})
