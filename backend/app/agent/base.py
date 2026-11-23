
from abc import ABC, abstractmethod


class Tool(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the tool's unique name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Explain what the tool does and when to use it."""
        pass

    @abstractmethod
    def execute(self, tool_input: str):
        """Execute the tool using the provided input."""
        pass
