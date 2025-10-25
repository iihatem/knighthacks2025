"""
Evidence Sorter Agent.
Organizes documents, evidence, and attachments.
"""
from typing import Dict, Any, List
import logging
from .base_agent import TenderPilotBaseAgent

logger = logging.getLogger(__name__)


class EvidenceSorterAgent(TenderPilotBaseAgent):
    """
    Specialized agent for organizing evidence and documents.
    Extracts, labels, and categorizes attachments and media files.
    """
    
    def __init__(self):
        """Initialize the Evidence Sorter agent."""
        super().__init__(
            name="EvidenceSorter",
            description="Organizes documents, evidence, and attachments for case management"
        )
        self.evidence_categories = self._initialize_evidence_categories()
    
    def _initialize_evidence_categories(self) -> Dict[str, List[str]]:
        """Initialize evidence categorization rules."""
        return {
            "medical_records": ["medical", "hospital", "doctor", "treatment", "diagnosis", "prescription"],
            "billing_documents": ["bill", "invoice", "payment", "charge", "receipt", "statement"],
            "correspondence": ["email", "letter", "message", "communication", "memo"],
            "legal_documents": ["contract", "agreement", "policy", "notice", "complaint", "motion"],
            "photographs": ["photo", "image", "picture", "jpg", "jpeg", "png"],
            "police_reports": ["police", "accident", "incident", "report", "officer"],
            "witness_statements": ["witness", "statement", "testimony", "affidavit", "declaration"],
            "expert_reports": ["expert", "analysis", "evaluation", "assessment", "opinion"],
            "financial_records": ["bank", "financial", "tax", "income", "employment", "wage"]
        }
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process evidence organization request.
        
        Args:
            context: Task context containing:
                - content: Description of evidence
                - task_type: Type of organization task
                - metadata: File information, attachments, etc.
                
        Returns:
            Result with organized evidence and categorization
        """
        self.log_action("Processing evidence organization", {"task_type": context.get("task_type")})
        
        content = context.get("content", "")
        metadata = context.get("metadata", {})
        
        # Extract evidence information
        evidence_info = self._extract_evidence_info(content, metadata)
        
        # Categorize evidence
        categorization = self._categorize_evidence(evidence_info)
        
        # Generate organization plan
        organization_plan = self._generate_organization_plan(categorization)
        
        # Extract metadata from files
        file_metadata = self._extract_file_metadata(evidence_info)
        
        return {
            "status": "success",
            "agent": self.name,
            "evidence_info": evidence_info,
            "categorization": categorization,
            "organization_plan": organization_plan,
            "file_metadata": file_metadata,
            "requires_approval": False,  # Organization doesn't need approval
            "confidence": categorization["confidence"]
        }
    
    def _extract_evidence_info(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract information about the evidence to organize."""
        return {
            "description": content,
            "files": metadata.get("files", []),
            "case_id": metadata.get("case_id", ""),
            "source": metadata.get("source", "unknown"),
            "date_received": metadata.get("date_received", ""),
            "sender": metadata.get("sender", "")
        }
    
    def _categorize_evidence(self, evidence_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Categorize evidence based on content and file types.
        
        Args:
            evidence_info: Evidence information
            
        Returns:
            Categorization results
        """
        description = evidence_info["description"].lower()
        files = evidence_info["files"]
        
        # Determine primary category
        category_scores = {}
        for category, keywords in self.evidence_categories.items():
            score = sum(1 for keyword in keywords if keyword in description)
            if score > 0:
                category_scores[category] = score
        
        # Get primary and secondary categories
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        primary_category = sorted_categories[0][0] if sorted_categories else "miscellaneous"
        secondary_categories = [cat for cat, _ in sorted_categories[1:3]]
        
        # Categorize individual files
        file_categories = []
        for file_info in files:
            file_cat = self._categorize_file(file_info)
            file_categories.append(file_cat)
        
        # Calculate confidence
        confidence = self._calculate_categorization_confidence(category_scores, files)
        
        return {
            "primary_category": primary_category,
            "secondary_categories": secondary_categories,
            "file_categories": file_categories,
            "confidence": confidence,
            "total_files": len(files)
        }
    
    def _categorize_file(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize an individual file."""
        filename = file_info.get("filename", "").lower()
        file_type = file_info.get("type", "").lower()
        
        # Determine category based on filename and type
        category = "miscellaneous"
        
        for cat, keywords in self.evidence_categories.items():
            if any(keyword in filename for keyword in keywords):
                category = cat
                break
        
        # Override based on file type
        if file_type in ["image/jpeg", "image/png", "image/jpg"]:
            category = "photographs"
        elif file_type == "application/pdf":
            if "bill" in filename or "invoice" in filename:
                category = "billing_documents"
            elif "medical" in filename:
                category = "medical_records"
        
        return {
            "filename": file_info.get("filename"),
            "category": category,
            "file_type": file_type,
            "size": file_info.get("size", 0)
        }
    
    def _generate_organization_plan(self, categorization: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a plan for organizing the evidence.
        
        Args:
            categorization: Categorization results
            
        Returns:
            Organization plan
        """
        primary_category = categorization["primary_category"]
        
        # Generate folder structure
        folder_structure = {
            "root": f"Case_{categorization.get('case_id', 'Unknown')}",
            "primary_folder": primary_category.replace("_", " ").title(),
            "subfolders": []
        }
        
        # Add subfolders for secondary categories
        for secondary in categorization["secondary_categories"]:
            folder_structure["subfolders"].append(secondary.replace("_", " ").title())
        
        # Generate file placement instructions
        file_placements = []
        for file_cat in categorization["file_categories"]:
            placement = {
                "filename": file_cat["filename"],
                "destination_folder": file_cat["category"].replace("_", " ").title(),
                "action": "move",
                "tags": [file_cat["category"], primary_category]
            }
            file_placements.append(placement)
        
        return {
            "folder_structure": folder_structure,
            "file_placements": file_placements,
            "total_actions": len(file_placements),
            "estimated_time": f"{len(file_placements) * 2} seconds"
        }
    
    def _extract_file_metadata(self, evidence_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract metadata from files for indexing."""
        metadata_list = []
        
        for file_info in evidence_info.get("files", []):
            metadata = {
                "filename": file_info.get("filename"),
                "file_type": file_info.get("type"),
                "size_bytes": file_info.get("size", 0),
                "date_received": evidence_info.get("date_received"),
                "source": evidence_info.get("source"),
                "case_id": evidence_info.get("case_id"),
                "indexed": True,
                "ocr_required": self._requires_ocr(file_info)
            }
            metadata_list.append(metadata)
        
        return metadata_list
    
    def _requires_ocr(self, file_info: Dict[str, Any]) -> bool:
        """Determine if file requires OCR processing."""
        file_type = file_info.get("type", "").lower()
        return file_type in ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    
    def _calculate_categorization_confidence(
        self, 
        category_scores: Dict[str, int], 
        files: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for categorization."""
        if not category_scores:
            return 0.3  # Low confidence if no matches
        
        max_score = max(category_scores.values())
        total_files = len(files)
        
        # Base confidence on keyword matches and file count
        confidence = min(0.5 + (max_score * 0.1) + (min(total_files, 5) * 0.05), 0.95)
        
        return round(confidence, 2)

