# src/model/gemini_llm.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

class GeminiLLM:
    def __init__(self, model: str = None):
        # Load environment variables
        load_dotenv()
        
        # Get API key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in .env file.")
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Set model (use env var or default)
        self.model_name = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.model = genai.GenerativeModel(self.model_name)
        
        # Get generation settings from env or use defaults
        self.temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
        self.max_output_tokens = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "2048"))
        
        print(f"GeminiLLM initialized for model: {self.model_name}")

    def generate(self, prompt: str, max_new_tokens: int = None, temperature: float = None) -> str:
        """Generate text using Gemini API"""
        try:
            # Use provided parameters or fall back to instance defaults
            temp = temperature if temperature is not None else self.temperature
            max_tokens = max_new_tokens if max_new_tokens is not None else self.max_output_tokens
            
            # Create generation config
            generation_config = genai.GenerationConfig(
                temperature=temp,
                max_output_tokens=max_tokens,
                top_p=0.95,
                top_k=40
            )
            
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract text from response
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    return candidate.content.parts[0].text.strip()
                else:
                    return f"Response blocked. Finish reason: {candidate.finish_reason}"
            else:
                # Handle cases where response might be blocked or empty
                return f"No response generated. Response: {response}"
                
        except Exception as e:
            return f"Error generating response: {str(e)}"

if __name__ == "__main__":
    # Test the Gemini LLM
    try:
        gemini = GeminiLLM()
        test_prompt = "Say hello from Gemini API for a Rails upgrade agent test."
        response = gemini.generate(test_prompt, max_new_tokens=100)
        print("Test Response:")
        print(response)
    except Exception as e:
        print(f"Test failed: {e}")
        print("Make sure to set GEMINI_API_KEY in your .env file")
