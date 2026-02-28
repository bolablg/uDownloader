# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in uDownloader, please email security@example.com instead of using the issue tracker.

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

We will acknowledge your report within 48 hours and provide an estimated timeline for a fix.

## Security Considerations

### Using uDownloader Securely

1. **Keep it updated** - Use the latest version from PyPI
2. **Verify downloads** - Check file integrity after downloading
3. **Protect your credentials** - Don't commit config files with sensitive data
4. **Use HTTPS URLs only** - Prefer secure connections
5. **Report issues responsibly** - Don't publicly disclose vulnerabilities

## Supported Versions

| Version | Status | Support |
|---------|--------|---------|
| 0.1.x   | Current | Full support |
| 0.0.x   | EOL | No support |

## Dependencies Security

We use `yt-dlp` which is actively maintained. We regularly check for security updates.

To check for vulnerabilities:
```bash
pip install safety
safety check
```

## Contact

For security inquiries: security@example.com
For general questions: See [CONTRIBUTING.md](CONTRIBUTING.md)
