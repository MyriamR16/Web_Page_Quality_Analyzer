import time
import requests
from typing import List
from objects.error import Error
from error_enums.error_type import ErrorType
from error_enums.error_subtype import ErrorSubType
from playwright.async_api import async_playwright

def check_page_loading_time(url: str) -> float:
    """
    Measures the page load time for a given URL.

    Args:
        url (str): The URL of the web page to measure.
    Returns:
        float: The page load time in seconds.
    """

def check_slow_images(url: str, threshold : int) -> List[Error]:
    """
    Checks for images that take longer than the specified threshold to load.

    Args:
        url (str): The URL of the web page to check.
        threshold_ms (int): The time threshold in milliseconds for considering an image as slow.    
    Returns:
        List[Error]: A list of Error objects representing slow loading images.      

    """

def check_total_page_size(url:str, threshold : float) -> Error: 
    """
    Checks the total page size of the web page and returns an Error object if it exceeds a certain threshold.

    Args:
        url (str): The URL of the web page to check.
    Returns:
        Error: An Error object representing the total page size issue, or None if the page size is within acceptable limits.
    """

def check_total_http_requests(url:str, threshold : int) -> Error:
    """
    Checks the total number of HTTP requests made by the web page and returns an Error object if it exceeds a certain threshold.

    Args:
        url (str): The URL of the web page to check.
    Returns:
        Error: An Error object representing the total HTTP requests issue, or None if the number of
        HTTP requests is within acceptable limits.
    """

