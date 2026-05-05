"""
Converter module for transforming JSONL files to Amazon Nova Bedrock conversation format.

This module converts OpenAI-style message format to the Bedrock conversation format
required by Amazon Nova customization.
"""

import json
from typing import Dict, List, Any


def convert_message_to_bedrock_format(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a single message from OpenAI format to Bedrock format.
    
    OpenAI format: {"content": "text", "role": "user"}
    Bedrock format: {"role": "user", "content": [{"text": "text"}]}
    
    Args:
        message: Message in OpenAI format
        
    Returns:
        Message in Bedrock format
    """
    return {
        "role": message["role"],
        "content": [
            {
                "text": message["content"]
            }
        ]
    }


def convert_record_to_bedrock_format(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a complete record from OpenAI format to Bedrock conversation format.
    
    Args:
        record: Record with "messages" array in OpenAI format
        
    Returns:
        Record in Bedrock conversation format with schemaVersion
    """
    bedrock_record = {
        "schemaVersion": "bedrock-conversation-2024",
        "messages": [
            convert_message_to_bedrock_format(msg)
            for msg in record["messages"]
        ]
    }
    
    return bedrock_record


def convert_jsonl_file(input_content: str) -> List[Dict[str, Any]]:
    """
    Convert entire JSONL file content from OpenAI to Bedrock format.
    
    Args:
        input_content: String content of JSONL file
        
    Returns:
        List of converted records in Bedrock format
    """
    converted_records = []
    
    for line in input_content.strip().split('\n'):
        if line.strip():
            record = json.loads(line)
            converted_record = convert_record_to_bedrock_format(record)
            converted_records.append(converted_record)
    
    return converted_records


def format_output_filename(input_filename: str) -> str:
    """
    Generate output filename by replacing extension with _transform2ed.jsonl.
    
    Args:
        input_filename: Original filename (e.g., "train_sft_1k.jsonl")
        
    Returns:
        Output filename (e.g., "train_sft_1k_transform2ed.jsonl")
    """
    if input_filename.endswith('.jsonl'):
        base_name = input_filename[:-6]  # Remove .jsonl
    else:
        base_name = input_filename
    
    return f"{base_name}_transform2ed.jsonl"
