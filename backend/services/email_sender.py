"""
Email Sender Service - SMTP-based email sending for client communications
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from services.activity_logger import log_agent_activity


def prepare_email_for_approval(to_email: str, to_name: str, subject: str, body: str, case_id: str, session_id: str = None) -> dict:
    """
    Prepare email for approval (log to database but DON'T send)
    
    Args:
        to_email: Client's email address (not used - fetched from DB on approval)
        to_name: Client's full name (not used - fetched from DB on approval)
        subject: Email subject line
        body: HTML email body
        case_id: Case identifier (used to fetch client email/name on approval)
        session_id: Optional session ID for tracking
    
    Returns:
        dict with activity_id and status
    """
    
    if not case_id:
        return {
            "status": "error",
            "error": "No case_id provided",
            "activity_id": None
        }
    
    try:
        # Create a plain text preview for the activity log (strip ALL HTML)
        import re
        import json
        # First remove <style> tags and their contents
        plain_preview = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)
        # Then remove all other HTML tags
        plain_preview = re.sub(r'<[^>]+>', '', plain_preview)
        # Clean up extra whitespace
        plain_preview = ' '.join(plain_preview.split())
        # Truncate
        preview_text = plain_preview[:200] + '...' if len(plain_preview) > 200 else plain_preview
        
        # Log activity as 'pending' - email will be sent only after approval
        # Store HTML body in agent_response, subject in prompt
        # Client email/name will be fetched from CASE_DATA when approved
        activity_id = log_agent_activity(
            case_id=case_id,
            agent_type='ClientCommunicationGuru',
            agent_action='send_email',
            prompt=f"Subject: {subject}",
            agent_response=body,  # Store full HTML body here
            action_data=None,  # Skip JSON - client info fetched from CASE_DATA on approval
            requires_approval=True,
            session_id=session_id
        )
        
        return {
            "status": "success",
            "activity_id": activity_id,
            "message": f"Email prepared for approval. Activity ID: {activity_id}"
        }
        
    except Exception as e:
        print(f"❌ Error preparing email for approval: {e}")
        return {
            "status": "error",
            "error": str(e),
            "activity_id": None
        }


def send_client_email(to_email: str, to_name: str, subject: str, body: str, case_id: str, session_id: str = None) -> dict:
    """
    Send email to client via SMTP (internal function - use after approval)
    
    Args:
        to_email: Client's email address
        to_name: Client's full name
        subject: Email subject line
        body: HTML email body
        case_id: Case identifier
        session_id: Optional session ID for tracking
    
    Returns:
        dict with status and timestamp
    """
    
    # Get SMTP configuration from environment
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    firm_email = os.getenv('FIRM_EMAIL')
    firm_password = os.getenv('FIRM_EMAIL_PASSWORD')
    firm_name = os.getenv('FIRM_NAME', 'Morgan & Morgan')
    
    if not firm_email or not firm_password:
        return {
            "status": "error",
            "error": "Email credentials not configured",
            "sent": False
        }
    
    if not to_email or to_email == "client":
        return {
            "status": "error",
            "error": "No valid client email address",
            "sent": False
        }
    
    try:
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{firm_name} <{firm_email}>"
        msg['To'] = f"{to_name} <{to_email}>"
        msg['Subject'] = subject
        msg['Reply-To'] = firm_email
        
        # Add plain text version (strip HTML tags for basic compatibility)
        plain_text = body.replace('<br>', '\n').replace('</p>', '\n\n')
        import re
        plain_text = re.sub('<[^<]+?>', '', plain_text)
        
        msg.attach(MIMEText(plain_text, 'plain'))
        msg.attach(MIMEText(body, 'html'))
        
        # Send email via SMTP
        print(f"📧 Connecting to SMTP server: {smtp_server}:{smtp_port}")
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(firm_email, firm_password)
            server.send_message(msg)
        
        timestamp = datetime.now().isoformat()
        
        print(f"✅ Email sent successfully to {to_email}")
        
        return {
            "status": "success",
            "sent": True,
            "to_email": to_email,
            "timestamp": timestamp
        }
        
    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "sent": False
        }


def send_approved_email(activity_id: str) -> dict:
    """
    Send email after it has been approved
    
    Args:
        activity_id: The approved activity ID
    
    Returns:
        dict with send status
    """
    try:
        # Import here to avoid circular imports
        from app import get_snowflake_conn
        import json
        
        # Fetch the activity details
        conn = get_snowflake_conn()
        if not conn:
            return {
                "status": "error",
                "error": "Database connection failed"
            }
        
        cursor = conn.cursor()
        
        # Get activity details
        cursor.execute("""
            SELECT prompt, activity_status, agent_response, case_id
            FROM agent_activities
            WHERE activity_id = %s
        """, (activity_id,))
        
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return {
                "status": "error",
                "error": f"Activity {activity_id} not found"
            }
        
        prompt = result[0]
        current_status = result[1]
        html_body = result[2]  # HTML body is stored in agent_response
        case_id = result[3]
        
        if current_status != 'approved':
            cursor.close()
            conn.close()
            return {
                "status": "error",
                "error": f"Activity status is '{current_status}', not 'approved'"
            }
        
        # Parse subject from prompt: "Subject: ..."
        import re
        subject_match = re.search(r'Subject: (.+)$', prompt)
        subject = subject_match.group(1).strip() if subject_match else "Case Update"
        
        # Fetch client email and name from CASE_DATA using case_id
        cursor.execute("""
            SELECT client_email, client_name
            FROM CASE_DATA
            WHERE case_id = %s
            LIMIT 1
        """, (case_id,))
        
        client_result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not client_result or not client_result[0]:
            return {
                "status": "error",
                "error": f"Client email not found for case_id: {case_id}"
            }
        
        to_email = client_result[0]
        to_name = client_result[1] if client_result[1] else "Client"
        
        if not html_body:
            return {
                "status": "error",
                "error": "Email body is empty"
            }
        
        # Send the email
        send_result = send_client_email(
            to_email=to_email,
            to_name=to_name,
            subject=subject,
            body=html_body,
            case_id=None,  # Already logged
            session_id=None
        )
        
        if send_result["sent"]:
            # Update activity to 'completed'
            from services.activity_logger import update_activity_status
            update_activity_status(
                activity_id,
                status='completed',
                execution_result=f"Email sent to {to_email} at {send_result['timestamp']}"
            )
        
        return send_result
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to send approved email: {str(e)}"
        }


def format_email_html(body_text: str) -> str:
    """
    Convert plain text email to HTML format
    
    Args:
        body_text: Plain text email body
    
    Returns:
        HTML formatted email
    """
    
    # Convert plain text to HTML paragraphs
    # Split by double newlines for paragraphs
    paragraphs = body_text.strip().split('\n\n')
    html_paragraphs = []
    
    for para in paragraphs:
        # Replace single newlines with <br> within paragraphs
        para = para.strip().replace('\n', '<br>')
        if para:
            html_paragraphs.append(f'<p style="margin: 0 0 16px 0; color: #333333;">{para}</p>')
    
    formatted_content = '\n'.join(html_paragraphs)
    
    # Professional HTML email template with forced light background
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="light">
    <meta name="supported-color-schemes" content="light">
    <style>
        :root {{
            color-scheme: light only;
        }}
        body {{
            background-color: #ffffff !important;
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, Helvetica, sans-serif; background-color: #ffffff !important;">
    <div style="width: 100%; background-color: #ffffff; padding: 20px 0;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px 20px;">
            <div style="color: #333333; font-size: 16px; line-height: 1.6;">
                {formatted_content}
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_template
