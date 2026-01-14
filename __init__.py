import requests
import os


class PromptTunerNode:
    """
    ComfyUI node that tunes/expands simple prompts into detailed image generation prompts
    using free LLM APIs (Ollama local or Groq cloud).
    Supports custom instruction override/merge and exposes the effective system prompt for debugging.

    Notes:
    - Groq model IDs change over time. This node includes a remap for deprecated IDs
      so older workflows don't hard-fail with HTTP 400.
    """

    # Backward-compatibility: deprecated Groq model IDs -> supported replacements
    GROQ_MODEL_REMAP = {
        "llama3-70b-8192": "llama-3.3-70b-versatile",
        "mixtral-8x7b-32768": "llama-3.3-70b-versatile",
        "gemma2-9b-it": "llama-3.1-8b-instant",
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "simple_prompt": ("STRING", {
                    "default": "a leopard resting on a large tree branch, three-quarter profile view",
                    "multiline": True
                }),
                "llm_provider": (["groq", "ollama"], {"default": "groq"}),
                # Keep this list to currently supported Groq IDs to avoid 400s from dead models.
                # If you use Ollama, you must enter an Ollama-installed model name here (ComfyUI dropdown limitation).
                "model": ([
                    "llama-3.3-70b-versatile",
                    "llama-3.1-8b-instant",
                    "openai/gpt-oss-120b",
                    "openai/gpt-oss-20b",
                ], {"default": "llama-3.3-70b-versatile"}),
                "style": (["cinematic", "anime", "photorealistic", "artistic", "niji"], {"default": "cinematic"}),
                "detail_level": (["minimal", "medium", "detailed", "extreme"], {"default": "detailed"}),
            },
            "optional": {
                "groq_api_key": ("STRING", {"default": "", "multiline": False}),
                "custom_instructions": ("STRING", {"default": "", "multiline": True}),
                "merge_default_instructions": ("BOOLEAN", {"default": False}),
                "output_negative_prompt": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING",)
    RETURN_NAMES = ("positive_prompt", "negative_prompt", "system_prompt",)
    FUNCTION = "tune_prompt"
    CATEGORY = "Peteclt92/AI"

    def _normalize_groq_model(self, model: str) -> str:
        return self.GROQ_MODEL_REMAP.get(model, model)

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

        return f"""You are an expert AI image generation prompt engineer. Your task is to tune simple prompts into detailed, high-quality prompts for image generation models like Stable Diffusion, Midjourney, or Flux.

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
        except requests.exceptions.Timeout:
            return "ERROR: Ollama request timed out"
        except requests.exceptions.HTTPError as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            body = getattr(getattr(e, "response", None), "text", "")
            return f"ERROR: Ollama HTTP error{f' ({status})' if status else ''} - {body[:800] if body else str(e)}"
        except Exception as e:
            return f"ERROR: Ollama error - {str(e)}"

    def call_groq(self, prompt, system_prompt, model, api_key):
        """Call Groq API (OpenAI-compatible chat completions)"""
        if not api_key:
            api_key = os.environ.get("GROQ_API_KEY", "")

        if not api_key:
            return "ERROR: Groq API key required. Get free key at console.groq.com"

        groq_model = self._normalize_groq_model(model)

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
                        {"role": "user", "content": f"Tune this simple prompt into a detailed image generation prompt: {prompt}"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1024,
                },
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

        except requests.exceptions.Timeout:
            return "ERROR: Groq request timed out"
        except requests.exceptions.HTTPError as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            body = getattr(getattr(e, "response", None), "text", "")
            if status == 401:
                return "ERROR: Invalid Groq API key"
            # Include response body (truncated) so 400s explain exactly what Groq rejected.
            return f"ERROR: Groq API HTTP error ({status}) - {body[:800] if body else str(e)}"
        except Exception as e:
            return f"ERROR: Groq error - {str(e)}"

    def parse_response(self, response, include_negative):
        """Parse LLM response to extract positive and negative prompts"""
        if response.startswith("ERROR:"):
            return response, ""

        if include_negative and "POSITIVE:" in response and "NEGATIVE:" in response:
            try:
                parts = response.split("NEGATIVE:", 1)
                positive = parts[0].replace("POSITIVE:", "", 1).strip()
                negative = parts[1].strip()
                return positive, negative
            except Exception:
                pass

        default_negative = "blurry, low quality, distorted, deformed, ugly, bad anatomy, watermark, signature, text"
        return response.strip(), default_negative

    def tune_prompt(
        self,
        simple_prompt,
        llm_provider,
        model,
        style,
        detail_level,
        groq_api_key="",
        custom_instructions="",
        merge_default_instructions=False,
        output_negative_prompt=True
    ):
        custom_text = (custom_instructions or "").strip()

        if custom_text:
            if merge_default_instructions:
                system_prompt = self.get_system_prompt(style, detail_level, output_negative_prompt).rstrip() + "\n\n" + custom_text
            else:
                system_prompt = custom_text
        else:
            system_prompt = self.get_system_prompt(style, detail_level, output_negative_prompt)

        if llm_provider == "ollama":
            response = self.call_ollama(simple_prompt, system_prompt, model)
        else:
            response = self.call_groq(simple_prompt, system_prompt, model, groq_api_key)

        positive, negative = self.parse_response(response, output_negative_prompt)
        return (positive, negative, system_prompt)


class PromptTunerSimpleNode:
    """
    Simplified version - Ollama only.
    Supports custom instruction override of the built-in system instructions.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "simple_prompt": ("STRING", {
                    "default": "a girl walking in rain",
                    "multiline": True
                }),
            },
            "optional": {
                "custom_instructions": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tuned_prompt",)
    FUNCTION = "tune"
    CATEGORY = "Peteclt92/AI"

    def tune(self, simple_prompt, custom_instructions=""):
        built_in_system = (
            "Expand the following key concept or prompt to add more detail for a sota t2i model. "
            "Create a detailed prompt with every possible detail, around 150-200 words.\n"
            "Style focus: Focus on photorealistic details, natural lighting, real-world textures, authentic materials, high resolution.\n"
            "Rules:\n"
            "- Add specific details about lighting, atmosphere, composition, colors, textures\n"
            "- Describe clothing, environment, mood, time of day when relevant\n"
            "- Use comma-separated descriptive phrases\n"
            "- DO NOT add any explanations, just output the prompt(s)"
        )

        system = (custom_instructions or "").strip() or built_in_system

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": f"Tune: {simple_prompt}",
                    "system": system,
                    "stream": False,
                },
                timeout=60
            )
            response.raise_for_status()
            result = response.json().get("response", simple_prompt)
            return (result.strip(),)
        except Exception:
            return (f"{simple_prompt}, detailed, high quality, masterpiece",)


NODE_CLASS_MAPPINGS = {
    "PromptTunerNode": PromptTunerNode,
    "PromptTunerSimple": PromptTunerSimpleNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptTunerNode": "🎛️ Prompt Tuner (LLM)",
    "PromptTunerSimple": "🎛️ Prompt Tuner (Simple)",
}
