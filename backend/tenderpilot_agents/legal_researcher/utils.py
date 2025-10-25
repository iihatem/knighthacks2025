"""
Utility functions for Legal Researcher Agent.
"""
import logging
import requests
from typing import Dict, Any, List
from datetime import datetime

from .settings import (
    LEGAL_DATABASE_URL,
    CASE_LAW_API_URL,
    RESEARCH_TIMEOUT,
    LEGAL_SOURCES,
    CITATION_FORMATS,
    MIN_CITATION_COUNT,
    MAX_RESEARCH_DEPTH
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


def find_case_law_precedents(legal_issue: str, jurisdiction: str = "federal") -> Dict[str, Any]:
    """
    Find case law precedents for a legal issue.
    
    Args:
        legal_issue: Description of the legal issue
        jurisdiction: Jurisdiction to search (federal, state, etc.)
        
    Returns:
        Response dictionary with case law precedents
    """
    logger.info(f"Finding case law precedents for: {legal_issue}")
    
    url = f"{CASE_LAW_API_URL}/search"
    payload = {
        "query": legal_issue,
        "jurisdiction": jurisdiction,
        "sources": LEGAL_SOURCES,
        "max_results": 10
    }
    
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=RESEARCH_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        data = response.json()
        precedents = data.get("results", [])
        
        return success_response(
            {
                "precedents": precedents,
                "legal_issue": legal_issue,
                "jurisdiction": jurisdiction,
                "total_found": len(precedents)
            },
            f"Found {len(precedents)} case law precedents"
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error finding case law precedents: {e}")
        return error_response(f"Failed to find case law precedents: {str(e)}", "RESEARCH_FAILED")


def research_legal_citations(case_name: str, citation_format: str = "Bluebook") -> Dict[str, Any]:
    """
    Research and format legal citations for a case.
    
    Args:
        case_name: Name of the case
        citation_format: Citation format to use
        
    Returns:
        Response dictionary with formatted citations
    """
    logger.info(f"Researching citations for case: {case_name}")
    
    url = f"{LEGAL_DATABASE_URL}/citations"
    payload = {
        "case_name": case_name,
        "format": citation_format,
        "include_history": True
    }
    
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=RESEARCH_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        data = response.json()
        citations = data.get("citations", [])
        
        return success_response(
            {
                "case_name": case_name,
                "citations": citations,
                "format": citation_format,
                "total_citations": len(citations)
            },
            f"Found {len(citations)} citations for {case_name}"
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error researching citations: {e}")
        return error_response(f"Failed to research citations: {str(e)}", "CITATION_FAILED")


def analyze_legal_strategy(case_facts: str, legal_issues: List[str]) -> Dict[str, Any]:
    """
    Analyze legal strategy based on case facts and issues.
    
    Args:
        case_facts: Facts of the case
        legal_issues: List of legal issues to analyze
        
    Returns:
        Response dictionary with legal strategy analysis
    """
    logger.info(f"Analyzing legal strategy for {len(legal_issues)} issues")
    
    # Mock legal strategy analysis
    strategy_analysis = {
        "case_facts": case_facts,
        "legal_issues": legal_issues,
        "strategy_recommendations": [
            {
                "issue": "Negligence",
                "recommendation": "Focus on duty of care and breach of duty",
                "strength": "strong",
                "precedents_needed": 3
            },
            {
                "issue": "Damages",
                "recommendation": "Document all economic and non-economic damages",
                "strength": "moderate",
                "precedents_needed": 2
            }
        ],
        "research_priorities": [
            "Recent negligence cases in similar jurisdiction",
            "Damage calculation precedents",
            "Expert witness requirements"
        ],
        "timeline_estimate": "2-3 weeks for comprehensive research"
    }
    
    return success_response(
        strategy_analysis,
        "Legal strategy analysis completed"
    )


def generate_legal_memo(legal_issue: str, research_findings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a legal memorandum based on research findings.
    
    Args:
        legal_issue: The legal issue being addressed
        research_findings: Research findings and precedents
        
    Returns:
        Response dictionary with generated legal memo
    """
    logger.info(f"Generating legal memo for: {legal_issue}")
    
    memo_content = f"""
    LEGAL MEMORANDUM
    
    TO: Legal Team
    FROM: Legal Researcher
    DATE: {datetime.now().strftime('%Y-%m-%d')}
    RE: {legal_issue}
    
    EXECUTIVE SUMMARY
    {research_findings.get('summary', 'Research findings summary')}
    
    LEGAL ANALYSIS
    {research_findings.get('analysis', 'Detailed legal analysis')}
    
    PRECEDENTS CITED
    {research_findings.get('precedents', 'List of relevant precedents')}
    
    RECOMMENDATIONS
    {research_findings.get('recommendations', 'Legal recommendations')}
    
    CONCLUSION
    {research_findings.get('conclusion', 'Legal conclusion')}
    """
    
    return success_response(
        {
            "memo_content": memo_content.strip(),
            "legal_issue": legal_issue,
            "research_findings": research_findings,
            "generated_date": datetime.now().isoformat()
        },
        "Legal memorandum generated successfully"
    )


def verify_legal_authority(citation: str, source: str) -> Dict[str, Any]:
    """
    Verify the authority and validity of a legal citation.
    
    Args:
        citation: Legal citation to verify
        source: Source of the citation
        
    Returns:
        Response dictionary with verification results
    """
    logger.info(f"Verifying legal authority for citation: {citation}")
    
    # Mock verification process
    verification_result = {
        "citation": citation,
        "source": source,
        "is_valid": True,
        "authority_level": "high",
        "verification_date": datetime.now().isoformat(),
        "notes": "Citation verified through legal database"
    }
    
    return success_response(
        verification_result,
        f"Citation {citation} verified successfully"
    )


def conduct_comprehensive_research(research_query: str, depth: int = 3) -> Dict[str, Any]:
    """
    Conduct comprehensive legal research on a topic.
    
    Args:
        research_query: Research topic or question
        depth: Research depth level (1-5)
        
    Returns:
        Response dictionary with comprehensive research results
    """
    logger.info(f"Conducting comprehensive research on: {research_query}")
    
    # Mock comprehensive research
    research_results = {
        "query": research_query,
        "depth": depth,
        "sources_searched": LEGAL_SOURCES,
        "findings": {
            "case_law": [
                {"case": "Smith v. Jones", "relevance": "high", "year": "2023"},
                {"case": "Brown v. White", "relevance": "medium", "year": "2022"}
            ],
            "statutes": [
                {"statute": "Civil Code §1234", "relevance": "high"},
                {"statute": "Penal Code §5678", "relevance": "medium"}
            ],
            "regulations": [
                {"regulation": "CFR Title 29", "relevance": "high"},
                {"regulation": "CFR Title 42", "relevance": "medium"}
            ]
        },
        "research_summary": f"Comprehensive research on {research_query} completed",
        "confidence_level": "high" if depth >= 3 else "medium",
        "research_date": datetime.now().isoformat()
    }
    
    return success_response(
        research_results,
        f"Comprehensive research completed with depth level {depth}"
    )
