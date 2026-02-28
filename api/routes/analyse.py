from flask import Blueprint, request, jsonify
from pydantic import BaseModel
from flask_pydantic import validate
from api.objects.error import Error
from api.error_enums.error_type import ErrorType
from api.error_enums.error_subtype import ErrorSubType

analyse_bp = Blueprint('analyse', __name__)

@analyse_bp.route('/analyse', methods=["GET", "POST"])
@validate()
def analyse(data: BaseModel):
    """
    Route to analyze a web page and return detected errors.
    """
    