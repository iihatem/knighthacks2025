"""Communication tools for drafting emails and messages"""

def draft_email(recipient_type: str, subject: str, context: str, tone: str = "professional") -> str:
    """
    Draft an email message
    
    Args:
        recipient_type: "client", "provider", "insurance", "counsel"
        subject: Email subject
        context: What to say in the email
        tone: "professional", "empathetic", "urgent"
    
    Returns:
        Formatted email draft
    """
    
    greetings = {
        "client": "Dear Valued Client",
        "provider": "Dear Healthcare Provider",
        "insurance": "To Whom It May Concern",
        "counsel": "Counselor"
    }
    
    openings = {
        "professional": "I am writing to provide you with an update.",
        "empathetic": "I hope this message finds you well.",
        "urgent": "This is an important update regarding your case."
    }
    
    email = f"""Subject: {subject}

{greetings.get(recipient_type, 'Hello')},

{openings.get(tone, openings['professional'])}

{context}

We are committed to keeping you informed every step of the way. If you have any questions, please don't hesitate to contact us.

Best regards,
Morgan & Morgan Legal Team
For The People
"""
    
    return email
