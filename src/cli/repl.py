from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style

class InteractiveREPL:
    def __init__(self):
        self.session = PromptSession(history=FileHistory('history.txt'))
        self.completer = WordCompleter(['/save', '/plot', '/cost', '/exit'], ignore_case=True)
        self.style = Style.from_dict({
            'completion-menu.completion': '#008000',
            'completion-menu.completion.current': '#008000 bg:#ansigray',
            'scrollbar.arrow': '#008000',
            'scrollbar.background': '#cccccc',
            'scrollbar.button': '#008000',
        })

    def start(self):
        print("Interactive REPL started. Type '/exit' to quit.")
        while True:
            try:
                user_input = self.session.prompt('> ', completer=self.completer, auto_suggest=AutoSuggestFromHistory(), style=self.style)
                if user_input.lower() == '/exit':
                    break
                self._handle_command(user_input)
            except EOFError:
                break
            except KeyboardInterrupt:
                continue

    def _handle_command(self, command: str):
        """Handles user input, including built-in commands and passing to Agent."""
        if command.startswith('/'):
            if command == '/save':
                print("Saving current state...")
            elif command == '/plot':
                print("Plotting data...")
            elif command == '/cost':
                print("Displaying cost information...")
            else:
                print(f"Unknown built-in command: {command}")
        else:
            print(f"Processing user input: {command}")
            # Here, integrate with the Agent core to process the input

if __name__ == '__main__':
    repl = InteractiveREPL()
    repl.start()
