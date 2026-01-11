"""
Main dataset transformation orchestrator.
"""
from typing import List, Iterator
import logging
from pathlib import Path

from data_models import TransformResult, extract_messages, create_prompt_completion
from file_handler import FileHandler


class DatasetTransformer:
    """Main orchestrator that coordinates the transformation process."""
    
    def __init__(self, input_dir: str, output_dir: str):
        """
        Initialize the dataset transformer.
        
        Args:
            input_dir: Path to directory containing input JSONL files
            output_dir: Path to directory for output JSONL files
        """
        self.file_handler = FileHandler(input_dir, output_dir)
        logging.info(f"DatasetTransformer initialized: {input_dir} -> {output_dir}")
    
    def transform_file(self, input_file: str) -> TransformResult:
        """
        Transform a single JSONL file from messages format to prompt-completion format.
        
        Args:
            input_file: Path to the input JSONL file
            
        Returns:
            TransformResult with transformation statistics and status
        """
        output_file = self.file_handler.get_output_path(input_file)
        result = TransformResult(
            input_file=input_file,
            output_file=output_file,
            records_processed=0,
            records_transformed=0,
            errors=[],
            success=False
        )
        
        logging.info(f"Starting transformation: {input_file} -> {output_file}")
        
        try:
            # Transform records
            transformed_records = self._transform_records(input_file, result)
            
            # Write to output file
            records_written = self.file_handler.write_jsonl(output_file, transformed_records)
            result.records_transformed = records_written
            
            # Update success status
            result.success = records_written > 0 or result.records_processed == 0
            
        except Exception as e:
            error_msg = f"Unexpected error during transformation: {e}"
            result.add_error(error_msg)
        
        result.log_summary()
        return result
    
    def _transform_records(self, input_file: str, result: TransformResult) -> Iterator[dict]:
        """
        Transform records from input file, updating the result object.
        
        Args:
            input_file: Path to input file
            result: TransformResult to update with statistics
            
        Yields:
            Transformed prompt-completion records
        """
        for record in self.file_handler.read_jsonl(input_file):
            result.records_processed += 1
            
            # Extract messages
            messages = extract_messages(record)
            if messages is None:
                result.add_error(f"Could not extract messages from record {result.records_processed}")
                continue
            
            user_msg, assistant_msg = messages
            
            # Create prompt-completion record
            transformed_record = create_prompt_completion(user_msg, assistant_msg)
            yield transformed_record
    
    def transform_all_files(self) -> List[TransformResult]:
        """
        Transform all JSONL files in the input directory.
        
        Returns:
            List of TransformResult objects for each file processed
        """
        input_files = self.file_handler.get_input_files()
        results = []
        
        if not input_files:
            logging.warning("No JSONL files found in input directory")
            return results
        
        logging.info(f"Starting batch transformation of {len(input_files)} files")
        
        for input_file in input_files:
            try:
                result = self.transform_file(input_file)
                results.append(result)
            except Exception as e:
                # Create error result for failed file
                error_result = TransformResult(
                    input_file=input_file,
                    output_file="",
                    records_processed=0,
                    records_transformed=0,
                    errors=[f"Failed to process file: {e}"],
                    success=False
                )
                results.append(error_result)
                logging.error(f"Failed to process {input_file}: {e}")
        
        self._log_batch_summary(results)
        return results
    
    def _log_batch_summary(self, results: List[TransformResult]) -> None:
        """Log summary statistics for batch processing."""
        total_files = len(results)
        successful_files = sum(1 for r in results if r.success)
        total_processed = sum(r.records_processed for r in results)
        total_transformed = sum(r.records_transformed for r in results)
        
        logging.info(f"Batch transformation complete:")
        logging.info(f"  Files processed: {successful_files}/{total_files}")
        logging.info(f"  Records processed: {total_processed}")
        logging.info(f"  Records transformed: {total_transformed}")