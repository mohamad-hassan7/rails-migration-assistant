#!/usr/bin/env python3
"""
Rails Project Scanner

Automatically scans Rails project directories to identify:
1. Rails version and gems
2. Deprecated code patterns
3. Files that need upgrading
4. Security vulnerabilities
5. Performance improvements

Usage:
  from src.analyzer.project_scanner import RailsProjectScanner
  scanner = RailsProjectScanner()
  analysis = scanner.scan_project("/path/to/rails/project")
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import subprocess

class RailsProjectScanner:
    def __init__(self):
        self.rails_patterns = {
            # Deprecated patterns for different Rails versions
            'rails_4_to_5': [
                {
                    'pattern': r'before_filter\s+',
                    'replacement': 'before_action ',
                    'explanation': 'before_filter is deprecated in Rails 5+, use before_action instead',
                    'file_types': ['.rb']
                },
                {
                    'pattern': r'after_filter\s+',
                    'replacement': 'after_action ',
                    'explanation': 'after_filter is deprecated in Rails 5+, use after_action instead',
                    'file_types': ['.rb']
                },
                {
                    'pattern': r'skip_before_filter\s+',
                    'replacement': 'skip_before_action ',
                    'explanation': 'skip_before_filter is deprecated in Rails 5+, use skip_before_action instead',
                    'file_types': ['.rb']
                }
            ],
            'rails_5_to_6': [
                {
                    'pattern': r'config\.secrets\.',
                    'replacement': 'Rails.application.credentials.',
                    'explanation': 'Rails.application.secrets is deprecated in Rails 6+, use credentials instead',
                    'file_types': ['.rb']
                },
                {
                    'pattern': r'update_attributes\(',
                    'replacement': 'update(',
                    'explanation': 'update_attributes is deprecated in Rails 6+, use update instead',
                    'file_types': ['.rb']
                }
            ],
            'rails_6_to_7': [
                {
                    'pattern': r'config\.force_ssl\s*=\s*true',
                    'replacement': 'config.assume_ssl = true\\nconfig.force_ssl = true',
                    'explanation': 'Rails 7 requires assume_ssl when force_ssl is used',
                    'file_types': ['.rb']
                },
                {
                    'pattern': r'ActiveRecord::Base\.establish_connection',
                    'replacement': 'ApplicationRecord.establish_connection',
                    'explanation': 'Use ApplicationRecord instead of ActiveRecord::Base in Rails 7+',
                    'file_types': ['.rb']
                }
            ],
            'security_patterns': [
                {
                    'pattern': r'\.(?:create|update|update_attributes)\s*\(\s*params(?:\[[^\]]+\])?\s*\)(?!\s*\.permit)',
                    'replacement': 'Use strong parameters with permit',
                    'explanation': 'Mass assignment vulnerability detected. Use strong parameters to whitelist allowed attributes.',
                    'file_types': ['.rb'],
                    'severity': 'critical',
                    'capture_method': True
                },
                {
                    'pattern': r'params(?:\[[^\]]+\])?\s*(?!\.permit)(?=\s*[,\)])',
                    'replacement': 'Use strong parameters with permit',
                    'explanation': 'Unsafe parameter usage detected. Use strong parameters to prevent mass assignment.',
                    'file_types': ['.rb'],
                    'severity': 'high',
                    'capture_method': True
                },
                {
                    'pattern': r'raw\s*\(',
                    'replacement': 'sanitize() or safe_join()',
                    'explanation': 'raw() can lead to XSS vulnerabilities, use sanitize() instead',
                    'file_types': ['.erb', '.html.erb'],
                    'severity': 'high'
                },
                {
                    'pattern': r'\.html_safe\b',
                    'replacement': 'sanitize() or content_tag()',
                    'explanation': 'html_safe can be dangerous, ensure content is properly sanitized first',
                    'file_types': ['.rb', '.erb'],
                    'severity': 'medium'
                }
            ],
            'performance_patterns': [
                {
                    'pattern': r'find\(\d+\)',
                    'replacement': 'find_by(id: n)',
                    'explanation': 'find_by is safer and more explicit than find with ID',
                    'file_types': ['.rb'],
                    'severity': 'medium'
                },
                {
                    'pattern': r'\.each\s+do.*?\n.*?\.save.*?\n.*?end',
                    'replacement': 'Use bulk operations like insert_all or upsert_all',
                    'explanation': 'Bulk operations are much faster than individual saves in loops',
                    'file_types': ['.rb'],
                    'severity': 'medium'
                }
            ]
        }
        
        self.rails_files = {
            'gemfile': 'Gemfile',
            'routes': 'config/routes.rb',
            'application': 'config/application.rb',
            'database': 'config/database.yml',
            'environment': 'config/environment.rb'
        }
        
    def scan_project(self, project_path: str) -> Dict:
        """
        Scan a Rails project and return comprehensive analysis.
        
        Args:
            project_path: Path to the Rails project directory
            
        Returns:
            Dictionary containing scan results and suggestions
        """
        project_path = Path(project_path)
        
        if not project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
            
        analysis = {
            'project_path': str(project_path),
            'is_rails_project': self._is_rails_project(project_path),
            'rails_version': None,
            'gems': {},
            'issues': [],
            'suggestions': [],
            'files_scanned': 0,
            'summary': {}
        }
        
        if not analysis['is_rails_project']:
            return analysis
            
        # Get Rails version and gems
        analysis['rails_version'] = self._get_rails_version(project_path)
        analysis['gems'] = self._get_gems(project_path)
        
        # Scan for issues and generate suggestions
        issues = self._scan_for_issues(project_path)
        analysis['issues'] = issues
        analysis['suggestions'] = self._generate_suggestions(issues, analysis['rails_version'])
        
        # Generate summary
        analysis['summary'] = self._generate_summary(analysis)
        
        return analysis
        
    def _is_rails_project(self, project_path: Path) -> bool:
        """Check if the directory is a Rails project."""
        gemfile_path = project_path / 'Gemfile'
        if not gemfile_path.exists():
            return False
            
        try:
            with open(gemfile_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return 'rails' in content.lower()
        except:
            return False
            
    def _get_rails_version(self, project_path: Path) -> Optional[str]:
        """Extract Rails version from Gemfile or Gemfile.lock."""
        # Try Gemfile.lock first (more accurate)
        lock_file = project_path / 'Gemfile.lock'
        if lock_file.exists():
            try:
                with open(lock_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    match = re.search(r'rails \(([^)]+)\)', content)
                    if match:
                        return match.group(1)
            except:
                pass
                
        # Try Gemfile
        gemfile = project_path / 'Gemfile'
        if gemfile.exists():
            try:
                with open(gemfile, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Look for gem 'rails', '~> 6.1.0'
                    match = re.search(r'gem\s+[\'"]rails[\'"],\s*[\'"]([^\'\"]+)[\'"]', content)
                    if match:
                        return match.group(1).replace('~>', '').replace('>=', '').strip()
            except:
                pass
                
        return None
        
    def _get_gems(self, project_path: Path) -> Dict:
        """Extract gem list from Gemfile."""
        gems = {}
        gemfile = project_path / 'Gemfile'
        
        if not gemfile.exists():
            return gems
            
        try:
            with open(gemfile, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Match gem lines: gem 'name', 'version'
                gem_pattern = r'gem\s+[\'"]([^\'\"]+)[\'"](?:,\s*[\'"]([^\'\"]+)[\'"])?'
                matches = re.findall(gem_pattern, content)
                
                for gem_name, version in matches:
                    gems[gem_name] = version if version else 'latest'
                    
        except Exception as e:
            print(f"Error reading Gemfile: {e}")
            
        return gems
        
    def _scan_for_issues(self, project_path: Path) -> List[Dict]:
        """Scan project files for deprecated patterns and issues."""
        issues = []
        
        # Define file extensions to scan
        extensions = ['.rb', '.erb', '.html.erb', '.yml', '.yaml']
        
        # Scan directories
        scan_dirs = ['app', 'config', 'lib', 'spec', 'test']
        
        for dir_name in scan_dirs:
            dir_path = project_path / dir_name
            if dir_path.exists():
                issues.extend(self._scan_directory(dir_path, extensions))
                
        return issues
        
    def _scan_directory(self, directory: Path, extensions: List[str]) -> List[Dict]:
        """Recursively scan directory for issues."""
        issues = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                file_issues = self._scan_file(file_path)
                issues.extend(file_issues)
                
        return issues
    
    def find_vulnerable_lines(self, controller_content: str) -> List[int]:
        """
        Find lines containing mass assignment vulnerabilities using precise pattern matching.
        
        This method reduces false positives by specifically targeting dangerous patterns:
        - .new(params[...])
        - .create(params[...]) 
        - .update(params[...])
        - .update_attributes(params[...])
        
        But excludes safe patterns like:
        - Model.find(params[:id])
        - params with .permit calls
        - Strong parameter method definitions
        
        Args:
            controller_content (str): The complete content of a controller file
            
        Returns:
            List[int]: Line numbers (1-indexed) containing vulnerable patterns
        """
        vulnerable_lines = []
        lines = controller_content.split('\n')
        
        # Improved regex patterns that target actual mass assignment vulnerabilities
        mass_assignment_patterns = [
            # Pattern 1: .new(params[...]) - but not in private methods defining strong params
            r'\.new\s*\(\s*params\[',
            
            # Pattern 2: .create(params[...]) - direct mass assignment
            r'\.create\s*\(\s*params\[',
            
            # Pattern 3: .update(params[...]) - direct mass assignment  
            r'\.update\s*\(\s*params\[',
            
            # Pattern 4: .update_attributes(params[...]) - deprecated and unsafe
            r'\.update_attributes\s*\(\s*params\[',
            
            # Pattern 5: Model.new(params) without specific key
            r'\.new\s*\(\s*params\s*\)',
            
            # Pattern 6: Model.create(params) without specific key
            r'\.create\s*\(\s*params\s*\)',
            
            # Pattern 7: Model.update(params) without specific key
            r'\.update\s*\(\s*params\s*\)'
        ]
        
        # Patterns to exclude (safe usage)
        safe_patterns = [
            r'\.find\s*\(',                    # Model.find(params[:id]) is safe
            r'\.find_by\s*\(',                 # Model.find_by(...) is safe
            r'\.where\s*\(',                   # Model.where(...) is safe
            r'params\[.*\]\.permit\(',         # Already using strong parameters
            r'def\s+\w+_params',               # Strong parameter method definitions
            r'params\.require\(',               # Strong parameter usage
            r'params\.permit\(',                # Strong parameter usage
            r'#.*params',                       # Comments mentioning params
        ]
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Skip empty lines and comments
            if not line_stripped or line_stripped.startswith('#'):
                continue
                
            # Check if line contains safe patterns - if so, skip
            is_safe = False
            for safe_pattern in safe_patterns:
                if re.search(safe_pattern, line, re.IGNORECASE):
                    is_safe = True
                    break
                    
            if is_safe:
                continue
                
            # Check for vulnerable patterns
            for pattern in mass_assignment_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Additional context check: make sure it's not in a comment or string
                    # Simple check for common comment patterns
                    if not (line.strip().startswith('#') or line.strip().startswith('//')):
                        vulnerable_lines.append(line_num)
                        break  # Found vulnerability, move to next line
                        
        return vulnerable_lines
        
    def _scan_file(self, file_path: Path) -> List[Dict]:
        """Scan individual file for deprecated patterns."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Check all pattern categories
                all_patterns = []
                all_patterns.extend(self.rails_patterns.get('rails_4_to_5', []))
                all_patterns.extend(self.rails_patterns.get('rails_5_to_6', []))
                all_patterns.extend(self.rails_patterns.get('rails_6_to_7', []))
                all_patterns.extend(self.rails_patterns.get('performance_patterns', []))
                
                # Handle security patterns with enhanced mass assignment detection
                security_patterns = self.rails_patterns.get('security_patterns', [])
                
                # Use new precise method for mass assignment detection on controller files
                if file_path.suffix == '.rb' and ('controller' in str(file_path).lower() or 'app/controllers' in str(file_path)):
                    vulnerable_lines = self.find_vulnerable_lines(content)
                    
                    for line_num in vulnerable_lines:
                        if line_num <= len(lines):
                            line_content = lines[line_num - 1].strip()
                            
                            # Extract method context for the vulnerability
                            method_context = self._extract_method_context(content, 
                                content.find(line_content), lines)
                            
                            issues.append({
                                'file': str(file_path),
                                'line': line_num,
                                'line_content': line_content,
                                'pattern': 'mass_assignment_vulnerability',
                                'old_code': line_content,
                                'suggested_code': 'Use strong parameters with permit',
                                'explanation': 'Mass assignment vulnerability detected. Use strong parameters to whitelist allowed attributes.',
                                'severity': 'critical',
                                'category': 'Security',
                                'method_context': method_context
                            })
                
                # Process other security patterns (non-mass assignment)
                other_security_patterns = [p for p in security_patterns 
                                         if 'mass assignment' not in p.get('explanation', '').lower()]
                all_patterns.extend(other_security_patterns)
                
                for pattern_info in all_patterns:
                    if file_path.suffix in pattern_info.get('file_types', []):
                        matches = re.finditer(pattern_info['pattern'], content, re.MULTILINE | re.DOTALL)
                        
                        for match in matches:
                            # Find line number
                            line_num = content[:match.start()].count('\n') + 1
                            line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                            
                            # Capture method context if needed
                            method_context = None
                            if pattern_info.get('capture_method', False):
                                method_context = self._extract_method_context(content, match.start(), lines)
                            
                            issues.append({
                                'file': str(file_path),
                                'line': line_num,
                                'line_content': line_content.strip(),
                                'pattern': pattern_info['pattern'],
                                'old_code': match.group(0),
                                'suggested_code': pattern_info['replacement'],
                                'explanation': pattern_info['explanation'],
                                'severity': pattern_info.get('severity', 'medium'),
                                'category': self._get_pattern_category(pattern_info),
                                'method_context': method_context
                            })
                            
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")
            
        return issues
    
    def _extract_method_context(self, content: str, match_position: int, lines: List[str]) -> Dict:
        """Extract the full method definition containing the vulnerability."""
        try:
            # Find the line number of the match
            line_num = content[:match_position].count('\n') + 1
            
            # Look backwards to find the method definition
            method_start_line = None
            method_name = None
            indent_level = None
            
            for i in range(line_num - 1, max(0, line_num - 50), -1):  # Look up to 50 lines back
                line = lines[i].strip()
                if re.match(r'^\s*def\s+(\w+)', line):
                    method_match = re.match(r'^(\s*)def\s+(\w+)', lines[i])
                    if method_match:
                        indent_level = len(method_match.group(1))
                        method_name = method_match.group(2)
                        method_start_line = i + 1
                        break
            
            if method_start_line is None:
                return None
            
            # Look forwards to find the end of the method
            method_end_line = len(lines)
            for i in range(line_num, min(len(lines), line_num + 100)):  # Look up to 100 lines forward
                line = lines[i]
                # Check if we've reached the same indentation level with 'end'
                if line.strip() == 'end' and len(line) - len(line.lstrip()) <= indent_level:
                    method_end_line = i + 1
                    break
                # Check if we've reached another method definition at the same level
                elif re.match(r'^\s{0,' + str(indent_level) + r'}def\s+', line) and i > method_start_line - 1:
                    method_end_line = i
                    break
            
            # Extract the method content
            method_lines = lines[method_start_line - 1:method_end_line]
            method_content = '\n'.join(method_lines)
            
            # Determine if this is a controller action
            is_controller_action = 'controller' in str(self._get_file_context(content)).lower()
            
            return {
                'method_name': method_name,
                'method_content': method_content,
                'start_line': method_start_line,
                'end_line': method_end_line,
                'is_controller_action': is_controller_action,
                'vulnerable_line': line_num - method_start_line + 1  # Line within the method
            }
            
        except Exception as e:
            print(f"Error extracting method context: {e}")
            return None
    
    def _get_file_context(self, content: str) -> str:
        """Extract class/module context from file content."""
        # Look for class definitions
        class_match = re.search(r'class\s+(\w+(?:::\w+)*)', content)
        if class_match:
            return class_match.group(1)
        
        # Look for module definitions
        module_match = re.search(r'module\s+(\w+(?:::\w+)*)', content)
        if module_match:
            return module_match.group(1)
        
        return "Unknown"
        
    def _get_pattern_category(self, pattern_info: Dict) -> str:
        """Determine the category of a pattern."""
        for category, patterns in self.rails_patterns.items():
            if pattern_info in patterns:
                return category
        return 'unknown'
        
    def _generate_suggestions(self, issues: List[Dict], rails_version: Optional[str]) -> List[Dict]:
        """Generate upgrade suggestions based on found issues."""
        suggestions = []
        
        for issue in issues:
            suggestion = {
                'file_path': issue['file'],
                'line_number': issue['line'],
                'old_code': issue['line_content'],
                'new_code': self._generate_fix_code(issue),
                'explanation': self._generate_detailed_explanation(issue),
                'confidence': self._calculate_confidence(issue),
                'rails_version': rails_version or 'unknown',
                'change_type': issue['category'],
                'severity': issue['severity'],
                'status': 'pending',
                'ai_prompt': self._generate_ai_prompt(issue),
                'method_context': issue.get('method_context')
            }
            suggestions.append(suggestion)
            
        return suggestions
    
    def _generate_fix_code(self, issue: Dict) -> str:
        """Generate specific fix code based on the issue type."""
        if 'security' in issue['category'] and issue.get('method_context'):
            # For security issues with method context, generate a complete fix
            method_context = issue['method_context']
            if method_context['is_controller_action']:
                return self._generate_controller_fix(issue)
        
        # Default fix
        return issue['line_content'].replace(issue['old_code'], issue['suggested_code'])
    
    def _generate_controller_fix(self, issue: Dict) -> str:
        """Generate a complete controller action fix for mass assignment."""
        method_context = issue['method_context']
        method_name = method_context['method_name']
        
        # Extract model name from the vulnerable line
        vulnerable_line = issue['line_content']
        model_match = re.search(r'(\w+)\.(?:create|update)', vulnerable_line)
        model_name = model_match.group(1).lower() if model_match else 'resource'
        
        # Generate the fixed method
        fixed_method = f"""def {method_name}
    # ... existing code before the vulnerability ...
    
    # Fixed: Use strong parameters instead of raw params
    @{model_name} = {model_name.capitalize()}.create({model_name}_params)
    
    # ... rest of method ...
  end

  private

  def {model_name}_params
    params.require(:{model_name}).permit(:allowed_attribute1, :allowed_attribute2)
    # TODO: Replace :allowed_attribute1, :allowed_attribute2 with actual allowed attributes
  end"""
        
        return fixed_method
    
    def _generate_detailed_explanation(self, issue: Dict) -> str:
        """Generate detailed explanation including security context."""
        base_explanation = issue['explanation']
        
        if 'security' in issue['category']:
            if 'mass assignment' in base_explanation.lower():
                return f"""{base_explanation}

🔒 Security Impact:
- Attackers could modify unintended model attributes
- Could lead to privilege escalation or data corruption
- Rails security best practice violation

✅ Recommended Fix:
1. Create a private method (e.g., user_params) that uses .permit()
2. Whitelist only the attributes that should be user-modifiable
3. Use this method instead of raw params in create/update calls

Example: params.require(:user).permit(:name, :email)"""
        
        return base_explanation
    
    def _generate_ai_prompt(self, issue: Dict) -> str:
        """Generate a detailed AI prompt for fixing the issue."""
        if 'security' in issue['category'] and issue.get('method_context'):
            method_context = issue['method_context']
            
            return f"""You are an expert Rails security consultant. You've found a critical mass assignment vulnerability.

**Context:**
- File: {issue['file']}
- Controller Action: {method_context['method_name']}
- Vulnerable Line: {issue['line_content']}
- Security Issue: Mass assignment vulnerability

**Current Vulnerable Code:**
```ruby
{method_context['method_content']}
```

**Task:**
Rewrite the {method_context['method_name']} action to fix the mass assignment vulnerability by:

1. Creating a private `{method_context['method_name'].replace('create', '').replace('update', '').lower() or 'resource'}_params` method
2. Using strong parameters with `.require()` and `.permit()`
3. Replacing the vulnerable parameter usage with the secure method
4. Adding appropriate comments explaining the security fix

**Requirements:**
- Maintain all existing functionality
- Follow Rails security best practices
- Include TODO comments for attribute whitelisting
- Preserve the method structure and logic flow

**Response Format:**
Provide the complete fixed method definition with the private parameter method."""

        else:
            return f"""You are an expert Rails developer. Please fix this {issue['severity']} priority issue:

**Context:**
- File: {issue['file']}
- Issue: {issue['explanation']}
- Current Code: {issue['line_content']}

**Task:**
Provide the corrected code that follows Rails best practices and fixes the identified issue.

**Response Format:**
Provide only the corrected line(s) of code without additional explanation."""
        
    def _calculate_confidence(self, issue: Dict) -> str:
        """Calculate confidence level for a suggestion."""
        severity = issue.get('severity', 'medium')
        category = issue.get('category', 'unknown')
        
        # Critical security issues are very high confidence
        if severity == 'critical':
            return 'very_high'
            
        # Security issues are high confidence
        if 'security' in category or severity == 'high':
            return 'high'
            
        # Rails version upgrade patterns are high confidence
        if 'rails_' in category:
            return 'high'
            
        # Performance improvements are medium confidence
        if 'performance' in category:
            return 'medium'
            
        return 'medium'
        
    def _generate_summary(self, analysis: Dict) -> Dict:
        """Generate summary statistics."""
        issues = analysis.get('issues', [])
        suggestions = analysis.get('suggestions', [])
        
        summary = {
            'total_issues': len(issues),
            'total_suggestions': len(suggestions),
            'by_severity': {},
            'by_category': {},
            'files_with_issues': len(set(issue['file'] for issue in issues))
        }
        
        # Count by severity
        for issue in issues:
            severity = issue.get('severity', 'unknown')
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
            
        # Count by category  
        for issue in issues:
            category = issue.get('category', 'unknown')
            summary['by_category'][category] = summary['by_category'].get(category, 0) + 1
            
        return summary
        
    def get_upgrade_priority(self, analysis: Dict) -> List[str]:
        """Get prioritized list of upgrade recommendations."""
        priorities = []
        
        rails_version = analysis.get('rails_version')
        if rails_version:
            try:
                major_version = int(rails_version.split('.')[0])
                
                if major_version < 5:
                    priorities.append("🚨 URGENT: Upgrade from Rails 4 to 5+ (End of Life)")
                elif major_version < 6:
                    priorities.append("⚠️ HIGH: Upgrade from Rails 5 to 6+ (Security & Performance)")
                elif major_version < 7:
                    priorities.append("📈 MEDIUM: Upgrade from Rails 6 to 7 (Latest Features)")
                else:
                    priorities.append("✅ GOOD: Rails 7+ detected")
                    
            except:
                priorities.append("❓ UNKNOWN: Could not determine Rails version")
                
        # Security issues
        security_count = analysis.get('summary', {}).get('by_category', {}).get('security_patterns', 0)
        if security_count > 0:
            priorities.append(f"🔒 SECURITY: Fix {security_count} security issue(s)")
            
        # Performance issues
        perf_count = analysis.get('summary', {}).get('by_category', {}).get('performance_patterns', 0)
        if perf_count > 0:
            priorities.append(f"⚡ PERFORMANCE: Optimize {perf_count} performance issue(s)")
            
        return priorities
