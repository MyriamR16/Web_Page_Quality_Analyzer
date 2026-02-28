from urllib import request
from urllib.parse import urljoin
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import requests

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

def check_broken_link(absolute_url: str, base_url: str) -> dict:
    # Skip the base URL itself
    if absolute_url == base_url:
        return None
    try:
        # Create a HEAD request to check if the link is valid
        req = request.Request(absolute_url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)') # User-Agent header to not let think im a bot
        
        response = request.urlopen(req, timeout=5)
        status_code = response.status
        
        # If status code is >= 400, it's a broken link 
        if status_code >= 400:
            return {
                'url': absolute_url,
                'status_code': status_code,
            }
        
        return None # Link is not broken
            
    except HTTPError as e:
        # HTTPError is raised for 4xx and 5xx status codes
        return {
            'url': absolute_url,
            'status_code': e.code,
            'error': str(e),
        }
    except (URLError, Exception) as e:
        # URLError or other exceptions (timeout, connection error, etc.)
        return {
            'url': absolute_url,
            'status_code': None,
            'error': str(e),
        }

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
        broken_images.append(result)
        
    return broken_images


def check_alt_attributes(soup: BeautifulSoup) -> list:
    """
    Checks for images without alt attributes in the web page and returns a list of such images.
    
    Args:
        soup (BeautifulSoup): A BeautifulSoup object representing the parsed HTML.
    
    Returns:
        list: A list of image URLs that do not have alt attributes.
    """
    images_without_alt = []
    images = soup.find_all('img')

    for img in images:
        if not img.has_attr('alt') or not img['alt'].strip():
            images_without_alt.append(img.get('src', ''))
    return images_without_alt

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
        if not text:
            non_descriptive_elements.append({
                'type': 'link',
                'element': str(link),
            })
    
    # Check buttons
    buttons = soup.find_all('button')
    for button in buttons:
        text = button.get_text(strip=True)
        if not text:
            non_descriptive_elements.append({
                'type': 'button',
                'element': str(button),
            })
    return non_descriptive_elements