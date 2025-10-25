"""
Voice Scheduler Agent.
Coordinates appointments using voice calls via ElevenLabs.
"""
from typing import Dict, Any
import logging
from .base_agent import TenderPilotBaseAgent

logger = logging.getLogger(__name__)


class VoiceSchedulerAgent(TenderPilotBaseAgent):
    """
    Specialized agent for scheduling via voice calls.
    Uses ElevenLabs for natural voice interactions.
    """
    
    def __init__(self):
        """Initialize the Voice Scheduler agent."""
        super().__init__(
            name="VoiceScheduler",
            description="Coordinates depositions, mediations, and appointments via voice calls"
        )
        self.voice_personas = self._initialize_voice_personas()
    
    def _initialize_voice_personas(self) -> Dict[str, Dict[str, str]]:
        """Initialize voice personas for different recipient types."""
        return {
            "client": {
                "voice_id": "empathetic_client_voice",
                "tone": "warm, empathetic, reassuring",
                "speaking_rate": "moderate",
                "description": "Friendly and supportive tone for client interactions"
            },
            "medical_provider": {
                "voice_id": "professional_provider_voice",
                "tone": "professional, courteous, efficient",
                "speaking_rate": "moderate",
                "description": "Professional tone for medical staff"
            },
            "legal_professional": {
                "voice_id": "formal_legal_voice",
                "tone": "formal, respectful, authoritative",
                "speaking_rate": "moderate",
                "description": "Formal tone for attorneys and court staff"
            }
        }
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process scheduling request.
        
        Args:
            context: Task context containing:
                - content: Scheduling request details
                - task_type: Type of appointment
                - metadata: Contact info, dates, etc.
                
        Returns:
            Result with call script and scheduling details
        """
        self.log_action("Processing scheduling request", {"task_type": context.get("task_type")})
        
        content = context.get("content", "")
        task_type = context.get("task_type", "")
        metadata = context.get("metadata", {})
        
        # Extract scheduling details
        scheduling_info = self._extract_scheduling_info(content, metadata)
        
        # Determine recipient type and voice persona
        recipient_type = self._determine_recipient_type(task_type, metadata)
        voice_persona = self.voice_personas[recipient_type]
        
        # Generate call script
        call_script = self._generate_call_script(scheduling_info, recipient_type)
        
        # Prepare voice call parameters
        voice_call_params = self._prepare_voice_call(call_script, voice_persona, scheduling_info)
        
        return {
            "status": "success",
            "agent": self.name,
            "scheduling_info": scheduling_info,
            "recipient_type": recipient_type,
            "voice_persona": voice_persona,
            "call_script": call_script,
            "voice_call_params": voice_call_params,
            "requires_approval": True,
            "approval_type": "voice_call",
            "confidence": 0.9
        }
    
    def _extract_scheduling_info(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract scheduling information from request."""
        return {
            "appointment_type": self._identify_appointment_type(content),
            "recipient_name": metadata.get("recipient_name", ""),
            "recipient_phone": metadata.get("recipient_phone", ""),
            "proposed_dates": metadata.get("proposed_dates", []),
            "duration": metadata.get("duration", "30 minutes"),
            "location": metadata.get("location", ""),
            "case_id": metadata.get("case_id", ""),
            "urgency": metadata.get("urgency", "normal"),
            "special_instructions": content
        }
    
    def _identify_appointment_type(self, content: str) -> str:
        """Identify the type of appointment to schedule."""
        content_lower = content.lower()
        
        if "deposition" in content_lower:
            return "deposition"
        elif "mediation" in content_lower:
            return "mediation"
        elif "medical" in content_lower or "doctor" in content_lower:
            return "medical_appointment"
        elif "client" in content_lower and "meeting" in content_lower:
            return "client_meeting"
        else:
            return "general_appointment"
    
    def _determine_recipient_type(self, task_type: str, metadata: Dict[str, Any]) -> str:
        """Determine the type of recipient for voice persona selection."""
        recipient_role = metadata.get("recipient_role", "").lower()
        
        if "client" in recipient_role or "client" in task_type.lower():
            return "client"
        elif any(word in recipient_role for word in ["doctor", "medical", "provider", "hospital"]):
            return "medical_provider"
        elif any(word in recipient_role for word in ["attorney", "lawyer", "court", "legal"]):
            return "legal_professional"
        else:
            return "client"  # Default to client voice
    
    def _generate_call_script(self, info: Dict[str, Any], recipient_type: str) -> str:
        """
        Generate a natural call script for the voice bot.
        
        Args:
            info: Scheduling information
            recipient_type: Type of recipient
            
        Returns:
            Call script text
        """
        recipient_name = info["recipient_name"] or "there"
        appointment_type = info["appointment_type"].replace("_", " ").title()
        
        if recipient_type == "client":
            script = f"""
Hello {recipient_name}, this is calling from Morgan & Morgan law firm.

I hope I'm reaching you at a good time. I'm calling to schedule your {appointment_type} for your case.

We have a few time slots available. Would any of these work for you?

[Present proposed dates]

This appointment should take approximately {info['duration']}.

Which time works best for your schedule?

[Wait for response and confirm]

Great! I've scheduled you for [confirmed time]. You'll receive a confirmation text and email shortly.

Is there anything else I can help you with today?

Thank you, and we look forward to seeing you then!
            """.strip()
        
        elif recipient_type == "medical_provider":
            script = f"""
Hello, this is calling from Morgan & Morgan law firm.

I'm reaching out to schedule a {appointment_type} for our client regarding case number {info['case_id']}.

We're hoping to schedule this for approximately {info['duration']}.

Do you have availability on any of the following dates?

[Present proposed dates]

[Wait for response]

Excellent. I'll confirm that appointment for [confirmed time] at {info['location'] or 'your office'}.

We'll send a formal confirmation via email. Is there any additional information you need from us?

Thank you for your time and cooperation.
            """.strip()
        
        else:  # legal_professional
            script = f"""
Good [morning/afternoon], this is calling from Morgan & Morgan.

I'm contacting you to coordinate a {appointment_type} for case number {info['case_id']}.

We're proposing the following dates for your consideration:

[Present proposed dates]

The anticipated duration is {info['duration']}.

Would any of these dates work with your schedule?

[Wait for response]

Perfect. I'll confirm [confirmed time] at {info['location'] or 'the agreed location'}.

A formal notice will follow via email. Please let me know if you need any additional information.

Thank you for your time.
            """.strip()
        
        return script
    
    def _prepare_voice_call(
        self, 
        script: str, 
        voice_persona: Dict[str, str], 
        info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare parameters for ElevenLabs voice call.
        
        Args:
            script: Call script
            voice_persona: Voice persona configuration
            info: Scheduling information
            
        Returns:
            Voice call parameters
        """
        return {
            "script": script,
            "voice_id": voice_persona["voice_id"],
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.5,
                "use_speaker_boost": True
            },
            "recipient_phone": info["recipient_phone"],
            "max_duration_seconds": 300,  # 5 minutes max
            "enable_transcription": True,
            "callback_url": "/api/voice-call/callback",
            "metadata": {
                "case_id": info["case_id"],
                "appointment_type": info["appointment_type"],
                "recipient_name": info["recipient_name"]
            }
        }

