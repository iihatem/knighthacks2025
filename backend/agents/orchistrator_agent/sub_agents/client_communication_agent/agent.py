"""
Client Communication Guru Agent - Empathetic client communications with email sending
"""
import os
import google.generativeai as genai
from services.session_manager import get_snowflake_conn
from services.email_sender import send_client_email, format_email_html


def client_communication_guru(case_context: str, task: str, case_id: str = None, session_id: str = None, send_email: bool = False):
    """
    Client Communication Guru - Draft empathetic, clear client communications
    Handles emails, letters, and updates with appropriate tone
    Can optionally send emails directly to clients via SMTP
    
    Args:
        case_context: Full case details and background
        task: Specific communication task (e.g., "Draft email updating client on settlement offer")
        case_id: Case identifier to fetch client details from Snowflake
        session_id: Optional session ID for tracking
        send_email: If True, actually send the email via SMTP (default: False, just draft)
    
    Returns:
        Dictionary with draft, metadata, approval requirement, and send status (if applicable)
    """
    
    # Fetch client details from Snowflake if case_id is provided
    client_name = "Valued Client"
    client_email = None
    
    if case_id:
        try:
            conn = get_snowflake_conn()
            cursor = conn.cursor()
            
            # Query to get client details
            cursor.execute("""
                SELECT MAX(client_name) as client_name,
                       MAX(client_email) as client_email
                FROM case_data
                WHERE case_id = %s
                GROUP BY case_id
            """, (case_id,))
            
            result = cursor.fetchone()
            if result:
                client_name = result[0] if result[0] else "Valued Client"
                client_email = result[1]
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not fetch client details from Snowflake: {e}")
            # Fall back to default values
    
    # Configure Gemini
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Extract first name for personalized greeting
    first_name = client_name.split()[0] if client_name != "Valued Client" else client_name
    
    prompt = f"""You are the Client Communication Handler for Morgan & Morgan law firm.

Client Name: {client_name}

Case Context:
{case_context}

Task: {task}

Draft a clear, empathetic email message for the client. Be professional yet warm.
Use plain English (no legal jargon). Show empathy. Be transparent about next steps.

CRITICAL FORMATTING RULES:
- Do NOT include "Subject:" in your response - the subject line is handled separately
- Start directly with the greeting: "Dear {first_name},"
- Do NOT include placeholder text like [Your Name], [Phone Number], [Email], etc.
- Sign off with:
  
  Sincerely,
  Client Communication Handler
  Morgan & Morgan

- Do NOT add any contact details, phone numbers, or email addresses
- Write ONLY the email body content (greeting to signature)
- Use professional paragraph breaks (double line breaks between paragraphs)

Example format:
Dear {first_name},

[First paragraph...]

[Second paragraph...]

Sincerely,
Client Communication Handler
Morgan & Morgan
"""

    response = model.generate_content(prompt)
    
    # Extract the draft from the response
    draft_text = response.text.strip()
    
    # Prepare return data
    result = {
        "draft": draft_text,
        "to": client_email if client_email else "client",
        "to_name": client_name,
        "subject": "Case Update",  # Could be enhanced to extract from task
        "requires_approval": True
    }
    
    # If send_email is True, prepare email for approval (but don't send yet!)
    if send_email:
        from services.email_sender import prepare_email_for_approval
        
        # Convert to HTML format
        html_body = format_email_html(draft_text)
        
        # Log email for approval (does NOT send)
        approval_result = prepare_email_for_approval(
            to_email=client_email,
            to_name=client_name,
            subject=result["subject"],
            body=html_body,
            case_id=case_id,
            session_id=session_id
        )
        
        # Add approval tracking to result
        result["email_sent"] = False  # Not sent yet - awaiting approval
        result["approval_status"] = "pending"
        result["activity_id"] = approval_result.get("activity_id")
        result["message"] = f"Email draft prepared. Awaiting approval (Activity ID: {approval_result.get('activity_id')})"
    
    return result
