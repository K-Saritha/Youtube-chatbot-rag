# Compatibility module for Python 3.13+
# This provides minimal cgi compatibility for libraries that still depend on it

import sys
import warnings

# Redirect to urllib.parse for the few functions that httpx might need
from urllib.parse import parse_qs, parse_qsl, quote, unquote, quote_plus, unquote_plus

# Add these to this module's namespace
__all__ = ['parse_qs', 'parse_qsl', 'quote', 'unquote', 'quote_plus', 'unquote_plus']

# Any attempt to import from cgi in the main code will use this module instead
