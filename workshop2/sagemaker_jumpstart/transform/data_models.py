"""
Data models and type definitions for dataset transformation.
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@dataclass
class TransformResult:
    """Encapsulates the results of a transformation operation."""
    input_file: str
    output_file: str
    records_processed: int
    records_transformed: int
    errors: List[str]
    success: bool
    
    def __post_init__(self):
        """Validate the result after initialization."""
        self.success = len(self.errors) == 0 or self.records_transformed > 0
    
    def add_error(self, error: str) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        logging.error(f"Transform error in {self.input_file}: {error}")
    
    def log_summary(self) -> None:
        """Log a summary of the transformation result."""
        if self.success:
            logging.info(f"Successfully transformed {self.records_transformed}/{self.records_processed} records from {self.input_file}")
        else:
            logging.error(f"Failed to transform {self.input_file}: {len(self.errors)} errors")


def extract_messages(record: dict) -> Optional[Tuple[str, str]]:
    """
    Extract user and assistant messages from a messages-based record.
    
    Args:
        record: Dictionary containing messages array
        
    Returns:
        Tuple of (user_message, assistant_message) or None if extraction fails
    """
    try:
        messages = record.get('messages', [])
        if not isinstance(messages, list) or len(messages) < 2:
            return None
            
        user_msg = None
        assistant_msg = None
        
        for message in messages:
            if not isinstance(message, dict):
                continue
                
            role = message.get('role')
            content = message.get('content')
            
            if role == 'user' and content:
                user_msg = content
            elif role == 'assistant' and content:
                assistant_msg = content
        
        if user_msg is not None and assistant_msg is not None:
            return (user_msg, assistant_msg)
            
        return None
        
    except Exception as e:
        logging.warning(f"Error extracting messages: {e}")
        return None


def create_prompt_completion(user_msg: str, assistant_msg: str) -> dict:
    """
    Create a prompt-completion record from user and assistant messages.
    
    Args:
        user_msg: The user's message content
        assistant_msg: The assistant's message content
        
    Returns:
        Dictionary with prompt and completion fields
    """
    return {
        "prompt": user_msg,
        "completion": assistant_msg
    }