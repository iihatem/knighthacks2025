"""Client Communication Guru - Empathetic message drafting specialist"""
import os
import google.generativeai as genai
from tools.communication_tools import draft_email

def client_communication_guru(case_context: str, task: str) -> dict:
    """
    Draft empathetic client communications using Gemini
    
    Args:
        case_context: Context about the case
        task: What communication is needed
    
    Returns:
        dict with 'draft' and 'requires_approval'
    """
    
    # Configure Gemini
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""You are the Client Communication Guru for Morgan & Morgan law firm.

Case Context:
{case_context}

Task: {task}

Draft a clear, empathetic message for the client. Be professional yet warm.
Use plain English (no legal jargon). Show empathy. Be transparent about next steps.

Format as email if appropriate, otherwise as a message.
"""

    response = model.generate_content(prompt)
    
    # Extract text from Gemini response
    draft_text = response.candidates[0].content.parts[0].text
    
    return {
        'draft': draft_text,
        'requires_approval': True,
        'agent': 'ClientCommunicationGuru'
    }