from typing import List
from bs4 import BeautifulSoup
import re

from objects.error import Error
from error_enums.error_type import ErrorType
from error_enums.error_subtype import ErrorSubType


def hex_to_rgb(hex_color: str):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def relative_luminance(rgb):
    """Calculate relative luminance of a color."""
    if not rgb or len(rgb) != 3:
        return None
    
    def srgb_to_linear(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    
    r_lin, g_lin, b_lin = [srgb_to_linear(c) for c in rgb]
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(rgb_text, rgb_bg):
    """Calculate contrast ratio between text and background colors (WCAG)."""
    if not rgb_text or not rgb_bg:
        return None
    
    L1 = relative_luminance(rgb_text)
    L2 = relative_luminance(rgb_bg)
    
    if L1 is None or L2 is None:
        return None
    
    return (max(L1, L2) + 0.05) / (min(L1, L2) + 0.05)


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


def _check_sentence_length(text: str, max_words: int = 35) -> List[tuple[str, int]]:
    """
    Extract sentences and check if they exceed the recommended word count.
    Longer sentences are harder to read and reduce comprehension.
    
    Args:
        text (str): Text content to analyze.
        max_words (int): Maximum recommended words per sentence.
    
    Returns:
        List[tuple]: List of (sentence, word_count) for sentences exceeding max_words.
    """
    # Split by sentence-ending punctuation
    sentences = re.split(r'[.!?]+', text)
    long_sentences = []
    
    for sentence in sentences:
        # Clean and count words
        cleaned = sentence.strip()
        if not cleaned:
            continue
        
        words = cleaned.split()
        word_count = len(words)
        
        # Flag sentences exceeding threshold
        if word_count > max_words:
            long_sentences.append((cleaned[:100], word_count))  # Store first 100 chars
    
    return long_sentences


def check_readability(soup: BeautifulSoup) -> List[Error]:
    """
    Checks text readability: font size, line-height, and sentence length.
    
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
    
    # Check sentence length and color contrast in text content
    text_elements = soup.find_all(['p', 'li', 'span', 'div'])
    
    for elem in text_elements:
        # Check sentence length
        text = elem.get_text(strip=True)
        if text and len(text.split()) > 35:
            long_sentences = _check_sentence_length(text, max_words=35)
            for sentence, word_count in long_sentences:
                errors.append(
                    Error(
                        type=ErrorType.USER_EXPERIENCE,
                        subtype=ErrorSubType.READABILITY_SENTENCE_LENGTH,
                        message=f"Sentence too long ({word_count} words, max 35 recommended): '{sentence}...'",
                    )
                )
        
        # Check color contrast
        style = elem.get('style', '')
        if style:
            text_color_match = re.search(r'color\s*:\s*([^;]+)', style, re.IGNORECASE)
            bg_color_match = re.search(r'background(-color)?\s*:\s*([^;]+)', style, re.IGNORECASE)

            if text_color_match:
                text_rgb = hex_to_rgb(text_color_match.group(1).strip())
                if text_rgb:
                    bg_rgb = (255, 255, 255)  # default white
                    if bg_color_match:
                        bg_rgb = hex_to_rgb(bg_color_match.group(2).strip()) or (255, 255, 255)
                    
                    ratio = contrast_ratio(text_rgb, bg_rgb)
                    if ratio and ratio < 4.5:  # WCAG AA standard
                        errors.append(
                            Error(
                                type=ErrorType.USER_EXPERIENCE,
                                subtype=ErrorSubType.READABILITY_SENTENCE_LENGTH,
                                message=f"Low color contrast ({ratio:.2f}:1, min 4.5:1 WCAG AA): {str(elem)[:80]}",
                            )
                        )
    
    return errors
