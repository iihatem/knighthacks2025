"""
Records Wrangler Agent.
Handles medical records and billing requests.
"""
from typing import Dict, Any
import logging
from .base_agent import TenderPilotBaseAgent

logger = logging.getLogger(__name__)


class RecordsWranglerAgent(TenderPilotBaseAgent):
    """
    Specialized agent for handling medical records and billing requests.
    Extracts missing records, drafts provider requests, and tracks fulfillment.
    """
    
    def __init__(self):
        """Initialize the Records Wrangler agent."""
        super().__init__(
            name="RecordsWrangler",
            description="Handles medical records retrieval and billing requests from providers"
        )
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process medical records or billing request.
        
        Args:
            context: Task context containing:
                - content: Request description
                - task_type: Type of records request
                - metadata: Additional information (provider, dates, etc.)
                
        Returns:
            Result with drafted request and action items
        """
        self.log_action("Processing records request", {"task_type": context.get("task_type")})
        
        content = context.get("content", "")
        task_type = context.get("task_type", "")
        metadata = context.get("metadata", {})
        
        # Extract key information
        extracted_info = self._extract_request_info(content, metadata)
        
        # Draft request letter
        request_draft = self._draft_request_letter(extracted_info, task_type)
        
        # Generate action items
        action_items = self._generate_action_items(extracted_info)
        
        return {
            "status": "success",
            "agent": self.name,
            "extracted_info": extracted_info,
            "request_draft": request_draft,
            "action_items": action_items,
            "requires_approval": True,
            "approval_type": "records_request",
            "confidence": self._calculate_confidence(extracted_info)
        }
    
    def _extract_request_info(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant information from the request.
        
        Args:
            content: Request content
            metadata: Additional metadata
            
        Returns:
            Dictionary with extracted information
        """
        # In production, this would use NLP/LLM to extract entities
        # For now, we'll use a simplified extraction
        
        info = {
            "provider_name": metadata.get("provider_name", "Unknown Provider"),
            "patient_name": metadata.get("patient_name", ""),
            "case_id": metadata.get("case_id", ""),
            "record_type": self._identify_record_type(content),
            "date_range": metadata.get("date_range", ""),
            "urgency": self._assess_urgency(content),
            "contact_info": metadata.get("provider_contact", {})
        }
        
        return info
    
    def _identify_record_type(self, content: str) -> str:
        """Identify the type of records being requested."""
        content_lower = content.lower()
        
        if "mri" in content_lower or "imaging" in content_lower:
            return "imaging_records"
        elif "billing" in content_lower or "invoice" in content_lower:
            return "billing_records"
        elif "treatment" in content_lower or "medical" in content_lower:
            return "medical_records"
        elif "prescription" in content_lower:
            return "prescription_records"
        else:
            return "general_records"
    
    def _assess_urgency(self, content: str) -> str:
        """Assess the urgency of the request."""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["urgent", "asap", "immediate", "deadline"]):
            return "high"
        elif any(word in content_lower for word in ["soon", "timely"]):
            return "medium"
        else:
            return "normal"
    
    def _draft_request_letter(self, info: Dict[str, Any], task_type: str) -> str:
        """
        Draft a professional records request letter.
        
        Args:
            info: Extracted information
            task_type: Type of request
            
        Returns:
            Drafted letter text
        """
        # Template-based letter generation
        # In production, this would use an LLM for more sophisticated drafting
        
        letter = f"""
Dear {info['provider_name']},

RE: Medical Records Request - {info['patient_name']} (Case ID: {info['case_id']})

We are writing to request {info['record_type'].replace('_', ' ')} for our client, {info['patient_name']}.

Requested Records:
- Type: {info['record_type'].replace('_', ' ').title()}
- Date Range: {info['date_range'] or 'All available records'}
- Urgency: {info['urgency'].upper()}

Please provide these records at your earliest convenience. We have enclosed the necessary authorization forms.

If you have any questions, please contact our office.

Thank you for your prompt attention to this matter.

Sincerely,
Morgan & Morgan Legal Team
        """.strip()
        
        return letter
    
    def _generate_action_items(self, info: Dict[str, Any]) -> list:
        """
        Generate action items for the request.
        
        Args:
            info: Extracted information
            
        Returns:
            List of action items
        """
        actions = [
            {
                "action": "send_request_letter",
                "description": f"Send records request to {info['provider_name']}",
                "priority": info['urgency'],
                "requires_approval": True
            },
            {
                "action": "track_fulfillment",
                "description": "Set up tracking for records receipt",
                "priority": "normal",
                "requires_approval": False
            }
        ]
        
        if info['urgency'] == 'high':
            actions.append({
                "action": "follow_up_call",
                "description": f"Schedule follow-up call with {info['provider_name']}",
                "priority": "high",
                "requires_approval": True
            })
        
        return actions
    
    def _calculate_confidence(self, info: Dict[str, Any]) -> float:
        """
        Calculate confidence score for the extraction.
        
        Args:
            info: Extracted information
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Simple confidence calculation based on available information
        score = 0.0
        total_fields = 7
        
        if info.get("provider_name") and info["provider_name"] != "Unknown Provider":
            score += 1
        if info.get("patient_name"):
            score += 1
        if info.get("case_id"):
            score += 1
        if info.get("record_type"):
            score += 1
        if info.get("date_range"):
            score += 1
        if info.get("urgency"):
            score += 1
        if info.get("contact_info"):
            score += 1
        
        return round(score / total_fields, 2)

