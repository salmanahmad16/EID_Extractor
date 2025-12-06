import unittest
from app.parsers.base import BaseParser

class TestDateParsing(unittest.TestCase):
    def setUp(self):
        self.parser = BaseParser()

    def test_standard_dates(self):
        self.assertEqual(self.parser.parse_date("01/01/2000"), "2000-01-01")
        self.assertEqual(self.parser.parse_date("31-12-1990"), "1990-12-31")
        self.assertEqual(self.parser.parse_date("1985.05.20"), "1985-05-20")

    def test_dirty_dates(self):
        self.assertEqual(self.parser.parse_date("Date: 01/01/2000"), "2000-01-01")
        self.assertEqual(self.parser.parse_date("01.01,2000"), "2000-01-01") # comma issue
        self.assertEqual(self.parser.parse_date("01-01.2000"), "2000-01-01") # mixed separators
        self.assertEqual(self.parser.parse_date("...01/01/2000..."), "2000-01-01")

    def test_invalid_dates(self):
        self.assertEqual(self.parser.parse_date("Not a date"), "Not a date")
        # should return original if fails (or None if None passed)
        self.assertIsNone(self.parser.parse_date(None))

    def test_no_separators(self):
        # Assuming we support DDMMYYYY if cleaning removes everything else, 
        # but my regex `[^\d\.\/\-]` keeps separators. 
        # If input is raw "01012000", let's see if my parser handles it.
        # My implementation added '%d%m%Y' to formats.
        self.assertEqual(self.parser.parse_date("01012000"), "2000-01-01")

if __name__ == '__main__':
    unittest.main()
