"""
Legal Research Agent using Gemini 2.5 Pro with Google Search Grounding

This agent finds supporting verdicts, citations, and novel legal theories
to strengthen cases. Uses Gemini's built-in web search for automatic
citation and source attribution.
"""

import os
import json
from google import genai
from datetime import datetime


def legal_researcher(case_id, query, case_context):
    """
    Legal research agent using Gemini 2.5 Pro + Google Search Grounding
    
    Capabilities:
    1. Find similar verdicts/precedents with citations
    2. Identify novel legal theories
    3. Provide verifiable sources automatically
    4. Summarize case law
    5. Suggest counter-arguments
    
    Args:
        case_id: Case identifier
        query: Research question from lawyer
        case_context: Case background/details
    
    Returns:
        {
            "summary": "Key findings...",
            "supporting_cases": [...],  # With citations
            "novel_theories": [...],
            "counter_arguments": [...],
            "sources": [...],  # Actual web sources used
            "web_search_queries": [...],  # What Gemini searched for
            "strength_rating": 7,  # 1-10
            "requires_approval": False
        }
    """
    
    try:
        # Step 1: Initialize Gemini client
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Step 2: Build research prompt
        research_prompt = f"""
You are an expert legal researcher assisting a lawyer. Conduct comprehensive legal research on this query.

**Research Request:** {query}

**Case Context:** {case_context}

**Your Task:**
1. Search for relevant case law, statutes, and legal precedents
2. Find supporting verdicts that strengthen this case
3. Identify 2-3 novel legal theories to explore
4. Analyze potential counter-arguments from opposing counsel
5. Rate the case strength (1-10) with reasoning

**Required Output Format (JSON):**
{{
    "summary": "3-5 sentence overview of findings",
    "supporting_cases": [
        {{
            "case_name": "Smith v. Jones (2023)",
            "citation": "123 F.3d 456 (9th Cir. 2023)",
            "relevance": "Why this case matters",
            "key_holding": "Main legal principle",
            "similarity_score": 8
        }}
    ],
    "novel_theories": [
        {{
            "theory": "Theory name",
            "description": "How to apply this",
            "precedent_support": "Cases that support this approach",
            "risk_level": "low/medium/high"
        }}
    ],
    "counter_arguments": [
        "Opposing counsel might argue X...",
        "Defense could cite Y..."
    ],
    "strength_rating": 7,
    "strength_reasoning": "Why this rating",
    "recommended_next_steps": [
        "Action 1",
        "Action 2"
    ]
}}

**Important:** Base your research on actual legal sources. Cite real cases, statutes, and legal principles.
"""
        
        # Step 3: Call Gemini 2.5 Pro with Google Search Grounding enabled
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=research_prompt,
            config={
                "tools": [{"google_search": {}}],  # Enable Google Search grounding
                "temperature": 0.3,  # Lower for factual accuracy
                "top_p": 0.8,
                "max_output_tokens": 8192
            }
        )
        
        # Step 4: Extract research findings
        research_text = response.text
        
        # Try to parse JSON response
        try:
            # Find JSON in response (might be wrapped in markdown)
            if "```json" in research_text:
                json_start = research_text.find("```json") + 7
                json_end = research_text.find("```", json_start)
                research_json = json.loads(research_text[json_start:json_end])
            elif research_text.strip().startswith('{'):
                research_json = json.loads(research_text)
            else:
                # If no JSON, create structured response from text
                research_json = {
                    "summary": research_text[:500],
                    "supporting_cases": [],
                    "novel_theories": [],
                    "counter_arguments": [],
                    "strength_rating": 5,
                    "strength_reasoning": "Unable to parse detailed analysis",
                    "recommended_next_steps": []
                }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            research_json = {
                "summary": research_text,
                "supporting_cases": [],
                "novel_theories": [],
                "counter_arguments": [],
                "strength_rating": 5,
                "strength_reasoning": "Analysis provided in summary",
                "recommended_next_steps": []
            }
        
        # Step 5: Extract grounding metadata (sources!)
        grounding_metadata = {}
        web_search_queries = []
        sources = []
        
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            
            # Extract grounding metadata
            if hasattr(candidate, 'grounding_metadata'):
                metadata = candidate.grounding_metadata
                
                # Get search queries used
                if hasattr(metadata, 'web_search_queries'):
                    web_search_queries = metadata.web_search_queries or []
                
                # Get grounding chunks (actual sources)
                if hasattr(metadata, 'grounding_chunks'):
                    for chunk in (metadata.grounding_chunks or []):
                        if hasattr(chunk, 'web'):
                            sources.append({
                                'url': chunk.web.uri,
                                'title': chunk.web.title if hasattr(chunk.web, 'title') else 'Unknown'
                            })
                
                # Get grounding supports (which parts of response are supported by which sources)
                if hasattr(metadata, 'grounding_supports'):
                    grounding_metadata['supports'] = len(metadata.grounding_supports or [])
        
        # Step 6: Return comprehensive research result
        return {
            "query": query,
            "case_id": case_id,
            "summary": research_json.get('summary', 'No summary available'),
            "supporting_cases": research_json.get('supporting_cases', []),
            "novel_theories": research_json.get('novel_theories', []),
            "counter_arguments": research_json.get('counter_arguments', []),
            "strength_rating": research_json.get('strength_rating', 5),
            "strength_reasoning": research_json.get('strength_reasoning', ''),
            "recommended_next_steps": research_json.get('recommended_next_steps', []),
            
            # Grounding sources (THE KEY FEATURE!)
            "sources": sources,  # Actual web sources Gemini used
            "web_search_queries": web_search_queries,  # What Gemini searched for
            "source_count": len(sources),
            "grounded": len(sources) > 0,  # True if response is backed by sources
            
            # Metadata
            "timestamp": datetime.now().isoformat(),
            "saveable": True,  # Flag for "add to evidence sorter"
            "requires_approval": False,  # Research doesn't need approval
            "research_type": "legal_research"
        }
        
    except Exception as e:
        print(f"Error in legal_researcher: {e}")
        return {
            "query": query,
            "case_id": case_id,
            "summary": f"Research failed: {str(e)}",
            "supporting_cases": [],
            "novel_theories": [],
            "counter_arguments": [],
            "sources": [],
            "web_search_queries": [],
            "strength_rating": 0,
            "error": str(e),
            "requires_approval": False,
            "saveable": False
        }