"""
Settings for Records Wrangler Agent.
"""
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Google API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

# Agent Configuration
AGENT_NAME = "records_wrangler"
AGENT_MODEL = "gemini-2.0-flash"
AGENT_DESCRIPTION = "Handles medical records and billing requests from providers"

# Medical Records Configuration
MEDICAL_RECORDS_BASE_URL = os.getenv("MEDICAL_RECORDS_BASE_URL", "https://api.medical-records.com")
PROVIDER_TIMEOUT = int(os.getenv("PROVIDER_TIMEOUT", "30"))
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))

# Billing Configuration
BILLING_SYSTEM_URL = os.getenv("BILLING_SYSTEM_URL", "https://api.billing.com")
BILLING_TIMEOUT = int(os.getenv("BILLING_TIMEOUT", "60"))

# Notification Configuration
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")
NOTIFICATION_SLACK_WEBHOOK = os.getenv("NOTIFICATION_SLACK_WEBHOOK")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENABLE_AUDIT_LOGGING = os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"
