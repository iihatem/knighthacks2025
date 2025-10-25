"""
Utility functions for Voice Scheduler Agent.
"""
import logging
import requests
from typing import Dict, Any, List
from datetime import datetime, timedelta

from .settings import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_BASE_URL,
    VOICE_MODEL,
    DEFAULT_VOICE_ID,
    VOICE_STABILITY,
    VOICE_SIMILARITY_BOOST,
    CALENDAR_API_URL,
    SCHEDULING_TIMEOUT,
    MAX_RETRY_ATTEMPTS,
    APPOINTMENT_TYPES,
    VOICE_PERSONAS,
    NOTIFICATION_EMAIL,
    NOTIFICATION_SLACK_WEBHOOK
)

logger = logging.getLogger(__name__)


def error_response(error_message: str, error_code: str = "GENERIC_ERROR") -> Dict[str, Any]:
    """Create a standardized error response."""
    return {
        "status": "error",
        "error_code": error_code,
        "message": error_message,
        "timestamp": datetime.now().isoformat()
    }


def success_response(data: Dict[str, Any], message: str = "Success") -> Dict[str, Any]:
    """Create a standardized success response."""
    return {
        "status": "success",
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }


def generate_voice_script(appointment_type: str, recipient_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a natural voice script for appointment scheduling.
    
    Args:
        appointment_type: Type of appointment to schedule
        recipient_type: Type of recipient (client, provider, expert, etc.)
        details: Appointment details
        
    Returns:
        Response dictionary with generated voice script
    """
    logger.info(f"Generating voice script for {appointment_type} with {recipient_type}")
    
    # Get appropriate voice persona
    persona = VOICE_PERSONAS.get("professional", VOICE_PERSONAS["professional"])
    if recipient_type == "client":
        persona = VOICE_PERSONAS.get("empathetic", VOICE_PERSONAS["professional"])
    elif recipient_type == "expert":
        persona = VOICE_PERSONAS.get("authoritative", VOICE_PERSONAS["professional"])
    
    # Generate script based on appointment type
    if appointment_type == "deposition":
        script = f"""
        Hello, this is calling from TenderPilot Legal regarding a deposition scheduling.
        We need to schedule a deposition for {details.get('case_name', 'your case')} 
        on {details.get('preferred_date', 'your preferred date')}.
        The deposition is expected to last approximately {details.get('duration', '2-3 hours')}.
        Please let us know your availability for the following dates: {details.get('available_dates', 'next week')}.
        Thank you for your time.
        """
    elif appointment_type == "mediation":
        script = f"""
        Good day, this is calling from TenderPilot Legal about mediation scheduling.
        We would like to schedule a mediation session for {details.get('case_name', 'your case')}.
        The mediation is scheduled for {details.get('preferred_date', 'your preferred date')}
        and will be held at {details.get('location', 'our office')}.
        Please confirm your availability and let us know if you need any special accommodations.
        Thank you.
        """
    else:
        script = f"""
        Hello, this is calling from TenderPilot Legal regarding {appointment_type} scheduling.
        We need to schedule a {appointment_type} for {details.get('case_name', 'your case')}
        on {details.get('preferred_date', 'your preferred date')}.
        Please let us know your availability.
        Thank you.
        """
    
    return success_response(
        {
            "script": script.strip(),
            "appointment_type": appointment_type,
            "recipient_type": recipient_type,
            "voice_persona": persona,
            "details": details,
            "generated_date": datetime.now().isoformat()
        },
        f"Voice script generated for {appointment_type}"
    )


def schedule_appointment_via_voice(recipient_name: str, phone_number: str, script: str, voice_persona: str) -> Dict[str, Any]:
    """
    Schedule an appointment via voice call using ElevenLabs.
    
    Args:
        recipient_name: Name of the recipient
        phone_number: Phone number to call
        script: Voice script to use
        voice_persona: Voice persona configuration
        
    Returns:
        Response dictionary with scheduling status
    """
    logger.info(f"Scheduling appointment via voice for {recipient_name}")
    
    # Prepare ElevenLabs API call
    url = f"{ELEVENLABS_BASE_URL}/text-to-speech/{voice_persona['voice_id']}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    payload = {
        "text": script,
        "model_id": VOICE_MODEL,
        "voice_settings": {
            "stability": VOICE_STABILITY,
            "similarity_boost": VOICE_SIMILARITY_BOOST
        }
    }
    
    try:
        # Generate voice audio
        response = requests.post(url, json=payload, headers=headers, timeout=SCHEDULING_TIMEOUT)
        response.raise_for_status()
        
        # In a real implementation, you would:
        # 1. Save the audio file
        # 2. Make the actual phone call
        # 3. Play the audio to the recipient
        # 4. Handle the conversation
        
        return success_response(
            {
                "recipient_name": recipient_name,
                "phone_number": phone_number,
                "script": script,
                "voice_persona": voice_persona,
                "call_status": "scheduled",
                "scheduled_date": datetime.now().isoformat()
            },
            f"Voice call scheduled for {recipient_name}"
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error scheduling voice call: {e}")
        return error_response(f"Failed to schedule voice call: {str(e)}", "VOICE_CALL_FAILED")


def coordinate_mediation_scheduling(parties: List[str], mediator: str, preferred_dates: List[str]) -> Dict[str, Any]:
    """
    Coordinate mediation scheduling with multiple parties.
    
    Args:
        parties: List of parties involved
        mediator: Mediator information
        preferred_dates: List of preferred dates
        
    Returns:
        Response dictionary with coordination status
    """
    logger.info(f"Coordinating mediation scheduling for {len(parties)} parties")
    
    coordination_data = {
        "parties": parties,
        "mediator": mediator,
        "preferred_dates": preferred_dates,
        "status": "coordinating",
        "coordination_date": datetime.now().isoformat()
    }
    
    # Generate scripts for each party
    scripts = []
    for party in parties:
        script = generate_voice_script(
            "mediation",
            "party",
            {
                "case_name": "Mediation Case",
                "preferred_date": preferred_dates[0] if preferred_dates else "TBD",
                "mediator": mediator
            }
        )
        scripts.append(script["data"])
    
    return success_response(
        {
            **coordination_data,
            "scripts": scripts,
            "next_steps": [
                "Contact all parties",
                "Confirm availability",
                "Schedule mediation session",
                "Send confirmation details"
            ]
        },
        f"Mediation coordination initiated for {len(parties)} parties"
    )


def handle_appointment_conflicts(existing_appointments: List[Dict[str, Any]], new_appointment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle appointment scheduling conflicts.
    
    Args:
        existing_appointments: List of existing appointments
        new_appointment: New appointment to schedule
        
    Returns:
        Response dictionary with conflict resolution
    """
    logger.info("Handling appointment scheduling conflicts")
    
    conflicts = []
    for appointment in existing_appointments:
        if appointment.get("date") == new_appointment.get("date"):
            conflicts.append(appointment)
    
    if not conflicts:
        return success_response(
            {
                "conflicts": [],
                "resolution": "no_conflicts",
                "new_appointment": new_appointment
            },
            "No scheduling conflicts found"
        )
    
    # Generate conflict resolution options
    resolution_options = [
        {
            "option": "reschedule_existing",
            "description": "Reschedule existing appointment",
            "impact": "low"
        },
        {
            "option": "reschedule_new",
            "description": "Reschedule new appointment",
            "impact": "medium"
        },
        {
            "option": "find_alternative_time",
            "description": "Find alternative time slot",
            "impact": "low"
        }
    ]
    
    return success_response(
        {
            "conflicts": conflicts,
            "resolution_options": resolution_options,
            "recommended_action": "find_alternative_time",
            "conflict_date": new_appointment.get("date")
        },
        f"Found {len(conflicts)} scheduling conflicts"
    )


def send_appointment_reminder(recipient_name: str, appointment_details: Dict[str, Any], reminder_type: str = "24_hour") -> Dict[str, Any]:
    """
    Send appointment reminder via voice call.
    
    Args:
        recipient_name: Name of the recipient
        appointment_details: Details of the appointment
        reminder_type: Type of reminder (24_hour, 1_hour, etc.)
        
    Returns:
        Response dictionary with reminder status
    """
    logger.info(f"Sending {reminder_type} reminder to {recipient_name}")
    
    # Generate reminder script
    reminder_script = f"""
    Hello {recipient_name}, this is a reminder about your upcoming appointment.
    Your {appointment_details.get('type', 'appointment')} is scheduled for 
    {appointment_details.get('date', 'the scheduled date')} at 
    {appointment_details.get('time', 'the scheduled time')}.
    Location: {appointment_details.get('location', 'as previously arranged')}.
    Please arrive 15 minutes early. If you need to reschedule, please contact us immediately.
    Thank you.
    """
    
    # Use empathetic voice for reminders
    voice_persona = VOICE_PERSONAS["empathetic"]
    
    return success_response(
        {
            "recipient_name": recipient_name,
            "appointment_details": appointment_details,
            "reminder_type": reminder_type,
            "reminder_script": reminder_script,
            "voice_persona": voice_persona,
            "sent_date": datetime.now().isoformat()
        },
        f"{reminder_type} reminder sent to {recipient_name}"
    )


def track_appointment_status(appointment_id: str) -> Dict[str, Any]:
    """
    Track the status of an appointment.
    
    Args:
        appointment_id: ID of the appointment to track
        
    Returns:
        Response dictionary with appointment status
    """
    logger.info(f"Tracking appointment status for {appointment_id}")
    
    # Mock appointment status tracking
    status_data = {
        "appointment_id": appointment_id,
        "status": "confirmed",
        "last_updated": datetime.now().isoformat(),
        "details": {
            "date": "2025-10-30",
            "time": "2:00 PM",
            "location": "Conference Room A",
            "participants": ["John Doe", "Jane Smith"],
            "type": "deposition"
        }
    }
    
    return success_response(
        status_data,
        f"Appointment {appointment_id} status retrieved"
    )
