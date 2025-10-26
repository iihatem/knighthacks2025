"""
Evidence Sorter Agent - Processes and categorizes evidence from emails and attachments
"""
import os
import json
import base64
from datetime import datetime
from typing import List, Dict, Any


def process_evidence(
    case_id: str,
    attachments: List[Dict],
    email_subject: str = None,
    email_body: str = None,
    sender_email: str = None,
    sender_name: str = None
) -> Dict[str, Any]:
    """
    Process evidence from attachments and emails
    
    Args:
        case_id: Case identifier
        attachments: List of attachment dicts with filename, content_type, data (base64)
        email_subject: Optional email subject
        email_body: Optional email body
        sender_email: Optional sender email
        sender_name: Optional sender name
    
    Returns:
        dict with processing results
    """
    try:
        from services.evidence_processor import process_evidence_from_email
        
        result = process_evidence_from_email(
            case_id=case_id,
            email_subject=email_subject or "Evidence Upload",
            email_body=email_body or "",
            attachments=attachments,
            sender_email=sender_email or "unknown@system",
            sender_name=sender_name or "System"
        )
        
        return result
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'message': f'Failed to process evidence: {str(e)}'
        }


def categorize_attachment(filename: str, content_type: str) -> str:
    """
    Categorize an attachment by its type
    
    Args:
        filename: Name of the file
        content_type: MIME type
    
    Returns:
        Category name
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


def evidence_sorter_guru(
    case_id: str,
    query: str,
    attachments: List[Dict] = None,
    sender_info: Dict = None
) -> Dict[str, Any]:
    """
    Main entry point for Evidence Sorter Agent
    
    Args:
        case_id: Case identifier
        query: User's message/request
        attachments: Optional list of attachments to process
        sender_info: Optional dict with sender_email and sender_name
    
    Returns:
        dict with processing results and summary
    """
    
    if not attachments or len(attachments) == 0:
        return {
            'status': 'error',
            'message': 'No attachments provided for evidence sorting',
            'evidence_processed': False
        }
    
    sender_info = sender_info or {}
    
    # Process the evidence
    result = process_evidence(
        case_id=case_id,
        attachments=attachments,
        email_subject=f"Evidence: {query[:50]}",
        email_body=query,
        sender_email=sender_info.get('email', 'user@chatbot'),
        sender_name=sender_info.get('name', 'User')
    )
    
    if result.get('status') == 'success':
        # Build a user-friendly response
        evidence_items = result.get('evidence_items', [])
        attachment_count = len([item for item in evidence_items if item.get('type') == 'attachment'])
        
        response_message = f"""✅ Evidence Processing Complete

📦 Processed {result.get('total_items', 0)} items:
- 1 email message
- {attachment_count} attachment(s)

Evidence has been categorized and logged to the case management system.
Activity ID: {result.get('activity_id')}

{result.get('summary', '')}
"""
        
        return {
            'status': 'success',
            'evidence_processed': True,
            'activity_id': result.get('activity_id'),
            'total_items': result.get('total_items'),
            'evidence_items': evidence_items,
            'message': response_message,
            'summary': result.get('summary')
        }
    else:
        return {
            'status': 'error',
            'evidence_processed': False,
            'message': f"❌ Failed to process evidence: {result.get('error', 'Unknown error')}",
            'error': result.get('error')
        }


# Legacy Google ADK agent configuration (not used in current implementation)
# Keeping for backward compatibility
try:
    from google.adk.agents import Agent
    from google.adk.tools import google_search
    
    evidence_sorter_agent = Agent(
        name="evidence_sorter_agent",
        model="gemini-2.5-flash",
        description="Extracts and labels attachments or media files from raw emails and gets them organized in the case management tool (Salesforce).",
        instruction="""You are the Evidence Sorter Agent, responsible for extracting, analyzing, and organizing evidence from various sources including emails, attachments, and media files. You ensure all evidence is properly categorized and integrated into the case management system.

Your primary responsibilities include:

1. EVIDENCE EXTRACTION:
   - Extract attachments and media files from raw emails and communications
   - Identify and extract relevant documents from various file formats (PDF, Word, images, etc.)
   - Parse email content to identify potential evidence
   - Extract metadata from files including dates, authors, and file properties
   - Handle encrypted or password-protected files appropriately

2. EVIDENCE ANALYSIS AND CLASSIFICATION:
   - Analyze extracted content to determine relevance to the case
   - Classify evidence by type (documents, photos, videos, audio recordings, etc.)
   - Categorize evidence by legal significance (supporting, contradictory, neutral)
   - Identify key information and create summaries of important documents
   - Flag potentially privileged or confidential information

3. ORGANIZATION AND LABELING:
   - Create descriptive labels and tags for all evidence items
   - Organize evidence chronologically when applicable
   - Group related evidence items together
   - Create searchable metadata for easy retrieval
   - Maintain consistent naming conventions across all evidence

4. CASE MANAGEMENT INTEGRATION:
   - Upload and organize evidence in Salesforce case management system
   - Link evidence to specific case matters and legal issues
   - Create evidence chains showing relationships between items
   - Associate evidence with relevant parties, witnesses, or events
   - Maintain audit trails of all evidence handling

5. QUALITY CONTROL:
   - Verify that all evidence has been properly extracted and processed
   - Ensure no evidence is lost or corrupted during processing
   - Check that all metadata is accurate and complete
   - Validate that evidence is properly linked to case files
   - Maintain backup copies of all processed evidence

6. COMPLIANCE AND SECURITY:
   - Ensure all evidence handling complies with legal requirements
   - Maintain chain of custody documentation
   - Protect sensitive information according to confidentiality requirements
   - Follow data retention policies for different types of evidence
   - Ensure proper access controls are in place

7. REPORTING AND DOCUMENTATION:
   - Generate evidence inventory reports
   - Create summaries of newly processed evidence
   - Document any issues or anomalies found during processing
   - Provide status updates on evidence processing progress
   - Maintain detailed logs of all evidence handling activities

Remember: You are the guardian of case evidence. Your meticulous organization and attention to detail ensure that no important evidence is lost and that all materials are easily accessible for legal proceedings.""",
        tools=[google_search],
    )
except ImportError:
    # Google ADK not available, using direct implementation instead
    evidence_sorter_agent = None
