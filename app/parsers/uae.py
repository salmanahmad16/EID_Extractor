from .base import BaseParser
import re

class UAEParser(BaseParser):
    def parse(self, ocr_data, side_hint=None):
        all_text = "\n".join([item['text'] for item in ocr_data])
        lines = [item['text'] for item in ocr_data]
        
        # Detect side if not provided (basic heuristic)
        # Detect side if not provided (improved heuristic)
        if not side_hint:
            # Strong signals for Front
            if 'Name' in all_text or 'Nationality' in all_text or 'United Arab Emirates' in all_text:
                side_hint = 'Front'
            # Strong signals for Back
            elif 'Resident Identity Card' in all_text:
                side_hint = 'Back'
            # MRZ check: must be distinct
            elif '<<' in all_text:
                # noise check: ensure '<<' is part of a longer string typical of MRZ
                # find lines with << and check length
                mrz_candidates = [l for l in lines if '<<' in l and len(l) > 15]
                if mrz_candidates:
                    side_hint = 'Back'
                else:
                     # '<<' might be noise
                    side_hint = 'Front'
            else:
                side_hint = 'Front'

        data = {
            'country': 'UAE',
            'side': side_hint,
            'id_number': None,
            'name': None,
            'nationality': None,
            'dob': None,
            'expiry_date': None,
            'issuing_date': None,
            'sex': None
        }

        # ID Number: 784-1980-1234567-1
        id_match = re.search(r'784-\d{4}-\d{7}-\d', all_text)
        if id_match:
            data['id_number'] = id_match.group(0)

        # Date pattern - more permissive
        date_pattern = r'\d{2}[\./\-]\d{2}[\./\-]\d{4}'
        
        # Find all dates first
        all_dates = re.findall(date_pattern, all_text)
        parsed_dates = [self.parse_date(d) for d in all_dates if self.parse_date(d)]

        if side_hint == 'Front':
            # Name
            for i, line in enumerate(lines):
                if 'Name' in line:
                    clean_line = line.replace('Name', '').strip()
                    if clean_line.startswith(':') or clean_line.startswith('.'):
                        clean_line = clean_line[1:].strip()
                    
                    if len(clean_line) > 3:
                         data['name'] = clean_line
                    elif i + 1 < len(lines):
                        data['name'] = lines[i+1].strip()
                    break
            
            # Nationality
            for i, line in enumerate(lines):
                if 'Nationality' in line:
                    clean_line = line.replace('Nationality', '').strip()
                    if clean_line.startswith(':') or clean_line.startswith('.'):
                        clean_line = clean_line[1:].strip()
                    
                    if len(clean_line) > 2:
                         data['nationality'] = clean_line
                    elif i + 1 < len(lines):
                        data['nationality'] = lines[i+1].strip()
                    break

            # DOB
            dob_match = re.search(r'(?:Date of Birth|DOB)\s*[:\.]?\s*(' + date_pattern + ')', all_text, re.IGNORECASE)
            if dob_match:
                data['dob'] = self.parse_date(dob_match.group(1))
            elif parsed_dates:
                 # Heuristic: DOB is usually the earliest date if explicit label missing? 
                 # But let's stick to label or specific position if possible.
                 pass

            # Issuing Date
            issue_match = re.search(r'(?:Issuing Date|Date of Issue)\s*[:\./]?\s*(' + date_pattern + ')', all_text, re.IGNORECASE)
            if issue_match:
                data['issuing_date'] = self.parse_date(issue_match.group(1))
                
            # Expiry Date
            exp_match = re.search(r'Expiry Date\s*[:\./]?\w*\s*(' + date_pattern + ')', all_text, re.IGNORECASE)
            if exp_match:
                data['expiry_date'] = self.parse_date(exp_match.group(1))
            
            # Fallback for Expiry and others using Orphan Dates
            # If explicit parsing failed, use the sorted list of all valid dates found
            if parsed_dates:
                # Sort dates
                sorted_dates = sorted(list(set(parsed_dates))) # Deduplicate and sort
                
                # Heuristic: 
                # Oldest = DOB (if DOB is null)
                # Newest = Expiry (if Expiry is null)
                # Middle (if exists) = Issuing Date
                
                if not data['dob'] and sorted_dates:
                    data['dob'] = sorted_dates[0]
                    
                if not data['expiry_date'] and sorted_dates:
                    data['expiry_date'] = sorted_dates[-1]
                    
                if not data['issuing_date'] and len(sorted_dates) > 2:
                    # If we have at least 3 dates, the middle one might be issuing
                    # (DOB, Issue, Expiry)
                    data['issuing_date'] = sorted_dates[1]

            # Cleanup text fields
            for field in ['name', 'nationality']:
                if data[field]:
                    # Remove leading non-alphanumeric chars (like commas, dots)
                    data[field] = re.sub(r'^[^a-zA-Z0-9]+', '', data[field]).strip()

            # Sex
            sex_match = re.search(r'Sex\s*[:\.]?\s*([MF])', all_text, re.IGNORECASE)
            if sex_match:
                data['sex'] = sex_match.group(1)

        elif side_hint == 'Back':
             # Back side logic (MRZ or text)
             # Expiry Date often on back for old IDs
            exp_match = re.search(r'Expiry Date\s*[:\.]?\s*(' + date_pattern + ')', all_text, re.IGNORECASE)
            if exp_match:
                data['expiry_date'] = self.parse_date(exp_match.group(1))
            
            # MRZ extraction (simplified)
            mrz_lines = []
            for line in lines:
                if len(line) > 20 and '<' in line:
                    mrz_lines.append(line.replace(' ', ''))
            if mrz_lines:
                data['mrz'] = mrz_lines

        return data
