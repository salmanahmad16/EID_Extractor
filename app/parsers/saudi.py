from .base import BaseParser
from ..mrz_handler import MRZHandler
import re

class SaudiParser(BaseParser):
    def parse(self, ocr_data, side_hint=None):
        raw_lines = [item['text'] for item in ocr_data]
        all_text = "\n".join(raw_lines)
        
        data = {
            'country': 'Saudi Arabia',
            'id_number': None,
            'id_type': None, # National ID or Iqama
            'name': None,
            'nationality': None,
            'dob': None,
            'sex': None,
            'expiry_date': None, # Hijri likely
            'issue_date': None,
            'occupation': None, # For Iqama
            'employer': None, # For Iqama
            'mrz': None
        }

        # 1. MRZ (Passports / Modern Cards)
        mrz_lines = MRZHandler.clean_mrz_lines(raw_lines)
        if mrz_lines:
            mrz_data = MRZHandler.parse_mrz(mrz_lines)
            if mrz_data.get('id_number'):
                data.update({k: v for k, v in mrz_data.items() if v})
                data['mrz'] = mrz_lines
                return data # MRZ is usually sufficient if present

        # 2. Heuristic Backups (Visual)

        # ID Number
        # National ID: 10 digits starting with 1
        # Iqama: 10 digits starting with 2
        id_match = re.search(r'\b([12]\d{9})\b', all_text)
        if id_match:
            id_val = id_match.group(1)
            data['id_number'] = id_val
            data['id_type'] = 'National ID' if id_val.startswith('1') else 'Iqama'

        # Dates (Usually YYYY/MM/DD in Hijri)
        # Look for 4 digits / 2 digits / 2 digits
        # This is tricky as Western dates also exist.
        # We will extract raw date strings.
        date_pattern = r'\d{4}[\./\-]\d{2}[\./\-]\d{2}'
        dates = re.findall(date_pattern, all_text)
        if dates:
            # Heuristic: Expiry is usually the latest date, DOB earliest
            dates.sort()
            # If > 1900, probably Gregorian. If < 1500, probably Hijri.
            # We'll just store the string for now.
            if not data['dob']: data['dob'] = dates[0]
            if not data['expiry_date']: data['expiry_date'] = dates[-1]

        # Name (English)
        # Often "Name:" or just English text
        # Strategy: Find lines with exclusively Latin characters + spaces, long enough
        for line in raw_lines:
            if re.match(r'^[A-Za-z\s]+$', line) and len(line) > 5:
                # exclude known keywords
                if any(k in line.lower() for k in ['kingdom', 'saudi', 'arabia', 'ministry', 'interior', 'resident', 'identity', 'labor']):
                    continue
                if not data['name']:
                    data['name'] = line.replace('Name:', '').replace('Name', '').strip()
                    break

        return data
