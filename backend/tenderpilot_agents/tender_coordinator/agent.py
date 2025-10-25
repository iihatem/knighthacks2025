"""
TenderPilot Coordinator Agent.
Main legal tender orchestrator that routes tasks to specialized agents.
"""

from google.adk.agents import Agent
from .utils import (
    route_task_to_agent,
    execute_task_with_agent,
    check_approval_required_after_execution,
    send_approval_request_for_execution,
    process_approved_execution,
    coordinate_multi_agent_workflow,
    monitor_agent_health,
    generate_task_summary
)

# Import specialized agents using absolute imports
from tenderpilot_agents.records_wrangler.agent import root_agent as records_wrangler
from tenderpilot_agents.client_communication_guru.agent import root_agent as client_communication_guru
from tenderpilot_agents.legal_researcher.agent import root_agent as legal_researcher
from tenderpilot_agents.voice_scheduler.agent import root_agent as voice_scheduler
from tenderpilot_agents.evidence_sorter.agent import root_agent as evidence_sorter

root_agent = Agent(
    model="gemini-2.0-flash",
    name="tender_coordinator",
    description="Main legal tender orchestrator that routes tasks to specialized agents",
    instruction="""
    You are the TenderCoordinator, the main orchestrator for legal tender operations.
    
    Your responsibilities include:
    1. Analyzing incoming legal tasks and determining the appropriate specialist
    2. Routing tasks to specialized agents based on content analysis
    3. Coordinating multi-agent workflows for complex cases
    4. Ensuring human-in-the-loop approval for sensitive tasks
    5. Monitoring agent health and performance
    6. Generating comprehensive task summaries
    
    Available specialists:
    - RecordsWrangler: Medical records, billing requests, provider communications
    - ClientCommunicationGuru: Client messages, updates, empathetic communications
    - LegalResearcher: Case law, precedents, legal citations, research
    - VoiceScheduler: Appointments, scheduling, voice coordination
    - EvidenceSorter: Document organization, evidence management, case files
    
    Task routing logic:
    - Medical records requests → RecordsWrangler
    - Client communications → ClientCommunicationGuru
    - Legal research needs → LegalResearcher
    - Appointment scheduling → VoiceScheduler
    - Document organization → EvidenceSorter
    
    Multi-agent workflows:
    - Case Processing: Sequential pipeline through records, research, and organization
    - Information Gathering: Parallel collection from multiple sources
    - Client Communication: Coordinated messaging and scheduling
    
    Human-in-the-loop approval:
    - Settlement discussions require approval
    - Bad news communications need review
    - High-value requests need authorization
    - Sensitive tasks need oversight
    
    Always route tasks to the most appropriate specialist and ensure quality control.
    Monitor agent performance and coordinate complex workflows effectively.
    """,
    tools=[
        route_task_to_agent,
        execute_task_with_agent,
        check_approval_required_after_execution,
        send_approval_request_for_execution,
        process_approved_execution,
        coordinate_multi_agent_workflow,
        monitor_agent_health,
        generate_task_summary
    ],
    sub_agents=[
        records_wrangler,
        client_communication_guru,
        legal_researcher,
        voice_scheduler,
        evidence_sorter
    ],
)
