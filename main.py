import argparse
import sys
import json
from app.core import UniversalIDExtractor

def main():
    parser = argparse.ArgumentParser(description="UAE Emirates ID Extractor")
    parser.add_argument("input_file", nargs='?', help="Path to the image or PDF file")
    parser.add_argument("--side", choices=['Front', 'Back'], help="Force extraction for a specific side (optional)")
    parser.add_argument("--output", help="Path to save the JSON output (optional)")
    parser.add_argument("--list-countries", action="store_true", help="List supported countries")

    args = parser.parse_args()

    if args.list_countries:
        from app.config import SUPPORTED_COUNTRIES
        print("Supported Countries:")
        for country in SUPPORTED_COUNTRIES:
            print(f"- {country}")
        sys.exit(0)

    if not args.input_file:
         print("Error: input_file is required unless --list-countries is used", file=sys.stderr)
         parser.print_help()
         sys.exit(1)

    try:
        extractor = UniversalIDExtractor()
        result_json = extractor.extract_to_json(args.input_file, side_hint=args.side)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result_json)
            print(f"Output saved to {args.output}")
        else:
            print(result_json)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
