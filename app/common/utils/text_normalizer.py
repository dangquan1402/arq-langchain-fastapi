"""
Text normalization utilities for standardizing text from various sources.
"""

import re
import unicodedata
from typing import Dict, List, Set, Optional
from loguru import logger

class TextNormalizer:
    """
    A class providing various text normalization functions for cleaning
    and standardizing text extracted from documents.
    """
    
    # Common normalization dictionaries
    LIGATURE_REPLACEMENTS = {
        'ﬁ': 'fi',
        'ﬂ': 'fl',
        'ﬀ': 'ff',
        'ﬃ': 'ffi',
        'ﬄ': 'ffl',
    }
    
    QUOTE_REPLACEMENTS = {
        ''': "'",
        ''': "'",
        '"': '"',
        '"': '"',
        '„': '"',
        '«': '"',
        '»': '"',
        '‹': "'",
        '›': "'",
    }
    
    DASH_REPLACEMENTS = {
        '—': '-',  # em dash
        '–': '-',  # en dash
        '‐': '-',  # hyphen
        '−': '-',  # minus
        '‒': '-',  # figure dash
        '―': '-',  # horizontal bar
    }
    
    OTHER_PUNCTUATION = {
        '…': '...',
        '•': '*',
        '‣': '*',
        '⁃': '-',
        '·': '*',
    }
    
    @staticmethod
    def normalize_unicode(text: str, form: str = 'NFC') -> str:
        """
        Apply Unicode normalization to the input text.
        
        Args:
            text: The text to normalize
            form: Unicode normalization form ('NFC', 'NFD', 'NFKC', 'NFKD')
                  NFC: Canonical composition
                  NFD: Canonical decomposition
                  NFKC: Compatibility composition
                  NFKD: Compatibility decomposition
        
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        logger.debug(f"Applying Unicode normalization form {form}")
        return unicodedata.normalize(form, text)
    
    @staticmethod
    def remove_accents(text: str) -> str:
        """
        Remove accents from characters.
        
        Args:
            text: The text to process
            
        Returns:
            Text without accents
        """
        if not text:
            return ""
            
        logger.debug("Removing accents from text")
        nfkd_form = unicodedata.normalize('NFKD', text)
        return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalize whitespace in text.
        
        Args:
            text: The text to normalize
            
        Returns:
            Text with normalized whitespace
        """
        if not text:
            return ""
            
        logger.debug("Normalizing whitespace")
        # Replace all whitespace sequences (including tabs, newlines) with single space
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        return text.strip()
    
    @staticmethod
    def normalize_line_breaks(text: str, max_consecutive: int = 2) -> str:
        """
        Normalize line breaks in text.
        
        Args:
            text: The text to normalize
            max_consecutive: Maximum number of consecutive line breaks to keep
            
        Returns:
            Text with normalized line breaks
        """
        if not text:
            return ""
            
        logger.debug(f"Normalizing line breaks (max {max_consecutive})")
        # Replace multiple newlines with the maximum allowed
        pattern = r'\n{' + str(max_consecutive + 1) + r',}'
        replacement = '\n' * max_consecutive
        return re.sub(pattern, replacement, text)
    
    @staticmethod
    def replace_characters(text: str, replacements: Dict[str, str]) -> str:
        """
        Replace characters according to a replacement dictionary.
        
        Args:
            text: The text to process
            replacements: Dictionary mapping characters to their replacements
            
        Returns:
            Text with characters replaced
        """
        if not text:
            return ""
        
        logger.debug(f"Replacing {len(replacements)} character patterns")
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    @staticmethod
    def filter_categories(text: str, allowed_categories: Optional[Set[str]] = None) -> str:
        """
        Keep only characters from specified Unicode categories.
        
        Args:
            text: The text to filter
            allowed_categories: Set of allowed Unicode category prefixes
                                (e.g. {'L', 'N', 'P', 'Z'} for letters, numbers, 
                                punctuation, and separators)
                                
        Returns:
            Filtered text
        """
        if not text:
            return ""
        
        if allowed_categories is None:
            # Default: Allow letters, numbers, punctuation, symbols, and separators
            allowed_categories = {'L', 'N', 'P', 'S', 'Z'}
        
        logger.debug(f"Filtering Unicode categories: keeping {allowed_categories}")
        return ''.join(c for c in text if unicodedata.category(c)[0] in allowed_categories)
    
    @classmethod
    def comprehensive_normalize(cls, text: str) -> str:
        """
        Apply comprehensive text normalization.
        
        Args:
            text: The text to normalize
            
        Returns:
            Fully normalized text
        """
        if not text:
            return ""
        
        logger.debug("Starting comprehensive text normalization")
        
        # Apply initial Unicode normalization
        text = cls.normalize_unicode(text, 'NFC')
        
        # Replace special characters
        all_replacements = {}
        all_replacements.update(cls.LIGATURE_REPLACEMENTS)
        all_replacements.update(cls.QUOTE_REPLACEMENTS)
        all_replacements.update(cls.DASH_REPLACEMENTS)
        all_replacements.update(cls.OTHER_PUNCTUATION)
        text = cls.replace_characters(text, all_replacements)
        
        # Normalize line breaks
        text = cls.normalize_line_breaks(text)
        
        # Remove control characters
        text = ''.join(c for c in text if unicodedata.category(c)[0] != 'C' or c in '\n\t')
        
        # Keep only allowed categories plus newlines and tabs
        allowed = {'L', 'N', 'P', 'S', 'Z'}
        text = ''.join(c for c in text if unicodedata.category(c)[0] in allowed or c in '\n\t')
        
        # Normalize whitespace within lines
        lines = text.split('\n')
        normalized_lines = []
        for line in lines:
            # Replace multiple spaces with a single space and trim
            normalized_line = re.sub(r' +', ' ', line).strip()
            if normalized_line:  # Only add non-empty lines
                normalized_lines.append(normalized_line)
                
        # Join lines with newlines
        text = '\n'.join(normalized_lines)
        
        logger.debug("Comprehensive text normalization complete")
        return text
