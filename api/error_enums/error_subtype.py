from enum import Enum

class ErrorSubType(Enum):
    "Defines specific subtypes of errors for each main error type."
    
    # User Experience SubErrors
    PAGE_LOAD_TIME = "page_load_time"
    READABILITY_CONTRAST = "readability_contrast"
    READABILITY_FONT_SIZE = "readability_font_size"
    READABILITY_LINE_HEIGHT = "readability_line_height"
    READABILITY_SENTENCE_LENGTH = "readability_sentence_length"
    NON_RESPONSIVE_LAYOUT = "non_responsive_layout"
    BROKEN_BUTTON = "broken_button"
    BROKEN_FORM = "broken_form"
    BROKEN_LINK = "broken_link"
    UNNECESSARY_REDIRECTION = "unnecessary_redirection"
    PAGE_NOT_FOUND_404 = "page_not_found_404"

    # JAVASCRIPT SubErrors
    JS_CONSOLE_ERROR = "js_console_error"

    # HTML SubErrors
    INVALID_HTML_STRUCTURE = "invalid_html_structure"

    # Security SubErrors
    MISSING_HTTPS = "missing_https"
    INVALID_SSL_CERT = "invalid_ssl_cert"
    UNSECURE_FORM = "unsecure_form"
    COOKIE_MISSING_SECURE_FLAG = "cookie_missing_secure_flag"
    COOKIE_MISSING_HTTPONLY_FLAG = "cookie_missing_httponly_flag"
    COOKIE_MISSING_SAMESITE_FLAG = "cookie_missing_samesite_flag"

    # Performance SubErrors
    TOTAL_PAGE_SIZE = "total_page_size"
    TOTAL_HTTP_REQUESTS = "total_http_requests"
    SLOW_IMAGE_LOADING = "slow_image_loading"

    # Accessibility SubErrors
    MISSING_ALT_ATTRIBUTE = "missing_alt_attribute"
    NON_DESCRIPTIVE_LINK_TEXT = "non_descriptive_link_text"
    NON_DESCRIPTIVE_BUTTON_TEXT = "non_descriptive_button_text"