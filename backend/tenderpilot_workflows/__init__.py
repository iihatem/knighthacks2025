# TenderPilot Workflows Package
from . import workflows

# Export workflows
from .workflows import (
    case_processing_pipeline,
    information_gatherer,
    client_communication_workflow,
    legal_research_loop,
    legal_approval_workflow,
    settlement_approval_workflow,
    new_case_intake,
    deposition_preparation,
    settlement_negotiation
)
