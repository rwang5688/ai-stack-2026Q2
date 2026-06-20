# Container Remediation Findings

## StudentServicesPhase2-stl-front

### Resource Details

| Field | Value |
|-------|-------|
| Task ID | `99214afe58334c36a245b467df8518bf` |
| Start time | 8 days ago |
| Image URI | `149057604171.dkr.ecr.us-west-2.amazonaws.com/cdk-hnb659fds-container-assets-149057604171-us-west-2:78a5911a06baff2a6ba9eae4f9140abcea65242fee32c3635d8b5eaf055c9ab1` |
| Owner | Robert Wang (@wangrob) |
| Updated at | 9 hours ago |
| Service name | `StudentServicesPhase2-stl-front` |
| Container status | Running |
| Region | US West (Oregon) us-west-2 |
| In compliance scope | False |
| Task status | RUNNING |
| Image type | ECR |
| Tags | **Out of SLA** |
| Orchestration source | ECS |
| Image hash | `sha256:e4d17585f210de35fc6d7e759191d76529976f9d8500f2cf937833ef37913b91` |
| Last observed at | 9 hours ago |
| Automated Patching Enabled | Unavailable |

### Finding: OS Container Updates Required

| Field | Value |
|-------|-------|
| Finding ID | `finding:softwareVulnerability:asset:container:ECS:us-west-2:fc93bb23-d11e-4299-8b75-128cf295cf40` |
| Priority | Priority 2 (72) |
| Status | Assigned |
| SLA date | 20 hours ago (**overdue**) |
| First observed at | June 11, 2026, 06:53 (UTC-07:00) |
| Updated at | 9 hours ago |
| Last observed at | June 19, 2026, 14:06 (UTC-07:00) |
| Orchestration source | ECS |

**Description:** One or more packages within this image are vulnerable and require remediation.

#### Impacted Resource

| Field | Value |
|-------|-------|
| Container account ID | `149057604171` (wangrob-aiml-03) |
| Image hash | `sha256:e4d17585f210de35fc6d7e759191d76529976f9d8500f2cf937833ef37913b91` |
| Repository account ID | `149057604171` (wangrob-aiml-03) |
| Task definition family | `StudentServicesPhase2StudentServicesPhase2WebappTaskDefEAF36447` |
| Service name | `StudentServicesPhase2-stl-front` |
| Launch type | Fargate |
| Host type | NAWS |
| Region | US West (Oregon) us-west-2 |

#### Package Details

##### Critical Severity

| Package | CVE | Installed Version | Fixed Version |
|---------|-----|-------------------|---------------|
| unbound | CVE-2026-33278 | 1.22.0-2+deb13u2 | 1.22.0-2+deb13u3 |
| unbound | CVE-2026-42960 | 1.22.0-2+deb13u2 | 1.22.0-2+deb13u3 |
| openssl | CVE-2026-34182 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |

##### High Severity

| Package | CVE | Installed Version | Fixed Version |
|---------|-----|-------------------|---------------|
| unbound | CVE-2026-40622 | 1.22.0-2+deb13u2 | 1.22.0-2+deb13u3 |
| unbound | CVE-2026-42944 | 1.22.0-2+deb13u2 | 1.22.0-2+deb13u3 |
| unbound | CVE-2026-41292 | 1.22.0-2+deb13u2 | 1.22.0-2+deb13u3 |
| unbound | CVE-2026-42959 | 1.22.0-2+deb13u2 | 1.22.0-2+deb13u3 |
| openssl | CVE-2026-34181 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-34180 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-34183 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-42764 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-45445 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-45447 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-7383 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-9076 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| imagemagick | CVE-2026-46522 | 7.1.1.43+dfsg1-1+deb13u8 | 7.1.1.43+dfsg1-1+deb13u9 |
| imagemagick | CVE-2026-46520 | 7.1.1.43+dfsg1-1+deb13u8 | 7.1.1.43+dfsg1-1+deb13u9 |

##### Medium Severity

| Package | CVE | Installed Version | Fixed Version |
|---------|-----|-------------------|---------------|
| libgcrypt20 | CVE-2026-41989 | 1.11.0-7 | 1.11.0-7+deb13u1 |
| krb5 | CVE-2026-40355 | 1.21.3-5 | 1.21.3-5+deb13u1 |
| krb5 | CVE-2026-40356 | 1.21.3-5 | 1.21.3-5+deb13u1 |
| imagemagick | CVE-2026-42050 | 7.1.1.43+dfsg1-1+deb13u8 | 7.1.1.43+dfsg1-1+deb13u9 |
| unbound | CVE-2026-32792 | 1.22.0-2+deb13u2 | 1.22.0-2+deb13u3 |
| unbound | CVE-2026-42923 | 1.22.0-2+deb13u2 | 1.22.0-2+deb13u3 |
| unbound | CVE-2026-42534 | 1.22.0-2+deb13u2 | 1.22.0-2+deb13u3 |
| unbound | CVE-2026-44390 | 1.22.0-2+deb13u2 | 1.22.0-2+deb13u3 |
| unbound | CVE-2026-44608 | 1.22.0-2+deb13u2 | 1.22.0-2+deb13u3 |
| openssl | CVE-2026-42766 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-42767 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-42769 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-45446 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| imagemagick | CVE-2026-45358 | 7.1.1.43+dfsg1-1+deb13u8 | 7.1.1.43+dfsg1-1+deb13u9 |
| imagemagick | CVE-2026-42326 | 7.1.1.43+dfsg1-1+deb13u8 | 7.1.1.43+dfsg1-1+deb13u9 |
| imagemagick | CVE-2026-45031 | 7.1.1.43+dfsg1-1+deb13u8 | 7.1.1.43+dfsg1-1+deb13u9 |
| imagemagick | CVE-2026-45624 | 7.1.1.43+dfsg1-1+deb13u8 | 7.1.1.43+dfsg1-1+deb13u9 |
| imagemagick | CVE-2026-45359 | 7.1.1.43+dfsg1-1+deb13u8 | 7.1.1.43+dfsg1-1+deb13u9 |
| imagemagick | CVE-2026-45664 | 7.1.1.43+dfsg1-1+deb13u8 | 7.1.1.43+dfsg1-1+deb13u9 |
| imagemagick | CVE-2026-46523 | 7.1.1.43+dfsg1-1+deb13u8 | 7.1.1.43+dfsg1-1+deb13u9 |
| imagemagick | CVE-2026-46521 | 7.1.1.43+dfsg1-1+deb13u8 | 7.1.1.43+dfsg1-1+deb13u9 |
| imagemagick | CVE-2026-46559 | 7.1.1.43+dfsg1-1+deb13u8 | 7.1.1.43+dfsg1-1+deb13u9 |
| imagemagick | CVE-2026-46557 | 7.1.1.43+dfsg1-1+deb13u8 | 7.1.1.43+dfsg1-1+deb13u9 |
| imagemagick | CVE-2026-46693 | 7.1.1.43+dfsg1-1+deb13u8 | 7.1.1.43+dfsg1-1+deb13u9 |
| imagemagick | CVE-2026-46692 | 7.1.1.43+dfsg1-1+deb13u8 | 7.1.1.43+dfsg1-1+deb13u9 |
| imagemagick | CVE-2026-47165 | 7.1.1.43+dfsg1-1+deb13u8 | 7.1.1.43+dfsg1-1+deb13u9 |
| imagemagick | CVE-2026-47166 | 7.1.1.43+dfsg1-1+deb13u8 | 7.1.1.43+dfsg1-1+deb13u9 |

##### Low Severity

| Package | CVE | Installed Version | Fixed Version |
|---------|-----|-------------------|---------------|
| openssl | CVE-2026-42770 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-42768 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |

#### Additional Details

| Field | Value |
|-------|-------|
| AWS Account Classification | Non-Prod |
| AWS Account ID | `149057604171` |
| AWS Account Name | wangrob-aiml-03 |
| AWS Account Email | wangrob+aiml-03@amazon.com |

---

## StudentServicesPhase3-stl-front

### Resource Details

| Field | Value |
|-------|-------|
| Task ID | `36f16a478fec4d1b83c9ee7496b16882` |
| Start time | 9 days ago |
| Image URI | `149057604171.dkr.ecr.us-west-2.amazonaws.com/cdk-hnb659fds-container-assets-149057604171-us-west-2:fb3956776f584741e3ec0c40099ad77676f74e5ae320a6de00eaee8fb7d0ff28` |
| Owner | Robert Wang (@wangrob) |
| Updated at | 4 hours ago |
| Service name | `StudentServicesPhase3-stl-front` |
| Container status | Running |
| Region | US West (Oregon) us-west-2 |
| In compliance scope | False |
| Task status | RUNNING |
| Image type | ECR |
| Tags | **Within SLA** |
| Orchestration source | ECS |
| Image hash | `sha256:43c829d04206dca01603be9800ffff8a78cf9c32241f984c94635124bf7c3f07` |
| Last observed at | 4 hours ago |
| Automated Patching Enabled | Unavailable |

### Finding: OS Container Updates Required

| Field | Value |
|-------|-------|
| Finding ID | `finding:softwareVulnerability:asset:container:ECS:us-west-2:36d5df6a-b41a-432a-a951-9864e6c3324b` |
| Priority | Priority 2 (70) |
| Status | Assigned |
| SLA date | in 19 days |
| First observed at | June 10, 2026, 18:49 (UTC-07:00) |
| Updated at | 4 hours ago |
| Last observed at | June 19, 2026, 19:03 (UTC-07:00) |
| Orchestration source | ECS |

**Description:** One or more packages within this image are vulnerable and require remediation.

#### Impacted Resource

| Field | Value |
|-------|-------|
| Container account ID | `149057604171` (wangrob-aiml-03) |
| Image hash | `sha256:43c829d04206dca01603be9800ffff8a78cf9c32241f984c94635124bf7c3f07` |
| Repository account ID | `149057604171` (wangrob-aiml-03) |
| Task definition family | `StudentServicesPhase3StudentServicesPhase3WebappTaskDef0409F928` |
| Service name | `StudentServicesPhase3-stl-front` |
| Launch type | Fargate |
| Host type | NAWS |
| Region | US West (Oregon) us-west-2 |

#### Package Details

##### Critical Severity

| Package | CVE | Installed Version | Fixed Version |
|---------|-----|-------------------|---------------|
| openssl | CVE-2026-34182 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |

##### High Severity

| Package | CVE | Installed Version | Fixed Version |
|---------|-----|-------------------|---------------|
| openssl | CVE-2026-34181 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-34180 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-34183 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-42764 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-45445 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-45447 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-7383 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-9076 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |

##### Medium Severity

| Package | CVE | Installed Version | Fixed Version |
|---------|-----|-------------------|---------------|
| openssl | CVE-2026-42766 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-42767 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-42769 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-45446 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |

##### Low Severity

| Package | CVE | Installed Version | Fixed Version |
|---------|-----|-------------------|---------------|
| openssl | CVE-2026-42770 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |
| openssl | CVE-2026-42768 | 3.5.6-1~deb13u1 | 3.5.6-1~deb13u2 |

#### Additional Details

| Field | Value |
|-------|-------|
| AWS Account Classification | Non-Prod |
| AWS Account ID | `149057604171` |
| AWS Account Name | wangrob-aiml-03 |
| AWS Account Email | wangrob+aiml-03@amazon.com |

---

## Remediation Guidance

The following remediation steps apply to both findings:

1. If the container is no longer needed, terminate the container from the specific orchestration platform to address the findings.
2. For containers still in use, consult your team's remediation runbook to see if there are existing established processes for updating and deploying the latest container image.
3. Prior to deploying the new container image, verify if the new container image has been scanned by Inspector and is free of the CVE-IDs listed in the package details section.
4. Prior to running Amazon Inspector, make sure to enable enhanced scanning for your private ECR registry.
5. For pipeline-dependent container images, verify that the pipeline is not blocked and merging from live to use the most up-to-date base image and dependencies.
6. If your team is dependent on a base image from another team or external vendor, you're responsible for retrieving the updated image and deploying them in accordance to remediation SLAs.
7. For container images using version-specific OS packages, assess whether these pinned dependencies require updating to a newer version.
8. If your team installs additional OS packages as part of the build process, `apt-get upgrade` should be configured in the image's Dockerfile to run after these packages are installed.
9. For teams that do not use DockerFileBuild, review your Dockerfiles to see if `apt-get upgrade` is included as part of the build. If it is, a re-build/re-deploy should also remediate all findings.
10. Ensure all container deployments in all regions are using the latest patched container images.
11. Prevent the deployment of containers using any known vulnerable container images.
