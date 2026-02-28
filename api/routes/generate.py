from flask import Blueprint, request, jsonify
from pydantic import BaseModel
from flask_pydantic import validate
from objects.error import Error
from error_enums.error_type import ErrorType
from error_enums.error_subtype import ErrorSubType

generate_bp = Blueprint('generate', __name__)

class GenerateQuery(BaseModel):
    data: str  # Adjust this based on what data you expect

@generate_bp.get('/generate')
@validate()
def generate(query: GenerateQuery):
    """
    Route to generate a web page quality report using LLMs.
    """
    return jsonify({"message": "Generate endpoint", "data": query.data})
    