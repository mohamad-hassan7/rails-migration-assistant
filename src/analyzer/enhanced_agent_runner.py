#!/usr/bin/env python3
"""
Enhanced agent_runner.py with improved mass assignment detection workflow.

This version implements the requested workflow:
1. Call find_mass_assignment_risks to get actual vulnerabilities
2. For each vulnerability, call extract_method_context to get full method code  
3. Use build_strong_params_prompt to generate detailed AI prompts
4. Send prompts to local LLM for secure refactoring suggestions
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Import our enhanced code analysis tools
from src.analyzer.code_parser import (
    find_mass_assignment_risks,
    extract_method_context, 
    build_strong_params_prompt,
    extract_controller_name
)
from src.model.local_llm import LocalLLM
from src.retriever.retriever import Retriever


class EnhancedRailsAnalyzer:
    """Enhanced Rails analyzer focusing on mass assignment vulnerabilities."""
    
    def __init__(self, use_retriever: bool = True):
        """Initialize the analyzer with local LLM and optional retriever."""
        print("🚀 Initializing Enhanced Rails Analyzer...")
        
        # Initialize local LLM (no Gemini dependency)
        self.llm = LocalLLM()
        print("✅ Local LLM loaded successfully")
        
        # Initialize retriever if available
        self.retriever = None
        if use_retriever:
            try:
                index_path = "data/faiss.index"
                meta_path = "data/meta.jsonl" 
                if os.path.exists(index_path) and os.path.exists(meta_path):
                    self.retriever = Retriever(index_path, meta_path)
                    print("✅ Document retriever loaded")
                else:
                    print("⚠️  Retriever data not found, using LLM only")
            except Exception as e:
                print(f"⚠️  Failed to load retriever: {e}")
    
    def analyze_controller_file(self, file_path: str) -> Dict:
        """
        Analyze a single Rails controller file using the enhanced workflow.
        
        Args:
            file_path (str): Path to the Rails controller file
            
        Returns:
            Dict: Analysis results with vulnerabilities and refactoring suggestions
        """
        print(f"\n📁 Analyzing: {file_path}")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Failed to read file: {e}"}
        
        # Step 1: Find mass assignment risks
        print("🔍 Step 1: Finding mass assignment vulnerabilities...")
        risks = find_mass_assignment_risks(content)
        print(f"   Found {len(risks)} potential vulnerabilities")
        
        if not risks:
            return {
                "file": file_path,
                "vulnerabilities_found": 0,
                "status": "No mass assignment vulnerabilities detected",
                "suggestions": []
            }
        
        # Extract controller name for context
        controller_name = extract_controller_name(file_path)
        
        analysis_results = {
            "file": file_path,
            "controller_name": controller_name,
            "vulnerabilities_found": len(risks),
            "vulnerabilities": [],
            "suggestions": []
        }
        
        # Step 2 & 3: For each vulnerability, extract method and build prompt
        print("🔧 Step 2-3: Extracting method context and building prompts...")
        
        processed_methods = set()  # Avoid duplicate processing
        
        for line_num, vulnerable_line in risks:
            print(f"   Processing vulnerability at line {line_num}: {vulnerable_line[:50]}...")
            
            # Step 2: Extract method context
            method_context = extract_method_context(content, line_num)
            
            if not method_context:
                print(f"   ⚠️  Could not extract method context for line {line_num}")
                continue
            
            method_name = method_context['method_name']
            
            # Skip if we already processed this method
            if method_name in processed_methods:
                print(f"   ⏭️  Method '{method_name}' already processed")
                continue
                
            processed_methods.add(method_name)
            
            # Step 3: Build strong params prompt
            prompt = build_strong_params_prompt(
                method_context['content'],
                controller_name,
                vulnerable_line
            )
            
            # Step 4: Get LLM suggestion
            print(f"   🤖 Getting AI refactoring suggestion for method '{method_name}'...")
            suggestion = self._get_llm_suggestion(prompt, method_context)
            
            # Store results
            vulnerability_info = {
                "line_number": line_num,
                "vulnerable_line": vulnerable_line,
                "method_name": method_name,
                "method_context": method_context,
                "ai_suggestion": suggestion
            }
            
            analysis_results["vulnerabilities"].append(vulnerability_info)
            analysis_results["suggestions"].append({
                "method": method_name,
                "original_code": method_context['content'],
                "refactored_code": suggestion.get('refactored_code', ''),
                "explanation": suggestion.get('explanation', ''),
                "confidence": suggestion.get('confidence', 0.8)
            })
        
        return analysis_results
    
    def _get_llm_suggestion(self, prompt: str, method_context: Dict) -> Dict:
        """Get LLM suggestion for fixing mass assignment vulnerability."""
        try:
            # Get Rails-specific context if retriever is available
            context = ""
            if self.retriever:
                search_query = f"Rails strong parameters {method_context['method_name']} mass assignment"
                results = self.retriever.search(search_query, top_k=3)
                context_parts = []
                for result in results:
                    meta = result.get('meta', {})
                    text = result.get('text', '')[:200]
                    context_parts.append(f"Source: {meta.get('source', 'Unknown')}\n{text}")
                context = "\n\n".join(context_parts)
            
            # Enhanced prompt with context
            if context:
                enhanced_prompt = f"""Rails Documentation Context:
{context}

{prompt}"""
            else:
                enhanced_prompt = prompt
            
            # Generate suggestion with parameters optimized for code generation
            response = self.llm.generate(enhanced_prompt, max_new_tokens=1200, temperature=0.1)
            
            # Parse the response
            return self._parse_llm_response(response, method_context)
            
        except Exception as e:
            return {
                "error": f"Failed to get LLM suggestion: {e}",
                "refactored_code": "",
                "explanation": "Error occurred during AI analysis",
                "confidence": 0.0
            }
    
    def _parse_llm_response(self, response: str, method_context: Dict) -> Dict:
        """Parse LLM response to extract refactored code and explanation."""
        
        # Clean the response first
        response = response.strip()
        
        # Extract code blocks (look for Ruby code)
        import re
        
        # Method 1: Look for explicit code blocks
        code_blocks = re.findall(r'```ruby\n(.*?)```', response, re.DOTALL)
        
        # Method 2: If no explicit blocks, look for def...end patterns (the response might be direct Ruby)
        if not code_blocks:
            # Check if the response starts directly with Ruby code
            if response.startswith('def ') or 'def ' in response[:100]:
                # Treat the entire response as Ruby code
                code_blocks = [response]
        
        # Method 3: Extract everything between "def" and the last "end"
        if not code_blocks:
            def_match = re.search(r'(def\s+.*?)(?:\n\n|\Z)', response, re.DOTALL)
            if def_match:
                code_blocks = [def_match.group(1)]
        
        refactored_code = ""
        if code_blocks:
            # Take the longest code block (likely the complete refactored method)
            refactored_code = max(code_blocks, key=len).strip()
            
            # Clean up common formatting issues
            refactored_code = refactored_code.replace('```ruby', '').replace('```', '').strip()
        
        # If still no code found, try to extract any Ruby-looking content
        if not refactored_code:
            lines = response.split('\n')
            ruby_lines = []
            for line in lines:
                stripped = line.strip()
                # Look for Ruby keywords and patterns
                if (stripped.startswith('def ') or 
                    stripped.startswith('end') or
                    stripped.startswith('@') or
                    'params.require' in stripped or
                    '.permit(' in stripped or
                    'private' in stripped):
                    ruby_lines.append(line)
            
            if ruby_lines:
                refactored_code = '\n'.join(ruby_lines)
        
        # Extract explanation (text that doesn't look like Ruby code)
        explanation = ""
        if refactored_code:
            # Remove the code part and use the rest as explanation
            response_without_code = response
            for block in code_blocks:
                response_without_code = response_without_code.replace(block, '')
            
            # Clean up the explanation
            explanation = re.sub(r'```ruby.*?```', '', response_without_code, flags=re.DOTALL)
            explanation = explanation.replace('```', '').strip()
            
            # If no meaningful explanation, provide a default
            if len(explanation) < 20:
                explanation = f"Refactored method to use strong parameters with {method_context.get('method_name', 'method')}_params private method."
        else:
            explanation = "Failed to extract refactored code from LLM response."
        
        # Estimate confidence based on response quality
        confidence = 0.9 if (refactored_code and 
                           "permit" in refactored_code and 
                           "params.require" in refactored_code and
                           "def " in refactored_code) else 0.6
        
        # Lower confidence if the code seems incomplete
        if refactored_code and not refactored_code.count('def ') >= 1:
            confidence *= 0.7
            
        return {
            "refactored_code": refactored_code,
            "explanation": explanation,
            "confidence": confidence,
            "raw_response": response
        }
    
    def analyze_project(self, project_path: str, output_dir: str = None) -> Dict:
        """
        Analyze an entire Rails project for mass assignment vulnerabilities.
        
        Args:
            project_path (str): Path to Rails project root
            output_dir (str): Directory to save analysis results
            
        Returns:
            Dict: Overall project analysis results
        """
        project_path = Path(project_path)
        
        if not project_path.exists():
            return {"error": f"Project path not found: {project_path}"}
        
        # Find controller files
        controllers_dir = project_path / "app" / "controllers"
        if not controllers_dir.exists():
            return {"error": f"Controllers directory not found: {controllers_dir}"}
        
        controller_files = list(controllers_dir.glob("**/*.rb"))
        
        if not controller_files:
            return {"error": "No controller files found"}
        
        print(f"🔍 Found {len(controller_files)} controller files to analyze")
        
        project_results = {
            "project_path": str(project_path),
            "total_controllers": len(controller_files),
            "controllers_analyzed": 0,
            "total_vulnerabilities": 0,
            "controllers_with_issues": 0,
            "results": []
        }
        
        # Analyze each controller
        for controller_file in controller_files:
            print(f"\n{'='*60}")
            file_results = self.analyze_controller_file(str(controller_file))
            
            if "error" not in file_results:
                project_results["controllers_analyzed"] += 1
                vuln_count = file_results.get("vulnerabilities_found", 0)
                project_results["total_vulnerabilities"] += vuln_count
                
                if vuln_count > 0:
                    project_results["controllers_with_issues"] += 1
            
            project_results["results"].append(file_results)
        
        # Save results if output directory specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            results_file = output_path / "mass_assignment_analysis.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(project_results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Results saved to: {results_file}")
        
        return project_results


def main():
    """Main CLI interface for the enhanced analyzer."""
    parser = argparse.ArgumentParser(description="Enhanced Rails Mass Assignment Analyzer")
    parser.add_argument("--file", help="Analyze a single controller file")
    parser.add_argument("--project", help="Analyze entire Rails project")
    parser.add_argument("--output", help="Output directory for results")
    parser.add_argument("--no-retriever", action="store_true", 
                       help="Disable document retriever (LLM only)")
    
    args = parser.parse_args()
    
    if not args.file and not args.project:
        print("❌ Error: Specify either --file or --project")
        parser.print_help()
        return
    
    # Initialize analyzer
    analyzer = EnhancedRailsAnalyzer(use_retriever=not args.no_retriever)
    
    if args.file:
        # Analyze single file
        results = analyzer.analyze_controller_file(args.file)
        
        if args.output:
            output_path = Path(args.output)
            output_path.mkdir(parents=True, exist_ok=True)
            
            filename = Path(args.file).stem
            results_file = output_path / f"{filename}_analysis.json"
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Results saved to: {results_file}")
        else:
            print("\n📊 Analysis Results:")
            print(json.dumps(results, indent=2))
    
    elif args.project:
        # Analyze entire project
        results = analyzer.analyze_project(args.project, args.output)
        
        print(f"\n📊 Project Analysis Summary:")
        print(f"   Controllers analyzed: {results.get('controllers_analyzed', 0)}")
        print(f"   Total vulnerabilities: {results.get('total_vulnerabilities', 0)}")
        print(f"   Controllers with issues: {results.get('controllers_with_issues', 0)}")


if __name__ == "__main__":
    main()
