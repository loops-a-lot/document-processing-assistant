# Contributing to Document Processing Assistant

Thank you for considering contributing to this project! This document outlines the process for contributing to the Document Processing Assistant.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

## How Can I Contribute?

### Reporting Bugs

- Check if the bug has already been reported in the Issues section
- Use the bug report template when creating a new issue
- Include detailed steps to reproduce the bug
- Include screenshots if applicable
- Describe the expected behavior and what actually happened

### Suggesting Enhancements

- Check if the enhancement has already been suggested in the Issues section
- Use the feature request template when creating a new issue
- Provide a clear description of the proposed enhancement
- Explain why this enhancement would be useful to users

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure they pass (`pytest tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Process

### Setting Up Your Development Environment

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Coding Standards

- Follow PEP 8 style guide for Python code
- Use descriptive variable names
- Include docstrings for all functions, classes, and modules
- Write unit tests for new functionality

### Running Tests

```bash
pytest tests/
```

## Pull Request Process

1. Update the README.md with details of changes if appropriate
2. Update the documentation if necessary
3. The PR should work for Python 3.7+
4. PRs will be merged once they have been reviewed and approved

## Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.