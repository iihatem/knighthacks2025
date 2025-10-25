"""
Settings for Client Communication Guru Agent.
"""
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Google API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

# Agent Configuration
AGENT_NAME = "client_communication_guru"
AGENT_MODEL = "gemini-2.0-flash"
AGENT_DESCRIPTION = "Drafts clear, empathetic messages to clients and reviews outgoing communications"

# Communication Configuration
EMAIL_SYSTEM_URL = os.getenv("EMAIL_SYSTEM_URL", "https://api.email.com")
SMS_SYSTEM_URL = os.getenv("SMS_SYSTEM_URL", "https://api.sms.com")
COMMUNICATION_TIMEOUT = int(os.getenv("COMMUNICATION_TIMEOUT", "30"))

# Tone Guidelines
DEFAULT_TONE = "professional and empathetic"
URGENT_TONE = "urgent but reassuring"
SENSITIVE_TONE = "empathetic and supportive"

# Message Types
MESSAGE_TYPES = [
    "case_update",
    "document_request", 
    "appointment_reminder",
    "settlement_discussion",
    "bad_news",
    "good_news",
    "general"
]

# Approval Configuration
REQUIRE_APPROVAL_FOR = ["settlement_discussion", "bad_news", "good_news"]
AUTO_APPROVE_FOR = ["appointment_reminder", "document_request"]

# Notification Configuration
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")
NOTIFICATION_SLACK_WEBHOOK = os.getenv("NOTIFICATION_SLACK_WEBHOOK")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENABLE_AUDIT_LOGGING = os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"
