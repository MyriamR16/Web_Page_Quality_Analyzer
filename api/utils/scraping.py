from urllib import request
from urllib.parse import urljoin
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import requests
from playwright.sync_api import sync_playwright

def get_page_html(url: str) -> str :
    """
    Fetches the HTML content of a web page using its URL.
    
    Args:
        url (str): The URL of the web page to fetch.
    
    Returns:
        str: The HTML content of the web page.
    
    Raises:
        Exception: If there is an error during the fetching process.
    """
    try:
        response = requests.get(url, timeout=30, verify=True)
        response.raise_for_status() 
        html_content = response.text
        return html_content
    except requests.exceptions.SSLError:
        # Retry without SSL verification if certificate fails
        try:
            response = requests.get(url, timeout=30, verify=False)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise Exception(f"Error fetching page HTML: {str(e)}")
    except Exception as e:
        raise Exception(f"Error fetching page HTML: {str(e)}")


def get_soup(html : str) -> BeautifulSoup:
    """
    Parses the HTML content of a web page and returns a BeautifulSoup object.
    
    Args:
        html (str): The HTML content of the web page.
    Returns:
        BeautifulSoup: A BeautifulSoup object representing the parsed HTML.
    """
    return BeautifulSoup(html, 'html.parser')


def _check_link_with_playwright(absolute_url: str) -> dict | None:
    """
    Confirms link availability using a real browser navigation.
    Returns broken-link dict only when browser gets HTTP >= 400.
    """
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            response = page.goto(absolute_url, wait_until='domcontentloaded', timeout=15000)
            status_code = response.status if response else None
            browser.close()

            if status_code is not None and status_code >= 400:
                return {
                    'url': absolute_url,
                    'status_code': status_code,
                }
            return None
    except Exception:
        return None

def check_broken_link(absolute_url: str, base_url: str) -> dict:
    # Skip the base URL itself
    if absolute_url == base_url:
        return None

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    try:
        # Trying HEAD first
        req = request.Request(absolute_url, method='HEAD', headers=headers)
        response = request.urlopen(req, timeout=10)
        status_code = response.status

        if status_code >= 400:
            return {
                'url': absolute_url,
                'status_code': status_code,
            }
        return None

    except HTTPError as e:
        # Some servers reject HEAD; retry with GET before flagging broken
        if e.code in (403, 405):
            try:
                get_req = request.Request(absolute_url, headers=headers)
                get_response = request.urlopen(get_req, timeout=10)
                get_status = get_response.status
                if get_status >= 400:
                    return {
                        'url': absolute_url,
                        'status_code': get_status,
                    }
                return None
            except HTTPError as get_error:
                if get_error.code >= 400:
                    return {
                        'url': absolute_url,
                        'status_code': get_error.code,
                        'error': str(get_error),
                    }
                return None
            except (URLError, Exception):
                # Network or anti-bot issue: not enough proof that link is broken
                return None

        if e.code >= 400:
            playwright_result = _check_link_with_playwright(absolute_url)
            if playwright_result:
                playwright_result['error'] = str(e)
                return playwright_result
            return None
        return None

    except (URLError, Exception):
        # Timeout/DNS/connection issues are not reliable proof of broken link
        return None

def check_broken_links(soup: BeautifulSoup, base_url: str) -> list:
    """
    Checks for broken links in the web page and returns a list of broken links.
    
    Args:
        soup (BeautifulSoup): A BeautifulSoup object representing the parsed HTML.
        base_url (str): The base URL of the web page.
    
    Returns:
        list: A list of broken links found in the web page.
    """
    broken_links = []
    
    # Extract all links from the page
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link.get('href')
        
        # Skip anchors, javascript, mailto, and other non-HTTP links
        if not href or href.startswith(('#', 'javascript:', 'mailto:')):
            continue
        
        # Convert relative URLs to absolute URLs in the case of internal links
        absolute_url = urljoin(base_url, href)
        result = check_broken_link(absolute_url, base_url)
        if not result:
            continue
        
        result['link_text'] = link.get_text(strip=True) or '(no text)'
        result['href_attr'] = href
        result['html'] = str(link)[:200]
        broken_links.append(result)
    
    return broken_links

def check_broken_images(soup: BeautifulSoup, base_url: str) -> list:
    """
    Checks for broken images in the web page and returns a list of broken image URLs.
    
    Args:
        soup (BeautifulSoup): A BeautifulSoup object representing the parsed HTML.
        base_url (str): The base URL of the web page.
    
    Returns:
        list: A list of broken image URLs found in the web page.
    """
    broken_images = []
    
    # Extract all image tags from the page
    images = soup.find_all('img', src=True)
    
    for img in images:
        src = img.get('src')
        
        # Skip if src is empty
        if not src:
            continue
        
        # Convert relative URLs to absolute URLs
        absolute_url = urljoin(base_url, src)
        result = check_broken_link(absolute_url, base_url)
        if not result:
            continue
        
        result['alt_text'] = img.get('alt', '(missing alt)') or '(empty alt)'
        result['src_attr'] = src
        result['html'] = str(img)[:200]
        broken_images.append(result)
        
    return broken_images


def check_alt_attributes(soup: BeautifulSoup) -> list:
    """
    Checks for images without alt attributes in the web page and returns a list of such images.
    
    Args:
        soup (BeautifulSoup): A BeautifulSoup object representing the parsed HTML.
    
    Returns:
        list: A list of images without alt attributes with context.
    """
    images_without_alt = []
    images = soup.find_all('img')

    for img in images:
        if not img.has_attr('alt') or not img['alt'].strip():
            images_without_alt.append({
                'src': img.get('src', '(no src)'),
                'alt': img.get('alt', '(missing)'),
                'html': str(img)[:200],
            })
    return images_without_alt


def _has_accessible_name(element, soup: BeautifulSoup) -> bool:
    aria_label = (element.get('aria-label') or '').strip()
    title = (element.get('title') or '').strip()
    if aria_label or title:
        return True

    aria_labelledby = (element.get('aria-labelledby') or '').strip()
    if aria_labelledby:
        for label_id in aria_labelledby.split():
            labelled = soup.find(id=label_id)
            if labelled and labelled.get_text(strip=True):
                return True

    for img in element.find_all('img'):
        alt = (img.get('alt') or '').strip()
        if alt:
            return True

    for media in element.find_all(['svg', 'i']):
        media_aria = (media.get('aria-label') or '').strip()
        media_title = (media.get('title') or '').strip()
        if media_aria or media_title:
            return True

    return False

def check_descriptive_text(soup: BeautifulSoup) -> list:
    """
    Checks for absence of descriptive text in links and buttons.
    
    Args:
        soup (BeautifulSoup): A BeautifulSoup object representing the parsed HTML.
    Returns:
        list: A list of instances of non-descriptive text found in the web page.
    """
    non_descriptive_elements = []
    
    # Check links
    links = soup.find_all('a')
    for link in links:
        text = link.get_text(strip=True)
        if not text and not _has_accessible_name(link, soup):
            non_descriptive_elements.append({
                'type': 'link',
                'href': link.get('href', '(no href)'),
                'html': str(link)[:200],
            })
    
    # Check buttons
    buttons = soup.find_all('button')
    for button in buttons:
        text = button.get_text(strip=True)
        if not text and not _has_accessible_name(button, soup):
            non_descriptive_elements.append({
                'type': 'button',
                'html': str(button)[:200],
            })
    return non_descriptive_elements