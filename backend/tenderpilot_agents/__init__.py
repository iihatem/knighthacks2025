# TenderPilot Agents Package
from .tender_coordinator import agent as coordinator_agent
from .records_wrangler import agent as records_wrangler_agent
from .client_communication_guru import agent as client_communication_agent
from .legal_researcher import agent as legal_researcher_agent
from .voice_scheduler import agent as voice_scheduler_agent
from .evidence_sorter import agent as evidence_sorter_agent

# Export root agents
tender_coordinator = coordinator_agent.root_agent
records_wrangler = records_wrangler_agent.root_agent
client_communication_guru = client_communication_agent.root_agent
legal_researcher = legal_researcher_agent.root_agent
voice_scheduler = voice_scheduler_agent.root_agent
evidence_sorter = evidence_sorter_agent.root_agent
