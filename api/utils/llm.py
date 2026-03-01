import os
import logging
import json
from typing import List, Dict, Any
import cohere

logger = logging.getLogger(__name__)


def generate_report(errors: List[Dict[str, Any]], url: str) -> Dict[str, Any]:
    """
    Generates a quality report using OpenAI GPT.
    
    Args:
        errors: List of error dictionaries
        url: URL analyzed
    
    Returns:
        Dict with summary, recommendations, and prioritization
    """
    if not errors:
        return {
            "summary": "No errors detected. The web page meets quality standards.",
            "recommendations": [],
            "prioritization": {"critical": [], "warning": [], "info": []}
        }
    
    # Build prompt
    prompt = f"""Analyze this web page quality report for: {url}

Errors detected ({len(errors)} total):
{_format_errors(errors)}

Generate:
1. A clear summary (2-3 sentences)
2. Improvement recommendations (bullet points)
3. Prioritization of issues:
   - CRITICAL: Must fix immediately (security, major functionality)
   - WARNING: Should fix soon (performance, UX)
   - INFO: Nice to have (accessibility, minor issues)

Respond in JSON format:
{{
  "summary": "...",
  "recommendations": ["...", "..."],
  "prioritization": {{
    "critical": [{{"type": "...", "subtype": "...", "message": "..."}}, ...],
    "warning": [...],
    "info": [...]
  }}
}}"""
    
    try:
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise ValueError("COHERE_API_KEY environment variable not set")
        
        co = cohere.ClientV2(api_key=api_key)
        response = co.chat(
            model="command-r-plus-08-2024",
            messages=[
                {"role": "system", "content": "You are a web quality analysis expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        response_text = response.message.content[0].text
        
        # Extract JSON from markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        return json.loads(response_text)
    
    except Exception as e:
        logger.error(f"Cohere report generation failed: {e}")
        raise


def _format_errors(errors: List[Dict[str, Any]]) -> str:
    """Formats errors for the prompt."""
    lines = []
    for i, error in enumerate(errors, 1):
        lines.append(f"{i}. [{error['type']}] {error['subtype']}: {error['message']}")
    return "\n".join(lines[:50])  # Limit to 50 errors to avoid token limits
