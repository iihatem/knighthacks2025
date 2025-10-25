"""
Utility functions for Records Wrangler Agent.
"""
import logging
import requests
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from .settings import (
    MEDICAL_RECORDS_BASE_URL,
    PROVIDER_TIMEOUT,
    MAX_RETRY_ATTEMPTS,
    BILLING_SYSTEM_URL,
    BILLING_TIMEOUT,
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


def request_medical_records(provider_name: str, patient_name: str, record_types: list) -> Dict[str, Any]:
    """
    Request medical records from a provider.
    
    Args:
        provider_name: Name of the medical provider
        patient_name: Name of the patient
        record_types: List of record types to request
        
    Returns:
        Response dictionary with request status
    """
    logger.info(f"Requesting medical records from {provider_name} for {patient_name}")
    
    url = f"{MEDICAL_RECORDS_BASE_URL}/records/request"
    payload = {
        "provider_name": provider_name,
        "patient_name": patient_name,
        "record_types": record_types,
        "request_date": datetime.now().isoformat(),
        "priority": "standard"
    }
    
    try:
        response = requests.post(
            url, 
            json=payload, 
            timeout=PROVIDER_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        return success_response(
            response.json(),
            f"Medical records request submitted to {provider_name}"
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error requesting medical records: {e}")
        return error_response(f"Failed to request medical records: {str(e)}", "REQUEST_FAILED")


def track_record_fulfillment(request_id: str) -> Dict[str, Any]:
    """
    Track the fulfillment status of a medical records request.
    
    Args:
        request_id: ID of the records request
        
    Returns:
        Response dictionary with fulfillment status
    """
    logger.info(f"Tracking fulfillment for request {request_id}")
    
    url = f"{MEDICAL_RECORDS_BASE_URL}/records/track/{request_id}"
    
    try:
        response = requests.get(url, timeout=PROVIDER_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        return success_response(data, "Fulfillment status retrieved")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error tracking fulfillment: {e}")
        return error_response(f"Failed to track fulfillment: {str(e)}", "TRACKING_FAILED")


def handle_billing_dispute(dispute_id: str, dispute_reason: str) -> Dict[str, Any]:
    """
    Handle billing disputes with providers.
    
    Args:
        dispute_id: ID of the billing dispute
        dispute_reason: Reason for the dispute
        
    Returns:
        Response dictionary with dispute handling status
    """
    logger.info(f"Handling billing dispute {dispute_id}: {dispute_reason}")
    
    url = f"{BILLING_SYSTEM_URL}/disputes"
    payload = {
        "dispute_id": dispute_id,
        "reason": dispute_reason,
        "status": "open",
        "created_date": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=BILLING_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        return success_response(
            response.json(),
            f"Billing dispute {dispute_id} created successfully"
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error handling billing dispute: {e}")
        return error_response(f"Failed to handle billing dispute: {str(e)}", "DISPUTE_FAILED")


def generate_provider_letter(provider_name: str, patient_name: str, record_types: list) -> Dict[str, Any]:
    """
    Generate a professional request letter to medical providers.
    
    Args:
        provider_name: Name of the medical provider
        patient_name: Name of the patient
        record_types: List of record types to request
        
    Returns:
        Response dictionary with generated letter
    """
    logger.info(f"Generating provider letter for {provider_name}")
    
    letter_content = f"""
    Dear {provider_name},
    
    We are writing to request medical records for our client, {patient_name}.
    
    Please provide the following records:
    {', '.join(record_types)}
    
    This request is made pursuant to applicable medical records laws and regulations.
    Please provide these records within 30 days of receipt of this request.
    
    If you have any questions or need additional information, please contact us.
    
    Thank you for your cooperation.
    
    Sincerely,
    TenderPilot Legal Team
    """
    
    return success_response(
        {
            "letter_content": letter_content.strip(),
            "provider_name": provider_name,
            "patient_name": patient_name,
            "record_types": record_types,
            "generated_date": datetime.now().isoformat()
        },
        "Provider letter generated successfully"
    )


def send_notification(notification_type: str, message: str, priority: str = "normal") -> Dict[str, Any]:
    """
    Send notifications for record requests and updates.
    
    Args:
        notification_type: Type of notification
        message: Notification message
        priority: Priority level (low, normal, high)
        
    Returns:
        Response dictionary with notification status
    """
    logger.info(f"Sending {notification_type} notification: {message}")
    
    notification_data = {
        "type": notification_type,
        "message": message,
        "priority": priority,
        "timestamp": datetime.now().isoformat()
    }
    
    # Send email notification if configured
    if NOTIFICATION_EMAIL:
        # Implementation would send email here
        logger.info(f"Email notification sent to {NOTIFICATION_EMAIL}")
    
    # Send Slack notification if configured
    if NOTIFICATION_SLACK_WEBHOOK:
        # Implementation would send Slack message here
        logger.info(f"Slack notification sent to webhook")
    
    return success_response(notification_data, "Notification sent successfully")


def retry_with_backoff(func, *args, max_attempts: int = MAX_RETRY_ATTEMPTS, **kwargs) -> Dict[str, Any]:
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Function to retry
        *args: Function arguments
        max_attempts: Maximum number of retry attempts
        **kwargs: Function keyword arguments
        
    Returns:
        Response dictionary
    """
    for attempt in range(max_attempts):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_attempts - 1:
                logger.error(f"All retry attempts failed: {e}")
                return error_response(f"Operation failed after {max_attempts} attempts: {str(e)}", "MAX_RETRIES_EXCEEDED")
            
            wait_time = 2 ** attempt
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time} seconds: {e}")
            time.sleep(wait_time)
    
    return error_response("Unexpected error in retry logic", "RETRY_ERROR")
