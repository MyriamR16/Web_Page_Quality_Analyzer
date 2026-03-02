from typing import List
from bs4 import BeautifulSoup
import re

from objects.error import Error
from error_enums.error_type import ErrorType
from error_enums.error_subtype import ErrorSubType


def _extract_size_px(value: str) -> float | None:
    """Extract font size in pixels from CSS value."""
    if not value:
        return None
    
    value = value.strip().lower()
    
    # Direct pixel values
    if value.endswith('px'):
        try:
            return float(value[:-2])
        except ValueError:
            return None
    
    # Convert common relative units to approximate px
    if value.endswith('pt'):
        try:
            return float(value[:-2]) * 1.33  # 1pt ≈ 1.33px
        except ValueError:
            return None
    
    if value.endswith('em') or value.endswith('rem'):
        try:
            return float(value[:-2 if value.endswith('em') else -3]) * 16  # Assuming 16px base
        except ValueError:
            return None
    
    return None


def _extract_line_height(value: str) -> float | None:
    """Extract line-height as a ratio."""
    if not value:
        return None
    
    value = value.strip().lower()
    
    # Unitless (already a ratio)
    try:
        return float(value)
    except ValueError:
        pass
    
    # Percentage
    if value.endswith('%'):
        try:
            return float(value[:-1]) / 100
        except ValueError:
            return None
    
    return None


def check_readability(soup: BeautifulSoup) -> List[Error]:
    """
    Checks text readability: font size, line-height.
    
    Args:
        soup (BeautifulSoup): Parsed HTML document.
    
    Returns:
        List[Error]: List of readability errors found.
    """
    errors: List[Error] = []
    
    # Check inline styles for font-size
    elements_with_style = soup.find_all(style=True)
    for elem in elements_with_style[:20]:  # Limit to first 20 for performance
        style = elem.get('style', '')
        
        # Check font-size
        font_size_match = re.search(r'font-size\s*:\s*([^;]+)', style, re.IGNORECASE)
        if font_size_match:
            size_px = _extract_size_px(font_size_match.group(1))
            if size_px and size_px < 14:
                errors.append(
                    Error(
                        type=ErrorType.USER_EXPERIENCE,
                        subtype=ErrorSubType.NON_RESPONSIVE_LAYOUT,
                        message=f"Font size too small ({size_px:.0f}px, minimum 14px recommended): {str(elem)[:100]}",
                    )
                )
        
        # Check line-height
        line_height_match = re.search(r'line-height\s*:\s*([^;]+)', style, re.IGNORECASE)
        if line_height_match:
            ratio = _extract_line_height(line_height_match.group(1))
            if ratio and ratio < 1.4:
                errors.append(
                    Error(
                        type=ErrorType.USER_EXPERIENCE,
                        subtype=ErrorSubType.NON_RESPONSIVE_LAYOUT,
                        message=f"Line-height too small ({ratio:.1f}, minimum 1.4 recommended): {str(elem)[:100]}",
                    )
                )
    
    # Check <style> tags for global issues
    style_tags = soup.find_all('style')
    for style_tag in style_tags[:3]:  # Limit to first 3 style blocks
        css_content = style_tag.string or ''
        
        # Find all font-size declarations
        font_sizes = re.findall(r'font-size\s*:\s*([^;}\n]+)', css_content, re.IGNORECASE)
        for size_str in font_sizes[:10]:  # Check first 10
            size_px = _extract_size_px(size_str)
            if size_px and size_px < 14:
                errors.append(
                    Error(
                        type=ErrorType.USER_EXPERIENCE,
                        subtype=ErrorSubType.NON_RESPONSIVE_LAYOUT,
                        message=f"CSS font-size too small: {size_str.strip()} ({size_px:.0f}px, minimum 14px)",
                    )
                )
                break
    
    return errors
