# Tests Directory

This directory contains all test files for the Rails Upgrade Assistant project.

## 🧪 Test Structure

```
tests/
├── test_gemini.py              # AI/LLM integration tests
├── test_knowledge.py           # Knowledge base tests  
├── test_rails_upgrade_agent.py # Main agent functionality tests
├── test_retriever.py           # Vector search and retrieval tests
├── test_upgrade.py             # Upgrade suggestion tests
└── README.md                   # This file
```

## 🏃‍♂️ Running Tests

### Run All Tests
```bash
# From project root
python -m pytest tests/ -v

# Or run individual test files
python tests/test_retriever.py
python tests/test_gemini.py
```

### Run Specific Test Categories
```bash
# Test search functionality
python tests/test_retriever.py

# Test AI integration
python tests/test_gemini.py

# Test upgrade suggestions
python tests/test_upgrade.py
```

## 📋 Test Descriptions

### `test_retriever.py`
Tests for the vector search and document retrieval system:
- FAISS index loading and search
- Query embedding and similarity matching
- Document metadata handling
- Combined index functionality (docs + RailsDiff)

### `test_gemini.py`  
Tests for Gemini AI integration:
- API connection and authentication
- Response parsing and JSON extraction
- Error handling and rate limiting
- Suggestion generation quality

### `test_rails_upgrade_agent.py`
Tests for the main agent functionality:
- End-to-end upgrade suggestion workflow
- Integration between search and AI components
- Safety checks and validation
- Output formatting

### `test_knowledge.py`
Tests for knowledge base integrity:
- Document chunk quality
- Metadata completeness
- Version coverage
- Deduplication verification

### `test_upgrade.py`
Tests for upgrade-specific functionality:
- Rails version detection
- Code pattern recognition
- Suggestion relevance scoring
- Multi-version compatibility

## 🔧 Test Configuration

### Environment Setup
Tests require the same environment as the main application:
```bash
# Set API key
export GEMINI_API_KEY=your_key_here

# Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/Mac
```

### Test Data
Some tests use sample data from:
- `data/chunks_combined.jsonl` - Document embeddings
- `data/faiss_combined.index` - Vector search index
- `data/raildiff/` - Code diff samples

### Mock Data
For tests that don't require real API calls, mock data is used:
- Simulated search results
- Sample Rails documentation chunks
- Example code suggestions

## 🚨 Test Guidelines

### Writing New Tests
1. **Descriptive Names**: Use clear, descriptive test function names
2. **Isolated Tests**: Each test should be independent
3. **Mock External APIs**: Don't make real API calls in tests
4. **Test Both Success and Failure**: Cover error conditions
5. **Use Fixtures**: Share common test data via fixtures

### Test Categories
- **Unit Tests**: Test individual functions/classes
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Test search speed and memory usage

## 📊 Test Coverage

Current test coverage areas:
- ✅ Vector search and retrieval
- ✅ Basic AI integration
- ✅ Document loading and parsing
- ⚠️ GUI components (manual testing)
- ⚠️ Complex upgrade scenarios
- ❌ Performance benchmarks (TODO)

## 🐛 Debugging Tests

### Common Issues
1. **API Key Missing**: Set `GEMINI_API_KEY` environment variable
2. **Index Not Found**: Ensure FAISS index files exist in `data/`
3. **Import Errors**: Check that `src/` is in Python path
4. **Memory Issues**: Large embeddings may require more RAM

### Debug Commands
```bash
# Verbose test output
python tests/test_retriever.py -v

# Debug specific test
python -c "
import sys; sys.path.append('src')
from tests.test_retriever import *
# Run specific test function
"

# Check search functionality
python tools/debug_raildiff.py
```

## 📈 Future Test Improvements

### Planned Additions
- **Performance Benchmarks**: Search speed, memory usage
- **GUI Automation**: Automated GUI testing with tkinter
- **Load Testing**: Handle large document sets
- **Regression Tests**: Ensure upgrades don't break functionality

### Test Automation
- **CI/CD Integration**: Run tests on every commit
- **Coverage Reports**: Track test coverage percentage
- **Quality Gates**: Prevent low-quality code merges

## 🤝 Contributing Tests

When adding new features:
1. **Add corresponding tests** in appropriate test file
2. **Update this README** if adding new test categories
3. **Ensure tests pass** before submitting PR
4. **Add documentation** for complex test scenarios

Example test structure:
```python
def test_new_feature():
    """Test description of what this validates."""
    # Arrange
    setup_test_data()
    
    # Act
    result = call_feature_function()
    
    # Assert
    assert result.is_expected()
    assert result.meets_quality_standards()
```

---

**Need help with tests?** Check individual test files for specific examples and patterns.
