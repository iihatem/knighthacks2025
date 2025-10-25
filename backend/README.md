# TenderPilot Backend

AI-powered legal tender orchestrator using Google ADK multi-agent system.

## Architecture

TenderPilot uses a multi-agent architecture based on Google's Agent Development Kit (ADK):

### Coordinator Agent

- **TenderCoordinator**: Main orchestrator that routes tasks to specialized agents

### Specialized Agents

1. **RecordsWrangler**: Handles medical records and billing requests
2. **ClientCommunicationGuru**: Drafts empathetic client communications
3. **LegalResearcher**: Finds case law and legal precedents
4. **VoiceScheduler**: Manages appointments via voice calls (ElevenLabs)
5. **EvidenceSorter**: Organizes documents and evidence

## Setup

### Prerequisites

- Python 3.10 or higher
- pip or uv for package management

### Installation

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

```bash
cp env.example .env
# Edit .env with your API keys
```

### Required API Keys

- `GOOGLE_API_KEY`: Google AI/Gemini API key
- `ELEVENLABS_API_KEY`: ElevenLabs API key (for voice features)
- `SNOWFLAKE_*`: Snowflake credentials (for data management)

## Usage

### Run the test application:

```bash
python main.py
```

### Process a task programmatically:

```python
from main import app

task = {
    "task_type": "medical_records",
    "content": "Request MRI records from Dr. Smith",
    "metadata": {
        "provider_name": "Dr. Smith Medical Center",
        "patient_name": "John Doe",
        "case_id": "CASE-2025-001"
    },
    "requires_approval": True
}

result = await app.process_task(task)
print(result)
```

## Task Types

### Medical Records

- `medical_records`: Request medical records
- `billing_request`: Request billing documents

### Client Communication

- `client_communication`: Draft client messages
- `client_message`: General client correspondence

### Legal Research

- `legal_research`: Find case law and precedents
- `case_law`: Search for specific legal citations

### Scheduling

- `schedule_appointment`: Schedule appointments
- `schedule_deposition`: Schedule depositions
- `schedule_mediation`: Schedule mediations

### Document Management

- `document_organization`: Organize case documents
- `evidence_upload`: Process evidence uploads
- `attachment_processing`: Handle email attachments

## Agent Capabilities

### RecordsWrangler

- Extracts provider and patient information
- Drafts professional request letters
- Generates action items and follow-ups
- Tracks fulfillment status

### ClientCommunicationGuru

- Drafts empathetic client messages
- Reviews tone and clarity
- Ensures professional formatting
- Adapts to message type (updates, requests, news)

### LegalResearcher

- Searches case law databases
- Finds relevant precedents
- Provides citations and holdings
- Suggests legal strategies

### VoiceScheduler

- Generates natural call scripts
- Adapts voice persona to recipient
- Coordinates appointments via phone
- Integrates with ElevenLabs for voice synthesis

### EvidenceSorter

- Categorizes documents automatically
- Generates folder structures
- Extracts file metadata
- Identifies OCR requirements

## Human-in-the-Loop Approval

Tasks marked with `requires_approval: True` will:

1. Generate proposed actions
2. Wait for human review
3. Execute only after approval
4. Log all decisions for audit trail

## Development

### Project Structure

```
backend/
├── agents/              # Agent implementations
│   ├── base_agent.py
│   ├── coordinator.py
│   ├── records_wrangler.py
│   ├── client_communication_guru.py
│   ├── legal_researcher.py
│   ├── voice_scheduler.py
│   └── evidence_sorter.py
├── config.py           # Configuration management
├── main.py             # Main application
└── requirements.txt    # Python dependencies
```

### Adding New Agents

1. Create a new agent class inheriting from `TenderPilotBaseAgent`
2. Implement the `process()` method
3. Register the agent in `main.py`
4. Add routing rules in `coordinator.py`

## Integration

### A2A Protocol

Agents can be exposed via A2A protocol for inter-agent communication.

### Snowflake Integration

Legal research and case data stored in Snowflake for RAG capabilities.

### ElevenLabs Integration

Voice scheduling uses ElevenLabs for natural voice synthesis.

## License

Copyright © 2025 TenderPilot Team
