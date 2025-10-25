"""
Settings for Legal Researcher Agent.
"""
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Google API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

# Agent Configuration
AGENT_NAME = "legal_researcher"
AGENT_MODEL = "gemini-2.0-flash"
AGENT_DESCRIPTION = "Finds case law, precedents, and legal citations to strengthen cases"

# Legal Research Configuration
LEGAL_DATABASE_URL = os.getenv("LEGAL_DATABASE_URL", "https://api.legal-database.com")
CASE_LAW_API_URL = os.getenv("CASE_LAW_API_URL", "https://api.case-law.com")
RESEARCH_TIMEOUT = int(os.getenv("RESEARCH_TIMEOUT", "60"))

# Research Sources
LEGAL_SOURCES = [
    "Supreme Court Cases",
    "Federal Court Cases", 
    "State Court Cases",
    "Legal Journals",
    "Law Reviews",
    "Legal Precedents"
]

# Citation Formats
CITATION_FORMATS = [
    "Bluebook",
    "ALWD",
    "APA",
    "MLA"
]

# Research Quality Thresholds
MIN_CITATION_COUNT = int(os.getenv("MIN_CITATION_COUNT", "3"))
MAX_RESEARCH_DEPTH = int(os.getenv("MAX_RESEARCH_DEPTH", "5"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENABLE_AUDIT_LOGGING = os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"
