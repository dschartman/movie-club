from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Set

class SlackCommand(ABC):
    """Base class for all Slack commands."""
    
    def __init__(self, name: str, description: str, examples: List[str] = None):
        self.name = name
        self.description = description
        self.examples = examples or []
    
    @abstractmethod
    async def execute(self, ack: Callable, respond: Callable, command: Dict[str, Any], **kwargs) -> None:
        """Execute the command."""
        pass
    
    def get_usage(self) -> str:
        """Get the command usage information."""
        usage = f"*{self.name}*: {self.description}\n"
        if self.examples:
            usage += "Examples:\n"
            for example in self.examples:
                usage += f"• `{example}`\n"
        return usage

class CommandRegistry:
    """Registry for all Slack commands."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CommandRegistry, cls).__new__(cls)
            cls._instance.commands = {}
        return cls._instance
    
    def register(self, command_name: str, command: SlackCommand) -> None:
        """Register a command."""
        self.commands[command_name] = command
    
    def get_command(self, command_name: str) -> Optional[SlackCommand]:
        """Get a command by name."""
        return self.commands.get(command_name)
    
    def get_all_commands(self) -> Dict[str, SlackCommand]:
        """Get all registered commands."""
        return self.commands
    
    def list_commands(self) -> List[SlackCommand]:
        """List all registered commands."""
        return list(self.commands.values())

# Create a singleton instance of the registry
registry = CommandRegistry()

def register_command(command):
    """
    Decorator to register a command with the registry.
    Works with both classes and instances.
    """
    # If decorating a class, create an instance first
    if isinstance(command, type):
        instance = command()
        registry.register(instance.name, instance)
        return command
    # If decorating an instance
    else:
        registry.register(command.name, command)
        return command
