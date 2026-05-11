# Requirements Document

## Introduction

This feature transforms existing JSONL dataset files from a messages-based format to the prompt-completion format required by SageMaker Studio for model fine-tuning. The transformation script will be located in workshop2/transform directory, read input datasets from workshop2/input directory, and write transformed datasets to workshop2/output directory. The transformation ensures compatibility with SageMaker's customization techniques while preserving the original training data content.

## Glossary

- **Dataset_Transformer**: The Python script that converts dataset formats
- **Input_Directory**: The workshop2/input directory containing source JSONL files
- **Transform_Directory**: The workshop2/transform directory containing the transformation script
- **Output_Directory**: The workshop2/output directory for transformed JSONL files
- **Source_Dataset**: The original JSONL file with messages format in Input_Directory
- **Target_Dataset**: The transformed JSONL file with prompt-completion format in Output_Directory
- **SageMaker_Studio**: AWS service requiring specific dataset format for model customization

## Requirements

### Requirement 1: Dataset Format Transformation

**User Story:** As a machine learning engineer, I want to transform message-based datasets to prompt-completion format, so that I can use them with SageMaker Studio fine-tuning.

#### Acceptance Criteria

1. WHEN a source dataset with messages format is provided in Input_Directory, THE Dataset_Transformer SHALL extract the user message as "prompt" and assistant message as "completion"
2. WHEN transforming each record, THE Dataset_Transformer SHALL preserve the exact content of user and assistant messages
3. WHEN creating the target dataset, THE Dataset_Transformer SHALL output valid JSONL format with each line containing a single JSON object to Output_Directory
4. THE Dataset_Transformer SHALL create output files with the same base name as input files in Output_Directory

### Requirement 2: Data Validation and Error Handling

**User Story:** As a machine learning engineer, I want robust error handling during transformation, so that I can identify and resolve data quality issues.

#### Acceptance Criteria

1. WHEN a source file contains invalid JSON, THE Dataset_Transformer SHALL log the error and continue processing valid records
2. WHEN a record lacks required message structure, THE Dataset_Transformer SHALL skip the record and log a warning
3. WHEN transformation completes, THE Dataset_Transformer SHALL report the number of successfully transformed records
4. IF no valid records are found, THEN THE Dataset_Transformer SHALL create an empty output file and report the issue

### Requirement 3: Multiple Dataset Processing

**User Story:** As a machine learning engineer, I want to transform multiple dataset files at once, so that I can efficiently prepare all training data for SageMaker Studio.

#### Acceptance Criteria

1. WHEN multiple source files are specified in Input_Directory, THE Dataset_Transformer SHALL process each file independently
2. WHEN processing multiple files, THE Dataset_Transformer SHALL generate separate output files in Output_Directory for each source
3. THE Dataset_Transformer SHALL process all available dataset files in Input_Directory when no specific files are specified
4. WHEN batch processing, THE Dataset_Transformer SHALL continue processing remaining files if one file fails

### Requirement 4: Output Format Compliance

**User Story:** As a machine learning engineer, I want the output format to exactly match SageMaker Studio requirements, so that my datasets are immediately usable for fine-tuning.

#### Acceptance Criteria

1. THE Dataset_Transformer SHALL output each record as a single JSON object with "prompt" and "completion" fields
2. WHEN creating JSON objects, THE Dataset_Transformer SHALL ensure proper escaping of special characters
3. THE Dataset_Transformer SHALL validate that each output line is valid JSON before writing to file
4. THE Dataset_Transformer SHALL preserve Unicode characters and special formatting in the original content