from flask import Blueprint, jsonify
from flask_pydantic import validate
from pydantic import BaseModel
from typing import List, Dict, Any

from utils.llm import generate_report

generate_bp = Blueprint('generate', __name__)


class GenerateRequest(BaseModel):
    url: str
    errors: List[Dict[str, Any]]


@generate_bp.post('/generate')
@validate()
def generate(body: GenerateRequest):
    """
    Route to generate a quality report using OpenAI GPT.
    
    Expects JSON body:
    {
        "url": "https://example.com",
        "errors": [...]
    }
    
    Returns:
    {
        "url": "...",
        "report": {
            "summary": "...",
            "recommendations": [...],
            "prioritization": {
                "critical": [...],
                "warning": [...],
                "info": [...]
            }
        }
    }
    """
    try:
        report = generate_report(errors=body.errors, url=body.url)
        
        return jsonify({
            "url": body.url,
            "report": report
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    