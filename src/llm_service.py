# src/llm_service.py
import os
import time
from google import genai

class GeminiClient:
    """
    A resilient client for interacting with the Gemini API that handles
    key rotation, model fallbacks, and rate limit errors.
    """
    def __init__(self):
        """
        Initializes the client by loading API keys and models from environment variables.
        """
        api_keys_str = os.getenv("GEMINI_API_KEYS")
        models_str = os.getenv("GEMINI_MODELS")

        if not api_keys_str or not models_str:
            raise ValueError("GEMINI_API_KEYS and GEMINI_MODELS must be set in the .env file.")

        self.api_keys = [key.strip() for key in api_keys_str.split(',')]
        self.models = [model.strip() for model in models_str.split(',')]
        self.current_key_index = 0
        print(f"LLM Service initialized with {len(self.api_keys)} API key(s) and {len(self.models)} model(s).")

    def _get_next_key(self) -> str:
        """Rotates to the next API key and returns it."""
        key = self.api_keys[self.current_key_index]
        print(f"Using API key index: {self.current_key_index}")
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key

    def generate_content(self, prompt: str) -> str | None:
        """
        Generates content using the Gemini API with model fallback and key rotation.

        Args:
            prompt (str): The full prompt to send to the model.

        Returns:
            str | None: The text response from the model, or None if all attempts fail.
        """
        # Loop through each model (primary, then fallbacks)
        for model_name in self.models:
            # Try each API key for the current model
            for _ in range(len(self.api_keys)):
                try:
                    api_key = self._get_next_key()
                    
                    # Create a client configured with the specific key for this attempt.
                    client = genai.Client(api_key=api_key)

                    print(f"Attempting to generate content with model: {model_name}...")
                    
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    
                    print("Successfully received response from API.")
                    return response.text

                except Exception as e:
                    # Specifically check for the rate limit error (429)
                    if "429" in str(e) and "RESOURCE_EXHAUSTED" in str(e):
                        print(f"Rate limit hit for the current key. Trying next key...")
                        time.sleep(1) # Wait a second before retrying
                        continue # Try the next key
                    else:
                        # For any other error, print it and try the next model
                        print(f"An unexpected error occurred with model {model_name}: {e}")
                        break # Break the inner loop (keys) and try the next model
            
            print(f"All API keys failed for model {model_name}. Trying next model...")

        print("All models and API keys failed. Could not get a response.")
        return None