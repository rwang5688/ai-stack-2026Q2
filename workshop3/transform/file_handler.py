"""
File handling operations for dataset transformation.
"""
import json
import os
from pathlib import Path
from typing import Iterator, List
import logging

class FileHandler:
    """Manages file operations and directory structure."""
    
    def __init__(self, input_dir: str, output_dir: str):
        """
        Initialize file handler with input and output directories.
        
        Args:
            input_dir: Path to directory containing input JSONL files
            output_dir: Path to directory for output JSONL files
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.ensure_output_directory()
    
    def ensure_output_directory(self) -> None:
        """Create output directory if it doesn't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Output directory ready: {self.output_dir}")
    
    def get_input_files(self) -> List[str]:
        """
        Get list of JSONL files in the input directory.
        
        Returns:
            List of input file paths
        """
        if not self.input_dir.exists():
            logging.error(f"Input directory does not exist: {self.input_dir}")
            return []
        
        jsonl_files = list(self.input_dir.glob("*.jsonl"))
        file_paths = [str(f) for f in jsonl_files]
        logging.info(f"Found {len(file_paths)} JSONL files in {self.input_dir}")
        return file_paths
    
    def read_jsonl(self, file_path: str) -> Iterator[dict]:
        """
        Read records from a JSONL file.
        
        Args:
            file_path: Path to the JSONL file
            
        Yields:
            Dictionary records from the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        record = json.loads(line)
                        yield record
                    except json.JSONDecodeError as e:
                        logging.warning(f"Invalid JSON at line {line_num} in {file_path}: {e}")
                        continue
                        
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
    
    def write_jsonl(self, file_path: str, records: Iterator[dict]) -> int:
        """
        Write records to a JSONL file.
        
        Args:
            file_path: Path to the output JSONL file
            records: Iterator of dictionary records to write
            
        Returns:
            Number of records written
        """
        count = 0
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for record in records:
                    # Validate JSON before writing
                    try:
                        json_line = json.dumps(record, ensure_ascii=False)
                        f.write(json_line + '\n')
                        count += 1
                    except (TypeError, ValueError) as e:
                        logging.warning(f"Failed to serialize record: {e}")
                        continue
            
            logging.info(f"Wrote {count} records to {file_path}")
            return count
            
        except Exception as e:
            logging.error(f"Error writing to file {file_path}: {e}")
            return 0
    
    def get_output_path(self, input_file_path: str) -> str:
        """
        Generate output file path based on input file path.
        
        Args:
            input_file_path: Path to the input file
            
        Returns:
            Path to the corresponding output file
        """
        input_path = Path(input_file_path)
        base_name = input_path.stem  # filename without extension
        output_filename = f"{base_name}_transformed.jsonl"
        return str(self.output_dir / output_filename)