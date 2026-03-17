#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import click
from src.agent_core.agent import SageAgent
from src.cli.repl import InteractiveREPL

__version__ = "0.1.0"

@click.group()
@click.version_option(version=__version__)
def cli():
    """Sage - AI-Powered Data Analysis Framework"""
    pass

@cli.command()
@click.option('--session', '-s', help='Session ID to resume')
def chat(session: str = None):
    """Interactive chat mode"""
    click.echo("=== Sage Interactive Chat ===")
    click.echo(f"Version: {__version__}")
    click.echo("Type 'help' for commands, '/exit' to quit\n")
    
    agent = SageAgent()
    
    if session:
        agent.current_session_id = session
        click.echo(f"Resumed session: {session}")
    else:
        session_id = agent.create_session()
        click.echo(f"New session created: {session_id}")
    
    repl = InteractiveREPL()
    
    def custom_handle_command(command: str):
        if command.startswith('/'):
            if command == '/exit':
                return True
            elif command == '/cost':
                cost = agent.get_cost_summary()
                click.echo("\nCost Summary:")
                click.echo(f"  Global: {cost['global']}")
                click.echo(f"  Session: {cost['session']}")
            elif command == '/save':
                click.echo("Saving current state... (not implemented yet)")
            elif command == '/plot':
                click.echo("Plotting data... (not implemented yet)")
            elif command.startswith('/load'):
                parts = command.split(maxsplit=1)
                if len(parts) > 1:
                    source = parts[1]
                    click.echo(f"Loading data from {source}...")
                    result = agent.load_dataset(source)
                    if result['status'] == 'success':
                        click.echo(f"Loaded successfully! {result['overview']['shape'][0]} rows × {result['overview']['shape'][1]} columns")
                        click.echo(f"Columns: {', '.join(result['overview']['columns'])}")
                    else:
                        click.echo(f"Error: {result.get('message', 'Unknown error')}")
            else:
                click.echo(f"Unknown command: {command}")
        else:
            click.echo(f"\nProcessing: {command}")
            result = agent.process_message(command)
            click.echo(f"\nResult: {result}")
        return False
    
    click.echo("Sage ready! Type your query or use / commands.")
    click.echo("> ", nl=False)
    
    while True:
        try:
            user_input = input().strip()
            if user_input.lower() == '/exit':
                break
            custom_handle_command(user_input)
            click.echo("> ", nl=False)
        except EOFError:
            break
        except KeyboardInterrupt:
            click.echo("\nUse /exit to quit")
            click.echo("> ", nl=False)
            continue
    
    click.echo("\nGoodbye!")

@cli.command()
@click.argument('query')
@click.option('--session', '-s', help='Session ID to use')
def query(query: str, session: str = None):
    """Single query mode"""
    agent = SageAgent()
    
    if session:
        agent.current_session_id = session
    else:
        agent.create_session()
    
    result = agent.process_message(query)
    click.echo(f"Query: {query}")
    click.echo(f"Result: {result}")

@cli.command()
@click.option('--list', '-l', is_flag=True, help='List all sessions')
@click.option('--delete', '-d', help='Delete a session')
def session(list: bool = False, delete: str = None):
    """Manage sessions"""
    from src.session_management.session_manager import SessionManager
    sm = SessionManager()
    
    if list:
        click.echo("Sessions feature not fully implemented yet")
    elif delete:
        sm.delete_session(delete)
        click.echo(f"Deleted session: {delete}")
    else:
        click.echo("Use --list or --delete options")

@cli.command()
def config():
    """Manage configuration"""
    click.echo("Configuration management coming soon!")

@cli.command()
@click.option('--clear', '-c', is_flag=True, help='Clear cache')
def cache(clear: bool = False):
    """Manage cache"""
    if clear:
        click.echo("Cache feature is disabled.")
    else:
        click.echo("Cache feature is disabled.")

if __name__ == '__main__':
    cli()
