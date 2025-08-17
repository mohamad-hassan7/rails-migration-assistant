#!/usr/bin/env python3
"""
code_parser.py

Enhanced code parsing utilities for Rails upgrade analysis.
Provides precise method extraction and context analysis.
"""

import re
from typing import List, Tuple, Optional, Dict


def find_mass_assignment_risks(controller_content: str) -> List[Tuple[int, str]]:
    """
    Find lines with high probability of mass assignment vulnerabilities.
    
    Uses precise regular expressions to identify dangerous patterns:
    - .new(params[...])
    - .create(params[...])
    - .update(params[...])
    - .update_attributes(params[...])
    
    Args:
        controller_content (str): Complete Rails controller file content
        
    Returns:
        List[Tuple[int, str]]: List of (line_number, line_content) tuples
    """
    risks = []
    lines = controller_content.split('\n')
    
    # Precise regex patterns for mass assignment vulnerabilities
    risk_patterns = [
        # Pattern 1: .new(params[key]) or .new(params)
        r'\.new\s*\(\s*params(?:\[[^\]]+\])?\s*\)',
        
        # Pattern 2: .create(params[key]) or .create(params)
        r'\.create\s*\(\s*params(?:\[[^\]]+\])?\s*\)',
        
        # Pattern 3: .update(params[key]) or .update(params)
        r'\.update\s*\(\s*params(?:\[[^\]]+\])?\s*\)',
        
        # Pattern 4: .update_attributes(params[key]) - deprecated method
        r'\.update_attributes\s*\(\s*params(?:\[[^\]]+\])?\s*\)'
    ]
    
    # Safe patterns to exclude
    safe_patterns = [
        r'params\[.*\]\.permit\(',         # Already using strong parameters
        r'params\.require\(',               # Strong parameter usage
        r'params\.permit\(',                # Strong parameter usage
        r'def\s+\w+_params',               # Strong parameter method definitions
        r'#.*',                            # Comments
    ]
    
    for line_num, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        # Skip empty lines
        if not line_stripped:
            continue
            
        # Check if line contains safe patterns - if so, skip
        is_safe = any(re.search(pattern, line, re.IGNORECASE) for pattern in safe_patterns)
        if is_safe:
            continue
            
        # Check for risky patterns
        for pattern in risk_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                risks.append((line_num, line_stripped))
                break  # Found risk, move to next line
                
    return risks


def extract_method_context(file_content: str, line_number: int) -> Optional[Dict[str, any]]:
    """
    Extract the full Ruby method definition containing the given line number.
    
    Correctly handles nested blocks (do...end, if...end) to find the proper
    method boundaries.
    
    Args:
        file_content (str): Complete file content
        line_number (int): 1-based line number to find method for
        
    Returns:
        Optional[Dict]: Method context with name, start_line, end_line, and content,
                       or None if no method found
    """
    lines = file_content.split('\n')
    
    if line_number < 1 or line_number > len(lines):
        return None
    
    # Look backwards to find method definition
    method_start_line = None
    method_name = None
    method_indent = None
    
    for i in range(line_number - 1, max(0, line_number - 100), -1):
        line = lines[i]
        
        # Check for method definition
        method_match = re.match(r'^(\s*)def\s+([a-zA-Z_][a-zA-Z0-9_]*[!?]?)', line)
        if method_match:
            method_start_line = i + 1  # Convert to 1-based
            method_name = method_match.group(2)
            method_indent = len(method_match.group(1))
            break
    
    if not method_start_line:
        return None
    
    # Find method end by tracking indentation and block nesting
    method_end_line = None
    block_depth = 0
    base_indent = method_indent
    
    for i in range(method_start_line - 1, len(lines)):
        line = lines[i]
        
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            continue
        
        # Calculate current line indentation
        current_indent = len(line) - len(line.lstrip())
        
        # Track block nesting (do/end, if/end, case/end, etc.)
        line_content = line.strip()
        
        # Count block opening keywords
        block_openers = re.findall(r'\b(do|if|unless|case|while|until|begin|class|module|def)\b', line_content)
        block_depth += len(block_openers)
        
        # Count block closing keywords  
        block_closers = re.findall(r'\bend\b', line_content)
        block_depth -= len(block_closers)
        
        # Check for method end
        if (current_indent <= base_indent and 
            line_content == 'end' and 
            block_depth <= 0):
            method_end_line = i + 1  # Convert to 1-based
            break
    
    if not method_end_line:
        # If we can't find the end, assume it goes to end of file or class
        method_end_line = len(lines)
    
    # Extract method content
    method_lines = lines[method_start_line - 1:method_end_line]
    method_content = '\n'.join(method_lines)
    
    return {
        'method_name': method_name,
        'start_line': method_start_line,
        'end_line': method_end_line,
        'content': method_content,
        'line_count': method_end_line - method_start_line + 1
    }


def build_strong_params_prompt(method_content: str, controller_name: str, vulnerable_line: str) -> str:
    """
    Generate a detailed prompt for LLM to refactor a method using Strong Parameters.
    
    Creates a high-context "code generation" prompt that provides the entire method
    and asks for specific Ruby code output without explanations.
    
    Args:
        method_content (str): The complete method code that needs refactoring
        controller_name (str): Name of the controller (e.g., "UsersController")
        vulnerable_line (str): The specific line with mass assignment vulnerability
        
    Returns:
        str: Detailed prompt for LLM focused on code generation
    """
    import re
    
    # Extract model name from controller name or vulnerable line
    model_name = controller_name.replace('Controller', '').rstrip('s').lower()
    if not model_name:
        # Try to extract from vulnerable line
        model_match = re.search(r'(\w+)\.(?:new|create|update)', vulnerable_line)
        model_name = model_match.group(1).lower() if model_match else 'resource'
    
    # Extract action name from method content
    action_match = re.search(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', method_content)
    action_name = action_match.group(1) if action_match else 'action'
    
    # Build the high-context code generation prompt
    prompt = f"""Fix this Rails security vulnerability using Strong Parameters:

{method_content.strip()}

The line "{vulnerable_line.strip()}" is vulnerable.

Replace it with the secure version using a private strong parameters method.

Add this private method at the end:

private

def {model_name}_params
  params.require(:{model_name}).permit(:name, :email, :description)
end

Return the complete fixed method + private method. NO markdown, NO explanations, just Ruby code."""

    return prompt


def extract_controller_name(file_path: str) -> str:
    """
    Extract controller name from file path.
    
    Args:
        file_path (str): Path to controller file
        
    Returns:
        str: Controller class name (e.g., "UsersController")
    """
    import os
    filename = os.path.basename(file_path)
    
    # Convert from snake_case to PascalCase
    # users_controller.rb -> UsersController
    name_parts = filename.replace('.rb', '').split('_')
    controller_name = ''.join(word.capitalize() for word in name_parts)
    
    if not controller_name.endswith('Controller'):
        controller_name += 'Controller'
        
    return controller_name


# Test function
def test_code_parser():
    """Test the code parsing functions."""
    
    test_controller = '''
class UsersController < ApplicationController
  
  def create
    # Vulnerable mass assignment
    @user = User.new(params[:user])
    if @user.save
      redirect_to @user
    else
      render :new
    end
  end
  
  def update
    @user = User.find(params[:id])
    # Another vulnerable line
    if @user.update(params[:user])
      redirect_to @user
    else
      render :edit
    end
  end
  
  def safe_create
    @user = User.new(user_params)
    @user.save
  end
  
  private
  
  def user_params
    params.require(:user).permit(:name, :email)
  end
end
'''

    print("🧪 Testing find_mass_assignment_risks:")
    risks = find_mass_assignment_risks(test_controller)
    for line_num, content in risks:
        print(f"  Line {line_num}: {content}")
    
    print("\n🧪 Testing extract_method_context:")
    # Test extracting the create method (line 4)
    context = extract_method_context(test_controller, 5)
    if context:
        print(f"  Method: {context['method_name']}")
        print(f"  Lines: {context['start_line']}-{context['end_line']}")
        print(f"  Content preview: {context['content'][:100]}...")
    
    print("\n🧪 Testing build_strong_params_prompt:")
    if context:
        prompt = build_strong_params_prompt(context['content'], 'UsersController', '@user = User.new(params[:user])')
        print(f"  Prompt length: {len(prompt)} characters")
        print(f"  Prompt preview: {prompt[:200]}...")


if __name__ == "__main__":
    test_code_parser()
