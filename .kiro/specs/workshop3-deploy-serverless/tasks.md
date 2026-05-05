# Implementation Tasks

## Overview

Refactor the existing `workshop3/deploy_serverless/deploy_serverless.py` from using the `HuggingFaceModel` convenience wrapper to using explicit DLC image URI retrieval with the generic `sagemaker.model.Model` class. Update documentation to reflect the new educational approach.

## Tasks

- [ ] 1. Refactor deploy_serverless.py to use explicit DLC image URI
  - [ ] 1.1 Replace `from sagemaker.huggingface.model import HuggingFaceModel` with `from sagemaker.model import Model` and `from sagemaker import image_uris`
  - [ ] 1.2 Add DLC configuration constants: `IMAGE_SCOPE = "inference"`, update `PYTORCH_VERSION` to `"pytorch2.1.0"` format for `base_framework_version`, and add `INSTANCE_TYPE = "ml.m5.xlarge"` for image selection
  - [ ] 1.3 Add `retrieve_dlc_image_uri()` function that calls `image_uris.retrieve()` with framework, region, version, instance_type, image_scope, py_version, and base_framework_version parameters
  - [ ] 1.4 Print the retrieved DLC image URI so students can see the full ECR path being used
  - [ ] 1.5 Replace `HuggingFaceModel(...)` instantiation with `Model(image_uri=image_uri, env=HUB_CONFIG, role=role, sagemaker_session=sess)`
  - [ ] 1.6 Add educational comments explaining each parameter of `image_uris.retrieve()` and why the generic `Model` class is used

- [ ] 2. Update the deploy function flow
  - [ ] 2.1 Call `retrieve_dlc_image_uri()` after session/role setup and before model creation
  - [ ] 2.2 Pass the retrieved image URI to the `Model` constructor
  - [ ] 2.3 Verify the ServerlessInferenceConfig and `model.deploy()` call remain unchanged (they work the same with the generic Model class)

- [ ] 3. Update the module docstring and script header
  - [ ] 3.1 Update the module docstring to describe the DLC-based approach instead of the HuggingFaceModel approach
  - [ ] 3.2 Add a comment block explaining the educational purpose: showing how to use ANY DLC with the generic Model class
  - [ ] 3.3 Add a reference comment to the AWS DLC available images catalog URL

- [ ] 4. Update README.md documentation
  - [ ] 4.1 Add a section explaining the difference between `HuggingFaceModel` wrapper and explicit DLC approach
  - [ ] 4.2 Add a section on how to find available DLC images (link to AWS DLC GitHub repository)
  - [ ] 4.3 Add a section showing how to adapt the pattern for other frameworks (PyTorch DLC, TensorFlow DLC)
  - [ ] 4.4 Update the deployment description to mention explicit DLC image URI retrieval
  - [ ] 4.5 Ensure prerequisites, runbook (deploy/invoke/cleanup), and cost estimate sections remain accurate

- [ ] 5. Validate the refactored script
  - [ ] 5.1 Verify the script runs without import errors (`python deploy_serverless.py --help`)
  - [ ] 5.2 Verify `image_uris.retrieve()` returns a valid ECR URI for the specified parameters
  - [ ] 5.3 Confirm the deploy/invoke/cleanup commands still work end-to-end with the generic Model class
