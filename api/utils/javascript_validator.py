import asyncio
from typing import List

from objects.error import Error
from error_enums.error_type import ErrorType
from error_enums.error_subtype import ErrorSubType
from playwright.async_api import async_playwright


def check_console_exceptions(url: str) -> List[Error]:
    """
    Checks for JavaScript exceptions in the browser console when loading the specified URL.

    Args:
        url (str): The URL of the web page to check for JavaScript exceptions.
    Returns:
        List[Error]: A list of Error objects representing any JavaScript exceptions found in the console.
    """

def check_buttons_forms(url: str) -> List[Error]:
    """
    Checks for JavaScript exceptions related to buttons and forms on the web page.

    Args:
        url (str): The URL of the web page to check for JavaScript exceptions related to buttons and forms.
    Returns:
        List[Error]: A list of Error objects representing any JavaScript exceptions found related to buttons and forms.
    """

def check_responsiveness(url: str) -> List[Error]:
    """
    Checks if the web page is responsive and adapts correctly to different screen sizes.
    Args:
        url (str): The URL of the web page to check for responsiveness.
    Returns:
        List[Error]: A list of Error objects representing any responsiveness issues found on the web page
    """
    
    