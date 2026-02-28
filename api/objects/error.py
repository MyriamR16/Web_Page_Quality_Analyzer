from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from error_enums.error_type import ErrorType
from error_enums.error_subtype import ErrorSubType

class Error(BaseModel):
    "Defines the structure of an error detected during the analysis of a web page."
    
    type: ErrorType
    subtype: ErrorSubType
    message: str