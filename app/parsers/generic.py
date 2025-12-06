from .base import BaseParser
import re

class GenericParser(BaseParser):
    def parse(self, ocr_data, side_hint=None):
        """
        Generic parser that returns all extracted text and attempts to
        heuristically find common fields.
        """
        raw_text = []
        full_text_str = ""
        lines = []

        for line in ocr_data:
            if 'text' in line:
                cleaned = self.clean_text(line['text'])
                if cleaned:
                    raw_text.append(cleaned)
                    lines.append(cleaned)
        
        full_text_str = "\n".join(lines)

        data = {
            'generic_text': raw_text,
            'id_number': None,
            'dob': None,
            'expiry_date': None,
            'sex': None
        }

        # --- Heuristics ---

        # 1. ID Number
        # Look for long digit sequences or patterns like "123-456"
        # Strategy: Find any sequence of digits > 7, maybe with hyphens/spaces
        # Avoid dates by checking if it matches the date format
        id_candidates = re.findall(r'(\b[A-Z0-9\-\s]{8,20}\b)', full_text_str)
        best_id = None
        for cand in id_candidates:
            # simple filter: must have at least 5 digits
            digits = re.sub(r'\D', '', cand)
            if len(digits) >= 6 and len(digits) <= 18:
                # check if it looks like a date
                if re.match(r'\d{2,4}[\./\-]\d{2}[\./\-]\d{2,4}', cand.strip()):
                    continue
                # Pick the longest one as a heuristic guess for ID
                if not best_id or len(digits) > len(re.sub(r'\D', '', best_id)):
                    best_id = cand.strip()
        
        if best_id:
            data['id_number'] = best_id

        # 2. Dates (DOB / Expiry)
        # Search for Date of Birth keywords
        # Relaxed regex to allow "Date of Birth", "Né le", "Born on" etc.
        # \b to match word boundaries
        # (?:\w+\s+)? allows for one extra word like "le", "of", "on"
        dob_match = re.search(r'(?:Birth|DOB|N\u00e9|Geboren)(?:\s+\w+)?\s*[:\.]?\s*(\d{2}[\./\-]\d{2}[\./\-]\d{4}|\d{2}\s\d{2}\s\d{4}|\d{4}[\./\-]\d{2}[\./\-]\d{2})', full_text_str, re.IGNORECASE)
        if dob_match:
            data['dob'] = self.parse_date(dob_match.group(1))

        # Search for Expiry keywords
        exp_match = re.search(r'(?:Expiry|Exp|Valid|Until|Valida|G\u00fcltig)(?:\s+\w+)?\s*[:\.]?\s*(\d{2}[\./\-]\d{2}[\./\-]\d{4}|\d{2}\s\d{2}\s\d{4}|\d{4}[\./\-]\d{2}[\./\-]\d{2})', full_text_str, re.IGNORECASE)
        if exp_match:
            data['expiry_date'] = self.parse_date(exp_match.group(1))

        # 3. Sex
        sex_match = re.search(r'(?:Sex|Gender|Sexe|Geschlecht)(?:\s+\w+)?\s*[:\.]?\s*([MF]|Male|Female|Homme|Femme)', full_text_str, re.IGNORECASE)
        if sex_match:
            val = sex_match.group(1).upper()
            if val.startswith('M') or val.startswith('H'): 
                data['sex'] = 'M'
            elif val.startswith('F'): 
                data['sex'] = 'F'
        
        return data
