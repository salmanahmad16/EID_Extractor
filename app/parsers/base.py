from datetime import datetime
import re

class BaseParser:
    def clean_text(self, text):
        return text.strip()

    def parse_date(self, date_str):
        if not date_str:
            return None
            
        # Strategy 1: Clean the string (remove non-date chars)
        # Replacing common separator errors (comma to dot/slash)
        # e.g. 01.01,2000 -> 01.01.2000
        clean_str = re.sub(r'[,]', '.', date_str)
        clean_str = re.sub(r'[^\d\.\/\-]', '', clean_str)
        
        # Extended formats list
        formats = [
            '%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y',
            '%Y.%m.%d', '%Y/%m/%d', '%Y-%m-%d',
            '%d%m%Y',
            '%m/%d/%Y', # US Format
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(clean_str, fmt)
                if 1900 <= dt.year <= 2100:
                    return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
                
        # Strategy 2: Fallback regex on cleaned string
        try:
            # simple regex finder for DD.MM.YYYY or similar
            # Allow keys that might have been merged
            search = re.search(r'(\d{2})[\./\-](\d{2})[\./\-](\d{4})', clean_str)
            if search:
                d, m, y = search.groups()
                # Validate ranges slightly
                if 1 <= int(m) <= 12 and 1 <= int(d) <= 31:
                     return f"{y}-{m}-{d}"
        except:
            pass
            
        return date_str  # Return original if all else fails

    def parse(self, ocr_data, side_hint=None):
        """
        Abstract method to be implemented by country parsers.
        Should return a dictionary with parsed data.
        """
        raise NotImplementedError
