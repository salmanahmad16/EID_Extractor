from .base import BaseParser
import re

class USAParser(BaseParser):
    def parse(self, ocr_data, side_hint=None):
        raw_lines = [item['text'] for item in ocr_data]
        all_text = "\n".join(raw_lines)
        
        data = {
            'country': 'USA',
            'id_number': None,
            'name': None,
            'dob': None,
            'address': None,
            'expiry_date': None,
            'issue_date': None,
            'sex': None
        }
        
        # 1. ID Number (DL / LIC / ID)
        # Look for "DL", "LIC", "ID" followed by alphanumeric
        # Pattern varies wildly: 9 digits, 1 letter + digits, etc.
        # \b ensures we don't start in middle of word
        # Capture group should avoid newlines
        id_match = re.search(r'(?:DL|LIC|ID|No)\s*[:\.]?\s*([A-Za-z0-9\-]{5,20})', all_text, re.IGNORECASE)
        if id_match:
            cand = id_match.group(1).strip()
            # exclude dates
            if not re.search(r'\d{2}/\d{2}/\d{4}', cand):
                data['id_number'] = cand

        # 2. Dates
        # DOB
        dob_match = re.search(r'(?:DOB|Birth)\s*[:\.]?\s*(\d{2}[\./\-]\d{2}[\./\-]\d{4})', all_text, re.IGNORECASE)
        if dob_match:
            data['dob'] = self.parse_date(dob_match.group(1))
            
        # Expiry (EXP, END, Until)
        exp_match = re.search(r'(?:EXP|Expires|End)\s*[:\.]?\s*(\d{2}[\./\-]\d{2}[\./\-]\d{4})', all_text, re.IGNORECASE)
        if exp_match:
            data['expiry_date'] = self.parse_date(exp_match.group(1))

        # 3. Sex
        sex_match = re.search(r'(?:Sex|Sex\s*:)\s*([MF])', all_text, re.IGNORECASE)
        if sex_match:
            data['sex'] = sex_match.group(1)

        # 4. Name and Address (Heuristic)
        # Address usually follows name, or is at bottom. 
        # State ID usually has name on top.
        # This is very hard to generalize. 
        # Strategy: Look for lines that look like Name (CamelCase, no digits)
        # and lines that look like Address (Digits + Street Name).
        
        # Simple Name heuristic: "FN" "LN" fields sometimes exist (First Name, Last Name)
        ln_match = re.search(r'(?:LN|Last Name)\s*[:\.]?\s*([A-Za-z\- ]+)', all_text, re.IGNORECASE)
        fn_match = re.search(r'(?:FN|First Name)\s*[:\.]?\s*([A-Za-z\- ]+)', all_text, re.IGNORECASE)
        
        if ln_match and fn_match:
            data['name'] = f"{fn_match.group(1).strip()} {ln_match.group(1).strip()}"
        
        return data
