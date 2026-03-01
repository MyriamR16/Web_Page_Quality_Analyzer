import logging
from typing import List

from objects.error import Error
from error_enums.error_type import ErrorType
from error_enums.error_subtype import ErrorSubType
from playwright.async_api import async_playwright


logger = logging.getLogger(__name__)


async def _load_page_with_listeners(
    playwright, url: str, viewport: dict | None = None
):
    """
    Opens browser, navigates to URL, and attaches console/pageerror listeners.

    Args:
        playwright: The Playwright instance to use for browser automation.
        url (str): The URL of the web page to load.
        viewport (dict, optional): Viewport dimensions for the browser page. Defaults to None.
    
    Returns:
        tuple: (browser, page, console_messages, page_errors, nav_error)
        nav_error: Exception if navigation failed, else None
    """
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page(viewport=viewport)
    console_messages: list[tuple[str, str]] = []
    page_errors: list[str] = []
    nav_error = None

    page.on("console", lambda msg: console_messages.append((msg.type, msg.text)))
    page.on("pageerror", lambda exc: page_errors.append(str(exc)))

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
    except Exception as exc:
        nav_error = exc

    return browser, page, console_messages, page_errors, nav_error


def _append_js_errors(
    errors: List[Error],
    console_messages: list[tuple[str, str]],
    page_errors: list[str],
) -> None:
    """Append console and page errors to the errors list."""
    for msg_type, msg_text in console_messages:
        if msg_type == "error":
            errors.append(
                Error(
                    type=ErrorType.JAVASCRIPT,
                    subtype=ErrorSubType.JS_CONSOLE_ERROR,
                    message=f"console error: {msg_text}",
                )
            )

    for page_error in page_errors:
        errors.append(
            Error(
                type=ErrorType.JAVASCRIPT,
                subtype=ErrorSubType.JS_CONSOLE_ERROR,
                message=f"page error: {page_error}",
            )
        )


async def check_console_exceptions(url: str) -> List[Error]:
    """
    Checks for JavaScript exceptions in the browser console when loading the specified URL.

    Args:
        url (str): The URL of the web page to check for JavaScript exceptions.
    Returns:
        List[Error]: A list of Error objects representing any JavaScript exceptions found in the console.
    """
    errors: List[Error] = []

    async with async_playwright() as playwright:
        browser, page, console_messages, page_errors, nav_error = await _load_page_with_listeners(
            playwright, url
        )

        if nav_error:
            errors.append(
                Error(
                    type=ErrorType.JAVASCRIPT,
                    subtype=ErrorSubType.JS_CONSOLE_ERROR,
                    message=f"Navigation error: {nav_error}",
                )
            )

        _append_js_errors(errors, console_messages, page_errors)
        await browser.close()
    return errors

async def check_buttons_forms(url: str) -> List[Error]:
    """
    Checks for JavaScript exceptions related to buttons and forms on the web page.
    Warning: this function performs real clicks/submits and may trigger side effects.

    Args:
        url (str): The URL of the web page to check for JavaScript exceptions related to buttons and forms.
    Returns:
        List[Error]: A list of Error objects representing any JavaScript exceptions found related to buttons and forms.
    """
    errors: List[Error] = []

    async with async_playwright() as playwright:
        browser, page, console_messages, page_errors, nav_error = await _load_page_with_listeners(
            playwright, url
        )

        if nav_error:
            await browser.close()
            return [
                Error(
                    type=ErrorType.JAVASCRIPT,
                    subtype=ErrorSubType.JS_CONSOLE_ERROR,
                    message=f"Navigation error: {nav_error}",
                )
            ]

        buttons = await page.query_selector_all("button, input[type='button'], input[type='submit']")
        for button in buttons[:10]:
            try:
                await button.click(timeout=2000)
                await page.wait_for_timeout(300)
            except Exception as exc:
                logger.debug("Button interaction failed on %s: %s", url, exc)
                continue

        forms = await page.query_selector_all("form")
        for form in forms[:10]:
            try:
                await form.evaluate("f => f.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))")
                await page.wait_for_timeout(300)
            except Exception as exc:
                logger.debug("Form interaction failed on %s: %s", url, exc)
                continue

        _append_js_errors(errors, console_messages, page_errors)
        await browser.close()
    return errors

async def check_responsiveness(url: str) -> List[Error]:
    """
    Checks if the web page is responsive and adapts correctly to different screen sizes.
    Args:
        url (str): The URL of the web page to check for responsiveness.
    Returns:
        List[Error]: A list of Error objects representing any responsiveness issues found on the web page
    """
    errors: List[Error] = []
    viewports = [
        {"width": 375, "height": 667},
        {"width": 768, "height": 1024},
        {"width": 1366, "height": 768},
    ]

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)

        for viewport in viewports:
            page = await browser.new_page(viewport=viewport)
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                has_horizontal_overflow = await page.evaluate(
                    "() => document.documentElement.scrollWidth > window.innerWidth + 1"
                )
                has_vertical_overflow = await page.evaluate(
                    "() => document.documentElement.scrollHeight > window.innerHeight + 1"
                )

                if has_horizontal_overflow:
                    errors.append(
                        Error(
                            type=ErrorType.USER_EXPERIENCE,
                            subtype=ErrorSubType.NON_RESPONSIVE_LAYOUT,
                            message=f"Horizontal overflow detected at {viewport['width']}x{viewport['height']}",
                        )
                    )
                if has_vertical_overflow:
                    errors.append(
                        Error(
                            type=ErrorType.USER_EXPERIENCE,
                            subtype=ErrorSubType.NON_RESPONSIVE_LAYOUT,
                            message=f"Vertical overflow detected at {viewport['width']}x{viewport['height']}",
                        )
                    )
            except Exception as exc:
                errors.append(
                    Error(
                        type=ErrorType.USER_EXPERIENCE,
                        subtype=ErrorSubType.NON_RESPONSIVE_LAYOUT,
                        message=f"Responsive check failed at {viewport['width']}x{viewport['height']}: {exc}",
                    )
                )
            finally:
                await page.close()

        await browser.close()
    return errors

