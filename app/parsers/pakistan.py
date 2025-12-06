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
            # Strategy: look for line containing "Name" and take the NEXT line
            # Or if "Name" is mixed with value like "Name Salman"
            for i, line in enumerate(lines):
                if 'Name' in line and 'Father' not in line:
                    # check if the value is on the same line
                    parts = line.split('Name')
                    if len(parts) > 1 and len(parts[1].strip()) > 3:
                        data['name'] = parts[1].strip().strip(":").strip()
                    elif i + 1 < len(lines):
                        data['name'] = lines[i+1].strip()
                    break
            
            # Father Name
            for i, line in enumerate(lines):
                if 'Father' in line:
                    parts = line.split('Name') # Father Name...
                    if len(parts) > 1 and len(parts[-1].strip()) > 3:
                         data['father_name'] = parts[-1].strip().strip(":").strip()
                    elif i + 1 < len(lines):
                         data['father_name'] = lines[i+1].strip()
                    break

            # DOB
            # Try specific label first
            dob_match = re.search(r'(?:Date of Birth|DOB|Birth)\s*[:\.]?\s*(\d{2}[\./\-]\d{2}[\./\-]\d{4})', all_text, re.IGNORECASE)
            if dob_match:
                data['dob'] = self.parse_date(dob_match.group(1))
            
            # Expiry
            exp_match = re.search(r'(?:Date of Expiry|Expiry)\s*[:\.]?\s*(\d{2}[\./\-]\d{2}[\./\-]\d{4})', all_text, re.IGNORECASE)
            if exp_match:
                data['expiry_date'] = self.parse_date(exp_match.group(1))

            # Smart Date Fallback (if null)
            # Find ALL dates
            all_dates = re.findall(r'\d{2}[\./\-]\d{2}[\./\-]\d{4}', all_text)
            parsed_dates = [self.parse_date(d) for d in all_dates if self.parse_date(d)]
            parsed_dates = sorted(list(set(parsed_dates))) # dedupe and sort
            
            if parsed_dates:
                # Heuristics:
                # Oldest = DOB 
                # Newest = Expiry 
                # Middle = Issue
                
                # Robust Override: If we found 3 unique dates, we trust the order 
                # (DOB < Issue < Expiry) more than the spatial regex which fails on columns
                if len(parsed_dates) >= 3:
                    data['dob'] = parsed_dates[0]
                    data['expiry_date'] = parsed_dates[-1]
                else:
                    # Fallback if we have fewer dates
                    if not data['dob'] and parsed_dates:
                         data['dob'] = parsed_dates[0]
                    
                    if not data['expiry_date'] and parsed_dates:
                         data['expiry_date'] = parsed_dates[-1]

            # Sex
            # Line walking approach for robustness
            if not data['sex']:
                found_gender_label = False
                for i, line in enumerate(lines):
                    if 'Gender' in line or 'Sex' in line:
                        found_gender_label = True
                        # Check this line and next 3 lines
                        start = i
                        end = min(i + 4, len(lines))
                        for j in range(start, end):
                            # Look for M/F token
                            tokens = lines[j].split()
                            for token in tokens:
                                clean_token = token.strip().upper()
                                if clean_token in ['M', 'F', 'MALE', 'FEMALE']:
                                     data['sex'] = 'M' if clean_token.startswith('M') else 'F'
                                     break
                            if data['sex']: break
                    if data['sex']: break
            
            # Fallback if label missed
            if not data['sex']:
                 if 'Male' in all_text and 'Female' not in all_text:
                     data['sex'] = 'M'
                 elif 'Female' in all_text:
                     data['sex'] = 'F'

        return data

