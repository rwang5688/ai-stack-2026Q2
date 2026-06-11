# Requirements Document

## Introduction

Upgrade the OpenAI Whisper SageMaker deployment notebook (`pytorch_sagemaker_4.ipynb`) to work on SageMaker Distribution 4.x. The existing `pytorch_sagemaker_2.ipynb` notebook was developed approximately two years ago and targets SageMaker Distribution 2.x with outdated package versions and DLC image URIs. The upgraded notebook must maintain full functional parity with the original (same Whisper base model, same three deployment patterns) while using current, compatible dependencies and infrastructure references.

## Glossary

- **Notebook**: The Jupyter notebook file `pytorch_sagemaker_4.ipynb` located in `workshop3/openai_whisper/`
- **Baseline_Notebook**: The original `pytorch_sagemaker_2.ipynb` retained as reference and fallback for SageMaker Distribution 2.x
- **SageMaker_Distribution_4x**: The SageMaker Studio Distribution 4.x runtime image providing pre-installed ML libraries
- **DLC_Image**: AWS Deep Learning Container image URI used for PyTorch model inference on SageMaker endpoints
- **MMS**: Multi-Model Server, the model serving framework used in HuggingFace PyTorch DLC containers
- **TorchServe**: The PyTorch-native model serving framework that replaces MMS in newer DLC images
- **Real_Time_Endpoint**: A SageMaker endpoint that processes inference requests synchronously
- **Batch_Transform**: A SageMaker job that processes a collection of input data from S3 asynchronously
- **Async_Endpoint**: A SageMaker endpoint that queues inference requests and stores results in S3
- **Whisper_Base_Model**: The OpenAI Whisper "base" model for automatic speech recognition
- **SageMaker_Python_SDK**: The `sagemaker` Python library for interacting with SageMaker services

## Requirements

### Requirement 1: SageMaker Distribution 4.x Targeting

**User Story:** As a workshop participant, I want the notebook to specify SageMaker Distribution 4.x as the required runtime image, so that I can run the notebook on a current SageMaker Studio environment without compatibility issues.

#### Acceptance Criteria

1. THE Notebook SHALL instruct users to select the SageMaker Distribution 4.x image and an ml.m5.large instance in the setup markdown cell
2. WHEN a user opens the Notebook in SageMaker Studio, THE Notebook SHALL contain no references to "Data Science 2.0" or SageMaker Distribution 2.x in any cell

### Requirement 2: Updated Python Package Dependencies

**User Story:** As a workshop participant, I want the notebook to install current, compatible versions of all required Python packages, so that I can execute all cells without version conflicts on SageMaker Distribution 4.x.

#### Acceptance Criteria

1. THE Notebook SHALL install `openai-whisper` at version 20231117 or later using a `%pip install` command with a pinned version specifier
2. THE Notebook SHALL install `torchaudio` at a version matching the major and minor version of the PyTorch pre-installed in SageMaker Distribution 4.x (PyTorch 2.5.x requires torchaudio 2.5.x)
3. THE Notebook SHALL install `datasets` at version 3.0.0 or later using a pinned version specifier
4. THE Notebook SHALL install `sagemaker` Python SDK at version 2.200.0 or later using a pinned version specifier
5. THE Notebook SHALL install `librosa` and `soundfile` packages with pinned version specifiers
6. WHEN all `%pip install` cells have completed execution and the kernel has been restarted, THE Notebook SHALL execute the import cell containing `import torch`, `import whisper`, `import torchaudio`, `import sagemaker`, `import soundfile as sf`, and `from datasets import load_dataset` without raising `ImportError`, `ModuleNotFoundError`, or `RuntimeError` due to version conflicts

### Requirement 3: Updated DLC Inference Image URI

**User Story:** As a workshop participant, I want the notebook to reference a current PyTorch DLC inference image, so that model deployment uses a supported container with up-to-date libraries.

#### Acceptance Criteria

1. THE Notebook SHALL specify a HuggingFace PyTorch inference DLC image URI with a tag that includes PyTorch 2.x, CUDA 12.x, Python 3.10 or 3.11, and a GPU variant (the repository name must contain "inference")
2. THE Notebook SHALL use the AWS DLC ECR registry format `763104351884.dkr.ecr.[REGION].amazonaws.com/<repository>:<tag>` where `<repository>` is a HuggingFace PyTorch inference repository and `<tag>` corresponds to a published image in the AWS Deep Learning Containers catalog
3. THE Notebook SHALL include a code comment on the line immediately preceding or on the same line as the image URI assignment, instructing users to replace `[REGION]` with their AWS region (e.g., us-east-1)

### Requirement 4: Updated Model Serving Environment Variables

**User Story:** As a workshop participant, I want the notebook to use the correct model serving environment variables for the selected DLC image, so that large audio file inference requests succeed without timeout or size limit errors.

#### Acceptance Criteria

1. WHEN the selected DLC image uses TorchServe as the serving framework, THE Notebook SHALL set `TS_MAX_REQUEST_SIZE`, `TS_MAX_RESPONSE_SIZE`, and `TS_DEFAULT_RESPONSE_TIMEOUT` environment variables
2. WHEN the selected DLC image uses MMS as the serving framework, THE Notebook SHALL set `MMS_MAX_REQUEST_SIZE`, `MMS_MAX_RESPONSE_SIZE`, and `MMS_DEFAULT_RESPONSE_TIMEOUT` environment variables
3. THE Notebook SHALL configure the maximum request size to at least 2,000,000,000 bytes
4. THE Notebook SHALL configure the maximum response size to at least 2,000,000,000 bytes
5. THE Notebook SHALL configure the response timeout to at least 900 seconds

### Requirement 5: Real-Time Inference Deployment

**User Story:** As a workshop participant, I want to deploy the Whisper model as a real-time SageMaker endpoint, so that I can transcribe audio files with synchronous responses.

#### Acceptance Criteria

1. THE Notebook SHALL create a PyTorchModel using the DLC image URI, the S3 model artifacts path, the IAM execution role, an inference entry point script, a source directory, and environment variables for request size and response timeout configuration
2. THE Notebook SHALL deploy the model to a real-time endpoint on 1 ml.g4dn.xlarge instance with an audio data serializer (content type "audio/x-audio") and a JSON deserializer
3. WHEN an audio file with content type "audio/x-audio" is sent to the real-time endpoint, THE Real_Time_Endpoint SHALL return a JSON response containing a "text" field with the transcribed audio content
4. THE Notebook SHALL include a cell to delete the real-time endpoint after testing to stop incurring instance charges

### Requirement 6: Batch Transform Inference

**User Story:** As a workshop participant, I want to run batch transcription on multiple audio files stored in S3, so that I can process large audio datasets without managing an endpoint.

#### Acceptance Criteria

1. THE Notebook SHALL create a Transformer object using the PyTorchModel with 1 ml.g4dn.xlarge instance
2. THE Notebook SHALL configure the batch transform output path using the user's S3 bucket and prefix in the format `s3://{bucket}/{prefix}/batch-transform/`
3. THE Notebook SHALL start a batch transform job with a unique job name that processes audio files from a user-specified S3 input path
4. THE Notebook SHALL set `max_payload` to 100 to accommodate audio files up to 100 MB
5. THE Notebook SHALL start the batch transform job in non-blocking mode (`wait=False`)

### Requirement 7: Asynchronous Inference with Autoscaling

**User Story:** As a workshop participant, I want to deploy the Whisper model as an asynchronous endpoint with autoscaling, so that I can handle variable workloads efficiently and scale to zero when idle.

#### Acceptance Criteria

1. THE Notebook SHALL create an AsyncInferenceConfig with an S3 output path and a max concurrent invocations per instance value of 4
2. THE Notebook SHALL deploy the model to an ml.g4dn.xlarge instance as an async endpoint with an initial instance count of 1
3. WHEN an audio file S3 path is provided with content type `audio/x-audio`, THE Async_Endpoint SHALL accept the inference request and return an S3 output location path
4. THE Notebook SHALL configure Application Auto Scaling with a minimum capacity of 0 and maximum capacity of 3 for the `sagemaker:variant:DesiredInstanceCount` scalable dimension
5. THE Notebook SHALL define a target-tracking scaling policy using the `ApproximateBacklogSizePerInstance` metric with a target value of 3.0 and scale-in and scale-out cooldown periods of 60 seconds each
6. THE Notebook SHALL include a cell to delete the async endpoint after testing

### Requirement 8: SageMaker Python SDK API Compatibility

**User Story:** As a workshop participant, I want all SageMaker SDK calls to use current API patterns, so that the notebook does not trigger deprecation warnings or use removed APIs.

#### Acceptance Criteria

1. THE Notebook SHALL use SageMaker Python SDK method signatures and parameter names that are not deprecated or removed in the installed SDK version (minimum version 2.200.0 per Requirement 2)
2. IF the SageMaker Python SDK has replaced parameter names or method signatures between SDK version 2.184.0 and the installed version, THEN THE Notebook SHALL use the replacement API rather than the deprecated form
3. WHEN all notebook cells are executed sequentially in a SageMaker Distribution 4.x environment, THE Notebook SHALL produce zero DeprecationWarning messages in cell output (stdout or stderr)

### Requirement 9: Structural Parity with Baseline Notebook

**User Story:** As a workshop participant, I want the upgraded notebook to follow the same overall structure and flow as the baseline, so that workshop instructions and documentation remain applicable.

#### Acceptance Criteria

1. THE Notebook SHALL maintain the same markdown section ordering as the Baseline_Notebook: Common Setup, Model Artifacts, Real-Time Inference, Batch Transform, Async Inference, Autoscaling, Cleanup
2. THE Notebook SHALL use the Whisper "base" model for all deployment patterns
3. THE Notebook SHALL use the same S3 prefix structure (`whisper_blog_post`) for model artifacts and outputs
4. THE Notebook SHALL use the same test dataset source (`MLCommons/peoples_speech`) for real-time inference validation

### Requirement 10: Automatic S3 Bucket Resolution

**User Story:** As a workshop participant, I want the notebook to automatically resolve the default SageMaker bucket, so that I can run the notebook without manually editing a bucket name placeholder.

#### Acceptance Criteria

1. THE Notebook SHALL set the `bucket` variable using `sagemaker.Session().default_bucket()` instead of a hardcoded `[BUCKET NAME]` placeholder
2. WHEN the notebook is executed in a SageMaker Studio environment, THE bucket variable SHALL resolve to the format `sagemaker-{region}-{account_id}` without requiring any user edits
3. THE Baseline_Notebook SHALL apply the same automatic bucket resolution as the Notebook

### Requirement 11: Automatic Region Resolution for DLC Image URI

**User Story:** As a workshop participant, I want the DLC image URI to automatically use my current AWS region, so that I can run the notebook without manually replacing a region placeholder.

#### Acceptance Criteria

1. THE Notebook SHALL programmatically resolve the AWS region using `boto3.Session().region_name` or equivalent
2. THE Notebook SHALL construct the DLC image URI by inserting the resolved region into the ECR URL, eliminating the `[REGION]` placeholder that requires manual editing
3. THE Baseline_Notebook SHALL apply the same automatic region resolution as the Notebook

### Requirement 12: Updated load_dataset API Call

**User Story:** As a workshop participant, I want the dataset loading call to use the current `datasets` library API signature, so that the notebook does not fail due to API changes since the original notebook was developed.

#### Acceptance Criteria

1. THE Notebook SHALL call `load_dataset('MLCommons/peoples_speech', 'clean', split='train', streaming=True)` with `'clean'` as the second positional argument
2. THE Baseline_Notebook SHALL use the same `load_dataset` call signature with `'clean'` as the second positional argument

### Requirement 13: Structural Parity Between Notebooks

**User Story:** As a workshop instructor, I want both notebooks to be structurally and programmatically identical except for package versions and DLC image tags, so that the only difference between them is which SageMaker Distribution image they target.

#### Acceptance Criteria

1. THE Notebook and THE Baseline_Notebook SHALL have identical code cell logic and markdown structure, differing ONLY in the setup markdown cell (Distribution 2.x vs 4.x instruction), `%pip install` version specifiers, and the DLC image URI tag
2. WHEN a user selects the correct SageMaker Distribution image (2.x for Baseline_Notebook, 4.x for Notebook), both notebooks SHALL execute all cells successfully with equivalent functional behavior
3. THE Baseline_Notebook SHALL receive the same usability enhancements (automatic bucket resolution, automatic region resolution, updated `load_dataset` signature) as the Notebook
