import asyncio
from flask import Blueprint, jsonify
from flask_pydantic import validate
from pydantic import BaseModel
from typing import List

from objects.error import Error
from error_enums.error_type import ErrorType
from error_enums.error_subtype import ErrorSubType
from utils.html_validator import validate_html_w3c
from utils.scraping import get_page_html, get_soup, check_broken_links, check_broken_images, check_alt_attributes, check_descriptive_text
from utils.readability import check_readability
from utils.security import check_https, check_ssl_certificate, check_unsecure_forms, check_cookies_flags
from utils.javascript_validator import check_console_exceptions, check_buttons_forms, check_responsiveness
from utils.performance import check_performance_errors

analyse_bp = Blueprint('analyse', __name__)


class AnalyseQuery(BaseModel):
    url: str


def _map_scraping_checks_to_errors(soup, url: str) -> List[Error]:
    mapped_errors: List[Error] = []

    for broken_link in check_broken_links(soup, url):
        link_text = broken_link.get('link_text', '(no text)')[:80]
        href = broken_link.get('href_attr', broken_link.get('url', ''))[:100]
        status = broken_link.get('status_code', '?')
        mapped_errors.append(
            Error(
                type=ErrorType.USER_EXPERIENCE,
                subtype=ErrorSubType.BROKEN_LINK,
                message=f'Broken link: "{link_text}" → href="{href}" (HTTP {status})',
            )
        )

    for broken_image in check_broken_images(soup, url):
        alt = broken_image.get('alt_text', '(missing alt)')[:80]
        src = broken_image.get('src_attr', broken_image.get('url', ''))[:100]
        status = broken_image.get('status_code', '?')
        mapped_errors.append(
            Error(
                type=ErrorType.USER_EXPERIENCE,
                subtype=ErrorSubType.PAGE_NOT_FOUND_404,
                message=f'Broken image: alt="{alt}" → src="{src}" (HTTP {status})',
            )
        )

    for image_info in check_alt_attributes(soup):
        src = image_info.get('src', '(no src)')[:100]
        alt = image_info.get('alt', '(missing)')[:80]
        mapped_errors.append(
            Error(
                type=ErrorType.ACCESSIBILITY,
                subtype=ErrorSubType.MISSING_ALT_ATTRIBUTE,
                message=f'Image missing/empty alt: src="{src}" alt="{alt}"',
            )
        )

    for element in check_descriptive_text(soup):
        element_type = element.get("type")
        if element_type == "button":
            html_snippet = element.get("html", "")[:120]
            mapped_errors.append(
                Error(
                    type=ErrorType.ACCESSIBILITY,
                    subtype=ErrorSubType.NON_DESCRIPTIVE_BUTTON_TEXT,
                    message=f'Button empty/no text: {html_snippet}',
                )
            )
        else:
            href = element.get("href", "(no href)")[:80]
            html_snippet = element.get("html", "")[:120]
            mapped_errors.append(
                Error(
                    type=ErrorType.ACCESSIBILITY,
                    subtype=ErrorSubType.NON_DESCRIPTIVE_LINK_TEXT,
                    message=f'Link empty/no text: href="{href}" | {html_snippet}',
                )
            )

    return mapped_errors


async def collect_all_errors(url: str) -> List[Error]:
    """Collects all errors from all validators."""
    errors: List[Error] = []
    
    # HTML validation
    try:
        html_errors = validate_html_w3c(url)
        errors.extend(html_errors)
    except Exception as e:
        print(f"HTML validation error: {e}")
    
    # Scraping-based checks
    try:
        html = get_page_html(url)
        soup = get_soup(html)

        errors.extend(_map_scraping_checks_to_errors(soup, url))
        errors.extend(check_readability(soup))
    except Exception as e:
        print(f"Scraping error: {e}")
    
    # Security checks
    try:
        https_error = check_https(url)
        if https_error:
            errors.append(https_error)
        
        ssl_error = await check_ssl_certificate(url)
        if ssl_error:
            errors.append(ssl_error)
        
        errors.extend(await check_unsecure_forms(url))
        errors.extend(await check_cookies_flags(url))
    except Exception as e:
        print(f"Security check error: {e}")
    
    # JavaScript checks
    try:
        errors.extend(await check_console_exceptions(url))
        errors.extend(await check_buttons_forms(url))
        errors.extend(await check_responsiveness(url))
    except Exception as e:
        print(f"JavaScript check error: {e}")
    
    # Performance checks
    try:
        errors.extend(await check_performance_errors(url))
    except Exception as e:
        print(f"Performance check error: {e}")
    
    return errors


@analyse_bp.get('/analyse')
@validate()
def analyse(query: AnalyseQuery):
    """
    Route to analyze a web page and return all detected errors.
    """
    url = query.url
    print(f"Analyzing URL: {url}")
    
    errors = asyncio.run(collect_all_errors(url))
    
    return jsonify({
        "url": url,
        "errors": [error.model_dump(mode="json") for error in errors],
        "total_errors": len(errors)
    })

