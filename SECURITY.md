# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x     | :white_check_mark: |
| 1.x     | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please **do not** open a public issue.

Instead, report it privately:

1. Open a new GitHub issue with the `security` label (if available), or
2. Email the maintainers directly

### What to Include

- Description of the vulnerability
- Steps to reproduce (proof-of-concept)
- Potential impact assessment
- Suggested fix (optional)

### What to Expect

- We will acknowledge your report within **48 hours**
- We will aim to publish a fix within **30 days** for critical issues
- You will be credited in the release notes (unless you prefer anonymity)

### Scope

This policy covers vulnerabilities in:

- The transcription pipeline
- Configuration handling (`.env` parsing)
- Dependency usage

### Out of Scope

- HuggingFace model weights or server-side vulnerabilities
- YouTube video content issues
- Issues specific to your local environment setup

## Dependencies

This project uses several third-party dependencies. All are pinned with minimum versions in `requirements.txt`. We rely on the security audits of:

- [PyTorch](https://github.com/pytorch/pytorch/security)
- [HuggingFace Transformers](https://github.com/huggingface/transformers/security)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp/security)

Please report dependency-related issues to the respective upstream projects.
