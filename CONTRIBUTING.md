# Contributing to Rails Migration Assistant

We welcome contributions to the Rails Migration Assistant project. This document provides guidelines for contributing code, documentation, and other improvements.

## Getting Started

### Development Environment Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/rails-migration-assistant.git
   cd rails-migration-assistant
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv rails_env
   source rails_env/bin/activate  # On Windows: rails_env\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

4. **Run Tests**
   ```bash
   python -m pytest tests/
   ```

## Project Structure

```
rails-migration-assistant/
├── src/                     # Core source code
│   ├── analyzer/           # Analysis engines and pattern detection
│   ├── model/              # LLM integration and AI components
│   ├── retriever/          # RAG system and knowledge retrieval
│   ├── ingest/             # Data processing and ingestion
│   └── patcher/            # Code modification utilities
├── data/                   # Rails documentation and migration data
├── tests/                  # Test suite
├── demos/                  # Example usage and demonstrations
├── tools/                  # Utility scripts for maintenance
└── examples/               # Sample outputs and use cases
```

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code formatting
- Use type hints where applicable
- Write descriptive docstrings for all functions and classes
- Keep functions focused and modular
- Use meaningful variable and function names

### Testing

- Write tests for all new functionality
- Maintain test coverage above 80%
- Use pytest for testing framework
- Include both unit tests and integration tests
- Test edge cases and error conditions

### Documentation

- Update docstrings for any modified functions
- Add inline comments for complex logic
- Update README.md if adding new features
- Include usage examples in docstrings

## Types of Contributions

### Bug Fixes

1. **Identify the Issue**
   - Check existing issues first
   - Reproduce the bug locally
   - Document steps to reproduce

2. **Create Fix**
   - Write minimal code to fix the issue
   - Add regression test
   - Ensure all tests pass

3. **Submit Pull Request**
   - Reference the issue number
   - Describe the fix approach
   - Include test results

### Feature Additions

1. **Propose Feature**
   - Open an issue to discuss the feature
   - Explain use case and benefits
   - Get feedback from maintainers

2. **Implement Feature**
   - Follow existing code patterns
   - Write comprehensive tests
   - Add documentation

3. **Code Review**
   - Address reviewer feedback
   - Ensure backward compatibility
   - Update documentation

### Documentation Improvements

- Fix typos and grammatical errors
- Add usage examples
- Improve API documentation
- Create tutorials or guides

## Specific Contribution Areas

### Analyzer Components

When contributing to the analyzer modules:

- **Pattern Detection**: Add new Rails deprecation patterns
- **Security Analysis**: Enhance vulnerability detection
- **Code Generation**: Improve LLM prompt engineering
- **Performance**: Optimize analysis speed and memory usage

### LLM Integration

For improvements to the LLM system:

- **Model Support**: Add support for new models
- **Prompt Engineering**: Improve code generation quality
- **Performance**: Optimize inference speed
- **Memory Management**: Reduce memory footprint

### User Interface

For GUI and CLI improvements:

- **Usability**: Enhance user experience
- **Features**: Add new functionality
- **Error Handling**: Improve error messages
- **Performance**: Optimize responsiveness

## Pull Request Process

### Before Submitting

1. **Run Full Test Suite**
   ```bash
   python -m pytest tests/ -v
   ```

2. **Check Code Quality**
   ```bash
   flake8 src/
   black --check src/
   ```

3. **Update Documentation**
   - Add docstrings for new functions
   - Update README if needed
   - Include usage examples

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Updated existing tests if needed

## Documentation
- [ ] Updated docstrings
- [ ] Updated README if needed
- [ ] Added usage examples

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Backward compatibility maintained
```

## Issue Reporting

### Bug Reports

Include the following information:

- **Environment**: Python version, OS, GPU details
- **Steps to Reproduce**: Exact steps to trigger the bug
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Error Messages**: Full error traceback
- **Code Sample**: Minimal code to reproduce

### Feature Requests

Provide the following details:

- **Use Case**: Why is this feature needed
- **Proposed Solution**: How should it work
- **Alternatives**: Other approaches considered
- **Implementation**: Technical approach if known

## Code Review Guidelines

### For Contributors

- Keep pull requests focused and small
- Write clear commit messages
- Respond to feedback promptly
- Be open to suggestions and improvements

### For Reviewers

- Be constructive and specific in feedback
- Test the changes locally when possible
- Consider backward compatibility
- Check for proper test coverage

## Release Process

### Version Numbering

We follow semantic versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist

1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Create release tag
5. Update documentation

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Maintain professional communication

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **Pull Requests**: Code contributions and reviews
- **Documentation**: In-code comments and README

## Getting Help

### For New Contributors

- Start with "good first issue" labeled issues
- Ask questions in pull request comments
- Review existing code to understand patterns
- Read the codebase documentation

### For Experienced Contributors

- Help review pull requests
- Mentor new contributors
- Suggest architectural improvements
- Contribute to project planning

## Recognition

Contributors will be recognized in:

- CONTRIBUTORS.md file
- Release notes for significant contributions
- GitHub contributor statistics

Thank you for contributing to Rails Migration Assistant!
