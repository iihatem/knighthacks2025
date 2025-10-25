"""
Client Communication Guru Agent.
Drafts clear, empathetic messages to clients.
"""
from typing import Dict, Any
import logging
from .base_agent import TenderPilotBaseAgent

logger = logging.getLogger(__name__)


class ClientCommunicationGuruAgent(TenderPilotBaseAgent):
    """
    Specialized agent for client communications.
    Drafts empathetic, clear messages and acts as gatekeeper before messages go out.
    """
    
    def __init__(self):
        """Initialize the Client Communication Guru agent."""
        super().__init__(
            name="ClientCommunicationGuru",
            description="Drafts clear, empathetic messages to clients and reviews outgoing communications"
        )
        self.tone_guidelines = self._initialize_tone_guidelines()
    
    def _initialize_tone_guidelines(self) -> Dict[str, Dict[str, Any]]:
        """Initialize tone guidelines for different message types."""
        return {
            "case_update": {
                "tone": "professional and reassuring",
                "key_elements": ["current status", "next steps", "timeline"]
            },
            "document_request": {
                "tone": "polite and clear",
                "key_elements": ["what is needed", "why it's needed", "deadline"]
            },
            "appointment_reminder": {
                "tone": "friendly and helpful",
                "key_elements": ["date/time", "location", "preparation needed"]
            },
            "settlement_discussion": {
                "tone": "empathetic and informative",
                "key_elements": ["offer details", "options", "recommendation"]
            },
            "bad_news": {
                "tone": "empathetic and supportive",
                "key_elements": ["situation", "impact", "next steps", "support available"]
            },
            "good_news": {
                "tone": "positive and congratulatory",
                "key_elements": ["achievement", "details", "next steps"]
            },
            "general": {
                "tone": "professional and friendly",
                "key_elements": ["message", "context", "action"]
            }
        }
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process client communication request.
        
        Args:
            context: Task context containing:
                - content: Message context or request
                - task_type: Type of communication
                - metadata: Client info, case details, etc.
                
        Returns:
            Result with drafted message and review notes
        """
        self.log_action("Processing client communication", {"task_type": context.get("task_type")})
        
        content = context.get("content", "")
        task_type = context.get("task_type", "client_communication")
        metadata = context.get("metadata", {})
        
        # Determine message type
        message_type = self._determine_message_type(content, task_type)
        
        # Extract key information
        message_context = self._extract_message_context(content, metadata)
        
        # Draft message
        drafted_message = self._draft_message(message_type, message_context)
        
        # Review message for quality
        review_results = self._review_message(drafted_message, message_type)
        
        return {
            "status": "success",
            "agent": self.name,
            "message_type": message_type,
            "drafted_message": drafted_message,
            "review_results": review_results,
            "requires_approval": True,
            "approval_type": "client_communication",
            "confidence": review_results["quality_score"]
        }
    
    def _determine_message_type(self, content: str, task_type: str) -> str:
        """Determine the type of message to draft."""
        content_lower = content.lower()
        
        if "update" in content_lower or "status" in content_lower:
            return "case_update"
        elif "document" in content_lower or "need" in content_lower:
            return "document_request"
        elif "appointment" in content_lower or "schedule" in content_lower:
            return "appointment_reminder"
        elif "settlement" in content_lower or "offer" in content_lower:
            return "settlement_discussion"
        elif any(word in content_lower for word in ["denied", "rejected", "unfortunately"]):
            return "bad_news"
        elif any(word in content_lower for word in ["approved", "won", "success", "settlement"]):
            return "good_news"
        else:
            return "general"
    
    def _extract_message_context(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context information for message drafting."""
        return {
            "client_name": metadata.get("client_name", "Valued Client"),
            "case_id": metadata.get("case_id", ""),
            "case_type": metadata.get("case_type", ""),
            "specific_details": content,
            "attorney_name": metadata.get("attorney_name", "Your Legal Team"),
            "urgency": metadata.get("urgency", "normal")
        }
    
    def _draft_message(self, message_type: str, context: Dict[str, Any]) -> str:
        """
        Draft an empathetic, clear message.
        
        Args:
            message_type: Type of message
            context: Message context
            
        Returns:
            Drafted message text
        """
        client_name = context["client_name"]
        attorney_name = context["attorney_name"]
        
        # Get tone guidelines
        guidelines = self.tone_guidelines.get(message_type, self.tone_guidelines["general"])
        
        # Template-based message generation
        # In production, this would use an LLM for more sophisticated drafting
        
        if message_type == "case_update":
            message = f"""
Dear {client_name},

I hope this message finds you well. I wanted to provide you with an update on your case.

{context['specific_details']}

We are committed to fighting for the best possible outcome for you. If you have any questions or concerns, please don't hesitate to reach out.

Best regards,
{attorney_name}
Morgan & Morgan - For The People
            """.strip()
        
        elif message_type == "document_request":
            message = f"""
Dear {client_name},

Thank you for your continued cooperation with your case.

To move forward, we need the following from you:

{context['specific_details']}

These documents will help us build the strongest case possible. Please send them at your earliest convenience.

If you have any questions about what we need or why, please feel free to call our office.

Thank you,
{attorney_name}
Morgan & Morgan
            """.strip()
        
        elif message_type == "appointment_reminder":
            message = f"""
Dear {client_name},

This is a friendly reminder about your upcoming appointment:

{context['specific_details']}

Please let us know if you need to reschedule or have any questions.

Looking forward to seeing you,
{attorney_name}
Morgan & Morgan
            """.strip()
        
        elif message_type == "bad_news":
            message = f"""
Dear {client_name},

I want to personally reach out to you regarding an important update on your case.

{context['specific_details']}

I understand this may not be the news you were hoping for. Please know that we remain committed to exploring every available option and fighting for your rights.

I would like to schedule a call to discuss this further and answer any questions you may have.

You are not alone in this,
{attorney_name}
Morgan & Morgan - For The People
            """.strip()
        
        elif message_type == "good_news":
            message = f"""
Dear {client_name},

I am pleased to share some excellent news about your case!

{context['specific_details']}

This is a significant step forward, and I'm proud of what we've accomplished together.

Please call our office to discuss the next steps.

Congratulations,
{attorney_name}
Morgan & Morgan - For The People
            """.strip()
        
        else:
            message = f"""
Dear {client_name},

{context['specific_details']}

If you have any questions, please don't hesitate to contact our office.

Best regards,
{attorney_name}
Morgan & Morgan
            """.strip()
        
        return message
    
    def _review_message(self, message: str, message_type: str) -> Dict[str, Any]:
        """
        Review drafted message for quality and appropriateness.
        
        Args:
            message: Drafted message
            message_type: Type of message
            
        Returns:
            Review results with quality score and suggestions
        """
        review = {
            "quality_score": 0.0,
            "checks_passed": [],
            "checks_failed": [],
            "suggestions": []
        }
        
        # Check message length (not too short, not too long)
        if 100 < len(message) < 1000:
            review["checks_passed"].append("appropriate_length")
            review["quality_score"] += 0.2
        else:
            review["checks_failed"].append("length_issue")
            review["suggestions"].append("Consider adjusting message length")
        
        # Check for empathetic language
        empathy_words = ["understand", "committed", "help", "support", "together"]
        if any(word in message.lower() for word in empathy_words):
            review["checks_passed"].append("empathetic_tone")
            review["quality_score"] += 0.2
        else:
            review["suggestions"].append("Consider adding more empathetic language")
        
        # Check for clear call-to-action or next steps
        action_words = ["please", "next", "contact", "call", "send", "schedule"]
        if any(word in message.lower() for word in action_words):
            review["checks_passed"].append("clear_action")
            review["quality_score"] += 0.2
        else:
            review["suggestions"].append("Consider adding clear next steps")
        
        # Check for professional greeting and closing
        if message.startswith("Dear") and any(closing in message for closing in ["Best regards", "Sincerely", "Thank you"]):
            review["checks_passed"].append("professional_format")
            review["quality_score"] += 0.2
        else:
            review["suggestions"].append("Ensure professional greeting and closing")
        
        # Check for legal jargon (should be minimal)
        jargon_words = ["pursuant", "heretofore", "aforementioned", "whereas"]
        if not any(word in message.lower() for word in jargon_words):
            review["checks_passed"].append("accessible_language")
            review["quality_score"] += 0.2
        else:
            review["checks_failed"].append("excessive_jargon")
            review["suggestions"].append("Simplify legal language for client understanding")
        
        return review

