import logging
import time
from typing import List
from objects.error import Error
from error_enums.error_type import ErrorType
from error_enums.error_subtype import ErrorSubType
from playwright.async_api import async_playwright


logger = logging.getLogger(__name__)


async def check_performance_errors(
    url: str,
    slow_image_threshold: int = 500,
    page_size_threshold: float = 5.0,
    http_requests_threshold: int = 100,
) -> List[Error]:
    """
    Checks performance metrics and returns errors.

    Args:
        url: URL to check
        slow_image_threshold: Time in ms for slow images
        page_size_threshold: Size in MB
        http_requests_threshold: Max HTTP requests
    
    Returns:
        List of performance errors
    """
    errors: List[Error] = []
    load_time = 0
    total_size = 0
    http_request_count = 0

    def on_request(request):
        nonlocal http_request_count
        http_request_count += 1

    def on_response(response):
        nonlocal total_size
        try:
            content_length = response.headers.get("content-length")
            if content_length:
                total_size += int(content_length)
        except Exception as exc:
            logger.debug("Error measuring response size: %s", exc)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()

        page.on("request", on_request)
        page.on("response", on_response)

        start_time = time.time()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            # Wait for images and resources to load
            await page.wait_for_load_state("networkidle", timeout=10000)
        except Exception as exc:
            logger.warning("Navigation error on %s: %s", url, exc)
        load_time = time.time() - start_time

        # Check slow images
        try:
            perf_entries = await page.evaluate("""
                () => {
                    const entries = performance.getEntriesByType('resource');
                    return entries
                        .filter(e => e.initiatorType === 'img' && e.duration > 0)
                        .map(e => ({ url: e.name, duration: Math.round(e.duration) }));
                }
            """)

            for entry in perf_entries:
                if entry["duration"] > slow_image_threshold:
                    errors.append(
                        Error(
                            type=ErrorType.PERFORMANCE,
                            subtype=ErrorSubType.SLOW_IMAGE_LOADING,
                            message=f"Image slow loading ({entry['duration']}ms > {slow_image_threshold}ms): {entry['url']}",
                        )
                    )
        except Exception as exc:
            logger.warning("Error collecting image performance: %s", exc)

        await browser.close()

    # Check page size
    page_size_mb = total_size / (1024 * 1024)
    if page_size_mb > page_size_threshold:
        errors.append(
            Error(
                type=ErrorType.PERFORMANCE,
                subtype=ErrorSubType.TOTAL_PAGE_SIZE,
                message=f"Total page size too large: {page_size_mb:.2f}MB > {page_size_threshold}MB",
            )
        )

    # Check HTTP requests
    if http_request_count > http_requests_threshold:
        errors.append(
            Error(
                type=ErrorType.PERFORMANCE,
                subtype=ErrorSubType.TOTAL_HTTP_REQUESTS,
                message=f"Too many HTTP requests: {http_request_count} > {http_requests_threshold}",
            )
        )

    return errors

