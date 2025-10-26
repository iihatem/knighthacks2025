"""Legal Researcher Agent Executor"""
import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from agents.shared.base_executor import BaseAgentExecutor
from agents.a2a_agents.legal_researcher.agent import LegalResearcherAgent


class LegalResearcherExecutor(BaseAgentExecutor):
    """Executor for Legal Researcher Agent"""
    
    def __init__(self):
        super().__init__('LegalResearcherAgent')
        self.agent = LegalResearcherAgent()
    
    async def process_task(self, query: str, case_id: str, session_id: str) -> Dict[str, Any]:
        case_context = f"Case ID: {case_id}"
        result = await self.agent.ainvoke(query, case_context, session_id)
        return result

