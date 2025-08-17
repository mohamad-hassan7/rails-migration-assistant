import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import json
from datetime import datetime
from typing import Dict, Any, Optional

class LocalLLM:
    """
    Local LLM implementation for secure Rails upgrade assistance.
    
    Supports multiple models optimized for code generation and Rails knowledge:
    - deepseek-ai/deepseek-coder-6.7b-instruct: Best for code generation
    - codellama/CodeLlama-7b-Instruct-hf: Good alternative
    - microsoft/DialoGPT-medium: Lightweight option
    """
    
    # Recommended models for Rails upgrade tasks
    RECOMMENDED_MODELS = {
        "deepseek-coder": {
            "name": "deepseek-ai/deepseek-coder-6.7b-instruct",
            "description": "Best for Rails code generation and upgrades",
            "size": "6.7B parameters",
            "memory": "~13GB (4-bit: ~4GB)"
        },
        "codellama": {
            "name": "codellama/CodeLlama-7b-Instruct-hf", 
            "description": "Strong code understanding and generation",
            "size": "7B parameters",
            "memory": "~14GB (4-bit: ~4GB)"
        },
        "starcoder": {
            "name": "bigcode/starcoder-15.5b",
            "description": "Large model with excellent code capabilities",
            "size": "15.5B parameters", 
            "memory": "~31GB (4-bit: ~8GB)"
        }
    }
    
    def __init__(self, 
                 model_name_or_path: str = "deepseek-ai/deepseek-coder-6.7b-instruct",
                 use_4bit: bool = True,
                 load_in_8bit: bool = False,
                 device_map: str = "auto",
                 trust_remote_code: bool = True):
        
        self.model_name = model_name_or_path
        self.use_4bit = use_4bit
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"🚀 Loading local model: {model_name_or_path}")
        print(f"   📊 Quantization: {'4-bit' if use_4bit else '8-bit' if load_in_8bit else 'full precision'}")
        print(f"   💾 Device: {self.device}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name_or_path, 
            use_fast=True,
            trust_remote_code=trust_remote_code
        )

        
        # Set up padding token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Configure quantization for memory efficiency
        quantization_config = None
        if use_4bit:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        elif load_in_8bit:
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
            )

        # Model loading configuration
        model_kwargs = {
            "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
            "device_map": device_map,
            "low_cpu_mem_usage": True,
            "trust_remote_code": trust_remote_code
        }
        
        if quantization_config:
            model_kwargs["quantization_config"] = quantization_config

        try:
            # Try to load with quantization first (more memory efficient)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name_or_path,
                **model_kwargs
            )
            print("✅ Model loaded successfully with quantization.")
            
        except Exception as e:
            print(f"⚠️  Quantization failed: {e}")
            print("🔄 Falling back to standard loading...")
            
            # Fallback to standard loading
            model_kwargs.pop("quantization_config", None)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name_or_path,
                **model_kwargs
            )
            print("✅ Model loaded successfully (standard).")
            
        # Store model info
        self.model_info = {
            "name": model_name_or_path,
            "quantization": "4-bit" if use_4bit else "8-bit" if load_in_8bit else "full",
            "device": str(self.device),
            "loaded_at": datetime.now().isoformat()
        }

    def generate(self, prompt: str, max_new_tokens: int = 512, temperature: float = 0.7, **kwargs) -> str:
        """
        Generate response for Rails upgrade queries.
        
        Args:
            prompt: Input prompt (preferably Rails-specific)
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.1-1.0)
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
        """
        # Rails-specific prompt enhancement
        enhanced_prompt = self._enhance_rails_prompt(prompt)
        
        # Tokenize input
        inputs = self.tokenizer(
            enhanced_prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=2048
        )
        
        if self.device == "cuda":
            inputs = inputs.to("cuda")

        # Generation parameters optimized for Rails code
        generation_params = {
            "max_new_tokens": max_new_tokens,
            "do_sample": True,
            "temperature": min(temperature, 0.7),  # Cap temperature to reduce hallucinations
            "top_p": 0.9,  # More focused sampling
            "top_k": 40,   # Reduced for better quality
            "repetition_penalty": 1.2,  # Higher penalty for repetition
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
            **kwargs
        }

        try:
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    **generation_params
                )

            # Decode and clean response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the new content (remove the prompt)
            if enhanced_prompt in response:
                response = response.replace(enhanced_prompt, "").strip()
                
            return response
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _enhance_rails_prompt(self, prompt: str) -> str:
        """
        Enhance prompts with Rails-specific context for better responses.
        """
        rails_context = """You are a Rails expert helping with application upgrades. 
Provide specific, actionable code examples with clear explanations.
Focus on backward compatibility and gradual migration strategies.

"""
        
        return rails_context + prompt
    
    def generate_rails_suggestion(self, query: str, context: str = "", max_tokens: int = 1024) -> Dict[str, Any]:
        """
        Generate structured Rails upgrade suggestions.
        
        Args:
            query: User's Rails upgrade query
            context: Additional context from search results
            max_tokens: Maximum tokens for response
            
        Returns:
            Structured suggestion with old_code, new_code, explanation
        """
        prompt = f"""
Based on the Rails upgrade query and context, provide a specific upgrade suggestion in JSON format.

Query: {query}

Context: {context}

Please provide a JSON response with this structure:
{{
  "file_path": "path/to/file.rb",
  "old_code": "# Current code that needs updating",
  "new_code": "# Updated code for newer Rails version",
  "explanation": "Clear explanation of why this change is needed",
  "confidence": "high|medium|low",
  "rails_version": "target Rails version",
  "change_type": "deprecation|new_feature|security|performance"
}}

Provide realistic, tested code examples. Focus on one specific, actionable change.
"""
        
        response = self.generate(prompt, max_new_tokens=max_tokens, temperature=0.3)
        
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                suggestion = json.loads(json_str)
                
                # Add metadata
                suggestion['generated_by'] = 'local_llm'
                suggestion['model'] = self.model_name
                suggestion['timestamp'] = datetime.now().isoformat()
                
                return suggestion
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Failed to parse JSON response: {e}")
            
        # Fallback to text response if JSON parsing fails
        return {
            "file_path": "unknown",
            "old_code": "# Unable to generate specific code",
            "new_code": "# Please review the explanation below",
            "explanation": response,
            "confidence": "low",
            "rails_version": "unknown",
            "change_type": "general",
            "generated_by": "local_llm",
            "model": self.model_name,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return self.model_info.copy()
    
    @classmethod
    def list_recommended_models(cls) -> Dict[str, Dict[str, str]]:
        """Get list of recommended models for Rails upgrade tasks."""
        return cls.RECOMMENDED_MODELS.copy()
    
    @classmethod
    def check_system_requirements(cls) -> Dict[str, Any]:
        """Check system requirements for local LLM."""
        return {
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "cuda_memory_total": torch.cuda.get_device_properties(0).total_memory if torch.cuda.is_available() else 0,
            "recommended_memory_gb": 8,
            "minimum_memory_gb": 4
        }


def main():
    """Demo of local LLM for Rails upgrade tasks."""
    print("🚀 Rails Upgrade Local LLM Demo")
    print("=" * 50)
    
    # Check system requirements
    req = LocalLLM.check_system_requirements()
    print(f"💾 CUDA Available: {req['cuda_available']}")
    print(f"🎮 GPU Count: {req['cuda_device_count']}")
    if req['cuda_available']:
        print(f"📊 GPU Memory: {req['cuda_memory_total'] / 1024**3:.1f} GB")
    
    print("\n📋 Recommended Models:")
    for key, info in LocalLLM.list_recommended_models().items():
        print(f"  🔹 {key}: {info['name']}")
        print(f"    📝 {info['description']}")
        print(f"    💾 Memory: {info['memory']}")
        print()
    
    try:
        # Initialize local LLM
        llm = LocalLLM(use_4bit=True)
        
        print("\n🧪 Testing Rails Upgrade Query...")
        test_query = "How do I upgrade ApplicationRecord from Rails 4.2 to Rails 5?"
        
        # Test basic generation
        print(f"Query: {test_query}")
        response = llm.generate(test_query, max_new_tokens=256)
        print(f"Response: {response[:200]}...")
        
        # Test structured suggestion
        print("\n🎯 Testing Structured Suggestion...")
        suggestion = llm.generate_rails_suggestion(
            query=test_query,
            context="ApplicationRecord was introduced in Rails 5.0 as a base class for all models.",
            max_tokens=512
        )
        
        print("Generated Suggestion:")
        print(f"  📁 File: {suggestion['file_path']}")
        print(f"  🎯 Confidence: {suggestion['confidence']}")
        print(f"  📝 Explanation: {suggestion['explanation'][:100]}...")
        
        print("\n✅ Local LLM is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Try installing dependencies: pip install transformers accelerate bitsandbytes")


if __name__ == "__main__":
    main()
