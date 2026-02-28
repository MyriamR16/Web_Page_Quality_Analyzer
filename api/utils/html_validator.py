import requests
from objects.error import Error
from error_enums.error_type import ErrorType
from error_enums.error_subtype import ErrorSubType


def validate_html_w3c(url: str) -> list[Error]:
    """
    Validates HTML structure using W3C Validator API.
    Checks for missing tags, malformed structure, and other HTML validity issues.

    Args:
        url (str): The URL of the web page to validate.
    Returns:
        list[Error]: A list of Error objects representing HTML validation issues.
    """
    errors = []
    api_url = "https://validator.w3.org/nu/"
    params = {"out": "json", "doc": url}

    try:
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        for msg in data.get("messages", []):
            if msg["type"] == "error":
                # Build error message with line number and extract
                error_msg = msg["message"]
                if msg.get("lastLine"):
                    error_msg += f" (Line {msg.get('lastLine')}"
                    if msg.get("lastColumn"):
                        error_msg += f", Column {msg.get('lastColumn')}"
                    error_msg += ")"
                
                if msg.get("extract"):
                    error_msg += f" - Extract: {msg.get('extract')[:100]}"
                
                errors.append(
                    Error(
                        type=ErrorType.HTML,
                        subtype=ErrorSubType.INVALID_HTML_STRUCTURE,
                        message=error_msg
                    )
                )
    except requests.exceptions.RequestException as e:
        errors.append(
            Error(
                type=ErrorType.HTML,
                subtype=ErrorSubType.INVALID_HTML_STRUCTURE,
                message=f"W3C Validator API error: {str(e)}"
            )
        )
    except Exception as e:
        errors.append(
            Error(
                type=ErrorType.HTML,
                subtype=ErrorSubType.INVALID_HTML_STRUCTURE,
                message=f"Error validating HTML: {str(e)}"
            )
        )
    
    return errors