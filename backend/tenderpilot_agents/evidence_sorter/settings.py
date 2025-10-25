"""
Settings for Evidence Sorter Agent.
"""
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Google API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

# Agent Configuration
AGENT_NAME = "evidence_sorter"
AGENT_MODEL = "gemini-2.0-flash"
AGENT_DESCRIPTION = "Organizes documents, evidence, and attachments for case management"

# Document Processing Configuration
DOCUMENT_API_URL = os.getenv("DOCUMENT_API_URL", "https://api.documents.com")
OCR_API_URL = os.getenv("OCR_API_URL", "https://api.ocr.com")
PROCESSING_TIMEOUT = int(os.getenv("PROCESSING_TIMEOUT", "60"))

# Document Categories
DOCUMENT_CATEGORIES = [
    "medical_records",
    "billing_statements",
    "police_reports",
    "expert_reports",
    "photographs",
    "correspondence",
    "legal_documents",
    "financial_records"
]

# Evidence Types
EVIDENCE_TYPES = [
    "physical_evidence",
    "documentary_evidence",
    "testimonial_evidence",
    "expert_evidence",
    "circumstantial_evidence"
]

# Organization Rules
ORGANIZATION_RULES = {
    "medical_records": {
        "folder": "Medical_Evidence",
        "subcategories": ["diagnosis", "treatment", "billing", "imaging"],
        "priority": "high"
    },
    "billing_statements": {
        "folder": "Financial_Evidence",
        "subcategories": ["medical_bills", "insurance", "lost_wages"],
        "priority": "high"
    },
    "police_reports": {
        "folder": "Incident_Evidence",
        "subcategories": ["accident_report", "witness_statements", "photos"],
        "priority": "critical"
    }
}

# Metadata Extraction
METADATA_FIELDS = [
    "document_type",
    "date_created",
    "author",
    "case_relevance",
    "confidentiality_level",
    "page_count",
    "file_size"
]

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENABLE_AUDIT_LOGGING = os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"
