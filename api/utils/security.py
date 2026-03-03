import aiohttp
import ssl
from playwright.async_api import async_playwright
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
            type=ErrorType.SECURITY,
            subtype=ErrorSubType.MISSING_HTTPS,
            message="The URL does not use HTTPS, which can lead to security vulnerabilities.",
        )
    return None

async def check_ssl_certificate(url: str) -> Error:
    """
    Checks if the URL has a valid SSL certificate and returns an Error object if it does not.

    Args:
        url (str): The URL to check.
    Returns:
        Error: An Error object representing the invalid SSL certificate issue, or None if the SSL certificate
        is valid.   
    """
    if not url.startswith("https://"):
        return None
    
    try:
        # Create an SSL standard and secure context for the connection
        ssl_context = ssl.create_default_context()

        # TCP connector used by the HTTP client to manage connections and SSL settings
        connector = aiohttp.TCPConnector(ssl=ssl_context)

        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.head(url, timeout=aiohttp.ClientTimeout(total=10)):
                return None
            
    except (ssl.SSLError, aiohttp.ClientSSLError):
        return Error(
            type=ErrorType.SECURITY,
            subtype=ErrorSubType.INVALID_SSL_CERT,
            message="The URL has an invalid SSL certificate.",
        )
    except Exception:
        return None

async def check_unsecure_forms(url: str) -> list:
    """
    Checks that the FORM with the method POST is secure (i.e., uses HTTPS) and returns a list of Error objects for any unsecure forms found.
    Args
        url (str): The URL of the web page to check.
    Returns:
        list: A list of Error objects representing unsecure forms found in the web page.
    """
    errors = []
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Try navigation with retries for network errors
            nav_success = False
            for attempt in range(3):
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    nav_success = True
                    break
                except Exception as exc:
                    if attempt < 2 and any(err in str(exc) for err in ['ERR_NETWORK_CHANGED', 'ERR_CONNECTION', 'net::ERR', 'Timeout']):
                        continue
                    raise
            
            if nav_success:
                forms = await page.query_selector_all("form[method='POST']")
                for form in forms:
                    action = await form.get_attribute("action")
                    if action and not action.startswith("https://"):
                        errors.append(Error(
                            type=ErrorType.SECURITY,
                            subtype=ErrorSubType.UNSECURE_FORM,
                            message=f"Form submits to non-HTTPS URL: {action}",
                        ))
            
            await browser.close()
    except Exception:
        pass
    
    return errors

async def check_cookies_flags(url: str) -> list:
    """
    Checks the cookies used by the web page for security flags (Secure, HttpOnly, SameSite) and returns a list of Error objects for any issues found.

    Args:
        url (str): The URL of the web page to check.
    Returns:
        list: A list of Error objects representing cookie security issues found in the web page.
    """
    errors = []
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Try navigation with retries for network errors
            nav_success = False
            for attempt in range(3):
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    nav_success = True
                    break
                except Exception as exc:
                    if attempt < 2 and any(err in str(exc) for err in ['ERR_NETWORK_CHANGED', 'ERR_CONNECTION', 'net::ERR', 'Timeout']):
                        continue
                    raise
            
            if nav_success:
                cookies = await page.context.cookies()
                for cookie in cookies:
                    if not cookie.get("secure"):
                        errors.append(Error(
                            type=ErrorType.SECURITY,
                            subtype=ErrorSubType.COOKIE_MISSING_SECURE_FLAG,
                            message=f"Cookie '{cookie.get('name')}' is not marked as Secure.",
                        ))
                    if not cookie.get("httpOnly"):
                        errors.append(Error(
                            type=ErrorType.SECURITY,
                            subtype=ErrorSubType.COOKIE_MISSING_HTTPONLY_FLAG,
                            message=f"Cookie '{cookie.get('name')}' is not marked as HttpOnly.",
                        ))
                    if not cookie.get("sameSite"):
                        errors.append(Error(
                            type=ErrorType.SECURITY,
                            subtype=ErrorSubType.COOKIE_MISSING_SAMESITE_FLAG,
                            message=f"Cookie '{cookie.get('name')}' does not have SameSite flag.",
                        ))
            
            await browser.close()
    except Exception:
        pass
    
    return errors
    