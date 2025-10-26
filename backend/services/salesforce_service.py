"""Salesforce connection manager using simple-salesforce library"""
import os
from simple_salesforce import Salesforce
from dotenv import load_dotenv

load_dotenv()

class SalesforceService:
    """Singleton service for Salesforce API connection"""
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _connect(self):
        """Establish connection to Salesforce"""
        try:
            sf = Salesforce(
                username=os.getenv('SALESFORCE_USERNAME'),
                password=os.getenv('SALESFORCE_PASSWORD'),
                security_token=os.getenv('SALESFORCE_SECURITY_TOKEN', ''),
                domain=os.getenv('SALESFORCE_DOMAIN', 'login')
            )
            return sf
        except Exception as e:
            raise Exception(f"Failed to connect to Salesforce: {str(e)}")
    
    def get_client(self):
        """Get authenticated Salesforce client"""
        if self._client is None:
            self._client = self._connect()
        return self._client

# Global function to get Salesforce client
def get_salesforce_client():
    """Returns authenticated Salesforce client instance"""
    service = SalesforceService()
    return service.get_client()
