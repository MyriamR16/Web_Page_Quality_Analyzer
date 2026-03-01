import asyncio
from flask import Blueprint, jsonify
from flask_pydantic import validate
from pydantic import BaseModel
from typing import List

from objects.error import Error
from utils.html_validator import validate_html_w3c
from utils.scraping import get_page_html, get_soup, check_broken_links, check_broken_images, check_alt_attributes, check_descriptive_text
from utils.security import check_https, check_ssl_certificate, check_unsecure_forms, check_cookies_flags
from utils.javascript_validator import check_console_exceptions, check_buttons_forms, check_responsiveness
from utils.performance import check_performance_errors

analyse_bp = Blueprint('analyse', __name__)


class AnalyseQuery(BaseModel):
    url: str


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
        
        errors.extend(check_broken_links(soup, url))
        errors.extend(check_broken_images(soup, url))
        errors.extend(check_alt_attributes(soup))
        errors.extend(check_descriptive_text(soup))
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
        "errors": [error.model_dump() for error in errors],
        "total_errors": len(errors)
    })

