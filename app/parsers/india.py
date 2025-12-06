from .base import BaseParser
import re

class IndiaParser(BaseParser):
    def parse(self, ocr_data, side_hint=None):
        raw_lines = [item['text'] for item in ocr_data]
        all_text = "\n".join(raw_lines)
        
        data = {
            'country': 'India',
            'doc_type': None, # Aadhaar or PAN
            'id_number': None,
            'name': None,
            'father_name': None,
            'dob': None,
            'yob': None,
            'gender': None,
            'address': None
        }

        # Detect Doc Type
        if 'Aadhaar' in all_text or 'UIDAI' in all_text:
            data['doc_type'] = 'Aadhaar'
        elif 'Income Tax' in all_text or 'PAN' in all_text:
            data['doc_type'] = 'PAN'
        
        # 1. Aadhaar Logic
        if data['doc_type'] == 'Aadhaar' or not data['doc_type']:
            # ID: 12 digits (XXXX XXXX XXXX)
            uid_match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', all_text)
            if uid_match:
                data['id_number'] = uid_match.group(0)
                if not data['doc_type']: data['doc_type'] = 'Aadhaar'
            
            # DOB / YOB
            dob_match = re.search(r'(?:DOB|Date of Birth)\s*[:\.]?\s*(\d{2}[\./\-]\d{2}[\./\-]\d{4})', all_text, re.IGNORECASE)
            if dob_match:
                data['dob'] = self.parse_date(dob_match.group(1))
            else:
                yob_match = re.search(r'(?:Year of Birth|YOB)\s*[:\.]?\s*(\d{4})', all_text, re.IGNORECASE)
                if yob_match:
                    data['yob'] = yob_match.group(1)
            
            # Gender
            if 'Male' in all_text and 'Female' not in all_text:
                data['gender'] = 'M'
            elif 'Female' in all_text:
                data['gender'] = 'F'
            
            # Address (Back side usually contains "Address:")
            if 'Address' in all_text:
                parts = all_text.split('Address')
                if len(parts) > 1:
                    # Take up to 60-80 chars or until a pin code (6 digits)
                    addr_cand = parts[1].strip().strip(':').strip()
                    # heuristic cleanup
                    data['address'] = addr_cand[:100]

        # 2. PAN Logic
        if data['doc_type'] == 'PAN' or (not data['doc_type'] and not data['id_number']):
            # ID: 10 chars usually in middle (ABCDE1234F)
            # Regex: 5 letters, 4 digits, 1 letter
            pan_match = re.search(r'\b[A-Z]{5}\d{4}[A-Z]\b', all_text)
            if pan_match:
                data['id_number'] = pan_match.group(0)
                if not data['doc_type']: data['doc_type'] = 'PAN'
            
            # Father's Name
            # Usually lines are: Name \n Father Name \n DOB
            # This is hard without strict position, but we can try to look for 'Father' keyword if present (rare on actual card face, implies relationship)
            # Standard visual format:
            # INCOME TAX
            # NAME
            # FATHER NAME
            # DATE
            # So if we find Name, next is Father?
            pass

        return data
