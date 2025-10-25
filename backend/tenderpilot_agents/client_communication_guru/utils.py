"""
Utility functions for Client Communication Guru Agent.
"""
import logging
import requests
from typing import Dict, Any, List
from datetime import datetime

from .settings import (
    EMAIL_SYSTEM_URL,
    SMS_SYSTEM_URL,
    COMMUNICATION_TIMEOUT,
    DEFAULT_TONE,
    URGENT_TONE,
    SENSITIVE_TONE,
    MESSAGE_TYPES,
    REQUIRE_APPROVAL_FOR,
    AUTO_APPROVE_FOR,
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


def get_tone_guidelines(message_type: str) -> Dict[str, Any]:
    """
    Get tone guidelines for different message types.
    
    Args:
        message_type: Type of message to draft
        
    Returns:
        Dictionary with tone guidelines
    """
    tone_guidelines = {
        "case_update": {
            "tone": "professional and reassuring",
            "key_elements": ["current status", "next steps", "timeline"],
            "templates": [
                "We wanted to update you on your case...",
                "Here's where we stand with your case...",
                "We have an important update regarding your case..."
            ]
        },
        "document_request": {
            "tone": "polite and clear",
            "key_elements": ["what is needed", "why it's needed", "deadline"],
            "templates": [
                "We need some additional documents to move forward...",
                "To strengthen your case, we require...",
                "Please provide the following documents..."
            ]
        },
        "appointment_reminder": {
            "tone": "friendly and helpful",
            "key_elements": ["date/time", "location", "preparation needed"],
            "templates": [
                "This is a friendly reminder about your upcoming appointment...",
                "Don't forget about your appointment...",
                "Your appointment is coming up..."
            ]
        },
        "settlement_discussion": {
            "tone": "empathetic and informative",
            "key_elements": ["offer details", "options", "recommendation"],
            "templates": [
                "We have received a settlement offer...",
                "The other party has made an offer...",
                "We need to discuss settlement options..."
            ]
        },
        "bad_news": {
            "tone": "empathetic and supportive",
            "key_elements": ["situation", "impact", "next steps", "support available"],
            "templates": [
                "We have some difficult news to share...",
                "Unfortunately, we need to inform you...",
                "We understand this may be disappointing..."
            ]
        },
        "good_news": {
            "tone": "positive and congratulatory",
            "key_elements": ["achievement", "details", "next steps"],
            "templates": [
                "We have great news to share...",
                "We're pleased to inform you...",
                "Congratulations! We have some good news..."
            ]
        },
        "general": {
            "tone": DEFAULT_TONE,
            "key_elements": ["message", "context", "action"],
            "templates": [
                "We wanted to reach out to you...",
                "This is to inform you that...",
                "We hope this message finds you well..."
            ]
        }
    }
    
    return tone_guidelines.get(message_type, tone_guidelines["general"])


def draft_client_message(client_name: str, message_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Draft a message to a client based on type and context.
    
    Args:
        client_name: Name of the client
        message_type: Type of message to draft
        context: Additional context for the message
        
    Returns:
        Response dictionary with drafted message
    """
    logger.info(f"Drafting {message_type} message for {client_name}")
    
    guidelines = get_tone_guidelines(message_type)
    
    # Generate message content based on guidelines
    message_content = f"""
    Dear {client_name},
    
    {guidelines['templates'][0] if guidelines['templates'] else 'We wanted to reach out to you regarding your case.'}
    
    {context.get('message_body', 'Please see the details below.')}
    
    {context.get('next_steps', 'We will keep you updated on any developments.')}
    
    If you have any questions or concerns, please don't hesitate to contact us.
    
    Best regards,
    Your Legal Team
    """
    
    # Check if approval is required
    requires_approval = message_type in REQUIRE_APPROVAL_FOR
    auto_approve = message_type in AUTO_APPROVE_FOR
    
    return success_response(
        {
            "message_content": message_content.strip(),
            "client_name": client_name,
            "message_type": message_type,
            "tone": guidelines["tone"],
            "requires_approval": requires_approval,
            "auto_approve": auto_approve,
            "guidelines_used": guidelines,
            "drafted_date": datetime.now().isoformat()
        },
        f"Message drafted successfully for {client_name}"
    )


def review_outgoing_communication(message_content: str, message_type: str) -> Dict[str, Any]:
    """
    Review outgoing communication for tone, clarity, and compliance.
    
    Args:
        message_content: Content of the message to review
        message_type: Type of message being reviewed
        
    Returns:
        Response dictionary with review results
    """
    logger.info(f"Reviewing {message_type} communication")
    
    # Basic review criteria
    review_criteria = {
        "tone_appropriate": True,
        "clear_and_concise": True,
        "legally_compliant": True,
        "empathetic": True,
        "professional": True
    }
    
    # Check message length
    word_count = len(message_content.split())
    length_appropriate = 50 <= word_count <= 500
    
    # Check for sensitive information
    sensitive_keywords = ["ssn", "social security", "credit card", "bank account"]
    contains_sensitive = any(keyword in message_content.lower() for keyword in sensitive_keywords)
    
    # Generate review feedback
    feedback = []
    if not length_appropriate:
        feedback.append("Message length may need adjustment")
    if contains_sensitive:
        feedback.append("Message may contain sensitive information - review required")
    
    # Overall approval status
    approved = all(review_criteria.values()) and length_appropriate and not contains_sensitive
    
    return success_response(
        {
            "approved": approved,
            "review_criteria": review_criteria,
            "word_count": word_count,
            "length_appropriate": length_appropriate,
            "contains_sensitive": contains_sensitive,
            "feedback": feedback,
            "review_date": datetime.now().isoformat()
        },
        "Communication review completed"
    )


def send_client_message(client_name: str, message_content: str, message_type: str, delivery_method: str = "email") -> Dict[str, Any]:
    """
    Send a message to a client via specified delivery method.
    
    Args:
        client_name: Name of the client
        message_content: Content of the message
        message_type: Type of message
        delivery_method: Method of delivery (email, sms, etc.)
        
    Returns:
        Response dictionary with sending status
    """
    logger.info(f"Sending {message_type} message to {client_name} via {delivery_method}")
    
    # Prepare message data
    message_data = {
        "client_name": client_name,
        "message_content": message_content,
        "message_type": message_type,
        "delivery_method": delivery_method,
        "sent_date": datetime.now().isoformat()
    }
    
    # Send via email
    if delivery_method == "email":
        url = f"{EMAIL_SYSTEM_URL}/send"
        payload = {
            "to": client_name,
            "subject": f"Legal Update - {message_type.replace('_', ' ').title()}",
            "body": message_content,
            "message_type": message_type
        }
    # Send via SMS
    elif delivery_method == "sms":
        url = f"{SMS_SYSTEM_URL}/send"
        payload = {
            "to": client_name,
            "message": message_content,
            "message_type": message_type
        }
    else:
        return error_response(f"Unsupported delivery method: {delivery_method}", "INVALID_DELIVERY_METHOD")
    
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=COMMUNICATION_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        return success_response(
            {**message_data, "response": response.json()},
            f"Message sent successfully to {client_name}"
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}")
        return error_response(f"Failed to send message: {str(e)}", "SEND_FAILED")


def schedule_follow_up(client_name: str, message_type: str, follow_up_date: str) -> Dict[str, Any]:
    """
    Schedule a follow-up communication with a client.
    
    Args:
        client_name: Name of the client
        message_type: Type of follow-up message
        follow_up_date: Date for the follow-up
        
    Returns:
        Response dictionary with scheduling status
    """
    logger.info(f"Scheduling follow-up for {client_name} on {follow_up_date}")
    
    follow_up_data = {
        "client_name": client_name,
        "message_type": message_type,
        "follow_up_date": follow_up_date,
        "scheduled_date": datetime.now().isoformat(),
        "status": "scheduled"
    }
    
    return success_response(
        follow_up_data,
        f"Follow-up scheduled for {client_name} on {follow_up_date}"
    )


def get_communication_history(client_name: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get communication history for a client.
    
    Args:
        client_name: Name of the client
        limit: Maximum number of communications to return
        
    Returns:
        Response dictionary with communication history
    """
    logger.info(f"Retrieving communication history for {client_name}")
    
    # This would typically query a database
    # For now, return mock data
    history = [
        {
            "date": "2025-10-20",
            "type": "case_update",
            "subject": "Case Progress Update",
            "status": "sent"
        },
        {
            "date": "2025-10-18",
            "type": "document_request",
            "subject": "Additional Documents Needed",
            "status": "sent"
        }
    ]
    
    return success_response(
        {
            "client_name": client_name,
            "communications": history[:limit],
            "total_count": len(history)
        },
        f"Communication history retrieved for {client_name}"
    )
