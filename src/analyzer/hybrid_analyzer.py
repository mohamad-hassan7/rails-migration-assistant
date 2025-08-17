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
                confidence=0.9
            ))
        
        return results
    
    def detect_simple_deprecations(self, file_path: str, content: str) -> List[DetectionResult]:
        """Detect simple deprecation patterns."""
        results = []
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip lines with mass assignment - they're handled separately
            if 'params[' in line:
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
        
        return results
    
    def detect_all_tier1_issues(self, file_path: str, content: str) -> List[DetectionResult]:
        """Detect all Tier 1 issues in a file."""
        results = []
        
        # Mass assignment detection
        results.extend(self.detect_mass_assignment(file_path, content))
        
        # Simple deprecation detection
        results.extend(self.detect_simple_deprecations(file_path, content))
        
        return results
    
    def _is_controller_file(self, file_path: str) -> bool:
        """Check if file is a Rails controller."""
        return ('controller' in file_path.lower() or 
                '/app/controllers/' in file_path or
                '\\app\\controllers\\' in file_path)


class Tier2RAGAnalyzer:
    """General deprecation and configuration agent using RAG."""
    
    def __init__(self, retriever: Optional[Retriever] = None):
        """Initialize with optional retriever for RAG."""
        self.retriever = retriever
        
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
        
        # Config files always need RAG
        for pattern in self.config_patterns.values():
            if re.search(pattern, file_path):
                return True
        
        # Files with complex Rails API calls might need RAG
        return self._has_complex_rails_patterns(file_path)
    
    def analyze_with_rag(self, file_path: str, content: str) -> List[DetectionResult]:
        """Analyze file using RAG for complex deprecations."""
        results = []
        
        if not self.retriever:
            return results
        
        # Create search queries based on file content
        search_queries = self._generate_search_queries(file_path, content)
        
        # Search for relevant Rails documentation
        all_contexts = []
        for query in search_queries:
            rag_results = self.retriever.search(query, top_k=3)
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
                    confidence=0.7  # Lower confidence for RAG-based detection
                ))
        
        return results
    
    def _generate_search_queries(self, file_path: str, content: str) -> List[str]:
        """Generate search queries based on file content."""
        queries = []
        
        # Config file specific queries
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
        
        # Extract Rails-specific method calls for queries
        rails_methods = re.findall(r'config\.(\w+)', content)
        for method in set(rails_methods):
            queries.append(f'Rails config.{method} deprecation upgrade')
        
        return queries[:5]  # Limit to avoid too many queries
    
    def _scan_for_potential_issues(self, content: str) -> List[Dict]:
        """Scan for potential issues that might need RAG analysis."""
        issues = []
        lines = content.split('\n')
        
        # Patterns that might indicate deprecations
        potential_patterns = [
            r'config\.\w+\s*=',  # Config assignments
            r'Rails\.\w+\.',     # Rails API calls
            r'ActiveRecord::\w+', # ActiveRecord constants
            r'ActionController::\w+', # ActionController constants
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in potential_patterns:
                if re.search(pattern, line):
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
    
    def __init__(self, use_retriever: bool = True):
        """Initialize the hybrid analyzer."""
        print("🚀 Initializing Hybrid Rails Analyzer...")
        
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
                if os.path.exists("data/faiss.index") and os.path.exists("data/meta.jsonl"):
                    retriever = Retriever("data/faiss.index", "data/meta.jsonl")
                    print("✅ Tier 2 RAG Analyzer ready")
                else:
                    print("⚠️  RAG data not found, Tier 2 will use LLM only")
            except Exception as e:
                print(f"⚠️  Failed to load RAG: {e}")
        
        self.tier2_analyzer = Tier2RAGAnalyzer(retriever)
        print("✅ Hybrid analyzer initialized")
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file using the hybrid approach."""
        print(f"\n📁 Analyzing: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Failed to read file: {e}"}
        
        results = {
            "file_path": file_path,
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
                results["suggestions"].append(suggestion)
        
        # Tier 2: RAG-based analysis (if needed)
        if self.tier2_analyzer.needs_tier2_analysis(file_path):
            print("🔍 Tier 2: Performing RAG-based analysis...")
            tier2_issues = self.tier2_analyzer.analyze_with_rag(file_path, content)
            results["tier2_issues"] = tier2_issues
            
            if tier2_issues:
                print(f"   Found {len(tier2_issues)} Tier 2 issues")
                for issue in tier2_issues:
                    suggestion = self._process_tier2_issue(issue, content)
                    results["suggestions"].append(suggestion)
        else:
            print("⏭️  Tier 2: Not needed for this file type")
        
        results["total_issues"] = len(tier1_issues) + len(results["tier2_issues"])
        
        return results
    
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
            
            prompt += "\n\nOUTPUT REQUIREMENTS: Start with 'def' and end with 'end'. NO backticks, NO explanations, NO markdown."
            
            response = self.llm.generate(prompt, max_new_tokens=1200, temperature=0.1)
            
            return {
                "issue_type": issue.pattern_type,
                "tier": "tier1",
                "line_number": issue.line_number,
                "original_code": issue.line_content,
                "refactored_code": self._extract_ruby_code(response),
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
    
    def _process_tier2_issue(self, issue: DetectionResult, file_content: str) -> Dict[str, Any]:
        """Process a Tier 2 issue using RAG-enhanced prompts."""
        
        # Build RAG-enhanced prompt
        context = ""
        if self.tier2_analyzer.retriever:
            search_query = f"Rails deprecation {issue.line_content}"
            rag_results = self.tier2_analyzer.retriever.search(search_query, top_k=3)
            
            context_parts = []
            for result in rag_results:
                meta = result.get('meta', {})
                text = result.get('text', '')[:300]
                context_parts.append(f"Source: {meta.get('source', 'Unknown')}\n{text}")
            context = "\n\n".join(context_parts)
        
        prompt = f"""You are a Rails upgrade expert. Analyze this line for potential deprecations or issues:

LINE TO ANALYZE: {issue.line_content}

Rails Documentation Context:
{context}

Provide a suggestion for modernizing this code if needed. If no changes are required, respond with "NO_CHANGE_NEEDED".

Response format:
UPDATED_CODE: [your modernized code]
EXPLANATION: [brief explanation of the change]"""

        response = self.llm.generate(prompt, max_new_tokens=400, temperature=0.2)
        
        # Parse response
        updated_code = issue.line_content  # Default to original
        explanation = "Analyzed with RAG context"
        
        if "UPDATED_CODE:" in response:
            try:
                code_match = re.search(r'UPDATED_CODE:\s*(.+)', response)
                if code_match:
                    updated_code = code_match.group(1).strip()
            except:
                pass
        
        return {
            "issue_type": issue.pattern_type,
            "tier": "tier2",
            "line_number": issue.line_number,
            "original_code": issue.line_content,
            "refactored_code": updated_code,
            "explanation": explanation,
            "confidence": issue.confidence
        }
    
    def _extract_ruby_code(self, response: str) -> str:
        """Extract Ruby code from LLM response."""
        # Remove markdown formatting
        cleaned = re.sub(r'```ruby\n?', '', response)
        cleaned = re.sub(r'```\n?', '', cleaned)
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        
        # Remove explanatory text after the code
        # Split by common explanation starters
        for separator in ['\nThis solution', '\nThe above', '\nThis code', '\nNote:', '\nExplanation:']:
            if separator in cleaned:
                cleaned = cleaned.split(separator)[0]
        
        # Look for Ruby code patterns
        lines = cleaned.split('\n')
        ruby_lines = []
        
        in_ruby_block = False
        def_count = 0
        end_count = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines at the start
            if not in_ruby_block and not stripped:
                continue
                
            # Start collecting if we see Ruby keywords
            if (stripped.startswith('def ') or 
                stripped.startswith('class ') or
                stripped.startswith('private') or
                stripped.startswith('@') or
                in_ruby_block):
                in_ruby_block = True
                ruby_lines.append(line)
                
                # Count defs and ends to know when to stop
                if stripped.startswith('def '):
                    def_count += 1
                elif stripped == 'end':
                    end_count += 1
                    
                # Stop when we have balanced defs and ends
                if def_count > 0 and def_count == end_count:
                    break
        
        if ruby_lines:
            result = '\n'.join(ruby_lines)
            # Final cleanup
            result = result.strip()
            return result
        
        # Fallback: return cleaned response
        return cleaned.strip()


def main():
    """CLI interface for the hybrid analyzer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hybrid Rails Analyzer")
    parser.add_argument("--file", help="Analyze a single file")
    parser.add_argument("--project", help="Analyze entire Rails project")
    parser.add_argument("--output", help="Output directory for results")
    parser.add_argument("--no-rag", action="store_true", help="Disable RAG (Tier 2)")
    
    args = parser.parse_args()
    
    if not args.file and not args.project:
        print("❌ Error: Specify either --file or --project")
        return
    
    analyzer = HybridRailsAnalyzer(use_retriever=not args.no_rag)
    
    if args.file:
        results = analyzer.analyze_file(args.file)
        
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


if __name__ == "__main__":
    main()
