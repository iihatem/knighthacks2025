"""
Settings for TenderPilot Coordinator Agent.
"""
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Google API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

# Agent Configuration
AGENT_NAME = "tender_coordinator"
AGENT_MODEL = "gemini-2.0-flash"
AGENT_DESCRIPTION = "Main legal tender orchestrator that routes tasks to specialized agents"

# Specialized Agent URLs
RECORDS_WRANGLER_URL = os.getenv("RECORDS_WRANGLER_URL", "http://localhost:10031")
CLIENT_COMMUNICATION_URL = os.getenv("CLIENT_COMMUNICATION_URL", "http://localhost:10032")
LEGAL_RESEARCHER_URL = os.getenv("LEGAL_RESEARCHER_URL", "http://localhost:10033")
VOICE_SCHEDULER_URL = os.getenv("VOICE_SCHEDULER_URL", "http://localhost:10034")
EVIDENCE_SORTER_URL = os.getenv("EVIDENCE_SORTER_URL", "http://localhost:10035")

# Task Routing Configuration
TASK_ROUTING_TIMEOUT = int(os.getenv("TASK_ROUTING_TIMEOUT", "30"))
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))

# Human-in-the-Loop Configuration
REQUIRE_APPROVAL_FOR = [
    "settlement_discussion",
    "bad_news", 
    "good_news",
    "high_value_requests"
]

AUTO_APPROVE_FOR = [
    "appointment_reminder",
    "document_request",
    "routine_updates"
]

# Notification Configuration
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")
NOTIFICATION_SLACK_WEBHOOK = os.getenv("NOTIFICATION_SLACK_WEBHOOK")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENABLE_AUDIT_LOGGING = os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"
