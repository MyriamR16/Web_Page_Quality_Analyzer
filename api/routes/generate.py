from flask import Blueprint, request, jsonify
from pydantic import BaseModel
from flask_pydantic import validate
from api.objects.error import Error
from api.error_enums.error_type import ErrorType
from api.error_enums.error_subtype import ErrorSubType

generate_bp = Blueprint('generate', __name__)

@generate_bp.route('/generate', methods=["GET", "POST"])
@validate()
def generate(data: BaseModel):
    """
    Route to generate a web page quality report using LLMs.
    """
    