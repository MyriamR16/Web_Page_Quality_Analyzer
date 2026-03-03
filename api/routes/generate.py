from flask import Blueprint, jsonify, send_file
from flask_pydantic import validate
from pydantic import BaseModel
from typing import List, Dict, Any
import json
from io import BytesIO

from utils.llm import generate_report
from utils.pdf_generator import generate_report_pdf

generate_bp = Blueprint('generate', __name__)


class GenerateRequest(BaseModel):
    url: str
    errors: List[Dict[str, Any]]


class DownloadRequest(BaseModel):
    url: str
    report: Dict[str, Any]


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

    
@generate_bp.post('/download-pdf')
@validate()
def download_pdf(body: DownloadRequest):
    """
    Route to download the report as PDF.
    
    Expects JSON body:
    {
        "url": "https://example.com",
        "report": {...}
    }
    """
    try:
        pdf_buffer = generate_report_pdf(url=body.url, report=body.report)
        
        # Generate filename based on URL
        domain = body.url.replace('https://', '').replace('http://', '').split('/')[0].replace('.', '_')
        filename = f"report_{domain}.pdf"
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@generate_bp.post('/download-json')
@validate()
def download_json(body: DownloadRequest):
    """
    Route to download the report as JSON.
    
    Expects JSON body:
    {
        "url": "https://example.com",
        "report": {...}
    }
    """
    try:
        # Generate filename based on URL
        domain = body.url.replace('https://', '').replace('http://', '').split('/')[0].replace('.', '_')
        filename = f"report_{domain}.json"
        
        # Create JSON content
        report_data = {
            "url": body.url,
            "report": body.report
        }
        
        # Convert to JSON
        json_buffer = json.dumps(report_data, indent=2).encode('utf-8')
        
        buffer = BytesIO(json_buffer)
        
        return send_file(
            buffer,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    