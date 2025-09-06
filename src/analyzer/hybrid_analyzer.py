#!/usr/bin/env python3
"""
Hybrid Two-Tiered Rails Analyzer

Tier 1: High-Frequency Pattern Detector (No RAG)
- Mass assignment vulnerabilities
- Simple deprecations (update_attributes -> update)
- before_filter -> before_action

Tier 2: General Deprecation and Configuration Agent (With RAG)  
- Config file changes
- Obscure API deprecations
- Rails version-specific changes
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

# Import our components
from src.analyzer.code_parser import (
    find_mass_assignment_risks,
    extract_method_context,
    build_strong_params_prompt,
    extract_controller_name
)
from src.model.local_llm import LocalLLM
from src.retriever.retriever import Retriever

# Configuration constants
DEFAULT_FAISS_INDEX_PATH = "data/faiss.index"
DEFAULT_META_PATH = "data/meta.jsonl"
DEFAULT_COMBINED_FAISS_PATH = "data/faiss_combined.index"
DEFAULT_COMBINED_META_PATH = "data/meta_combined.jsonl"

# Analysis thresholds and limits
RAG_SEARCH_LIMIT = 3
FILE_CONTEXT_CACHE_SIZE = 100
TIER_1_CONFIDENCE = 0.9
TIER_2_CONFIDENCE = 0.8


@dataclass
class DetectionResult:
    """Result from pattern detection."""
    file_path: str
    pattern_type: str
    line_number: int
    line_content: str
    method_context: Optional[Dict] = None
    confidence: float = 1.0


@dataclass
class AnalysisResult:
    """Result from AI analysis."""
    original_code: str
    refactored_code: str
    explanation: str
    confidence: float
    tier_used: str  # "tier1" or "tier2"


class Tier1PatternDetector:
    """High-frequency pattern detector for common Rails issues (No RAG needed)."""
    
    def __init__(self):
        """Initialize with common Rails deprecation patterns."""
        self.simple_patterns = {
            'before_filter_deprecation': {
                'pattern': r'\bbefore_filter\s+',
                'replacement': 'before_action ',
                'explanation': 'before_filter is deprecated in Rails 5+, use before_action instead',
                'confidence': 0.95
            },
            'after_filter_deprecation': {
                'pattern': r'\bafter_filter\s+',
                'replacement': 'after_action ',
                'explanation': 'after_filter is deprecated in Rails 5+, use after_action instead',
                'confidence': 0.95
            },
            'skip_before_filter_deprecation': {
                'pattern': r'\bskip_before_filter\s+',
                'replacement': 'skip_before_action ',
                'explanation': 'skip_before_filter is deprecated in Rails 5+, use skip_before_action instead',
                'confidence': 0.95
            },
            'update_attributes_deprecation': {
                'pattern': r'\.update_attributes\s*\(',
                'replacement': '.update(',
                'explanation': 'update_attributes is deprecated in Rails 6+, use update instead',
                'confidence': 0.9
            },
            'attr_accessible_deprecation': {
                'pattern': r'\battr_accessible\s+',
                'replacement': '# Use strong parameters in controller instead',
                'explanation': 'attr_accessible is deprecated in Rails 4+, use strong parameters in controllers',
                'confidence': 0.95
            },
            'protected_attributes_gem': {
                'pattern': r"gem\s+['\"]protected_attributes['\"]",
                'replacement': "# Remove and use strong parameters",
                'explanation': 'protected_attributes gem is deprecated, migrate to strong parameters',
                'confidence': 0.9
            },
            'rails_observers_gem': {
                'pattern': r"gem\s+['\"]rails-observers['\"]",
                'replacement': "# Use ActiveJob or callbacks instead",
                'explanation': 'rails-observers gem was extracted from Rails core, consider alternatives',
                'confidence': 0.85
            },
            'paperclip_deprecation': {
                'pattern': r"gem\s+['\"]paperclip['\"]",
                'replacement': "gem 'image_processing'  # Use Active Storage",
                'explanation': 'Paperclip is deprecated, migrate to Active Storage (Rails 5.2+)',
                'confidence': 0.8
            },
            'factory_girl_rename': {
                'pattern': r"gem\s+['\"]factory_girl",
                'replacement': "gem 'factory_bot",
                'explanation': 'factory_girl was renamed to factory_bot',
                'confidence': 0.95
            },
            'quiet_assets_deprecation': {
                'pattern': r"gem\s+['\"]quiet_assets['\"]",
                'replacement': "# Not needed in Rails 5+",
                'explanation': 'quiet_assets gem is not needed in Rails 5+, asset quieting is built-in',
                'confidence': 0.9
            },
            'serve_static_assets_config': {
                'pattern': r'config\.serve_static_assets\s*=',
                'replacement': 'config.public_file_server.enabled =',
                'explanation': 'serve_static_assets is deprecated in Rails 5+, use public_file_server.enabled',
                'confidence': 0.95
            },
            'static_cache_control_config': {
                'pattern': r'config\.static_cache_control\s*=',
                'replacement': 'config.public_file_server.headers =',
                'explanation': 'static_cache_control is deprecated in Rails 5+, use public_file_server.headers',
                'confidence': 0.9
            },
            'raise_in_transactional_callbacks': {
                'pattern': r'config\.active_record\.raise_in_transactional_callbacks\s*=',
                'replacement': '# Remove this line',
                'explanation': 'raise_in_transactional_callbacks is deprecated in Rails 5+, this is now the default behavior',
                'confidence': 0.95
            },
            'eager_load_paths_deprecation': {
                'pattern': r'config\.eager_load_paths\s*\+=',
                'replacement': 'config.autoload_paths +=',
                'explanation': 'Consider using autoload_paths or autoload_lib_dirs instead',
                'confidence': 0.8
            },
            'devise_parameter_sanitizer_old': {
                'pattern': r'devise_parameter_sanitizer\.for\(',
                'replacement': 'devise_parameter_sanitizer.permit(',
                'explanation': 'devise_parameter_sanitizer.for is deprecated, use permit instead',
                'confidence': 0.9
            },
            'mysql2_version_constraint': {
                'pattern': r"gem\s+['\"]mysql2['\"],\s*['\"]~>\s*0\.[34]",
                'replacement': "gem 'mysql2', '~> 0.5'",
                'explanation': 'Update mysql2 gem version for Rails 5+ compatibility',
                'confidence': 0.85
            },
            'actiondispatch_parsers': {
                'pattern': r'ActionDispatch::ParamsParser',
                'replacement': '# Remove - parsing is built-in',
                'explanation': 'ActionDispatch::ParamsParser middleware was removed in Rails 5+',
                'confidence': 0.9
            },
            'actiondispatch_xml_parser': {
                'pattern': r'ActionDispatch::XmlParamsParser',
                'replacement': '# Remove or use actionpack-xml_parser gem',
                'explanation': 'XML parameter parsing was extracted to actionpack-xml_parser gem',
                'confidence': 0.85
            },
            'session_store_config': {
                'pattern': r'Rails\.application\.config\.session_store\s+:cookie_store',
                'replacement': 'Rails.application.config.session_store :cookie_store',
                'explanation': 'Session store configuration may need updates for Rails 6+ security requirements',
                'confidence': 0.7
            },
            'cookie_store_key_config': {
                'pattern': r'session_store\s+:cookie_store,\s*key:\s*[\'"][^\'\"]*[\'"]',
                'replacement': '# Update with secure configurations',
                'explanation': 'Cookie store key configuration should include secure options for Rails 6+',
                'confidence': 0.8
            },
            'test_case_inheritance': {
                'pattern': r'class\s+\w+\s*<\s*ActionController::TestCase',
                'replacement': 'class TestName < ActionDispatch::IntegrationTest',
                'explanation': 'ActionController::TestCase is deprecated, use ActionDispatch::IntegrationTest',
                'confidence': 0.9
            },
            'action_view_test_case': {
                'pattern': r'class\s+\w+\s*<\s*ActionView::TestCase',
                'replacement': 'class TestName < ActionView::TestCase',
                'explanation': 'ActionView::TestCase usage should be reviewed for Rails 6+ compatibility',
                'confidence': 0.6
            },
            'belongs_to_required': {
                'pattern': r'belongs_to\s+:\w+(?!.*required:\s*false)',
                'replacement': 'belongs_to :association, optional: true',
                'explanation': 'belongs_to associations are required by default in Rails 5+, add optional: true if needed',
                'confidence': 0.7
            },
            'find_by_dynamic_methods': {
                'pattern': r'\.find_by_\w+\(',
                'replacement': '.find_by(attribute: value)',
                'explanation': 'Dynamic find_by_* methods are deprecated, use find_by with hash syntax',
                'confidence': 0.85
            },
            'find_all_by_dynamic_methods': {
                'pattern': r'\.find_all_by_\w+\(',
                'replacement': '.where(attribute: value)',
                'explanation': 'Dynamic find_all_by_* methods are deprecated, use where instead',
                'confidence': 0.85
            },
            'rails_env_constant': {
                'pattern': r'\bRAILS_ENV\b',
                'replacement': 'Rails.env',
                'explanation': 'RAILS_ENV constant is deprecated, use Rails.env instead',
                'confidence': 0.9
            },
            'rails_root_constant': {
                'pattern': r'\bRAILS_ROOT\b',
                'replacement': 'Rails.root',
                'explanation': 'RAILS_ROOT constant is deprecated, use Rails.root instead',
                'confidence': 0.9
            },
            'scope_lambda_syntax': {
                'pattern': r'scope\s+:\w+,\s*lambda\s*\{',
                'replacement': 'scope :name, -> {',
                'explanation': 'Lambda syntax in scopes should use stabby lambda (->) for better performance',
                'confidence': 0.8
            }
        }
    
    def detect_mass_assignment(self, file_path: str, content: str) -> List[DetectionResult]:
        """Detect mass assignment vulnerabilities."""
        results = []
        
        # Only check controller files
        if not self._is_controller_file(file_path):
            return results
            
        risks = find_mass_assignment_risks(content)
        
        for line_num, line_content in risks:
            # Extract method context for each vulnerability
            method_context = extract_method_context(content, line_num)
            
            # Check if this line also has a deprecation (like update_attributes)
            pattern_type = 'mass_assignment'
            if 'update_attributes' in line_content:
                pattern_type = 'mass_assignment_with_deprecation'
            
            results.append(DetectionResult(
                file_path=file_path,
                pattern_type=pattern_type,
                line_number=line_num,
                line_content=line_content,
                method_context=method_context,
                confidence=TIER_1_CONFIDENCE
            ))
        
        return results
    
    def detect_simple_deprecations(self, file_path: str, content: str, processed_lines: set = None) -> List[DetectionResult]:
        """Detect simple deprecation patterns, avoiding already processed lines."""
        results = []
        if processed_lines is None:
            processed_lines = set()
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip lines already processed by mass assignment detection
            if line_num in processed_lines:
                continue
                
            # Skip lines with mass assignment patterns - they're handled separately
            if 'params[' in line and ('update_attributes' in line or 'attributes=' in line):
                continue
                
            for pattern_name, pattern_info in self.simple_patterns.items():
                if re.search(pattern_info['pattern'], line):
                    results.append(DetectionResult(
                        file_path=file_path,
                        pattern_type=pattern_name,
                        line_number=line_num,
                        line_content=line.strip(),
                        confidence=pattern_info['confidence']
                    ))
                    break  # Only one pattern per line to avoid duplicates
        
        return results
    
    def detect_all_tier1_issues(self, file_path: str, content: str) -> List[DetectionResult]:
        """Detect all Tier 1 issues in a file, avoiding duplicates."""
        results = []
        processed_lines = set()  # Track lines already processed to avoid duplicates
        
        # Mass assignment detection (highest priority)
        mass_assignment_results = self.detect_mass_assignment(file_path, content)
        results.extend(mass_assignment_results)
        
        # Track lines that had mass assignment issues
        for result in mass_assignment_results:
            processed_lines.add(result.line_number)
        
        # Simple deprecation detection (skip already processed lines)
        deprecation_results = self.detect_simple_deprecations(file_path, content, processed_lines)
        results.extend(deprecation_results)
        
        return results
    
    def _is_controller_file(self, file_path: str) -> bool:
        """Check if file is a Rails controller."""
        return ('controller' in file_path.lower() or 
                '/app/controllers/' in file_path or
                '\\app\\controllers\\' in file_path)


class Tier2RAGAnalyzer:
    """General deprecation and configuration agent using RAG."""
    
    def __init__(self, retriever: Optional[Retriever] = None, target_version: str = "7.0"):
        """Initialize with optional retriever for RAG."""
        self.retriever = retriever
        self.target_version = target_version
        
        # Config file patterns that need RAG analysis
        self.config_patterns = {
            'application_config': r'config/application\.rb',
            'environment_config': r'config/environments/.*\.rb',
            'initializer_config': r'config/initializers/.*\.rb',
            'routes_config': r'config/routes\.rb',
            'database_config': r'config/database\.yml',
            'gemfile': r'Gemfile'
        }
    
    def needs_tier2_analysis(self, file_path: str) -> bool:
        """Determine if a file needs Tier 2 RAG analysis."""
        
        # Always run RAG on important Rails files
        important_files = [
            'gemfile', 'gemspec', 'rakefile', 'routes.rb', 'application.rb',
            'environment.rb', 'boot.rb', 'schema.rb', 'seeds.rb'
        ]
        
        file_name = file_path.lower()
        for important in important_files:
            if important in file_name:
                return True
        
        # Config files always need RAG
        for pattern in self.config_patterns.values():
            if re.search(pattern, file_path):
                return True
        
        # Ruby files with Rails code should get RAG analysis
        if file_path.endswith('.rb'):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check for Rails-specific patterns that might need RAG
                rails_indicators = [
                    'Rails.', 'ActiveRecord', 'ActionController', 'ActionView',
                    'ActionMailer', 'config.', 'gem ', 'require ', 'include ',
                    'before_action', 'before_filter', 'validates', 'scope',
                    'belongs_to', 'has_many', 'has_one', 'serialize',
                    'update_attributes', 'find_by_', 'where('
                ]
                
                content_lower = content.lower()
                for indicator in rails_indicators:
                    if indicator.lower() in content_lower:
                        return True
                        
            except Exception:
                pass  # If we can't read, default to no RAG
        
        return False
    
    def analyze_with_rag(self, file_path: str, content: str, file_context: List[Dict] = None) -> List[DetectionResult]:
        """Analyze file using RAG for complex deprecations with optional cached context."""
        results = []
        
        try:
            if not self.retriever and not file_context:
                return results
            
            # Use provided context or generate new one
            if file_context:
                all_contexts = file_context
            else:
                # Fallback to individual searches (legacy behavior)
                search_queries = self._generate_search_queries(file_path, content)
                all_contexts = []
                for query in search_queries:
                    rag_results = self.retriever.search(query, top_k=RAG_SEARCH_LIMIT)
                    all_contexts.extend(rag_results)
            
            # Analyze content with RAG context
            if all_contexts:
                # Look for potential deprecation patterns
                potential_issues = self._scan_for_potential_issues(content)
                
                for issue in potential_issues:
                    results.append(DetectionResult(
                        file_path=file_path,
                        pattern_type='complex_deprecation',
                        line_number=issue['line_number'],
                        line_content=issue['line_content'],
                        confidence=TIER_2_CONFIDENCE
                    ))
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return []
        
        return results
    
    def _generate_search_queries(self, file_path: str, content: str) -> List[str]:
        """Generate search queries based on file content."""
        queries = []
        
        # File type specific queries
        if 'config/application.rb' in file_path:
            queries.extend([
                'Rails application configuration changes',
                'config.application settings deprecation',
                'Rails application.rb upgrade'
            ])
        elif 'config/environments' in file_path:
            queries.extend([
                'Rails environment configuration changes',
                'production development test config deprecation'
            ])
        elif 'Gemfile' in file_path:
            queries.extend([
                'Rails gem version compatibility',
                'Gemfile Rails upgrade'
            ])
        elif 'test/' in file_path or '_test.rb' in file_path:
            queries.extend([
                'Rails testing framework changes',
                'test deprecation Rails upgrade',
                'ActionController testing changes',
                'ActiveRecord testing deprecated methods'
            ])
        elif 'models/' in file_path:
            queries.extend([
                'ActiveRecord model deprecation',
                'Rails model API changes',
                'ActiveRecord upgrade issues'
            ])
        elif 'controllers/' in file_path:
            queries.extend([
                'ActionController deprecation',
                'Rails controller API changes',
                'before_filter before_action'
            ])
        elif 'views/' in file_path:
            queries.extend([
                'ActionView deprecation',
                'Rails view helper changes',
                'ERB template changes'
            ])
        elif 'helpers/' in file_path:
            queries.extend([
                'Rails helper deprecation',
                'ActionView helper changes'
            ])
        
        # Content-based queries - scan for Rails patterns
        content_lower = content.lower()
        
        # ActiveRecord patterns
        if any(pattern in content_lower for pattern in ['activerecord', 'belongs_to', 'has_many', 'validates']):
            queries.append('ActiveRecord deprecation upgrade')
        
        # ActionController patterns  
        if any(pattern in content_lower for pattern in ['actioncontroller', 'before_filter', 'before_action']):
            queries.append('ActionController deprecation upgrade')
            
        # Testing patterns
        if any(pattern in content_lower for pattern in ['test_', 'assert_', 'should_']):
            queries.append('Rails testing deprecation')
            
        # Gem patterns
        if 'gem ' in content_lower:
            queries.append('Rails gem compatibility')
            
        # Configuration patterns
        if 'config.' in content_lower:
            queries.append('Rails configuration deprecation')
        
        # Extract Rails-specific method calls for queries
        rails_methods = re.findall(r'config\.(\w+)', content)
        for method in set(rails_methods):
            queries.append(f'Rails config.{method} deprecation upgrade')
            
        # Add general Rails upgrade query if no specific patterns found
        if not queries and file_path.endswith('.rb'):
            queries.extend([
                'Rails upgrade deprecation',
                'Rails API changes',
                f'Rails {self.target_version} upgrade'
            ])
        
        return queries[:5]  # Limit to avoid too many queries
    
    def _scan_for_potential_issues(self, content: str) -> List[Dict]:
        """Scan for potential issues that might need RAG analysis."""
        issues = []
        lines = content.split('\n')
        
        # Comprehensive patterns for Rails upgrade issues
        potential_patterns = [
            r'config\.\w+\s*=',  # Config assignments
            r'Rails\.\w+\.',     # Rails API calls
            r'ActiveRecord::\w+', # ActiveRecord constants
            r'ActionController::\w+', # ActionController constants
            r'ActionDispatch::\w+', # ActionDispatch constants
            r'ActionMailer::\w+', # ActionMailer constants
            r'ActionView::\w+', # ActionView constants
            r'gem\s+[\'"][^\'"]+[\'"].*4\.\d+', # Gems with old version constraints
            r'serve_static_assets', # Rails 5 deprecation
            r'static_cache_control', # Rails 5 deprecation
            r'raise_in_transactional_callbacks', # Rails 5 deprecation
            r'eager_load_paths', # Potential Rails 6+ issue
            r'autoload_paths', # Rails 6+ zeitwerk concern
            r'middleware\.use.*Params', # Middleware deprecations
            r'attr_accessible', # Rails 4+ deprecation
            r'protected_attributes', # Gem deprecation
            r'paperclip', # Gem deprecation
            r'factory_girl', # Gem rename
            r'rails-observers', # Gem extraction
            r'quiet_assets', # Rails 5+ not needed
            r'mysql2.*0\.[34]', # Old mysql2 version
            r'devise_parameter_sanitizer\.for', # Devise deprecation
            r'before_filter', # Rails 5 deprecation
            r'update_attributes', # Rails 6 deprecation
            r'\.find_by_\w+\(', # Rails 4 deprecation
            r'\.find_all_by_\w+\(', # Rails 4 deprecation
            r'\.find_or_create_by_\w+\(', # Rails 4 deprecation
            r'scope\s*:.*lambda', # Rails 4+ prefer proc syntax
            r'validates_\w+_of', # Consider using validates
            r'RAILS_ENV', # Use Rails.env instead
            r'RAILS_ROOT', # Use Rails.root instead
            r'ActionController::Routing', # Rails 3+ deprecation
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in potential_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'line_number': line_num,
                        'line_content': line.strip()
                    })
                    break  # One issue per line
        
        return issues
    
    def _has_complex_rails_patterns(self, file_path: str) -> bool:
        """Check if file might have complex Rails patterns."""
        # This is a heuristic - could be expanded
        complex_indicators = [
            'initializer', 'config', 'application.rb', 
            'environment', 'routes.rb'
        ]
        
        return any(indicator in file_path.lower() for indicator in complex_indicators)


class HybridRailsAnalyzer:
    """Main hybrid analyzer combining Tier 1 and Tier 2 approaches."""
    
    def __init__(self, 
                 use_retriever: bool = True,
                 faiss_index_path: str = None,
                 meta_path: str = None):
        """Initialize the hybrid analyzer with configurable paths."""
        print("🚀 Initializing Hybrid Rails Analyzer...")
        
        # Use provided paths or fall back to defaults
        if faiss_index_path is None:
            faiss_index_path = DEFAULT_COMBINED_FAISS_PATH if os.path.exists(DEFAULT_COMBINED_FAISS_PATH) else DEFAULT_FAISS_INDEX_PATH
        if meta_path is None:
            meta_path = DEFAULT_COMBINED_META_PATH if os.path.exists(DEFAULT_COMBINED_META_PATH) else DEFAULT_META_PATH
        
        # Initialize LLM
        self.llm = LocalLLM()
        print("✅ Local LLM loaded")
        
        # Initialize Tier 1 detector
        self.tier1_detector = Tier1PatternDetector()
        print("✅ Tier 1 Pattern Detector ready")
        
        # Initialize Tier 2 RAG analyzer
        retriever = None
        if use_retriever:
            try:
                if os.path.exists(faiss_index_path) and os.path.exists(meta_path):
                    print(f"📚 Loading knowledge base from {faiss_index_path}")
                    retriever = Retriever(faiss_index_path, meta_path)
                    print(f"✅ Tier 2 RAG Analyzer ready (using {faiss_index_path})")
                    # Test the retriever with a simple query
                    test_results = retriever.search("Rails deprecation", top_k=1)
                    print(f"   📋 Knowledge base test: {len(test_results)} results found")
                else:
                    print(f"❌ RAG data not found at {faiss_index_path}, Tier 2 will use LLM only")
                    print(f"   Expected files: {faiss_index_path}, {meta_path}")
            except Exception as e:
                print(f"❌ Failed to load RAG: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠️  RAG disabled - using LLM only mode")
        
        self.tier2_analyzer = Tier2RAGAnalyzer(retriever, target_version="7.0")
        
        # Expose retriever for external access
        self.retriever = retriever
        
        # File context cache for optimization
        self.file_context_cache = {}
        
        print("✅ Hybrid analyzer initialized")
    
    def analyze_file(self, file_path: str, target_version: str = "7.0") -> Dict[str, Any]:
        """Analyze a single file using the hybrid approach."""
        print(f"\n📁 Analyzing: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Failed to read file: {e}"}
        
        # Set target version for analysis
        self.target_version = target_version
        self.tier2_analyzer.target_version = target_version
        
        results = {
            "file_path": file_path,
            "target_version": target_version,
            "tier1_issues": [],
            "tier2_issues": [],
            "total_issues": 0,
            "suggestions": []
        }
        
        # Tier 1: High-frequency pattern detection
        print("🔍 Tier 1: Detecting high-frequency patterns...")
        tier1_issues = self.tier1_detector.detect_all_tier1_issues(file_path, content)
        results["tier1_issues"] = tier1_issues
        
        if tier1_issues:
            print(f"   Found {len(tier1_issues)} Tier 1 issues")
            for issue in tier1_issues:
                suggestion = self._process_tier1_issue(issue)
                if suggestion:
                    results["suggestions"].append(suggestion)
                    print(f"   📋 Suggestion from {os.path.basename(file_path)}:")
                    print(f"      Type: {suggestion['issue_type']}")
                    print(f"      Old code: '{suggestion['original_code'][:50]}...'")
                    print(f"      New code: '{suggestion['refactored_code'][:50]}...'")
                    if suggestion['original_code'] != suggestion['refactored_code']:
                        print(f"      ✅ Added: Has different old/new code")
                    else:
                        print(f"      ❌ Skipped: Old and new code are the same")
        
        # Tier 2: RAG-based analysis (if needed or always for Rails files)
        tier2_should_run = (
            self.tier2_analyzer.needs_tier2_analysis(file_path) or 
            file_path.endswith('.rb') or 
            'rails' in content.lower() or
            'config' in file_path.lower()
        )
        
        if tier2_should_run:
            print("🔍 Tier 2: Performing RAG-based analysis...")
            
            # Get or create file-level context cache
            file_context = self._get_file_context(file_path, content)
            
            tier2_issues = self.tier2_analyzer.analyze_with_rag(file_path, content, file_context)
            results["tier2_issues"] = tier2_issues
            
            if tier2_issues:
                print(f"   Found {len(tier2_issues)} Tier 2 issues")
                for i, issue in enumerate(tier2_issues):
                    print(f"   Processing Tier 2 issue {i+1}: {issue.pattern_type if hasattr(issue, 'pattern_type') else 'Unknown'}")
                    
                    # Skip complex processing if too many issues to prevent hanging
                    if len(tier2_issues) > 5:
                        print(f"   ⏭️  Skipping detailed analysis (too many issues, {len(tier2_issues)} > 5)")
                        continue
                    
                    suggestion = self._process_tier2_issue(issue, content, file_context)
                    if suggestion:  # Only add non-None suggestions
                        results["suggestions"].append(suggestion)
                        print(f"   📋 Suggestion from {os.path.basename(file_path)}:")
                        print(f"      Type: {suggestion['issue_type']}")
                        print(f"      Old code: '{suggestion['original_code'][:50]}...'")
                        print(f"      New code: '{suggestion['refactored_code'][:50]}...'")
                        if suggestion['original_code'] != suggestion['refactored_code']:
                            print(f"      ✅ Added: Has different old/new code")
                        else:
                            print(f"      ❌ Skipped: Old and new code are the same")
                    else:
                        print(f"   ❌ Suggestion was None, skipped")
            else:
                print("   No Tier 2 issues found")
        else:
            print("⏭️  Tier 2: Not needed for this file type")
        
        results["total_issues"] = len(tier1_issues) + len(results["tier2_issues"])
        
        return results
    
    def analyze_project(self, project_path: str, target_version: str = "7.0") -> Dict[str, Any]:
        """Analyze an entire Rails project."""
        print(f"🚀 Starting Rails project analysis: {project_path}")
        print(f"📊 Target Rails version: {target_version}")
        
        # Find all Ruby files in the project
        ruby_files = []
        for root, dirs, files in os.walk(project_path):
            # Skip certain directories
            skip_dirs = {'.git', 'node_modules', 'tmp', 'log', 'vendor', '.bundle'}
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if file.endswith('.rb') or file == 'Gemfile' or file.endswith('.yml'):
                    ruby_files.append(os.path.join(root, file))
        
        print(f"📁 Found {len(ruby_files)} files to analyze")
        
        project_results = {
            "project_path": project_path,
            "target_version": target_version,
            "total_files": len(ruby_files),
            "analyzed_files": 0,
            "files_with_issues": 0,
            "total_suggestions": 0,
            "file_results": [],
            "summary": {}
        }
        
        # Analyze each file
        for i, file_path in enumerate(ruby_files, 1):
            print(f"\n[{i}/{len(ruby_files)}] Analyzing: {os.path.relpath(file_path, project_path)}")
            
            try:
                file_result = self.analyze_file(file_path, target_version)
                project_results["file_results"].append(file_result)
                project_results["analyzed_files"] += 1
                
                if file_result.get("total_issues", 0) > 0:
                    project_results["files_with_issues"] += 1
                
                project_results["total_suggestions"] += len(file_result.get("suggestions", []))
                
            except Exception as e:
                print(f"❌ Error analyzing {file_path}: {e}")
                continue
        
        # Generate summary
        project_results["summary"] = self._generate_project_summary(project_results)
        
        # Print final summary
        self._print_project_summary(project_results)
        
        return project_results
    
    def _generate_project_summary(self, project_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the project analysis."""
        summary = {
            "issue_types": {},
            "most_problematic_files": [],
            "upgrade_priority": []
        }
        
        # Count issue types
        for file_result in project_results["file_results"]:
            for suggestion in file_result.get("suggestions", []):
                issue_type = suggestion.get("issue_type", "unknown")
                if issue_type not in summary["issue_types"]:
                    summary["issue_types"][issue_type] = 0
                summary["issue_types"][issue_type] += 1
        
        # Find most problematic files
        file_issue_counts = []
        for file_result in project_results["file_results"]:
            if file_result.get("total_issues", 0) > 0:
                file_issue_counts.append({
                    "file": os.path.basename(file_result["file_path"]),
                    "issues": file_result["total_issues"],
                    "suggestions": len(file_result.get("suggestions", []))
                })
        
        summary["most_problematic_files"] = sorted(
            file_issue_counts, 
            key=lambda x: x["issues"], 
            reverse=True
        )[:10]
        
        # Priority upgrade areas
        priority_areas = [
            ("Security Issues", ["mass_assignment", "attr_accessible"]),
            ("Test Framework", ["test_case_inheritance", "action_view_test_case"]),
            ("Configuration", ["session_store_config", "static_cache_control_config"]),
            ("ActiveRecord", ["belongs_to_required", "find_by_dynamic_methods"]),
            ("ActionController", ["before_filter_deprecation", "update_attributes_deprecation"])
        ]
        
        for area_name, issue_types in priority_areas:
            count = sum(summary["issue_types"].get(issue_type, 0) for issue_type in issue_types)
            if count > 0:
                summary["upgrade_priority"].append({
                    "area": area_name,
                    "issues": count
                })
        
        return summary
    
    def _print_project_summary(self, project_results: Dict[str, Any]) -> None:
        """Print a formatted summary of the project analysis."""
        print(f"\n🎯 Analysis Complete: Found {project_results['total_suggestions']} total suggestions")
        print(f"   📁 Files analyzed: {project_results['analyzed_files']}")
        print(f"   ⚠️  Files with issues: {project_results['files_with_issues']}")
        
        summary = project_results["summary"]
        
        if summary["issue_types"]:
            print(f"\n📊 Issue Types Found:")
            for issue_type, count in sorted(summary["issue_types"].items(), key=lambda x: x[1], reverse=True):
                print(f"   • {issue_type}: {count}")
        
        if summary["most_problematic_files"]:
            print(f"\n🔥 Most Problematic Files:")
            for file_info in summary["most_problematic_files"][:5]:
                print(f"   • {file_info['file']}: {file_info['issues']} issues, {file_info['suggestions']} suggestions")
        
        if summary["upgrade_priority"]:
            print(f"\n🎯 Upgrade Priority Areas:")
            for area in summary["upgrade_priority"]:
                print(f"   • {area['area']}: {area['issues']} issues")
    
    def _get_file_context(self, file_path: str, content: str) -> List[Dict]:
        """Get or create cached file-level RAG context."""
        # Use file path as cache key
        cache_key = file_path
        
        if cache_key in self.file_context_cache:
            print(f"   Using cached context for {os.path.basename(file_path)}")
            return self.file_context_cache[cache_key]
        
        print(f"   Generating RAG context for {os.path.basename(file_path)}")
        
        # Generate file-level search queries
        search_queries = self.tier2_analyzer._generate_search_queries(file_path, content)
        print(f"   Search queries: {search_queries[:3]}")  # Show first 3 queries
        
        # Collect all RAG context for this file
        file_context = []
        if self.tier2_analyzer.retriever:
            for i, query in enumerate(search_queries[:2]):  # Limit to 2 main queries
                print(f"   🔍 Searching: {query}")
                rag_results = self.tier2_analyzer.retriever.search(query, top_k=RAG_SEARCH_LIMIT)
                print(f"   📋 Found {len(rag_results)} knowledge base entries")
                file_context.extend(rag_results)
        else:
            print("   ❌ No retriever available - knowledge base not loaded")
        
        print(f"   📚 Total context entries: {len(file_context)}")
        
        # Cache the context (with size limit)
        if len(self.file_context_cache) >= FILE_CONTEXT_CACHE_SIZE:
            # Remove oldest entry
            oldest_key = next(iter(self.file_context_cache))
            del self.file_context_cache[oldest_key]
        
        self.file_context_cache[cache_key] = file_context
        return file_context
    
    def _process_tier1_issue(self, issue: DetectionResult) -> Dict[str, Any]:
        """Process a Tier 1 issue using targeted prompts."""
        
        if issue.pattern_type in ['mass_assignment', 'mass_assignment_with_deprecation']:
            # Use our enhanced mass assignment prompt
            controller_name = extract_controller_name(issue.file_path)
            prompt = build_strong_params_prompt(
                issue.method_context['content'] if issue.method_context else issue.line_content,
                controller_name,
                issue.line_content
            )
            
            # For combined issues, add note about deprecation
            if issue.pattern_type == 'mass_assignment_with_deprecation':
                prompt += "\n\nCRITICAL: Also change 'update_attributes' to 'update' in the method call."
            
            prompt += """

OUTPUT REQUIREMENTS:
- Return ONLY the Ruby method code
- Start with 'def method_name' and end with 'end'
- NO explanations, NO markdown, NO backticks
- NO print statements or debug code
- Just clean Ruby code"""
            
            response = self.llm.generate(prompt, max_new_tokens=800, temperature=0.1)
            
            # Clean the response aggressively
            cleaned_response = self._clean_llm_response(response)
            refactored_code = self._extract_ruby_code(cleaned_response)
            
            return {
                "issue_type": issue.pattern_type,
                "tier": "tier1",
                "line_number": issue.line_number,
                "original_code": issue.line_content,
                "refactored_code": refactored_code,
                "explanation": "Mass assignment vulnerability fixed with strong parameters",
                "confidence": issue.confidence,
                "method_context": issue.method_context
            }
        
        else:
            # Simple deprecation - direct replacement
            pattern_info = self.tier1_detector.simple_patterns.get(issue.pattern_type, {})
            refactored = re.sub(
                pattern_info.get('pattern', ''),
                pattern_info.get('replacement', ''),
                issue.line_content
            )
            
            return {
                "issue_type": issue.pattern_type,
                "tier": "tier1",
                "line_number": issue.line_number,
                "original_code": issue.line_content,
                "refactored_code": refactored,
                "explanation": pattern_info.get('explanation', 'Deprecation fixed'),
                "confidence": issue.confidence
            }
    
    def _process_tier2_issue(self, issue: DetectionResult, file_content: str, file_context: List[Dict] = None) -> Dict[str, Any]:
        """Process a Tier 2 issue using RAG-enhanced prompts with cached context."""
        
        # Build RAG-enhanced prompt using cached file context
        context = ""
        if file_context:
            # Use the cached file context
            context_parts = []
            for result in file_context[:3]:  # Use top 3 results
                meta = result.get('meta', {})
                text = result.get('text', '')[:300]
                context_parts.append(f"Source: {meta.get('source', 'Unknown')}\n{text}")
            context = "\n\n".join(context_parts)
        elif self.tier2_analyzer.retriever:
            # Fallback to individual search (legacy)
            search_query = f"Rails deprecation {issue.line_content}"
            rag_results = self.tier2_analyzer.retriever.search(search_query, top_k=RAG_SEARCH_LIMIT)
            
            context_parts = []
            for result in rag_results:
                meta = result.get('meta', {})
                text = result.get('text', '')[:300]
                context_parts.append(f"Source: {meta.get('source', 'Unknown')}\n{text}")
            context = "\n\n".join(context_parts)
        
        prompt = f"""You are a Rails upgrade expert. Analyze this specific line of code for Rails {self.target_version} compatibility.

CODE TO ANALYZE:
{issue.line_content}

FILE CONTEXT (from Rails upgrade documentation):
{context}

TASK: Determine if this code needs updates for Rails {self.target_version}. Common issues include:

CONFIG FILES:
- Session store: add secure: true, httponly: true for Rails 6+
- serve_static_assets → public_file_server.enabled (Rails 5+)
- static_cache_control → public_file_server.headers (Rails 5+)
- raise_in_transactional_callbacks: remove (Rails 5+)

TEST FILES:
- ActionController::TestCase → ActionDispatch::IntegrationTest
- ActionView::TestCase updates may be needed

MODELS/CONTROLLERS:
- belongs_to requires optional: true in Rails 5+ if not required
- before_filter → before_action
- update_attributes → update

GEMS:
- factory_girl → factory_bot
- protected_attributes → use strong parameters

INSTRUCTIONS:
1. If code is already compatible with Rails {self.target_version}, respond exactly: "NO_CHANGE_NEEDED"
2. If code needs updates, provide the exact replacement code

RESPONSE FORMAT:
UPDATED_CODE: [exact replacement code OR "NO_CHANGE_NEEDED"]
EXPLANATION: [specific reason for Rails {self.target_version}]

Analyze: {issue.line_content}"""

        response = self.llm.generate(prompt, max_new_tokens=250, temperature=0.2)
        
        # Debug: Show what the LLM generated
        print(f"   🤖 LLM Raw Response: '{response[:100]}...'")
        
        # Clean response aggressively 
        response = self._clean_llm_response(response)
        
        # Debug: Show cleaned response
        print(f"   🧹 LLM Cleaned Response: '{response[:100]}...'")
        
        # Parse response more robustly
        updated_code = None  # Start with None to detect no change
        explanation = f"Analyzed for Rails {self.target_version} compatibility"
        
        # Check for explicit no change indication
        if any(phrase in response.upper() for phrase in [
            "NO_CHANGE_NEEDED", "NO CHANGE", "COMPATIBLE", "ALREADY VALID", 
            "DOESN'T REQUIRE", "NO UPDATE", "SAME AS BEFORE"
        ]):
            print(f"   ✅ LLM says no change needed")
            return None  # Skip suggestions that don't need changes
        
        # Extract updated code
        if "UPDATED_CODE:" in response:
            try:
                # Extract everything after UPDATED_CODE: until next section
                code_section = response.split("UPDATED_CODE:")[1]
                if "EXPLANATION:" in code_section:
                    code_section = code_section.split("EXPLANATION:")[0]
                updated_code = code_section.strip()
                
                # Clean common LLM artifacts
                updated_code = re.sub(r'^```[a-z]*\n?', '', updated_code)
                updated_code = re.sub(r'\n?```$', '', updated_code)
                updated_code = updated_code.strip()
                
                print(f"   📝 LLM suggested code: '{updated_code[:50]}...'")
                
                # Validate meaningful change
                if updated_code and updated_code != issue.line_content.strip():
                    # Remove common prefixes that indicate no real code
                    no_change_prefixes = [
                        "NO_CHANGE_NEEDED", "NO CHANGE", "SAME", "UNCHANGED", 
                        "# No Change", "# CODE HERE", "```", "**", "...", 
                        "Change Needed", "No Change"
                    ]
                    for prefix in no_change_prefixes:
                        if updated_code.upper().startswith(prefix.upper()):
                            print(f"   ⚠️ Detected no-change marker: {prefix}")
                            return None
                else:
                    print(f"   ⚠️ LLM returned same code, skipping")
                    return None
                    
            except Exception as e:
                print(f"   ❌ Failed to parse code: {e}")
                return None
                
        # Extract explanation  
        if "EXPLANATION:" in response:
            try:
                explanation_section = response.split("EXPLANATION:")[1].strip()
                explanation = explanation_section.split('\n')[0].strip()  # Take first line only
                print(f"   📝 LLM explanation: '{explanation[:50]}...'")
            except Exception as e:
                print(f"   ❌ Failed to parse explanation: {e}")
        
        # Final validation that we have a meaningful suggestion
        if not updated_code or updated_code.strip() == issue.line_content.strip():
            print(f"   ⚠️ No meaningful change detected, skipping")
            return None
        
        return {
            "issue_type": issue.pattern_type,
            "tier": "tier2",
            "line_number": issue.line_number,
            "original_code": issue.line_content,
            "refactored_code": updated_code,
            "explanation": explanation,
            "confidence": issue.confidence
        }
    
    def _clean_llm_response(self, response: str) -> str:
        """Aggressively clean LLM response to remove corruption."""
        if not response:
            return ""
        
        # Remove obvious corruption patterns
        corruption_patterns = [
            r'print\(["\'].*?["\'].*?\)',  # print statements
            r'console\.log.*',             # console.log
            r'import .*',                  # import statements
            r'from .* import .*',          # from imports
            r'<[^>]+>',                    # HTML tags
            r'```[a-z]*\n?',              # markdown code blocks
            r'\[image\.png\].*',           # image references
            r'attachment:.*',              # attachment references
            r'tensorflow.*',               # unrelated libraries
            r'sklearn.*',                  # unrelated libraries
            r'nltk.*',                     # unrelated libraries
            r'django.*',                   # unrelated frameworks
            r'jupyter.*',                  # jupyter references
            r'<empty_output>.*',           # jupyter output markers
        ]
        
        cleaned = response
        for pattern in corruption_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove lines with obvious corruption indicators
        lines = cleaned.split('\n')
        clean_lines = []
        
        for line in lines:
            # Skip lines with corruption indicators
            if any(indicator in line.lower() for indicator in [
                '", updated_code)', '", explanation)', 'reference_link', 
                'def analyze()', 'tokenizer =', 'sentence =', 'placeholder',
                'feedback so we could', 'thank you', 'please provide',
                'qwerqwer', 'asdfghjkl', 'sdfgdsfg'
            ]):
                continue
            clean_lines.append(line)
        
        return '\n'.join(clean_lines).strip()
    
    def _extract_ruby_code(self, response: str) -> str:
        """Extract clean Ruby code from LLM response."""
        if not response or not response.strip():
            return ""
        
        # Remove debug print statements and corrupted content
        lines = response.split('\n')
        clean_lines = []
        
        for line in lines:
            # Skip debug prints and corrupted content
            if any(skip in line.lower() for skip in [
                'print(', 'console.log', 'puts ', '", updated_code)', '", explanation)',
                'reference_link', 'tensorflow', 'import os', 'mnist', 'django',
                'sdfgdsfg', 'qwerqwer', 'asdfghjkl', 'from django'
            ]):
                continue
                
            # Skip empty lines and comments at start
            if line.strip() and not line.strip().startswith('#'):
                clean_lines.append(line)
        
        if not clean_lines:
            return ""
        
        # Join and clean up
        cleaned = '\n'.join(clean_lines)
        
        # Remove markdown formatting
        cleaned = re.sub(r'```ruby\n?', '', cleaned)
        cleaned = re.sub(r'```\n?', '', cleaned)
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        
        # Remove explanatory text after the code
        for separator in [
            '\nThis solution', '\nThe above', '\nThis code', '\nNote:', 
            '\nExplanation:', 'REFERENCE LINK', 'explainaiton:', 'explanation:'
        ]:
            if separator in cleaned:
                cleaned = cleaned.split(separator)[0]
        
        # Extract only Ruby method if present
        lines = cleaned.split('\n')
        ruby_lines = []
        
        in_method = False
        def_count = 0
        end_count = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines at the beginning
            if not ruby_lines and not stripped:
                continue
            
            # Start capturing when we see 'def' or class/module
            if stripped.startswith(('def ', 'class ', 'module ', 'private')):
                in_method = True
                def_count += stripped.count('def ')
                def_count += 1 if stripped.startswith(('class ', 'module ')) else 0
            
            if in_method:
                ruby_lines.append(line)
                
                # Count ends
                if stripped == 'end':
                    end_count += 1
                
                # Stop when we have balanced defs and ends
                if def_count > 0 and def_count == end_count:
                    break
        
        if ruby_lines:
            result = '\n'.join(ruby_lines).strip()
            return result
        
        # Fallback: return first meaningful non-empty line
        for line in lines:
            if line.strip() and not line.strip().startswith('#'):
                return line.strip()
        
        return cleaned.strip()[:200]  # Limit to 200 chars as fallback


def main():
    """CLI interface for the hybrid analyzer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hybrid Rails Analyzer")
    parser.add_argument("--file", help="Analyze a single file")
    parser.add_argument("--project", help="Analyze entire Rails project")
    parser.add_argument("--target-version", default="7.0", help="Target Rails version (default: 7.0)")
    parser.add_argument("--output", help="Output directory for results")
    parser.add_argument("--no-rag", action="store_true", help="Disable RAG (Tier 2)")
    
    args = parser.parse_args()
    
    if not args.file and not args.project:
        print("❌ Error: Specify either --file or --project")
        return
    
    analyzer = HybridRailsAnalyzer(use_retriever=not args.no_rag)
    
    if args.file:
        results = analyzer.analyze_file(args.file, args.target_version)
        
        print(f"\n📊 Analysis Results:")
        print(f"   Tier 1 issues: {len(results.get('tier1_issues', []))}")
        print(f"   Tier 2 issues: {len(results.get('tier2_issues', []))}")
        print(f"   Total suggestions: {len(results.get('suggestions', []))}")
        
        for i, suggestion in enumerate(results.get('suggestions', []), 1):
            print(f"\n🔧 Suggestion {i} ({suggestion['tier']}):")
            print(f"   Type: {suggestion['issue_type']}")
            print(f"   Line {suggestion['line_number']}: {suggestion['original_code']}")
            print(f"   Confidence: {suggestion['confidence']:.1f}")
            if suggestion['refactored_code'] != suggestion['original_code']:
                print(f"   Fix: {suggestion['refactored_code']}")
    
    elif args.project:
        results = analyzer.analyze_project(args.project, args.target_version)
        
        # Optionally save results to file
        if args.output:
            import json
            os.makedirs(args.output, exist_ok=True)
            output_file = os.path.join(args.output, f"rails_analysis_{args.target_version.replace('.', '_')}.json")
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"💾 Results saved to: {output_file}")


if __name__ == "__main__":
    main()
