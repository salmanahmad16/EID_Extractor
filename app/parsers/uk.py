from .base import BaseParser
from ..mrz_handler import MRZHandler
import re

class UKParser(BaseParser):
    def parse(self, ocr_data, side_hint=None):
        raw_lines = [item['text'] for item in ocr_data]
        all_text = "\n".join(raw_lines)
        
        data = {
            'country': 'United Kingdom',
            'id_number': None,
            'name': None,
            'nationality': 'GBR', # default guess if UK parser selected
            'dob': None,
            'sex': None,
            'expiry_date': None,
            'place_of_birth': None,
            'mrz': None
        }

        # 1. MRZ Logic (Primary)
        mrz_lines = MRZHandler.clean_mrz_lines(raw_lines)
        if mrz_lines:
            mrz_data = MRZHandler.parse_mrz(mrz_lines)
            if mrz_data.get('id_number'):
                data.update({k: v for k, v in mrz_data.items() if v})
                data['mrz'] = mrz_lines

        # 2. Heuristic Backups (if MRZ failed or incomplete)
        
        # Passport Number (visual, usually top right)
        if not data['id_number']:
            # 9 digit number often
            pass_match = re.search(r'(?:Passport No|No)\.?\s*(\d{9})', all_text, re.IGNORECASE)
            if pass_match:
                data['id_number'] = pass_match.group(1)

        # Name (Surname + Given Names)
        if not data['name']:
            # Surname line usually capitalized
            # This is hard visually without anchors
            pass

        # Place of Birth
        if not data['place_of_birth']:
            pob_match = re.search(r'(?:Place of Birth)\s*[:\.]?\s*([A-Z\s,]+)', all_text, re.IGNORECASE)
            if pob_match:
                # exclude dates or noise
                val = pob_match.group(1).strip()
                if len(val) > 3 and not any(c.isdigit() for c in val):
                    data['place_of_birth'] = val

        return data
