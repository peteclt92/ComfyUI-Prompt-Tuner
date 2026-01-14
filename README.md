# 🎛️ ComfyUI Prompt Tuner

An LLM-powered prompt tuning node for ComfyUI. Turn short prompts into detailed, model-ready **positive** prompts (and optionally **negative** prompts), using either Groq (cloud) or Ollama (local).

![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- 🚀 **Groq API** support (fast, generous free tier)
- 🏠 **Ollama** support (local, offline)
- 🎬 **5 Styles**: cinematic, anime, photorealistic, artistic, niji
- 📊 **4 Detail Levels**: minimal, medium, detailed, extreme
- ✅ **Positive + Negative** prompt output (toggleable)
- 🧩 **Custom instructions** with a clean override/merge model
- 🪲 **Debug output (advanced node)**: exposes the exact **system prompt** sent to the LLM
- 🧯 Groq **deprecated model ID remap** to avoid hard failures in older workflows

## 📦 Installation

Manual installation via Git:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/peteclt92/ComfyUI-Prompt-Tuner.git
```

Restart ComfyUI after installation.

## 🔑 API Setup

### Groq (Recommended)

1. Go to https://console.groq.com
2. Create an account
3. Create an API key
4. Paste the key into the node, or set an environment variable:

**Windows (Command Prompt):**
```cmd
setx GROQ_API_KEY "gsk_xxxxxxxxxxxxx"
```

**Windows (PowerShell):**
```powershell
[Environment]::SetEnvironmentVariable("GROQ_API_KEY", "gsk_xxxxxxxxxxxxx", "User")
```

**Linux/Mac:**
```bash
export GROQ_API_KEY="gsk_xxxxxxxxxxxxx"
```

### Ollama (Local/Offline)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download a model (example)
ollama pull llama3.2

# Start Ollama server
ollama serve
```

## 🎯 Nodes and Usage

Nodes are located under: **Peteclt92/AI**

### Node: `🎛️ Prompt Tuner (LLM)` (Advanced)

Supports Groq + Ollama, styles, detail levels, negative prompts, custom instructions, and debug output.

**Default prompt example**
```text
a leopard resting on a large tree branch, three-quarter profile view
```

**Inputs**
- `simple_prompt`: the short prompt you want to tune/expand
- `llm_provider`: `groq` or `ollama`
- `model`: the LLM model identifier  
  - Groq dropdown includes only currently supported Groq IDs  
  - Older workflows referencing deprecated Groq model IDs are auto-remapped to supported replacements
- `style`: cinematic / anime / photorealistic / artistic / niji
- `detail_level`: minimal / medium / detailed / extreme
- `groq_api_key`: optional if `GROQ_API_KEY` is set
- `custom_instructions`: your own instruction block for the LLM
- `merge_default_instructions`:
  - `false` (default): if `custom_instructions` is set, it **fully overrides** the built-in style/detail instructions
  - `true`: if `custom_instructions` is set, it will be **appended** after the built-in style/detail instructions
- `output_negative_prompt`: generate a negative prompt section (true/false)

**Outputs**
- `positive_prompt`: tuned/expanded prompt
- `negative_prompt`: negative prompt (generated when parseable, otherwise a fallback default)
- `system_prompt`: the exact instruction text that was sent to the LLM (debugging)

### Node: `🎛️ Prompt Tuner (Simple)`

Ollama-only node with minimal controls.

**Built-in behavior**
- Uses a fixed, photorealistic instruction preset targeting ~150–200 words.
- If `custom_instructions` is provided, it **fully overrides** the built-in instructions.

**Inputs**
- `simple_prompt`
- `custom_instructions` (optional)

**Output**
- `tuned_prompt`

## 🧠 Custom Instructions: Override vs Merge (Advanced Node)

If `custom_instructions` is empty, the node uses its built-in prompt engineering instructions (style + detail level + formatting rules).

If `custom_instructions` is set:
- With `merge_default_instructions = false`, your custom text becomes the **only** system prompt sent to the model.
- With `merge_default_instructions = true`, the node sends **defaults first**, then your custom text after it.

Note: if you want a negative prompt in full override mode, your `custom_instructions` must explicitly require the output format:
`POSITIVE: ...` and `NEGATIVE: ...` (otherwise the node will fall back to a default negative prompt).

## 🧩 Groq Model Compatibility Notes

Groq periodically retires model IDs. This repo keeps the UI dropdown restricted to currently supported Groq IDs to reduce 400 errors.  
For backward compatibility, the node also remaps a few common deprecated IDs used by older workflows to modern replacements.

## 📸 Example

**Input**
```text
a leopard resting on a large tree branch, three-quarter profile view
```

**Possible output (photorealistic, detailed)**
```text
A powerful adult leopard resting along a thick, moss-dusted tree branch in a sunlit savanna woodland, three-quarter profile view with the head slightly turned toward the camera, alert amber eyes and fine whisker detail, short dense coat with crisp rosette patterning, subtle scars and natural fur clumping, dappled midday light filtering through leaves creating soft shadow shapes across the shoulder and flank, realistic bark texture and lichen, shallow depth of field with a gently blurred background canopy, natural color balance, high resolution, sharp focus on the face and paws, calm yet watchful mood, photorealistic detail, clean composition
```

## 🛠️ Requirements

- ComfyUI
- Python 3.10+
- `requests` (commonly already present in ComfyUI environments)

## 📄 License

MIT — see `LICENSE`.

## 🙏 Credits

Original concept and base implementation by **Bora Ozkut**.
