"""
TenderPilot Multi-Agent Workflows using Google ADK patterns.
Implements SequentialAgent, ParallelAgent, and LoopAgent workflows.
"""

from google.adk.agents import SequentialAgent, ParallelAgent, LoopAgent
from tenderpilot_agents import (
    tender_coordinator,
    records_wrangler,
    client_communication_guru,
    legal_researcher,
    voice_scheduler,
    evidence_sorter
)

# Import additional agents
from tenderpilot_agents.legal_researcher import agent as legal_researcher_agent
from tenderpilot_agents.voice_scheduler import agent as voice_scheduler_agent
from tenderpilot_agents.evidence_sorter import agent as evidence_sorter_agent

# Get the root agents
legal_researcher = legal_researcher_agent.root_agent
voice_scheduler = voice_scheduler_agent.root_agent
evidence_sorter = evidence_sorter_agent.root_agent


class TenderPilotWorkflows:
    """
    TenderPilot Multi-Agent Workflows using Google ADK patterns.
    Implements the core architecture with proper sequentiality and workflows.
    """
    
    def __init__(self):
        """Initialize all TenderPilot workflows."""
        self._create_workflow_agents()
        self._create_approval_workflows()
        self._create_case_processing_workflows()
    
    def _create_workflow_agents(self):
        """Create Google ADK workflow agents."""
        
        # Create separate agent instances for workflows to avoid parent conflicts
        from google.adk.agents import Agent
        
        # Case Processing Pipeline agents
        pipeline_records = Agent(
            name="PipelineRecordsWrangler",
            model="gemini-2.0-flash",
            instruction="Process medical records in case processing pipeline",
            description="Records wrangler for case processing pipeline",
            output_key="pipeline_records_result"
        )
        
        pipeline_researcher = Agent(
            name="PipelineLegalResearcher",
            model="gemini-2.0-flash",
            instruction="Conduct legal research in case processing pipeline",
            description="Legal researcher for case processing pipeline",
            output_key="pipeline_research_result"
        )
        
        pipeline_sorter = Agent(
            name="PipelineEvidenceSorter",
            model="gemini-2.0-flash",
            instruction="Organize evidence in case processing pipeline",
            description="Evidence sorter for case processing pipeline",
            output_key="pipeline_organization_result"
        )
        
        # Case Processing Pipeline (Sequential)
        self.case_processing_pipeline = SequentialAgent(
            name="CaseProcessingPipeline",
            sub_agents=[
                pipeline_records,      # Step 1: Gather medical records
                pipeline_researcher,   # Step 2: Research case law
                pipeline_sorter       # Step 3: Organize evidence
            ]
        )
        
        # Information Gathering agents
        parallel_records = Agent(
            name="ParallelRecordsWrangler",
            model="gemini-2.0-flash",
            instruction="Gather medical records in parallel",
            description="Records wrangler for parallel information gathering",
            output_key="parallel_records_result"
        )
        
        parallel_researcher = Agent(
            name="ParallelLegalResearcher",
            model="gemini-2.0-flash",
            instruction="Conduct legal research in parallel",
            description="Legal researcher for parallel information gathering",
            output_key="parallel_research_result"
        )
        
        parallel_sorter = Agent(
            name="ParallelEvidenceSorter",
            model="gemini-2.0-flash",
            instruction="Organize evidence in parallel",
            description="Evidence sorter for parallel information gathering",
            output_key="parallel_organization_result"
        )
        
        # Information Gathering (Parallel)
        self.information_gatherer = ParallelAgent(
            name="InformationGatherer",
            sub_agents=[
                parallel_records,      # Gather medical records
                parallel_researcher,   # Research legal precedents
                parallel_sorter       # Organize existing evidence
            ]
        )
        
        # Client Communication Workflow agents
        workflow_communication = Agent(
            name="WorkflowClientCommunication",
            model="gemini-2.0-flash",
            instruction="Handle client communication in workflow context",
            description="Client communication guru for workflow",
            output_key="workflow_communication_result"
        )
        
        workflow_scheduler = Agent(
            name="WorkflowVoiceScheduler",
            model="gemini-2.0-flash",
            instruction="Handle scheduling in workflow context",
            description="Voice scheduler for workflow",
            output_key="workflow_scheduling_result"
        )
        
        # Client Communication Workflow (Sequential)
        self.client_communication_workflow = SequentialAgent(
            name="ClientCommunicationWorkflow",
            sub_agents=[
                workflow_communication,  # Step 1: Draft message
                workflow_scheduler      # Step 2: Schedule follow-up
            ]
        )
        
        # Legal Research Loop agent
        loop_researcher = Agent(
            name="LoopLegalResearcher",
            model="gemini-2.0-flash",
            instruction="Conduct iterative legal research",
            description="Legal researcher for iterative refinement",
            output_key="loop_research_result"
        )
        
        # Legal Research Refinement (Loop)
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
        from google.adk.agents import Agent
        
        class QualityChecker(Agent):
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
        
        return QualityChecker()
    
    def _create_approval_workflows(self):
        """Create Human-in-the-Loop approval workflows."""
        from google.adk.agents import Agent
        
        # Task Preparation Agent
        task_preparer = Agent(
            name="TaskPreparer",
            model="gemini-2.0-flash",
            instruction="Prepare task details for human approval",
            description="Prepares tasks for human review",
            output_key="prepared_task"
        )
        
        # Human Approval Agent
        human_approval = Agent(
            name="HumanApproval",
            model="gemini-2.0-flash",
            instruction="Wait for human approval before proceeding",
            description="Handles human-in-the-loop approval",
            output_key="approval_status"
        )
        
        # Task Executor Agent
        task_executor = Agent(
            name="TaskExecutor",
            model="gemini-2.0-flash",
            instruction="Execute approved tasks",
            description="Executes tasks after human approval",
            output_key="execution_result"
        )
        
        # Legal Approval Workflow (Sequential)
        self.legal_approval_workflow = SequentialAgent(
            name="LegalApprovalWorkflow",
            sub_agents=[
                task_preparer,      # Prepare task details
                human_approval,     # Wait for human approval
                task_executor       # Execute approved tasks
            ]
        )
        
        # Settlement Approval Workflow agents
        settlement_legal_researcher = Agent(
            name="SettlementApprovalLegalResearcher",
            model="gemini-2.0-flash",
            instruction="Research settlement precedents for approval workflow",
            description="Legal researcher for settlement approval",
            output_key="settlement_approval_research_result"
        )
        
        settlement_task_preparer = Agent(
            name="SettlementTaskPreparer",
            model="gemini-2.0-flash",
            instruction="Prepare settlement details for approval",
            description="Task preparer for settlement approval",
            output_key="settlement_prepared_task"
        )
        
        settlement_human_approval = Agent(
            name="SettlementHumanApproval",
            model="gemini-2.0-flash",
            instruction="Wait for human approval of settlement",
            description="Human approval for settlement",
            output_key="settlement_approval_status"
        )
        
        settlement_communication = Agent(
            name="SettlementApprovalCommunication",
            model="gemini-2.0-flash",
            instruction="Communicate settlement to client",
            description="Client communication for settlement approval",
            output_key="settlement_communication_result"
        )
        
        # Settlement Approval Workflow (Sequential)
        self.settlement_approval_workflow = SequentialAgent(
            name="SettlementApprovalWorkflow",
            sub_agents=[
                settlement_legal_researcher,   # Research settlement precedents
                settlement_task_preparer,     # Prepare settlement details
                settlement_human_approval,    # Wait for human approval
                settlement_communication     # Communicate to client
            ]
        )
    
    def _create_case_processing_workflows(self):
        """Create case processing workflows."""
        from google.adk.agents import Agent
        
        # New Case Intake agents
        intake_records = Agent(
            name="IntakeRecordsWrangler",
            model="gemini-2.0-flash",
            instruction="Gather initial records for new case intake",
            description="Records wrangler for case intake",
            output_key="intake_records_result"
        )
        
        intake_sorter = Agent(
            name="IntakeEvidenceSorter",
            model="gemini-2.0-flash",
            instruction="Organize initial evidence for new case",
            description="Evidence sorter for case intake",
            output_key="intake_organization_result"
        )
        
        intake_researcher = Agent(
            name="IntakeLegalResearcher",
            model="gemini-2.0-flash",
            instruction="Conduct initial legal research for new case",
            description="Legal researcher for case intake",
            output_key="intake_research_result"
        )
        
        intake_communication = Agent(
            name="IntakeClientCommunication",
            model="gemini-2.0-flash",
            instruction="Send intake confirmation to client",
            description="Client communication for case intake",
            output_key="intake_communication_result"
        )
        
        # New Case Intake (Sequential)
        self.new_case_intake = SequentialAgent(
            name="NewCaseIntake",
            sub_agents=[
                intake_records,           # Gather initial records
                intake_sorter,           # Organize initial evidence
                intake_researcher,       # Initial legal research
                intake_communication     # Send intake confirmation
            ]
        )
        
        # Deposition Preparation agents
        depo_researcher = Agent(
            name="DepoLegalResearcher",
            model="gemini-2.0-flash",
            instruction="Research deposition topics",
            description="Legal researcher for deposition preparation",
            output_key="depo_research_result"
        )
        
        depo_sorter = Agent(
            name="DepoEvidenceSorter",
            model="gemini-2.0-flash",
            instruction="Organize relevant evidence for deposition",
            description="Evidence sorter for deposition preparation",
            output_key="depo_organization_result"
        )
        
        depo_scheduler = Agent(
            name="DepoVoiceScheduler",
            model="gemini-2.0-flash",
            instruction="Schedule deposition",
            description="Voice scheduler for deposition preparation",
            output_key="depo_scheduling_result"
        )
        
        depo_communication = Agent(
            name="DepoClientCommunication",
            model="gemini-2.0-flash",
            instruction="Notify client about deposition",
            description="Client communication for deposition preparation",
            output_key="depo_communication_result"
        )
        
        # Deposition Preparation (Sequential)
        self.deposition_preparation = SequentialAgent(
            name="DepositionPreparation",
            sub_agents=[
                depo_researcher,      # Research deposition topics
                depo_sorter,          # Organize relevant evidence
                depo_scheduler,       # Schedule deposition
                depo_communication    # Notify client
            ]
        )
        
        # Settlement Negotiation agents
        settlement_researcher = Agent(
            name="SettlementLegalResearcher",
            model="gemini-2.0-flash",
            instruction="Research settlement options",
            description="Legal researcher for settlement negotiation",
            output_key="settlement_research_result"
        )
        
        settlement_communication = Agent(
            name="SettlementClientCommunication",
            model="gemini-2.0-flash",
            instruction="Communicate with client about settlement",
            description="Client communication for settlement negotiation",
            output_key="settlement_communication_result"
        )
        
        # Settlement Negotiation (Loop)
        self.settlement_negotiation = LoopAgent(
            name="SettlementNegotiation",
            max_iterations=5,
            sub_agents=[
                settlement_researcher,    # Research settlement options
                settlement_communication, # Communicate with client
                self._create_approval_workflow()  # Get approval for offers
            ]
        )
    
    def _create_approval_workflow(self):
        """Create a nested approval workflow."""
        from google.adk.agents import Agent, SequentialAgent
        
        # Approval sub-workflow
        approval_agent = Agent(
            name="ApprovalAgent",
            model="gemini-2.0-flash",
            instruction="Handle approval for settlement offers",
            description="Manages approval workflow",
            output_key="approval_result"
        )
        
        return SequentialAgent(
            name="NestedApprovalWorkflow",
            sub_agents=[approval_agent]
        )
    
    def get_all_workflows(self):
        """Get all available workflows."""
        return {
            "case_processing_pipeline": self.case_processing_pipeline,
            "information_gatherer": self.information_gatherer,
            "client_communication_workflow": self.client_communication_workflow,
            "legal_research_loop": self.legal_research_loop,
            "legal_approval_workflow": self.legal_approval_workflow,
            "settlement_approval_workflow": self.settlement_approval_workflow,
            "new_case_intake": self.new_case_intake,
            "deposition_preparation": self.deposition_preparation,
            "settlement_negotiation": self.settlement_negotiation
        }
    
    def get_workflow_info(self):
        """Get information about all workflows."""
        workflows = self.get_all_workflows()
        return {
            "total_workflows": len(workflows),
            "workflow_types": {
                "SequentialAgent": len([w for w in workflows.values() if isinstance(w, SequentialAgent)]),
                "ParallelAgent": len([w for w in workflows.values() if isinstance(w, ParallelAgent)]),
                "LoopAgent": len([w for w in workflows.values() if isinstance(w, LoopAgent)])
            },
            "workflows": {
                name: {
                    "type": type(workflow).__name__,
                    "sub_agents": len(workflow.sub_agents),
                    "max_iterations": getattr(workflow, 'max_iterations', None)
                }
                for name, workflow in workflows.items()
            }
        }


# Create global workflows instance
tenderpilot_workflows = TenderPilotWorkflows()

# Export workflows
case_processing_pipeline = tenderpilot_workflows.case_processing_pipeline
information_gatherer = tenderpilot_workflows.information_gatherer
client_communication_workflow = tenderpilot_workflows.client_communication_workflow
legal_research_loop = tenderpilot_workflows.legal_research_loop
legal_approval_workflow = tenderpilot_workflows.legal_approval_workflow
settlement_approval_workflow = tenderpilot_workflows.settlement_approval_workflow
new_case_intake = tenderpilot_workflows.new_case_intake
deposition_preparation = tenderpilot_workflows.deposition_preparation
settlement_negotiation = tenderpilot_workflows.settlement_negotiation
