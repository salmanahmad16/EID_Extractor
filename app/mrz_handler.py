import re
from datetime import datetime

class MRZHandler:
    """
    Helper class to extract and parse MRZ data (TD1, TD2, TD3).
    Does not use external 'mrz' library to keep dependencies low, 
    but implements standard ICAO 9303 logic.
    """

    @staticmethod
    def clean_mrz_lines(lines):
        """
        Filter and clean lines that look like MRZ.
        Returns a list of MRZ lines (2 or 3 lines).
        """
        mrz_lines = []
        # Basic filter: must contain '<<' or be mostly uppercase alphanumeric with length > 28
        for line in lines:
            clean = line.replace(' ', '').upper()
            if len(clean) < 28:
                continue
            # MRZ lines usually start with I, P, A, C, V or distinct patterns
            # and contain fillers '<'
            if '<' in clean:
                # noise removal: sometimes OCR puts garbage around
                # MRZ lines are typically 30 (TD1), 36 (TD2), or 44 (TD3) chars
                # We'll just keep the whole clean line for now
                mrz_lines.append(clean)
        
        # Sort by length similarity or just take the last N lines?
        # Typically MRZ is at the bottom.
        return mrz_lines[-3:] if len(mrz_lines) >= 3 else mrz_lines

    @staticmethod
    def parse_mrz(mrz_lines):
        """
        Parse MRZ lines and return a dict of fields.
        Supports:
        - TD1 (3 lines, 30 chars) - common for ID cards
        - TD2 (2 lines, 36 chars)
        - TD3 (2 lines, 44 chars) - Passports
        """
        data = {
            'mrz_type': None,
            'country': None,
            'name': None,
            'id_number': None, # Passport or Doc number
            'dob': None,
            'sex': None,
            'expiry_date': None,
            'nationality': None
        }

        if not mrz_lines:
            return data

        # Check for TD3 (Passport) - 2 lines, ~44 chars
        if len(mrz_lines) >= 2 and len(mrz_lines[-1]) > 40 and len(mrz_lines[-2]) > 40:
             return MRZHandler._parse_td3(mrz_lines[-2], mrz_lines[-1])
        
        # Check for TD1 (ID Card) - 3 lines, ~30 chars
        if len(mrz_lines) == 3 and len(mrz_lines[0]) > 25 and len(mrz_lines[1]) > 25:
             return MRZHandler._parse_td1(mrz_lines)

        return data

    @staticmethod
    def _parse_date(date_str):
        """
        Parse YYMMDD to YYYY-MM-DD.
        Pivot year is dynamic (e.g., >80 is 1900s, <80 is 2000s)
        """
        if not date_str or len(date_str) != 6 or not date_str.isdigit():
            return None
        
        val = int(date_str)
        # Year Handling
        y = int(date_str[0:2])
        m = int(date_str[2:4])
        d = int(date_str[4:6])

        # Simple pivot: if year > current year-2000 + 10 (future?), assume 19xx? 
        # Actually standard MRZ logic:
        # For DOB: usually relative to current year. 
        # For Expiry: usually 20xx.
        # Let's assume generic pivot around 50 for now? 
        # Better: let context decide, but here we return a partial struct or full year guess.
        
        # Pivot year 2000 vs 1900
        current_year_short = int(datetime.now().strftime('%y'))
        
        # This is ambiguous without knowing if it's DOB or Expiry
        # We will return the raw YYMMDD and let higher logic fix, OR just make a smart guess
        # Guess: if y > current_year + 10 -> 19yy, else 20yy
        # This works for DOB but might fail for very old expiries (unlikely).
        full_year = 0
        if y > (current_year_short + 10): 
            full_year = 1900 + y
        else:
            full_year = 2000 + y
            
        try:
             return f"{full_year}-{m:02d}-{d:02d}"
        except:
             return None

    @staticmethod
    def _parse_td3(line1, line2):
        """
        Passport format (2 lines, 44 chars)
        L1: P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<<<
        L2: L898902C<3UTO6908061F9406236ZE184226B<<<<<14
        """
        data = {}
        data['mrz_type'] = 'TD3'

        # Line 1
        # Pos 0-1: Type (P)
        # Pos 2-4: Issuer (Country)
        data['country'] = line1[2:5].replace('<', '')
        
        # Pos 5-43: Name
        # Format: SURNAME<<GIVEN<NAMES
        name_part = line1[5:].strip('<')
        parts = name_part.split('<<')
        if len(parts) >= 2:
            surname = parts[0].replace('<', ' ').strip()
            given = parts[1].replace('<', ' ').strip()
            data['name'] = f"{given} {surname}"
            data['surname'] = surname
            data['given_names'] = given
        else:
            data['name'] = name_part.replace('<', ' ').strip()
            data['surname'] = data['name']

        # Line 2
        # Pos 0-8: Doc Number
        data['id_number'] = line2[0:9].replace('<', '').strip()
        
        # Pos 9: Check digit
        # Pos 10-12: Nationality
        data['nationality'] = line2[10:13].replace('<', '')

        # Pos 13-18: DOB (YYMMDD)
        data['dob'] = MRZHandler._parse_date(line2[13:19])

        # Pos 20: Sex (M/F)
        data['sex'] = line2[20]

        # Pos 21-26: Expiry (YYMMDD)
        data['expiry_date'] = MRZHandler._parse_date(line2[21:27])

        return data

    @staticmethod
    def _parse_td1(lines):
        """
        ID Card format (3 lines, 30 chars or variable)
        L1: I<UTOD231458907<<<<<<<<<<<<<<<
        L2: 7408122F1204159UTO<<<<<<<<<<<6
        L3: ERIKSSON<<ANNA<MARIA<<<<<<<<<<
        
        Wait, standard TD1 is:
        L1: Doc Type, Country, Doc Num
        L2: DOB, Sex, Expiry, Nationality
        L3: Name
        """
        data = {}
        data['mrz_type'] = 'TD1'
        
        l1, l2, l3 = lines[0], lines[1], lines[2]
        
        # Clean lines to ensure length/padding
        # (Assuming they are roughly aligned)

        # L1
        # Pos 2-4: Issuer
        data['country'] = l1[2:5].replace('<', '')
        # Pos 5-13: Doc Num
        data['id_number'] = l1[5:14].replace('<', '')

        # L2
        # Pos 0-5: DOB
        data['dob'] = MRZHandler._parse_date(l2[0:6])
        
        # Pos 7: Sex
        data['sex'] = l2[7]
        
        # Pos 8-13: Expiry
        data['expiry_date'] = MRZHandler._parse_date(l2[8:14])
        
        # Pos 15-17: Nationality
        data['nationality'] = l2[15:18].replace('<', '')

        # L3: Name
        name_part = l3.strip('<')
        parts = name_part.split('<<')
        if len(parts) >= 2:
            surname = parts[0].replace('<', ' ').strip()
            given = parts[1].replace('<', ' ').strip()
            data['name'] = f"{given} {surname}"
            data['surname'] = surname
            data['given_names'] = given
        else:
            data['name'] = name_part.replace('<', ' ').strip()
            data['surname'] = data['name']
            
        return data
