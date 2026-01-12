import requests
import json
import os

class PromptExpanderNode:
    """
    ComfyUI node that expands simple prompts into detailed image generation prompts
    using free LLM APIs (Ollama local or Groq cloud)
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "simple_prompt": ("STRING", {
                    "default": "boy, blonde, driving a car in San Francisco",
                    "multiline": True
                }),
                "llm_provider": (["groq", "ollama"], {"default": "groq"}),
                "model": ([
                    "llama-3.3-70b-versatile",
                    "llama-3.1-8b-instant", 
                    "llama3-70b-8192",
                    "mixtral-8x7b-32768",
                    "gemma2-9b-it"
                ], {"default": "llama-3.3-70b-versatile"}),
                "style": (["cinematic", "anime", "photorealistic", "artistic", "niji"], {"default": "cinematic"}),
                "detail_level": (["minimal", "medium", "detailed", "extreme"], {"default": "detailed"}),
            },
            "optional": {
                "groq_api_key": ("STRING", {"default": "", "multiline": False}),
                "custom_instructions": ("STRING", {
                    "default": "",
                    "multiline": True
                }),
                "negative_prompt_request": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("positive_prompt", "negative_prompt",)
    FUNCTION = "expand_prompt"
    CATEGORY = "BoraOzkut/AI"

    def get_system_prompt(self, style, detail_level, include_negative):
        detail_instructions = {
            "minimal": "Keep the expanded prompt concise, around 50-80 words.",
            "medium": "Create a moderately detailed prompt, around 80-120 words.",
            "detailed": "Create a comprehensive detailed prompt, around 120-180 words.",
            "extreme": "Create an extremely detailed prompt with every possible detail, around 180-250 words."
        }
        
        style_instructions = {
            "cinematic": "Focus on cinematic lighting, dramatic composition, film-like quality, depth of field, color grading.",
            "anime": "Focus on anime/manga aesthetics, vibrant colors, expressive features, dynamic poses, cel-shading style.",
            "photorealistic": "Focus on photorealistic details, natural lighting, real-world textures, authentic materials, high resolution.",
            "artistic": "Focus on artistic interpretation, creative composition, painterly qualities, unique visual style.",
            "niji": "Focus on Japanese anime style, cute aesthetics, soft colors, detailed backgrounds, Studio Ghibli or modern anime influence."
        }
        
        negative_section = """

Also provide a negative prompt that lists things to avoid. Format your response EXACTLY as:
POSITIVE: [your expanded positive prompt here]
NEGATIVE: [your negative prompt here]""" if include_negative else """

Format your response as just the expanded prompt, nothing else."""

        return f"""You are an expert AI image generation prompt engineer. Your task is to expand simple prompts into detailed, high-quality prompts for image generation models like Stable Diffusion, Midjourney, or Flux.

Style focus: {style_instructions.get(style, style_instructions['cinematic'])}

{detail_instructions.get(detail_level, detail_instructions['detailed'])}

Rules:
- Add specific details about lighting, atmosphere, composition, colors, textures
- Include quality tags appropriate for the style (e.g., "masterpiece, best quality" for anime)
- Describe clothing, environment, mood, time of day when relevant
- Use comma-separated descriptive phrases
- DO NOT add any explanations, just output the prompt(s)
{negative_section}"""

    def call_ollama(self, prompt, system_prompt, model):
        """Call local Ollama API"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.ConnectionError:
            return "ERROR: Cannot connect to Ollama. Make sure Ollama is running (ollama serve)"
        except Exception as e:
            return f"ERROR: Ollama error - {str(e)}"

    def call_groq(self, prompt, system_prompt, model, api_key):
        """Call Groq API (free tier available)"""
        if not api_key:
            # Try environment variable
            api_key = os.environ.get("GROQ_API_KEY", "")
        
        if not api_key:
            return "ERROR: Groq API key required. Get free key at console.groq.com"
        
        # Model is already the correct Groq model ID from dropdown
        groq_model = model
        
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": groq_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Expand this simple prompt into a detailed image generation prompt: {prompt}"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1024,
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                return "ERROR: Invalid Groq API key"
            return f"ERROR: Groq API error - {str(e)}"
        except Exception as e:
            return f"ERROR: Groq error - {str(e)}"

    def parse_response(self, response, include_negative):
        """Parse LLM response to extract positive and negative prompts"""
        if response.startswith("ERROR:"):
            return response, ""
        
        if include_negative and "POSITIVE:" in response and "NEGATIVE:" in response:
            try:
                parts = response.split("NEGATIVE:")
                positive = parts[0].replace("POSITIVE:", "").strip()
                negative = parts[1].strip()
                return positive, negative
            except:
                pass
        
        # Default negative prompts by common issues
        default_negative = "blurry, low quality, distorted, deformed, ugly, bad anatomy, watermark, signature, text"
        
        return response.strip(), default_negative

    def expand_prompt(self, simple_prompt, llm_provider, model, style, detail_level, 
                      groq_api_key="", custom_instructions="", negative_prompt_request=True):
        
        system_prompt = self.get_system_prompt(style, detail_level, negative_prompt_request)
        
        if custom_instructions:
            system_prompt += f"\n\nAdditional instructions: {custom_instructions}"
        
        # Call appropriate LLM
        if llm_provider == "ollama":
            response = self.call_ollama(simple_prompt, system_prompt, model)
        else:  # groq
            response = self.call_groq(simple_prompt, system_prompt, model, groq_api_key)
        
        # Parse response
        positive, negative = self.parse_response(response, negative_prompt_request)
        
        return (positive, negative,)


class PromptExpanderSimpleNode:
    """
    Simplified version - just Ollama, no options
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "simple_prompt": ("STRING", {
                    "default": "a girl walking in rain",
                    "multiline": True
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("expanded_prompt",)
    FUNCTION = "expand"
    CATEGORY = "BoraOzkut/AI"

    def expand(self, simple_prompt):
        system = """You are a prompt engineer. Expand simple prompts into detailed image generation prompts.
Add lighting, atmosphere, composition, quality tags. Output ONLY the expanded prompt, nothing else."""
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": f"Expand: {simple_prompt}",
                    "system": system,
                    "stream": False,
                },
                timeout=60
            )
            result = response.json().get("response", simple_prompt)
            return (result.strip(),)
        except:
            return (f"{simple_prompt}, detailed, high quality, masterpiece",)


# Node registration
NODE_CLASS_MAPPINGS = {
    "PromptExpanderNode": PromptExpanderNode,
    "PromptExpanderSimple": PromptExpanderSimpleNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptExpanderNode": "🎨 Prompt Expander (LLM)",
    "PromptExpanderSimple": "🎨 Prompt Expander (Simple)",
}
