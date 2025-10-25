"""
Google ADK Agent Declarations for TenderPilot.
Implements proper Google ADK LlmAgent and workflow agents.
"""
import logging
from typing import List, Dict, Any
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.tools import agent_tool
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator

logger = logging.getLogger(__name__)


class TenderPilotADKAgents:
    """
    Google ADK Agent declarations for TenderPilot system.
    Implements the proper ADK multi-agent architecture.
    """
    
    def __init__(self):
        """Initialize all ADK agents."""
        self.logger = logging.getLogger(__name__)
        self._create_specialized_agents()
        self._create_workflow_agents()
        self._create_coordinator()
    
    def _create_specialized_agents(self):
        """Create specialized LlmAgent instances."""
        
        # Records Wrangler Agent
        self.records_wrangler = LlmAgent(
            name="RecordsWrangler",
            model="gemini-2.0-flash",
            instruction="""
            You are a Records Wrangler specializing in medical records and billing requests.
            Your responsibilities:
            1. Extract provider and patient information from requests
            2. Draft professional request letters to medical providers
            3. Generate action items and track fulfillment
            4. Handle billing disputes and missing records
            
            Always be professional, thorough, and empathetic in your communications.
            """,
            description="Handles medical records retrieval and billing requests from providers",
            output_key="records_result"
        )
        
        # Client Communication Guru Agent
        self.client_communication_guru = LlmAgent(
            name="ClientCommunicationGuru",
            model="gemini-2.0-flash",
            instruction="""
            You are a Client Communication Guru specializing in empathetic client communications.
            Your responsibilities:
            1. Draft clear, empathetic messages to clients
            2. Adapt tone based on message type (updates, requests, good/bad news)
            3. Ensure professional formatting and appropriate language
            4. Review messages for clarity and empathy
            
            Always prioritize client understanding and emotional support.
            """,
            description="Drafts clear, empathetic messages to clients and reviews outgoing communications",
            output_key="communication_result"
        )
        
        # Legal Researcher Agent
        self.legal_researcher = LlmAgent(
            name="LegalResearcher",
            model="gemini-2.0-flash",
            instruction="""
            You are a Legal Researcher specializing in case law and legal precedents.
            Your responsibilities:
            1. Find relevant case law and legal precedents
            2. Provide citations and holdings
            3. Generate research summaries with legal strategies
            4. Identify applicable legal theories
            
            Always provide accurate citations and clear legal analysis.
            """,
            description="Finds case law, precedents, and legal citations to strengthen cases",
            output_key="research_result"
        )
        
        # Voice Scheduler Agent
        self.voice_scheduler = LlmAgent(
            name="VoiceScheduler",
            model="gemini-2.0-flash",
            instruction="""
            You are a Voice Scheduler specializing in appointment coordination via voice calls.
            Your responsibilities:
            1. Generate natural call scripts for different recipient types
            2. Adapt voice persona (empathetic for clients, professional for providers)
            3. Coordinate appointments, depositions, and mediations
            4. Handle scheduling conflicts and follow-ups
            
            Always be courteous, clear, and efficient in scheduling communications.
            """,
            description="Coordinates appointments via voice calls using ElevenLabs",
            output_key="scheduling_result"
        )
        
        # Evidence Sorter Agent
        self.evidence_sorter = LlmAgent(
            name="EvidenceSorter",
            model="gemini-2.0-flash",
            instruction="""
            You are an Evidence Sorter specializing in document organization and categorization.
            Your responsibilities:
            1. Categorize documents automatically (medical, legal, billing, etc.)
            2. Generate folder structures and organization plans
            3. Extract file metadata and identify OCR requirements
            4. Create evidence indexes and case timelines
            
            Always be systematic and thorough in document organization.
            """,
            description="Organizes documents, evidence, and attachments for case management",
            output_key="organization_result"
        )
    
    def _create_workflow_agents(self):
        """Create ADK workflow agents for complex processes."""
        
        # Create separate agent instances for workflows to avoid parent conflicts
        # Sequential Pipeline for Case Processing
        pipeline_records = LlmAgent(
            name="PipelineRecordsWrangler",
            model="gemini-2.0-flash",
            instruction="Process medical records in pipeline context",
            description="Records wrangler for case processing pipeline",
            output_key="pipeline_records_result"
        )
        
        pipeline_researcher = LlmAgent(
            name="PipelineLegalResearcher",
            model="gemini-2.0-flash",
            instruction="Conduct legal research in pipeline context",
            description="Legal researcher for case processing pipeline",
            output_key="pipeline_research_result"
        )
        
        pipeline_sorter = LlmAgent(
            name="PipelineEvidenceSorter",
            model="gemini-2.0-flash",
            instruction="Organize evidence in pipeline context",
            description="Evidence sorter for case processing pipeline",
            output_key="pipeline_organization_result"
        )
        
        self.case_processing_pipeline = SequentialAgent(
            name="CaseProcessingPipeline",
            sub_agents=[
                pipeline_records,
                pipeline_researcher,
                pipeline_sorter
            ]
        )
        
        # Parallel Information Gathering
        parallel_records = LlmAgent(
            name="ParallelRecordsWrangler",
            model="gemini-2.0-flash",
            instruction="Gather medical records in parallel",
            description="Records wrangler for parallel information gathering",
            output_key="parallel_records_result"
        )
        
        parallel_researcher = LlmAgent(
            name="ParallelLegalResearcher",
            model="gemini-2.0-flash",
            instruction="Conduct legal research in parallel",
            description="Legal researcher for parallel information gathering",
            output_key="parallel_research_result"
        )
        
        parallel_sorter = LlmAgent(
            name="ParallelEvidenceSorter",
            model="gemini-2.0-flash",
            instruction="Organize evidence in parallel",
            description="Evidence sorter for parallel information gathering",
            output_key="parallel_organization_result"
        )
        
        self.information_gatherer = ParallelAgent(
            name="InformationGatherer",
            sub_agents=[
                parallel_records,
                parallel_researcher,
                parallel_sorter
            ]
        )
        
        # Client Communication Workflow
        workflow_communication = LlmAgent(
            name="WorkflowClientCommunication",
            model="gemini-2.0-flash",
            instruction="Handle client communication in workflow context",
            description="Client communication guru for workflow",
            output_key="workflow_communication_result"
        )
        
        workflow_scheduler = LlmAgent(
            name="WorkflowVoiceScheduler",
            model="gemini-2.0-flash",
            instruction="Handle scheduling in workflow context",
            description="Voice scheduler for workflow",
            output_key="workflow_scheduling_result"
        )
        
        self.client_communication_workflow = SequentialAgent(
            name="ClientCommunicationWorkflow",
            sub_agents=[
                workflow_communication,
                workflow_scheduler
            ]
        )
        
        # Iterative Refinement Loop for Legal Research
        loop_researcher = LlmAgent(
            name="LoopLegalResearcher",
            model="gemini-2.0-flash",
            instruction="Conduct iterative legal research",
            description="Legal researcher for iterative refinement",
            output_key="loop_research_result"
        )
        
        self.legal_research_loop = LoopAgent(
            name="LegalResearchLoop",
            max_iterations=3,
            sub_agents=[
                loop_researcher,
                self._create_quality_checker()
            ]
        )
    
    def _create_quality_checker(self):
        """Create a quality checker agent for iterative refinement."""
        
        class QualityChecker(LlmAgent):
            def __init__(self):
                super().__init__(
                    name="QualityChecker",
                    model="gemini-2.0-flash",
                    instruction="""
                    You are a Quality Checker for legal research.
                    Evaluate the research quality and completeness.
                    Output 'pass' if the research meets standards, 'fail' if it needs improvement.
                    """,
                    description="Checks the quality of legal research",
                    output_key="quality_status"
                )
            
            async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
                # Get the research result from state
                research_result = ctx.session.state.get("research_result", "")
                
                # Simple quality check (in production, this would be more sophisticated)
                quality_score = len(research_result.split()) if research_result else 0
                is_quality_good = quality_score > 100  # Minimum word count
                
                if is_quality_good:
                    ctx.session.state["quality_status"] = "pass"
                else:
                    ctx.session.state["quality_status"] = "fail"
                
                yield Event(
                    author=self.name,
                    content=f"Quality check: {'pass' if is_quality_good else 'fail'}"
                )
        
        return QualityChecker()
    
    def _create_coordinator(self):
        """Create the main coordinator using ADK patterns."""
        
        # Main Tender Coordinator using ADK LlmAgent
        self.tender_coordinator = LlmAgent(
            name="TenderCoordinator",
            model="gemini-2.0-flash",
            instruction="""
            You are the TenderCoordinator, the main orchestrator for legal tender operations.
            
            Your responsibilities:
            1. Analyze incoming legal tasks and determine the appropriate specialist
            2. Route tasks to specialized agents based on content analysis
            3. Coordinate multi-agent workflows for complex cases
            4. Ensure human-in-the-loop approval for sensitive tasks
            
            Available specialists:
            - RecordsWrangler: Medical records, billing requests
            - ClientCommunicationGuru: Client messages, updates
            - LegalResearcher: Case law, precedents, research
            - VoiceScheduler: Appointments, scheduling
            - EvidenceSorter: Document organization, evidence management
            
            Always route tasks to the most appropriate specialist and ensure quality control.
            """,
            description="Main legal tender orchestrator that routes tasks to specialized agents",
            sub_agents=[
                self.records_wrangler,
                self.client_communication_guru,
                self.legal_researcher,
                self.voice_scheduler,
                self.evidence_sorter
            ]
        )
        
        # Create AgentTool wrappers for explicit invocation
        self.records_tool = agent_tool.AgentTool(agent=self.records_wrangler)
        self.communication_tool = agent_tool.AgentTool(agent=self.client_communication_guru)
        self.research_tool = agent_tool.AgentTool(agent=self.legal_researcher)
        self.scheduling_tool = agent_tool.AgentTool(agent=self.voice_scheduler)
        self.organization_tool = agent_tool.AgentTool(agent=self.evidence_sorter)
        
        # Add tools to coordinator for explicit invocation
        self.tender_coordinator.tools = [
            self.records_tool,
            self.communication_tool,
            self.research_tool,
            self.scheduling_tool,
            self.organization_tool
        ]
    
    def get_coordinator(self) -> LlmAgent:
        """Get the main coordinator agent."""
        return self.tender_coordinator
    
    def get_specialized_agents(self) -> List[LlmAgent]:
        """Get all specialized agents."""
        return [
            self.records_wrangler,
            self.client_communication_guru,
            self.legal_researcher,
            self.voice_scheduler,
            self.evidence_sorter
        ]
    
    def get_workflow_agents(self) -> List:
        """Get all workflow agents."""
        return [
            self.case_processing_pipeline,
            self.information_gatherer,
            self.client_communication_workflow,
            self.legal_research_loop
        ]
    
    def get_agent_tools(self) -> List:
        """Get all agent tools for explicit invocation."""
        return [
            self.records_tool,
            self.communication_tool,
            self.research_tool,
            self.scheduling_tool,
            self.organization_tool
        ]
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            "coordinator": self.tender_coordinator.name,
            "specialized_agents": len(self.get_specialized_agents()),
            "workflow_agents": len(self.get_workflow_agents()),
            "agent_tools": len(self.get_agent_tools()),
            "model": "gemini-2.0-flash"
        }


# Global instance
adk_agents = TenderPilotADKAgents()


def get_tender_coordinator() -> LlmAgent:
    """Get the main TenderCoordinator agent."""
    return adk_agents.get_coordinator()


def get_specialized_agents() -> List[LlmAgent]:
    """Get all specialized agents."""
    return adk_agents.get_specialized_agents()


def get_workflow_agents():
    """Get all workflow agents."""
    return adk_agents.get_workflow_agents()


def get_agent_tools():
    """Get all agent tools."""
    return adk_agents.get_agent_tools()
