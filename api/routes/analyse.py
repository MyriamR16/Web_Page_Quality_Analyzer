from flask import Blueprint, request, jsonify
from flask_pydantic import validate
from pydantic import BaseModel
from objects.error import Error
from error_enums.error_type import ErrorType
from error_enums.error_subtype import ErrorSubType

analyse_bp = Blueprint('analyse', __name__)

class AnalyseQuery(BaseModel):
    url: str

@analyse_bp.get('/analyse')
@validate()
def analyse(query: AnalyseQuery):
    """
    Route to analyze a web page and return detected errors.
    """
    url = query.url
    print(f"Analyzing URL: {url}")
    return jsonify({"message": "Analysis endpoint", "url": url})

