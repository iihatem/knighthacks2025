"""
Utility functions for Evidence Sorter Agent.
"""
import logging
import requests
from typing import Dict, Any, List
from datetime import datetime

from .settings import (
    DOCUMENT_API_URL,
    OCR_API_URL,
    PROCESSING_TIMEOUT,
    DOCUMENT_CATEGORIES,
    EVIDENCE_TYPES,
    ORGANIZATION_RULES,
    METADATA_FIELDS
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


def categorize_documents(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Categorize documents automatically based on content and type.
    
    Args:
        documents: List of documents to categorize
        
    Returns:
        Response dictionary with categorization results
    """
    logger.info(f"Categorizing {len(documents)} documents")
    
    categorized_docs = []
    
    for doc in documents:
        doc_type = doc.get("type", "unknown")
        content = doc.get("content", "")
        
        # Determine category based on content analysis
        category = "general"
        if "medical" in content.lower() or "doctor" in content.lower():
            category = "medical_records"
        elif "bill" in content.lower() or "payment" in content.lower():
            category = "billing_statements"
        elif "police" in content.lower() or "officer" in content.lower():
            category = "police_reports"
        elif "expert" in content.lower() or "analysis" in content.lower():
            category = "expert_reports"
        elif "photo" in doc_type.lower() or "image" in doc_type.lower():
            category = "photographs"
        
        categorized_docs.append({
            **doc,
            "category": category,
            "folder": ORGANIZATION_RULES.get(category, {}).get("folder", "General"),
            "priority": ORGANIZATION_RULES.get(category, {}).get("priority", "medium")
        })
    
    return success_response(
        {
            "categorized_documents": categorized_docs,
            "total_documents": len(documents),
            "categories_found": list(set([doc["category"] for doc in categorized_docs])),
            "categorization_date": datetime.now().isoformat()
        },
        f"Successfully categorized {len(documents)} documents"
    )


def generate_folder_structure(case_name: str, document_categories: List[str]) -> Dict[str, Any]:
    """
    Generate a folder structure for organizing case documents.
    
    Args:
        case_name: Name of the case
        document_categories: List of document categories found
        
    Returns:
        Response dictionary with folder structure
    """
    logger.info(f"Generating folder structure for case: {case_name}")
    
    folder_structure = {
        "case_name": case_name,
        "root_folder": f"Case_{case_name.replace(' ', '_')}",
        "folders": []
    }
    
    # Create folders for each category
    for category in document_categories:
        rule = ORGANIZATION_RULES.get(category, {})
        folder_info = {
            "name": rule.get("folder", f"{category.title()}_Documents"),
            "category": category,
            "priority": rule.get("priority", "medium"),
            "subcategories": rule.get("subcategories", []),
            "path": f"Case_{case_name.replace(' ', '_')}/{rule.get('folder', f'{category.title()}_Documents')}"
        }
        folder_structure["folders"].append(folder_info)
    
    # Add standard folders
    standard_folders = [
        {"name": "Correspondence", "category": "correspondence", "priority": "medium"},
        {"name": "Legal_Documents", "category": "legal_documents", "priority": "high"},
        {"name": "Financial_Records", "category": "financial_records", "priority": "high"}
    ]
    
    for folder in standard_folders:
        folder_structure["folders"].append({
            **folder,
            "path": f"Case_{case_name.replace(' ', '_')}/{folder['name']}"
        })
    
    return success_response(
        folder_structure,
        f"Folder structure generated for case: {case_name}"
    )


def extract_document_metadata(document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metadata from a document.
    
    Args:
        document: Document to extract metadata from
        
    Returns:
        Response dictionary with extracted metadata
    """
    logger.info(f"Extracting metadata from document: {document.get('name', 'unknown')}")
    
    # Mock metadata extraction
    metadata = {
        "document_name": document.get("name", "unknown"),
        "document_type": document.get("type", "unknown"),
        "date_created": document.get("date_created", datetime.now().isoformat()),
        "author": document.get("author", "unknown"),
        "case_relevance": "high" if "medical" in document.get("content", "").lower() else "medium",
        "confidentiality_level": "confidential" if "medical" in document.get("content", "").lower() else "internal",
        "page_count": document.get("page_count", 1),
        "file_size": document.get("file_size", "unknown"),
        "extraction_date": datetime.now().isoformat()
    }
    
    return success_response(
        metadata,
        f"Metadata extracted from {document.get('name', 'document')}"
    )


def create_evidence_index(case_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create an evidence index for a case.
    
    Args:
        case_documents: List of documents for the case
        
    Returns:
        Response dictionary with evidence index
    """
    logger.info(f"Creating evidence index for {len(case_documents)} documents")
    
    evidence_index = {
        "case_id": case_documents[0].get("case_id", "unknown") if case_documents else "unknown",
        "total_documents": len(case_documents),
        "evidence_by_type": {},
        "evidence_by_category": {},
        "timeline": [],
        "created_date": datetime.now().isoformat()
    }
    
    # Group by evidence type
    for doc in case_documents:
        evidence_type = doc.get("evidence_type", "documentary_evidence")
        if evidence_type not in evidence_index["evidence_by_type"]:
            evidence_index["evidence_by_type"][evidence_type] = []
        evidence_index["evidence_by_type"][evidence_type].append(doc)
    
    # Group by category
    for doc in case_documents:
        category = doc.get("category", "general")
        if category not in evidence_index["evidence_by_category"]:
            evidence_index["evidence_by_category"][category] = []
        evidence_index["evidence_by_category"][category].append(doc)
    
    # Create timeline
    sorted_docs = sorted(case_documents, key=lambda x: x.get("date_created", ""))
    for doc in sorted_docs:
        evidence_index["timeline"].append({
            "date": doc.get("date_created"),
            "document": doc.get("name"),
            "type": doc.get("evidence_type"),
            "category": doc.get("category")
        })
    
    return success_response(
        evidence_index,
        f"Evidence index created with {len(case_documents)} documents"
    )


def organize_case_timeline(case_events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Organize case events into a chronological timeline.
    
    Args:
        case_events: List of case events to organize
        
    Returns:
        Response dictionary with organized timeline
    """
    logger.info(f"Organizing timeline for {len(case_events)} events")
    
    # Sort events by date
    sorted_events = sorted(case_events, key=lambda x: x.get("date", ""))
    
    timeline = {
        "total_events": len(case_events),
        "timeline": sorted_events,
        "key_milestones": [],
        "organized_date": datetime.now().isoformat()
    }
    
    # Identify key milestones
    for event in sorted_events:
        if event.get("type") in ["incident", "filing", "settlement", "trial"]:
            timeline["key_milestones"].append(event)
    
    return success_response(
        timeline,
        f"Timeline organized with {len(case_events)} events"
    )


def identify_ocr_requirements(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Identify documents that require OCR processing.
    
    Args:
        documents: List of documents to analyze
        
    Returns:
        Response dictionary with OCR requirements
    """
    logger.info(f"Identifying OCR requirements for {len(documents)} documents")
    
    ocr_requirements = {
        "documents_needing_ocr": [],
        "ocr_priority": [],
        "estimated_processing_time": 0
    }
    
    for doc in documents:
        doc_type = doc.get("type", "").lower()
        if any(img_type in doc_type for img_type in ["image", "photo", "scan", "pdf"]):
            ocr_requirements["documents_needing_ocr"].append({
                "document": doc.get("name"),
                "type": doc_type,
                "priority": "high" if "medical" in doc.get("content", "").lower() else "medium",
                "estimated_pages": doc.get("page_count", 1)
            })
    
    # Calculate estimated processing time (mock calculation)
    total_pages = sum(doc["estimated_pages"] for doc in ocr_requirements["documents_needing_ocr"])
    ocr_requirements["estimated_processing_time"] = total_pages * 2  # 2 minutes per page
    
    return success_response(
        ocr_requirements,
        f"OCR requirements identified for {len(ocr_requirements['documents_needing_ocr'])} documents"
    )
