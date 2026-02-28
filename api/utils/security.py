from objects.error import Error
from error_enums.error_type import ErrorType
from error_enums.error_subtype import ErrorSubType

def check_https(url: str) -> Error:
    """
    Checks if the URL uses HTTPS and returns an Error object if it does not.

    Args:
        url (str): The URL to check.
    Returns:
        Error: An Error object representing the missing HTTPS issue, or None if the URL uses HTTPS
    """
    if not url.startswith("https://"):
        return Error(
            error_type=ErrorType.SECURITY,
            error_subtype=ErrorSubType.MISSING_HTTPS,
            description="The URL does not use HTTPS, which can lead to security vulnerabilities.",
            url=url
        )
    return None

def check_ssl_certificate(url: str) -> Error:
    """
    Checks if the URL has a valid SSL certificate and returns an Error object if it does not.

    Args:
        url (str): The URL to check.
    Returns:
        Error: An Error object representing the invalid SSL certificate issue, or None if the SSL certificate
        is valid.   
    """

def check_unsecure_forms(url: str) -> list:
    """
    Checks that the FORM with the method POST is secure (i.e., uses HTTPS) and returns a list of Error objects for any unsecure forms found.
    Args
        url (str): The URL of the web page to check.
    Returns:
        list: A list of Error objects representing unsecure forms found in the web page.
    """
    errors = []

def check_cookies_flags(url: str) -> list:
    """
    Checks the cookies used by the web page for security flags (Secure, HttpOnly, SameSite) and returns a list of Error objects for any issues found.

    Args:
        url (str): The URL of the web page to check.
    Returns:
        list: A list of Error objects representing cookie security issues found in the web page.
    """
    