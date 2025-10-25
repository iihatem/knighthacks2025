"""
Base agent class for TenderPilot agents.
"""
from typing import AsyncGenerator, Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class TenderPilotBaseAgent(ABC):
    """
    Base class for all TenderPilot agents.
    Provides common functionality and interface for specialized agents.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize the base agent.
        
        Args:
            name: Agent name
            description: Agent description
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task with the given context.
        
        Args:
            context: Task context containing input data and state
            
        Returns:
            Result dictionary with processed data
        """
        pass
    
    async def validate_input(self, context: Dict[str, Any]) -> bool:
        """
        Validate input context before processing.
        
        Args:
            context: Task context to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["task_type", "content"]
        for field in required_fields:
            if field not in context:
                self.logger.error(f"Missing required field: {field}")
                return False
        return True
    
    def log_action(self, action: str, details: Optional[Dict[str, Any]] = None):
        """
        Log agent action for audit trail.
        
        Args:
            action: Action description
            details: Optional action details
        """
        log_message = f"[{self.name}] {action}"
        if details:
            log_message += f" - {details}"
        self.logger.info(log_message)
    
    def get_info(self) -> Dict[str, str]:
        """
        Get agent information.
        
        Returns:
            Dictionary with agent name and description
        """
        return {
            "name": self.name,
            "description": self.description
        }

