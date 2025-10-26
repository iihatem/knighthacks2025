"""
Evidence Processor Service - Extracts and organizes evidence from emails and attachments
"""
import os
import json
import base64
from datetime import datetime
from typing import List, Dict
import mimetypes
from services.activity_logger import log_agent_activity


def process_evidence_from_email(
    case_id: str,
    email_subject: str,
    email_body: str,
    attachments: List[Dict],
    sender_email: str,
    sender_name: str = None,
    session_id: str = None
) -> dict:
    """
    Process evidence from an email and its attachments
    
    Args:
        case_id: Case identifier
        email_subject: Subject of the email
        email_body: Body content of the email
        attachments: List of attachment dicts with 'filename', 'content_type', 'data' (base64)
        sender_email: Email address of sender
        sender_name: Name of sender (optional)
        session_id: Session ID for tracking
    
    Returns:
        dict with processing results and evidence summary
    """
    
    try:
        # Analyze email content
        evidence_items = []
        
        # 1. Extract information from email body
        email_evidence = {
            'type': 'email',
            'subject': email_subject,
            'from': f"{sender_name} <{sender_email}>" if sender_name else sender_email,
            'body_preview': email_body[:500] + '...' if len(email_body) > 500 else email_body,
            'received_at': datetime.now().isoformat()
        }
        evidence_items.append(email_evidence)
        
        # 2. Process attachments
        attachment_summaries = []
        for attachment in attachments:
            filename = attachment.get('filename', 'unknown')
            content_type = attachment.get('content_type', 'application/octet-stream')
            
            # Categorize attachment
            category = categorize_evidence_file(filename, content_type)
            
            attachment_info = {
                'type': 'attachment',
                'filename': filename,
                'content_type': content_type,
                'category': category,
                'size_bytes': len(attachment.get('data', '')),
                'extracted_at': datetime.now().isoformat()
            }
            
            evidence_items.append(attachment_info)
            attachment_summaries.append(f"{filename} ({category})")
        
        # 3. Generate evidence summary
        summary = generate_evidence_summary(
            email_subject=email_subject,
            sender=sender_name or sender_email,
            num_attachments=len(attachments),
            attachment_summaries=attachment_summaries
        )
        
        # 4. Log the evidence processing activity
        activity_id = log_agent_activity(
            case_id=case_id,
            agent_type='EvidenceSorter',
            agent_action='process_email_evidence',
            prompt=f"Process evidence from email: {email_subject} (from {sender_email})",
            agent_response=json.dumps({
                'evidence_items': evidence_items,
                'summary': summary,
                'total_items': len(evidence_items)
            }),
            action_data=None,
            requires_approval=False,  # Evidence sorting doesn't need approval
            session_id=session_id
        )
        
        return {
            'status': 'success',
            'activity_id': activity_id,
            'evidence_items': evidence_items,
            'summary': summary,
            'total_items': len(evidence_items),
            'message': f'Processed {len(evidence_items)} evidence items from email'
        }
        
    except Exception as e:
        print(f"❌ Error processing evidence: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


def categorize_evidence_file(filename: str, content_type: str) -> str:
    """
    Categorize evidence file by type
    
    Args:
        filename: Name of the file
        content_type: MIME type
    
    Returns:
        str: Category name
    """
    
    # Image files
    if content_type.startswith('image/'):
        return 'Photo Evidence'
    
    # Video files
    if content_type.startswith('video/'):
        return 'Video Evidence'
    
    # Audio files
    if content_type.startswith('audio/'):
        return 'Audio Recording'
    
    # Documents
    if content_type in ['application/pdf', 'application/x-pdf']:
        return 'PDF Document'
    
    if content_type in [
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]:
        return 'Word Document'
    
    if content_type in [
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]:
        return 'Spreadsheet'
    
    # Text files
    if content_type.startswith('text/'):
        return 'Text Document'
    
    # Default
    return 'General Attachment'


def generate_evidence_summary(
    email_subject: str,
    sender: str,
    num_attachments: int,
    attachment_summaries: List[str]
) -> str:
    """
    Generate a human-readable summary of evidence
    
    Args:
        email_subject: Email subject line
        sender: Sender name/email
        num_attachments: Number of attachments
        attachment_summaries: List of attachment descriptions
    
    Returns:
        str: Summary text
    """
    
    summary_parts = [
        f"📧 Email Evidence Processed",
        f"From: {sender}",
        f"Subject: {email_subject}",
        f"Total Items: {num_attachments + 1} (1 email + {num_attachments} attachments)"
    ]
    
    if attachment_summaries:
        summary_parts.append("\nAttachments:")
        for i, att_summary in enumerate(attachment_summaries, 1):
            summary_parts.append(f"  {i}. {att_summary}")
    
    summary_parts.append(f"\n✅ All evidence extracted and ready for review")
    
    return '\n'.join(summary_parts)


def upload_evidence_to_salesforce(
    case_id: str,
    evidence_items: List[Dict],
    salesforce_conn = None
) -> dict:
    """
    Upload processed evidence to Salesforce (placeholder for now)
    
    Args:
        case_id: Case identifier
        evidence_items: List of evidence items to upload
        salesforce_conn: Salesforce connection (optional)
    
    Returns:
        dict with upload status
    """
    
    # TODO: Implement Salesforce upload
    # This would use the Salesforce API to:
    # 1. Create ContentVersion records for files
    # 2. Link them to the case
    # 3. Add proper tags and metadata
    
    return {
        'status': 'pending',
        'message': 'Salesforce upload not yet implemented',
        'items_ready': len(evidence_items)
    }
