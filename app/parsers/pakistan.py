from .base import BaseParser
import re

class PakistanParser(BaseParser):
    def parse(self, ocr_data, side_hint=None):
        all_text = "\n".join([item['text'] for item in ocr_data])
        lines = [item['text'] for item in ocr_data]
        
        if not side_hint:
             # Heuristic
             if 'Family No' in all_text or 'Address' in all_text:
                 side_hint = 'Back'
             else:
                 side_hint = 'Front'

        data = {
            'country': 'Pakistan',
            'side': side_hint,
            'id_number': None,
            'name': None,
            'father_name': None,
            'dob': None,
            'expiry_date': None,
            'sex': None
        }

        # CNIC Number: 12345-1234567-1
        cnic_match = re.search(r'\d{5}-\d{7}-\d', all_text)
        if cnic_match:
            data['id_number'] = cnic_match.group(0)

        date_pattern = r'\d{2}[\./]\d{2}[\./]\d{4}'

        if side_hint == 'Front':
            # Name
            # Often follows "Name" or "Name" in Urdu/English
            for i, line in enumerate(lines):
                if 'Name' in line and i + 1 < len(lines):
                     data['name'] = lines[i+1].strip()
                     break
            
            # Father Name
            for i, line in enumerate(lines):
                if 'Father Name' in line and i + 1 < len(lines):
                     data['father_name'] = lines[i+1].strip()
                     break

            # DOB
            # Allow for more variation in separators and spacing
            dob_match = re.search(r'(?:Date of Birth|DOB)\s*[:\.]?\s*(\d{2}[\./\-]\d{2}[\./\-]\d{4}|\d{2}\s\d{2}\s\d{4})', all_text, re.IGNORECASE)
            if dob_match:
                data['dob'] = self.parse_date(dob_match.group(1))
            
            # Expiry
            exp_match = re.search(r'(?:Date of Expiry|Expiry Date|DOI)\s*[:\.]?\s*(\d{2}[\./\-]\d{2}[\./\-]\d{4}|\d{2}\s\d{2}\s\d{4})', all_text, re.IGNORECASE)
            if exp_match:
                data['expiry_date'] = self.parse_date(exp_match.group(1))

            # Sex
            sex_match = re.search(r'Gender\s*[:\.]?\s*([MF])', all_text, re.IGNORECASE)
            if sex_match:
                data['sex'] = sex_match.group(1)

        return data
