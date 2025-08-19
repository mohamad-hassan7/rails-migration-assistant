# API Documentation

This document provides comprehensive API documentation for the Rails Migration Assistant components.

## Core Components

### HybridRailsAnalyzer

The main analysis engine that combines pattern detection with AI-powered analysis.

#### Class: `HybridRailsAnalyzer`

```python
from src.analyzer.hybrid_analyzer import HybridRailsAnalyzer
from src.model.local_llm import LocalLLM

# Initialize
llm = LocalLLM()
analyzer = HybridRailsAnalyzer(llm=llm)
```

#### Methods

##### `analyze_file(file_path: str, content: str) -> Dict[str, Any]`

Analyzes a single Rails file for upgrade issues.

**Parameters:**
- `file_path` (str): Path to the file being analyzed
- `content` (str): File content as string

**Returns:**
- Dict containing analysis results with suggestions and metadata

**Example:**
```python
with open('app/models/user.rb', 'r') as f:
    content = f.read()

results = analyzer.analyze_file('app/models/user.rb', content)
print(f"Found {len(results['suggestions'])} issues")
```

##### `analyze_project(project_path: str) -> Dict[str, Any]`

Analyzes an entire Rails project directory.

**Parameters:**
- `project_path` (str): Path to Rails project root

**Returns:**
- Dict containing comprehensive project analysis results

**Example:**
```python
results = analyzer.analyze_project('/path/to/rails/project')
for suggestion in results['suggestions']:
    print(f"File: {suggestion['file_path']}")
    print(f"Issue: {suggestion['issue_type']}")
    print(f"Fix: {suggestion['refactored_code']}")
```

### LocalLLM

Local Large Language Model integration for code generation and analysis.

#### Class: `LocalLLM`

```python
from src.model.local_llm import LocalLLM

# Initialize with default settings
llm = LocalLLM()

# Initialize with custom model
llm = LocalLLM(model_name="custom-model-name")
```

#### Methods

##### `generate(prompt: str, max_new_tokens: int = 512, temperature: float = 0.7, **kwargs) -> str`

Generates text using the local LLM.

**Parameters:**
- `prompt` (str): Input prompt for generation
- `max_new_tokens` (int): Maximum tokens to generate
- `temperature` (float): Sampling temperature (0.0 to 1.0)
- `**kwargs`: Additional generation parameters

**Returns:**
- Generated text as string

**Example:**
```python
prompt = "Fix this Rails code: @user.update_attributes(params[:user])"
response = llm.generate(prompt, max_new_tokens=200, temperature=0.1)
print(response)
```

##### `generate_rails_suggestion(query: str, context: str = "", max_tokens: int = 1024) -> Dict[str, Any]`

Generates Rails-specific upgrade suggestions.

**Parameters:**
- `query` (str): Rails upgrade query
- `context` (str): Additional context for generation
- `max_tokens` (int): Maximum tokens in response

**Returns:**
- Dict containing structured Rails suggestions

**Example:**
```python
suggestion = llm.generate_rails_suggestion(
    "How to fix mass assignment vulnerability",
    context="Rails 7 controller code"
)
print(suggestion['advice'])
```

### Code Parser

Utility functions for Rails code analysis and parsing.

#### Functions

##### `find_vulnerable_lines(file_content: str) -> List[Tuple[int, str]]`

Finds lines with potential mass assignment vulnerabilities.

**Parameters:**
- `file_content` (str): Complete file content

**Returns:**
- List of tuples containing (line_number, line_content)

**Example:**
```python
from src.analyzer.code_parser import find_vulnerable_lines

with open('app/controllers/users_controller.rb', 'r') as f:
    content = f.read()

vulnerabilities = find_vulnerable_lines(content)
for line_num, line_content in vulnerabilities:
    print(f"Line {line_num}: {line_content}")
```

##### `extract_method_context(file_content: str, line_number: int) -> Optional[Dict]`

Extracts the complete method containing a specific line.

**Parameters:**
- `file_content` (str): Complete file content
- `line_number` (int): Target line number (1-based)

**Returns:**
- Dict with method information or None if not found

**Example:**
```python
from src.analyzer.code_parser import extract_method_context

method_info = extract_method_context(content, 15)
if method_info:
    print(f"Method: {method_info['name']}")
    print(f"Lines: {method_info['start_line']}-{method_info['end_line']}")
    print(f"Content: {method_info['content']}")
```

##### `build_strong_params_prompt(method_content: str, controller_name: str, vulnerable_line: str) -> str`

Builds an optimized prompt for Strong Parameters generation.

**Parameters:**
- `method_content` (str): Complete method code
- `controller_name` (str): Name of the controller
- `vulnerable_line` (str): Line with vulnerability

**Returns:**
- Optimized prompt string for LLM

**Example:**
```python
from src.analyzer.code_parser import build_strong_params_prompt

prompt = build_strong_params_prompt(
    "def create\n  @user = User.create(params[:user])\nend",
    "UsersController",
    "@user = User.create(params[:user])"
)
```

### Retriever

RAG (Retrieval-Augmented Generation) system for Rails documentation.

#### Class: `Retriever`

```python
from src.retriever.retriever import Retriever

# Initialize with default paths
retriever = Retriever()

# Initialize with custom paths
retriever = Retriever(
    index_path="custom/faiss.index",
    meta_path="custom/meta.jsonl"
)
```

#### Methods

##### `search(query: str, max_results: int = 10) -> List[Dict]`

Searches Rails documentation for relevant content.

**Parameters:**
- `query` (str): Search query
- `max_results` (int): Maximum number of results

**Returns:**
- List of search results with content and metadata

**Example:**
```python
results = retriever.search("Strong Parameters Rails", max_results=5)
for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Content: {result['text'][:100]}...")
    print(f"Source: {result['source']}")
```

##### `get_context_for_query(query: str, max_context_length: int = 4000) -> str`

Gets concatenated context for a query within token limits.

**Parameters:**
- `query` (str): Search query
- `max_context_length` (int): Maximum context length in characters

**Returns:**
- Concatenated context string

**Example:**
```python
context = retriever.get_context_for_query(
    "Rails 7 deprecations",
    max_context_length=2000
)
print(f"Context length: {len(context)}")
```

## GUI Components

### Rails Upgrade GUI

Tkinter-based graphical user interface.

#### Functions

##### `main()`

Launches the GUI application.

**Example:**
```python
# Run from command line
python rails_migration_assistant.py

# Or programmatically
from rails_migration_assistant import main
main()
```

## CLI Components

### Command Line Interface

#### Usage

```bash
# Basic usage
python src/cli.py --project-path /path/to/rails/project

# With output file
python src/cli.py --project-path /path/to/rails/project --output results.json

# Verbose mode
python src/cli.py --project-path /path/to/rails/project --verbose
```

#### Options

- `--project-path`: Path to Rails project directory
- `--output`: Output file for results (JSON format)
- `--verbose`: Enable verbose logging
- `--max-files`: Maximum number of files to analyze
- `--include-tests`: Include test files in analysis

## Data Types

### DetectionResult

```python
@dataclass
class DetectionResult:
    file_path: str
    pattern_type: str
    line_number: int
    line_content: str
    confidence: float
    method_context: Optional[Dict] = None
```

### Suggestion

```python
{
    "issue_type": str,           # Type of issue detected
    "tier": str,                 # "tier1" or "tier2"
    "file_path": str,            # Path to affected file
    "line_number": int,          # Line number of issue
    "original_code": str,        # Original problematic code
    "refactored_code": str,      # Suggested fix
    "explanation": str,          # Human-readable explanation
    "confidence": float,         # Confidence score (0.0-1.0)
    "method_context": Dict       # Full method context
}
```

## Configuration

### Environment Variables

- `RAILS_ASSISTANT_MODEL`: Override default model name
- `RAILS_ASSISTANT_CACHE_DIR`: Custom cache directory
- `RAILS_ASSISTANT_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Model Configuration

Edit `src/model/local_llm.py` to customize model settings:

```python
# Model configuration
MODEL_NAME = "deepseek-ai/deepseek-coder-6.7b-instruct"
QUANTIZATION = True
MAX_NEW_TOKENS = 1200
TEMPERATURE = 0.1
DEVICE = "cuda"  # or "cpu"
```

## Error Handling

### Common Exceptions

#### `ModelLoadError`

Raised when the LLM model fails to load.

```python
try:
    llm = LocalLLM()
except ModelLoadError as e:
    print(f"Failed to load model: {e}")
```

#### `AnalysisError`

Raised when file analysis fails.

```python
try:
    results = analyzer.analyze_file(file_path, content)
except AnalysisError as e:
    print(f"Analysis failed: {e}")
```

#### `SearchError`

Raised when documentation search fails.

```python
try:
    results = retriever.search(query)
except SearchError as e:
    print(f"Search failed: {e}")
```

## Performance Considerations

### Memory Usage

- Local LLM requires ~6GB GPU memory with quantization
- Vector index requires ~500MB RAM
- Analysis is CPU-intensive for large projects

### Optimization Tips

1. **Use GPU acceleration** for LLM inference
2. **Enable quantization** to reduce memory usage
3. **Process files in batches** for large projects
4. **Cache analysis results** for repeated runs
5. **Use SSD storage** for better I/O performance

### Benchmarks

- Pattern detection: ~1000 files/second
- LLM analysis: ~10 seconds per complex method
- Memory usage: ~6GB with quantized model
- Accuracy: 95%+ for deprecation fixes, 90%+ for security fixes

## Examples

### Complete Analysis Workflow

```python
from src.analyzer.hybrid_analyzer import HybridRailsAnalyzer
from src.model.local_llm import LocalLLM
import json

# Initialize components
print("Loading model...")
llm = LocalLLM()
analyzer = HybridRailsAnalyzer(llm=llm)

# Analyze project
print("Analyzing project...")
results = analyzer.analyze_project("/path/to/rails/project")

# Process results
print(f"Found {len(results['suggestions'])} issues")
for suggestion in results['suggestions']:
    print(f"\nFile: {suggestion['file_path']}")
    print(f"Issue: {suggestion['issue_type']}")
    print(f"Line {suggestion['line_number']}: {suggestion['original_code']}")
    print(f"Fix: {suggestion['refactored_code']}")
    print(f"Confidence: {suggestion['confidence']:.2f}")

# Save results
with open('analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

### Custom Pattern Detection

```python
from src.analyzer.hybrid_analyzer import Tier1PatternDetector

# Create custom detector
detector = Tier1PatternDetector()

# Add custom pattern
detector.simple_patterns['my_custom_pattern'] = {
    'pattern': r'\.my_deprecated_method\s*\(',
    'replacement': '.my_new_method(',
    'explanation': 'my_deprecated_method is deprecated, use my_new_method',
    'confidence': 0.95
}

# Use in analysis
results = detector.detect_all_tier1_issues(file_path, content)
```

This API documentation provides comprehensive coverage of the Rails Migration Assistant's programmatic interface. For usage examples and additional information, see the README.md and examples directory.
