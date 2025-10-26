"""Records Wrangler Agent - Pulls missing records and requests them from providers"""
import os
import json
import boto3
from datetime import datetime
from typing import List, Dict, Any


def search_case_records(case_id: str, query: str) -> List[Dict]:
    """Search for records in the case using RAG"""
    try:
        import sys
        sys.path.insert(0, '/Users/arjunbhatheja/Desktop/Aura_MM/knighthacks2025/backend')
        from app import rag_search
        
        results = rag_search(case_id, query, top_k=5)
        return results
        
    except Exception as e:
        print(f"Error searching records: {e}")
        return []


def retrieve_file_from_storage(source_url: str) -> Dict:
    """Retrieve actual file from Digital Ocean Spaces"""
    try:
        session = boto3.session.Session()
        s3_client = session.client(
            's3',
            region_name=os.getenv("DO_SPACES_REGION"),
            endpoint_url=f"https://{os.getenv('DO_SPACES_REGION')}.digitaloceanspaces.com",
            aws_access_key_id=os.getenv("DO_SPACES_KEY"),
            aws_secret_access_key=os.getenv("DO_SPACES_SECRET")
        )
        
        bucket_name = os.getenv("DO_SPACES_BUCKET")
        
        response = s3_client.get_object(Bucket=bucket_name, Key=source_url)
        file_data = response['Body'].read()
        
        return {
            'status': 'success',
            'filename': source_url.split('/')[-1],
            'size': len(file_data),
            'data': file_data,
            'content_type': response.get('ContentType', 'application/octet-stream')
        }
        
    except Exception as e:
        print(f"Error retrieving file: {e}")
        return {'status': 'error', 'error': str(e)}


def draft_records_request_email(provider_name: str, client_name: str, case_id: str, record_type: str = "medical records") -> Dict[str, str]:
    """Draft an email requesting records from a medical provider"""
    
    subject = f"Medical Records Request for {client_name}"
    
    body = f"""Dear {provider_name},

I am writing to request complete {record_type} for our client, {client_name}.

We are representing {client_name} in a legal matter and require all medical documentation related to their treatment at your facility.

We would appreciate receiving these records within 30 days.

Thank you for your assistance.

Best regards,
Case Reference: {case_id}"""

    return {'subject': subject, 'body': body, 'to': provider_name, 'record_type': record_type}


def records_wrangler_guru(case_id: str, query: str, action_type: str = 'search_records') -> Dict[str, Any]:
    """Main entry point for Records Wrangler Agent"""
    
    if action_type == 'search_records':
        results = search_case_records(case_id, query)
        
        if not results or len(results) == 0:
            return {
                'status': 'success',
                'action': 'search_records',
                'found': False,
                'results': [],
                'message': f"No records found matching: '{query}'"
            }
        
        response_parts = [f"Found {len(results)} record(s):\n"]
        
        for i, record in enumerate(results, 1):
            similarity = int(record.get('similarity_score', 0) * 100)
            response_parts.append(f"{i}. {record.get('source_url', 'Unknown')} (Match: {similarity}%)")
        
        return {
            'status': 'success',
            'action': 'search_records',
            'found': True,
            'results': results,
            'count': len(results),
            'message': '\n'.join(response_parts)
        }
    
    elif action_type == 'request_records':
        provider_name = "Medical Provider"
        
        if "from " in query.lower():
            parts = query.lower().split("from ")
            if len(parts) > 1:
                provider_name = parts[1].strip().title()
        
        email_draft = draft_records_request_email(provider_name, "Client", case_id)
        
        return {
            'status': 'success',
            'action': 'request_records',
            'requires_approval': True,
            'draft': email_draft,
            'message': f"Records request email drafted for {provider_name}"
        }
    
    else:
        return {
            'status': 'error',
            'error': f"Unknown action type: {action_type}",
            'message': "Use 'search_records' or 'request_records'"
        }
