# Implementation Plan: Workshop3 OpenAI Whisper Upgrade

## Overview

Update both OpenAI Whisper SageMaker deployment notebooks to achieve structural parity, with the upgraded notebook (`pytorch_sagemaker_4.ipynb`) targeting SageMaker Distribution 4.x and the baseline (`pytorch_sagemaker_2.ipynb`) retaining Distribution 2.x versions. Both notebooks receive usability enhancements (auto-bucket, auto-region, load_dataset fix). The only permitted differences between notebooks are: setup markdown, pip version specifiers, DLC image tag, and environment variable prefix (MMS_* vs TS_*).

## Tasks

- [x] 1. Update upgraded notebook (pytorch_sagemaker_4.ipynb) version specifiers and DLC image
  - [x] 1.1 Fix openai-whisper version pin to 20231117 in the pip install cell
    - Change `%pip install openai-whisper==20240930 -q` to `%pip install openai-whisper==20231117 -q`
    - _Requirements: 2.1_
  - [x] 1.2 Fix DLC image tag to match design specification
    - Change `huggingface-pytorch-inference:2.6.0-transformers4.51.3-gpu-py312-cu124-ubuntu22.04` to `huggingface-pytorch-inference:2.6.0-transformers5.5.3-gpu-py312-cu124-ubuntu22.04`
    - _Requirements: 3.1, 3.2_

- [x] 2. Update baseline notebook (pytorch_sagemaker_2.ipynb) package pins
  - [x] 2.1 Pin librosa and soundfile versions in the pip install cell
    - Change `%pip install librosa -q` to `%pip install librosa==0.10.1 -q`
    - Change `%pip install soundfile -q` to `%pip install soundfile==0.12.1 -q`
    - _Requirements: 2.5, 13.1_

- [ ] 3. Checkpoint - Verify structural parity between notebooks
  - Ensure all tests pass, ask the user if questions arise.
  - Compare both notebooks cell-by-cell to confirm they differ ONLY in:
    - Setup markdown (Distribution 2.x vs 4.x instruction)
    - `%pip install` version specifiers
    - DLC image tag (`2.0.0-transformers4.28.1-gpu-py310-cu118-ubuntu20.04` vs `2.6.0-transformers5.5.3-gpu-py312-cu124-ubuntu22.04`)
    - Environment variable prefix (`MMS_*` vs `TS_*`) and associated comment
    - `source_dir` (`code_sagemaker_2` vs `code_sagemaker_4`)
    - Endpoint instance type (`ml.g4dn.xlarge` vs `ml.g6.xlarge`)
  - Verify no occurrences of `[BUCKET NAME]` in either notebook
  - Verify no occurrences of `[REGION]` in either notebook
  - Verify no occurrences of "Data Science 2.0" in `pytorch_sagemaker_4.ipynb`
  - Verify `'clean'` appears in the `load_dataset` call in both notebooks
  - _Requirements: 9.1, 10.1, 10.2, 10.3, 11.1, 11.2, 11.3, 12.1, 12.2, 13.1, 13.2, 13.3_

## Notes

- Both notebooks already have auto-bucket resolution (`sess.default_bucket()`) and auto-region resolution (`boto3.Session().region_name`) in place
- Both notebooks already have the corrected `load_dataset('MLCommons/peoples_speech', 'clean', split='train', streaming=True)` call
- The upgraded notebook already uses `TS_*` environment variables; baseline already uses `MMS_*`
- No property-based tests apply — this is a notebook configuration upgrade with no pure functions or algorithmic logic
- The implementation language is Python (Jupyter notebook cells)
- Full functional validation requires manual execution in SageMaker Studio (cannot be automated locally)

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "2.1"] },
    { "id": 1, "tasks": [] }
  ]
}
```
