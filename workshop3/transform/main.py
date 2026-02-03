#!/usr/bin/env python3
"""
Main script for dataset transformation.
"""
import argparse
import sys
from pathlib import Path
import logging

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dataset_transformer import DatasetTransformer


def main():
    """Main entry point for the dataset transformation script."""
    parser = argparse.ArgumentParser(
        description="Transform JSONL datasets from messages format to prompt-completion format"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default="../input",
        help="Input directory containing JSONL files (default: ../input)"
    )
    parser.add_argument(
        "--output-dir", 
        type=str,
        default="../output",
        help="Output directory for transformed files (default: ../output)"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Transform a specific file instead of all files in input directory"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Resolve paths relative to script location
    script_dir = Path(__file__).parent
    input_dir = (script_dir / args.input_dir).resolve()
    output_dir = (script_dir / args.output_dir).resolve()
    
    logging.info(f"Input directory: {input_dir}")
    logging.info(f"Output directory: {output_dir}")
    
    # Validate input directory exists
    if not input_dir.exists():
        logging.error(f"Input directory does not exist: {input_dir}")
        sys.exit(1)
    
    # Initialize transformer
    transformer = DatasetTransformer(str(input_dir), str(output_dir))
    
    try:
        if args.file:
            # Transform specific file
            file_path = input_dir / args.file
            if not file_path.exists():
                logging.error(f"Specified file does not exist: {file_path}")
                sys.exit(1)
            
            result = transformer.transform_file(str(file_path))
            if not result.success:
                logging.error("Transformation failed")
                sys.exit(1)
        else:
            # Transform all files
            results = transformer.transform_all_files()
            failed_results = [r for r in results if not r.success]
            
            if failed_results:
                logging.warning(f"{len(failed_results)} files failed to transform")
                for result in failed_results:
                    logging.error(f"Failed: {result.input_file}")
            
            if not any(r.success for r in results):
                logging.error("All transformations failed")
                sys.exit(1)
    
    except KeyboardInterrupt:
        logging.info("Transformation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)
    
    logging.info("Transformation completed successfully")


if __name__ == "__main__":
    main()