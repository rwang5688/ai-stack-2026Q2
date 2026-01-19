"""
Main script for converting JSONL files to Amazon Nova Bedrock conversation format.

This script reads JSONL files from workshop2/input/, converts them to Bedrock format,
and writes the output to workshop2/output/ with _transform2ed.jsonl suffix.
"""

import json
import os
from pathlib import Path
from converter import convert_jsonl_file, format_output_filename


def main():
    """
    Main function to process all JSONL files in the input directory.
    """
    # Define paths relative to script location
    script_dir = Path(__file__).parent
    input_dir = script_dir.parent / "input"
    output_dir = script_dir.parent / "output"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Find all JSONL files in input directory
    jsonl_files = list(input_dir.glob("*.jsonl"))
    
    if not jsonl_files:
        print(f"No JSONL files found in {input_dir}")
        return
    
    print(f"Found {len(jsonl_files)} JSONL file(s) to convert")
    print()
    
    # Process each file
    for input_file in jsonl_files:
        print(f"Processing: {input_file.name}")
        
        try:
            # Read input file
            with open(input_file, 'r', encoding='utf-8') as f:
                input_content = f.read()
            
            # Convert to Bedrock format
            converted_records = convert_jsonl_file(input_content)
            
            # Generate output filename
            output_filename = format_output_filename(input_file.name)
            output_path = output_dir / output_filename
            
            # Write output file
            with open(output_path, 'w', encoding='utf-8') as f:
                for record in converted_records:
                    f.write(json.dumps(record) + '\n')
            
            print(f"  ✓ Converted {len(converted_records)} records")
            print(f"  ✓ Output: {output_path}")
            print()
            
        except Exception as e:
            print(f"  ✗ Error processing {input_file.name}: {e}")
            print()
    
    print("Conversion complete!")


if __name__ == "__main__":
    main()
