"""
Settings for Voice Scheduler Agent.
"""
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Google API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

# Agent Configuration
AGENT_NAME = "voice_scheduler"
AGENT_MODEL = "gemini-2.0-flash"
AGENT_DESCRIPTION = "Coordinates appointments via voice calls using ElevenLabs"

# ElevenLabs Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_BASE_URL = os.getenv("ELEVENLABS_BASE_URL", "https://api.elevenlabs.io/v1")
VOICE_MODEL = os.getenv("VOICE_MODEL", "eleven_multilingual_v2")

# Voice Configuration
DEFAULT_VOICE_ID = os.getenv("DEFAULT_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
VOICE_STABILITY = float(os.getenv("VOICE_STABILITY", "0.5"))
VOICE_SIMILARITY_BOOST = float(os.getenv("VOICE_SIMILARITY_BOOST", "0.75"))

# Scheduling Configuration
CALENDAR_API_URL = os.getenv("CALENDAR_API_URL", "https://api.calendar.com")
SCHEDULING_TIMEOUT = int(os.getenv("SCHEDULING_TIMEOUT", "30"))
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))

# Appointment Types
APPOINTMENT_TYPES = [
    "deposition",
    "mediation",
    "court_hearing",
    "client_meeting",
    "expert_consultation",
    "medical_examination"
]

# Voice Personas
VOICE_PERSONAS = {
    "professional": {
        "tone": "professional and courteous",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "use_case": "business calls"
    },
    "empathetic": {
        "tone": "empathetic and supportive",
        "voice_id": "AZnzlk1XvdvUeBnXmlld",
        "use_case": "client communications"
    },
    "authoritative": {
        "tone": "authoritative and confident",
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "use_case": "legal proceedings"
    }
}

# Notification Configuration
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")
NOTIFICATION_SLACK_WEBHOOK = os.getenv("NOTIFICATION_SLACK_WEBHOOK")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENABLE_AUDIT_LOGGING = os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"
