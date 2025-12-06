from .base import BaseParser
from ..mrz_handler import MRZHandler
import re

class GermanyParser(BaseParser):
    def parse(self, ocr_data, side_hint=None):
        raw_lines = [item['text'] for item in ocr_data]
        all_text = "\n".join(raw_lines)
        
        data = {
            'country': 'Germany',
            'id_number': None,
            'name': None,
            'given_names': None,
            'family_name': None,
            'nationality': 'D', # default
            'dob': None,
            'place_of_birth': None,
            'expiry_date': None,
            'address': None,
            'mrz': None
        }

        # 1. MRZ Logic (Primary for ID cards)
        mrz_lines = MRZHandler.clean_mrz_lines(raw_lines)
        if mrz_lines:
            mrz_data = MRZHandler.parse_mrz(mrz_lines)
            if mrz_data.get('id_number'):
                data.update({k: v for k, v in mrz_data.items() if v})
                data['mrz'] = mrz_lines
                
                # Use split fields
                if mrz_data.get('surname'):
                     data['family_name'] = mrz_data['surname']
                if mrz_data.get('given_names'):
                     data['given_names'] = mrz_data['given_names']

        # 2. Heuristic Backups (Visual)
        
        # ID Number (Personalausweis usually top right)
        # Often starts with letters
        if not data['id_number']:
             # Look for 10 alphanumeric pattern typical of German IDs (e.g., L898902C3)
             # But it's hard to be precise.
             pass

        # Name separation (German IDs have explicit Name / Vorname fields)
        if not data['family_name']:
            fam_match = re.search(r'Name\s+([A-Z\u00c4\u00d6\u00dc\u00df]+)', all_text, re.IGNORECASE)
            if fam_match:
                data['family_name'] = fam_match.group(1)
        
        if not data['given_names']:
            giv_match = re.search(r'Vorname[n]?\s+([A-Z\u00c4\u00d6\u00dc\u00df\s]+)', all_text, re.IGNORECASE)
            if giv_match:
                data['given_names'] = giv_match.group(1).strip()
                if not data['name']:
                    data['name'] = f"{data['given_names']} {data.get('family_name', '')}".strip()

        # Place of Birth (Geburtsort)
        if not data['place_of_birth']:
             pob_match = re.search(r'Geburtsort\s+([A-Z\u00c4\u00d6\u00dc\u00df\s]+)', all_text, re.IGNORECASE)
             if pob_match:
                 data['place_of_birth'] = pob_match.group(1).strip()

        return data
