from enum import Enum

class ErrorType(Enum):
    "Defines the main types of errors that can be detected during the analysis of a web page."
    
    USER_EXPERIENCE = "user_experience_error"
    HTML = "html_error"
    JAVASCRIPT = "javascript_error"
    SECURITY = "security_error"
    PERFORMANCE = "performance_error"
    ACCESSIBILITY = "accessibility_error"