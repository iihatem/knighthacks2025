"""Client Communication Agent Executor"""
import sys
import os
from typing import Dict, Any

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from agents.shared.base_executor import BaseAgentExecutor
from agents.a2a_agents.client_communication.agent import ClientCommunicationAgent


class ClientCommunicationExecutor(BaseAgentExecutor):
    """Executor for Client Communication Agent"""
    
    def __init__(self):
        super().__init__('ClientCommunicationAgent')
        self.agent = ClientCommunicationAgent()
    
    async def process_task(self, query: str, case_id: str, session_id: str) -> Dict[str, Any]:
        """
        Process a client communication task
        
        Args:
            query: User's request
            case_id: The case ID
            session_id: Session ID for context
        
        Returns:
            Dict with task result
        """
        # Get case context (would normally fetch from RAG/Snowflake)
        # For now, we'll pass a simple context
        case_context = f"Case ID: {case_id}"
        
        # Invoke the agent
        result = await self.agent.ainvoke(query, case_context, session_id)
        
        return result

